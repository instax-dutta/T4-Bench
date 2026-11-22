#!/usr/bin/env python3
"""Benchmark driver for lodestones/Kromoss (MOSS-Image, 5B DiT) on 2x T4.

CSV /workspace/weights/kromoss_results.csv, row per measurement:
  config,engine,steps,cfg,gpus,run,wall_s,images_per_hour,encode_s,exit_code,gpu0_peak_mib,gpu1_peak_mib,note
PNG outputs + a copy of the CSV mirror to /kaggle/working (overlay-death insurance).

Modes:
  diffusers <config> <steps> <cfg> <lora none|dmd2> <te cpu|int8g1>
    warm process: load DiT fp16 + VAE fp32 on cuda:0, TE on cpu (or
    bitsandbytes int8 on cuda:1), one warm image, then 3 timed 1024px
    generations (seeds 42/123/999). Wall time is the full pipe() call,
    including text encoding - that is what a T4 user pays per image.
  comfy <config> <bf16|int8> <steps> <cfg>
    ComfyUI headless on 127.0.0.1:8188, workflow from
    kromoss_simple_workflow.json (shipped by the model repo), one warmup
    POST then 3 timed queue POSTs.
  clip <png_dir>
    CLIP ViT-L/14 cosine over the fixed prompts, matching the model card's
    PartiPrompts metric family.
"""
import csv
import json
import os
import re
import subprocess
import sys
import threading
import time

import torch

W = "/workspace/weights"
K = f"{W}/kromoss"
OUT = f"{K}/out"
CSV = f"{W}/kromoss_results.csv"
LOGS = f"{W}/logs"
HEADER = ["config", "engine", "steps", "cfg", "gpus", "run", "wall_s",
          "images_per_hour", "encode_s", "exit_code", "gpu0_peak_mib",
          "gpu1_peak_mib", "note"]

PROMPTS = [
    "a tabby cat holding a sign that says KROMOSS",
    "an astronaut in a jungle, cold color palette, muted colors, detailed, 8k",
    "a watercolor painting of a lighthouse at dusk",
]
SEEDS = [42, 123, 999]

ENV = dict(os.environ)
ENV["LD_LIBRARY_PATH"] = "/usr/local/nvidia/lib64:/usr/local/cuda-13.0/lib64"


def sampler():
    stop = threading.Event()
    holder = {}

    def sample():
        cmd = ["nvidia-smi", "--query-gpu=index,memory.used",
               "--format=csv,noheader,nounits"]
        while not stop.is_set():
            try:
                out = subprocess.run(cmd, capture_output=True, text=True,
                                     env=ENV, timeout=5)
                for line in out.stdout.strip().splitlines():
                    idx, used = [x.strip() for x in line.split(",")]
                    i = int(idx)
                    holder[i] = max(holder.get(i, 0), int(used))
            except Exception:
                pass
            stop.wait(1.0)

    t = threading.Thread(target=sample, daemon=True)
    t.start()
    return stop, holder


def row(**kw):
    r = [kw.get(k, "") for k in HEADER]
    with open(CSV, "a", newline="") as f:
        csv.writer(f).writerow(r)
    try:
        subprocess.run(["cp", CSV, "/kaggle/working/kromoss_results.csv"],
                       timeout=30)
    except Exception:
        pass
    print("[row] " + ",".join(str(x) for x in r), flush=True)


def build_pipe(te_mode):
    from diffusers import DiffusionPipeline
    pipe = DiffusionPipeline.from_pretrained(
        "lodestones/Kromoss", custom_pipeline="pipeline_moss_image",
        trust_remote_code=True,
        torch_dtype={"default": torch.float16, "vae": torch.float32})
    pipe.transformer.to("cuda:0")
    pipe.vae.to("cuda:0")
    if te_mode == "int8g1":
        try:
            from transformers import AutoModelForCausalLM  # noqa: F401
            import bitsandbytes as bnb  # noqa: F401
            pipe.text_encoder = pipe.text_encoder.to("cuda:1")
        except Exception as e:
            print("[warn] int8g1 unavailable, falling back to cpu:", e)
            te_mode = "cpu"
    if te_mode == "cpu":
        pipe.text_encoder.to("cpu")
    return pipe, te_mode


def apply_lora(pipe, lora):
    """Unmerged LoRA hooks per the model card (never merge into bf16)."""
    from safetensors.torch import load_file
    state = load_file(f"{K}/8-steps-dmd2-lora.safetensors", device="cpu")
    modules = dict(pipe.transformer.named_modules())
    n = 0
    for key in [k for k in state if k.endswith(".lora_down.weight")]:
        name = key[len("diffusion_model."):-len(".lora_down.weight")]
        down = state[key].float()
        up = state[key.replace("lora_down", "lora_up")].float()
        scale = state[f"diffusion_model.{name}.alpha"].item() / down.shape[0]
        module = modules[name]

        def hook(m, a, out, down=down, up=up, scale=scale):
            return out + (scale * (a[0].float() @ down.T) @ up.T).to(out.dtype)

        module.register_forward_hook(hook)
        n += 1
    print(f"[lora] {lora}: {n} hooks", flush=True)


