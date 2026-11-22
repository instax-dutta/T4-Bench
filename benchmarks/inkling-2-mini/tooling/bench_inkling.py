#!/usr/bin/env python3
"""Benchmark driver for Inkling-2-Mini (and quants) on 2x Tesla T4.

One CSV row per measurement, appended to /workspace/weights/inkling_results.csv:
  engine,quant,gpus,ctx,run,pp_tok_s,tg_tok_s,eval_count,eval_tok_s,load_ms,wall_s,exit_code,gpu0_peak_mib,gpu1_peak_mib,note

Modes:
  llama-bench wrapper: python3 bench_inkling.py llamacpp <gguf> <gpus 1|2> [ctx]
    runs: llama-bench -m <gguf> -ngl 99 [-ts 1,1] -p 512 -n 256 -r 3 -c <ctx>
    plus 1 Hz nvidia-smi peak sampling around the whole process.
  ollama wrapper: python3 bench_inkling.py ollama <model-tag> <gpus> [ctx]
    warm run first (model load), then 3 timed /api/generate calls;
    tokens/s from eval_count / eval_duration.
  vision e2e: python3 bench_inkling.py vision <gguf> <mmproj> <gpus> [ctx]
    llama-server + one image chat completion, wall time and peaks recorded.
  attempt: python3 bench_inkling.py attempt <engine> <cmd...>
    run a command with a timeout, record exit code + last log line.
"""
import csv
import os
import re
import subprocess
import sys
import threading
import time

W = "/workspace/weights"
CSV = f"{W}/inkling_results.csv"
LOGS = f"{W}/logs"
HEADER = ["engine", "quant", "gpus", "ctx", "run", "pp_tok_s", "tg_tok_s",
          "eval_count", "eval_tok_s", "load_ms", "wall_s", "exit_code",
          "gpu0_peak_mib", "gpu1_peak_mib", "note"]

ENV = dict(os.environ)
ENV["LD_LIBRARY_PATH"] = "/usr/local/nvidia/lib64:/usr/local/cuda-13.0/lib64"

# 1 Hz per-GPU memory peak sampler, same protocol as the repo's other benchmarks
peaks = {}


def sampler_on():
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


def sampler_off(stop, holder):
    stop.set()
    time.sleep(1.5)
    peaks.update(holder)
    return holder.get(0, 0), holder.get(1, 0)


def row(**kw):
    r = [kw.get(k, "") for k in HEADER]
    with open(CSV, "a", newline="") as f:
        csv.writer(f).writerow(r)
    print("[row] " + ",".join(str(x) for x in r), flush=True)


def timed_run(cmd, log_path, timeout=3600):
    t0 = time.time()
    with open(log_path, "w") as log:
        try:
            p = subprocess.run(cmd, env=ENV, stdout=log,
                               stderr=subprocess.STDOUT, timeout=timeout)
            return p.returncode, time.time() - t0
        except subprocess.TimeoutExpired:
            return 124, time.time() - t0


def llamacpp(gguf, gpus, ctx, run_id):
    name = os.path.basename(gguf).replace(".gguf", "")
    cmd = ["/workspace/llama.cpp/build/bin/llama-bench", "-m", gguf,
           "-ngl", "99", "-p", "512", "-n", "256", "-r", "3",
           "-c", str(ctx)]
    if int(gpus) == 2:
        cmd += ["-ts", "1,1"]
    stop, holder = sampler_on()
    code, wall = timed_run(cmd, f"{LOGS}/llamacpp_{name}_{run_id}.log")
    g0, g1 = sampler_off(stop, holder)
    pp = tg = load_ms = ""
    try:
        text = open(f"{LOGS}/llamacpp_{name}_{run_id}.log").read()
        # llama-bench prints: | config | test | t/s |
        load_ms = (re.search(r"load ms\s*[|:]\s*([\d.]+)", text) or [None, ""])[1]
        for line in text.splitlines():
            if line.startswith("|") and "pp512" in line:
                pp = line.rsplit("|", 2)[-2].strip()
            if line.startswith("|") and "tg256" in line:
                tg = line.rsplit("|", 2)[-2].strip()
    except Exception:
        pass
    row(engine="llama.cpp", quant=name, gpus=gpus, ctx=ctx, run=run_id,
        pp_tok_s=pp, tg_tok_s=tg, load_ms=load_ms, wall_s=f"{wall:.1f}",
        exit_code=code, gpu0_peak_mib=g0, gpu1_peak_mib=g1)


def ollama(model, gpus, ctx, run_id):
    # warm run (load), then 3 timed calls
    warm = subprocess.run(
        ["curl", "-s", "http://localhost:11434/api/generate", "-d",
         '{"model":"%s","prompt":"warm","stream":false,"options":{"num_ctx":%d}}'
         % (model, ctx)], env=ENV, capture_output=True, text=True, timeout=1200)
    for i in range(1, 4):
        stop, holder = sampler_on()
        t0 = time.time()
        p = subprocess.run(
            ["curl", "-s", "http://localhost:11434/api/generate", "-d",
             '{"model":"%s","prompt":"Write a 200-word story about a lighthouse keeper.",'
             '"stream":false,"options":{"num_ctx":%d,"seed":42,"temperature":0}}'
             % (model, ctx)],
            env=ENV, capture_output=True, text=True, timeout=2400)
        wall = time.time() - t0
        g0, g1 = sampler_off(stop, holder)
        ec = et = lc = ""
        try:
            m = re.search(r'"eval_count":(\d+)', p.stdout)
            d = re.search(r'"eval_duration":(\d+)', p.stdout)
            ld = re.search(r'"load_duration":(\d+)', p.stdout)
            if m and d and int(d.group(1)) > 0:
                ec = m.group(1)
                et = f"{int(ec) / (int(d.group(1)) / 1e9):.2f}"
            if ld:
                lc = str(int(ld.group(1)) // 1000000)
        except Exception:
            pass
        row(engine="ollama", quant=model, gpus=gpus, ctx=ctx, run=i,
            eval_count=ec, eval_tok_s=et, load_ms=lc, wall_s=f"{wall:.1f}",
            exit_code=p.returncode if not ec else 0,
            gpu0_peak_mib=g0, gpu1_peak_mib=g1)


def vision(gguf, mmproj, gpus, ctx):
    name = os.path.basename(gguf).replace(".gguf", "")
    port = 8765
    cmd = ["/workspace/llama.cpp/build/bin/llama-server", "-m", gguf,
           "--mmproj", mmproj, "--jinja", "-c", str(ctx), "-ngl", "99",
           "--host", "127.0.0.1", "--port", str(port)]
    if int(gpus) == 2:
        cmd += ["-ts", "1,1"]
    stop, holder = sampler_on()
    server = subprocess.Popen(cmd, env=ENV,
                              stdout=open(f"{LOGS}/vision_{name}.log", "w"),
                              stderr=subprocess.STDOUT)
    time.sleep(30)  # load window; llama-server signals readiness in log
    body = ('{"messages":[{"role":"user","content":[{"type":"image_url","'
            'image_url":{"url":"data:image/jpeg;base64,%s"}},'
            '{"type":"text","text":"Describe this image in one sentence."}]}]}'
            % open("/workspace/weights/bench_image.b64").read().strip())
    t0 = time.time()
    p = subprocess.run(["curl", "-s", f"http://127.0.0.1:{port}/v1/chat/completions",
                        "-H", "Content-Type: application/json", "-d", body],
                       env=ENV, capture_output=True, text=True, timeout=600)
    wall = time.time() - t0
    server.terminate()
    g0, g1 = sampler_off(stop, holder)
    ok = 1 if '"content"' in p.stdout or '"message"' in p.stdout else 2
    row(engine="llama.cpp-vision", quant=name, gpus=gpus, ctx=ctx, run=1,
        wall_s=f"{wall:.1f}", exit_code=ok,
        gpu0_peak_mib=g0, gpu1_peak_mib=g1,
        note=("chars=%d" % len(p.stdout))[:60])


def attempt(engine, cmd):
    stop, holder = sampler_on()
    code, wall = timed_run(cmd, f"{LOGS}/attempt_{engine}.log", timeout=900)
    g0, g1 = sampler_off(stop, holder)
    tail = ""
    try:
        tail = open(f"{LOGS}/attempt_{engine}.log").read().strip().splitlines()[-1][:80]
    except Exception:
        pass
    row(engine=engine, quant="attempt", gpus=2, ctx="", run=1,
        wall_s=f"{wall:.1f}", exit_code=code,
        gpu0_peak_mib=g0, gpu1_peak_mib=g1, note=tail)


def main():
    if len(sys.argv) < 4:
        sys.exit(__doc__)
    os.makedirs(LOGS, exist_ok=True)
    if not os.path.exists(CSV):
        with open(CSV, "w", newline="") as f:
            csv.writer(f).writerow(HEADER)
    mode = sys.argv[1]
    if mode == "llamacpp":
        llamacpp(sys.argv[2], sys.argv[3],
                 int(sys.argv[4]) if len(sys.argv) > 4 else 8192, 1)
    elif mode == "ollama":
        ollama(sys.argv[2], sys.argv[3],
               int(sys.argv[4]) if len(sys.argv) > 4 else 8192, 1)
    elif mode == "vision":
        vision(sys.argv[2], sys.argv[3], sys.argv[4],
               int(sys.argv[5]) if len(sys.argv) > 5 else 8192)
    elif mode == "attempt":
        attempt(sys.argv[2], sys.argv[3:])
    else:
        sys.exit(__doc__)


if __name__ == "__main__":
    main()