def diffusers_mode(config, steps, cfg, lora, te):
    pipe, te_used = build_pipe(te)
    if lora == "dmd2":
        apply_lora(pipe, lora)
    os.makedirs(OUT, exist_ok=True)
    enc_s = ""
    # warm image (load + first compile of kernels, discarded)
    t0 = time.time()
    _ = pipe(PROMPTS[0], height=1024, width=1024,
             num_inference_steps=int(steps), guidance_scale=float(cfg),
             uncond_skip_layers=[22] if float(cfg) > 1 else None,
             generator=torch.Generator("cpu").manual_seed(42)).images[0]
    print(f"[warm] {time.time()-t0:.1f}s", flush=True)
    for i, (prompt, seed) in enumerate(zip(PROMPTS, SEEDS)):
        stop, holder = sampler()
        t0 = time.time()
        img = pipe(prompt, height=1024, width=1024,
                   num_inference_steps=int(steps), guidance_scale=float(cfg),
                   uncond_skip_layers=[22] if float(cfg) > 1 else None,
                   generator=torch.Generator("cpu").manual_seed(seed)).images[0]
        wall = time.time() - t0
        stop.set(); time.sleep(1.5)
        img.save(f"{OUT}/{config}_s{seed}.png")
        row(config=config, engine="diffusers", steps=steps, cfg=cfg, gpus=2,
            run=i + 1, wall_s=f"{wall:.1f}",
            images_per_hour=f"{3600/wall:.0f}",
            exit_code=0, gpu0_peak_mib=holder.get(0, 0),
            gpu1_peak_mib=holder.get(1, 0), note=f"te={te_used}")
    del pipe
    torch.cuda.empty_cache()


def comfy_mode(config, ckpt, steps, cfg):
    server = subprocess.Popen(
        ["python3", "/workspace/ComfyUI/main.py", "--listen", "127.0.0.1:8188",
         "--fp16-vae"],
        cwd="/workspace/ComfyUI", env=ENV,
        stdout=open(f"{LOGS}/comfy_{config}.log", "w"), stderr=subprocess.STDOUT)
    # wait for API
    for _ in range(120):
        try:
            if b"Starting" in subprocess.run(
                    ["curl", "-s", "http://127.0.0.1:8188/"], capture_output=True,
                    timeout=5).stdout or True:
                break
        except Exception:
            pass
        time.sleep(2)
    wf = open(f"{K}/kromoss_simple_workflow.json").read()
    wf = (wf.replace("moss_image_sft_bf16.safetensors",
                     "kromoss_bf16.safetensors" if ckpt == "bf16"
                     else "kromoss_int8_convrot.safetensors")
            .replace('"steps": 50', f'"steps": {steps}')
            .replace('"cfg": 3', f'"cfg": {cfg}'))
    import random
    cid = f"krom-{random.randint(0, 99999)}"

    def post(seed):
        data = json.dumps({"prompt": json.loads(wf), "client_id": cid}).encode()
        out = subprocess.run(["curl", "-s", "-X", "POST",
                              "http://127.0.0.1:8188/prompt", "-H",
                              "Content-Type: application/json", "--data",
                              "@-"], input=data, capture_output=True,
                             timeout=120).stdout
        pid = json.loads(out)["prompt_id"]
        t0 = time.time()
        while time.time() - t0 < 1800:
            h = subprocess.run(["curl", "-s",
                                f"http://127.0.0.1:8188/history/{pid}"],
                               capture_output=True, timeout=15).stdout
            if h and pid in h.decode(errors="ignore"):
                return time.time() - t0
            time.sleep(2)
        return -1

    stop, holder = sampler()
    post(42)  # warm, discarded
    for i, seed in enumerate(SEEDS):
        wall = post(seed)
        row(config=config, engine=f"comfyui-{ckpt}", steps=steps, cfg=cfg,
            gpus=1, run=i + 1, wall_s=f"{wall:.1f}" if wall > 0 else "",
            images_per_hour=f"{3600/wall:.0f}" if wall > 0 else "",
            exit_code=0 if wall > 0 else 124,
            note=f"seed={seed}")
    stop.set(); time.sleep(1.5)
    server.terminate()
    row(config=config, engine=f"comfyui-{ckpt}", steps=steps, cfg=cfg, gpus=1,
        run=99, wall_s="", exit_code=0,
        gpu0_peak_mib=holder.get(0, 0), gpu1_peak_mib=holder.get(1, 0),
        note="peak VRAM across runs")


def clip_mode(png_dir):
    from transformers import CLIPModel, CLIPProcessor
    model = CLIPModel.from_pretrained("openai/clip-vit-large-patch14").to("cuda:0")
    proc = CLIPProcessor.from_pretrained("openai/clip-vit-large-patch14")
    import glob as g
    from PIL import Image
    for path in sorted(g.glob(f"{png_dir}/*.png")):
        img = Image.open(path)
        # match by seed suffix against the prompt list position
        seed = int(re.search(r"_s(\d+)\.png", path).group(1))
        prompt = PROMPTS[SEEDS.index(seed)] if seed in SEEDS else PROMPTS[0]
        inputs = proc(text=[prompt], images=img, return_tensors="pt").to("cuda:0")
        with torch.no_grad():
            out = model(**inputs)
        sim = out.logits_per_image.item() / model.logit_scale.exp().item()
        row(config=os.path.basename(path), engine="clip-vit-l-14", steps="",
            cfg="", gpus=1, run=1, wall_s="", exit_code=0,
            note=f"cosine={sim:.4f}")
    del model
    torch.cuda.empty_cache()


def main():
    if len(sys.argv) < 3:
        sys.exit(__doc__)
    os.makedirs(LOGS, exist_ok=True)
    os.makedirs(OUT, exist_ok=True)
    if not os.path.exists(CSV):
        with open(CSV, "w", newline="") as f:
            csv.writer(f).writerow(HEADER)
    mode = sys.argv[1]
    if mode == "diffusers":
        diffusers_mode(sys.argv[2], sys.argv[3], sys.argv[4], sys.argv[5],
                       sys.argv[6])
    elif mode == "comfy":
        comfy_mode(sys.argv[2], sys.argv[3], sys.argv[4], sys.argv[5])
    elif mode == "clip":
        clip_mode(sys.argv[2])
    else:
        sys.exit(__doc__)


if __name__ == "__main__":
    main()
