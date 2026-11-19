import sys, time, os, json
os.environ['TMPDIR']='/kaggle/working/bench/tmp'
import torch
from diffsynth.configs import MODEL_CONFIGS
from diffsynth.pipelines.minimax_h3_image import MiniMaxH3ImagePipeline, ModelConfig

run_id, W, H, seed = sys.argv[1], int(sys.argv[2]), int(sys.argv[3]), int(sys.argv[4])
E='/root/bench/models/diffsynth/DiffSynth-Studio__MiniMax-H3-Image-EntroPack/models'
T='/kaggle/working/bench/models/diffsynth/text_encoder'
B='/kaggle/working/bench/models/diffsynth/base'
# Turing has no BF16 tensor cores: use FP16 as the preparing/computing dtype.
vram_config = {
  "offload_dtype": "disk", "offload_device": "disk",
  "onload_dtype": "disk", "onload_device": "disk",
  "preparing_dtype": torch.bfloat16, "preparing_device": "cuda",
  "computation_dtype": torch.bfloat16, "computation_device": "cuda",
}
def cfg(path, sidecar=None):
    if sidecar:
        entry=json.load(open(sidecar))
        if not any(c.get("model_hash")==entry.get("model_hash") for c in MODEL_CONFIGS):
            MODEL_CONFIGS.append(entry)
    return ModelConfig(path=path, **vram_config)

pipe = MiniMaxH3ImagePipeline.from_pretrained(
    torch_dtype=torch.bfloat16, device="cuda",
    model_configs=[
        cfg(E+'/dit_extreme_3bpp.safetensors', E+'/dit_extreme_3bpp.json'),
        cfg(T+'/text_encoder_3bpp.safetensors', T+'/text_encoder_3bpp.json'),
        cfg(B+'/pdd_fused_heads.safetensors'),
        cfg(E+'/vae_int8.safetensors', E+'/vae_int8.json'),
    ],
    processor_config=ModelConfig(path=B+'/processor'),
    vram_limit=int(os.environ.get("VRAM_LIMIT","13")),
)
prompt = "A silver tabby kitten holding a sign reading 'sd.cpp', natural daylight"
out='/kaggle/working/bench/results/'+run_id
os.makedirs(out, exist_ok=True)
open(out+'/prompt.txt','w').write(prompt)
t0=time.time()
img = pipe(prompt=prompt, height=H, width=W, seed=seed,
           min_generation_area=1024, tiling=True)
wall=time.time()-t0
img.save(out+'/out.png')
open(out+'/metrics.txt','w').write(
  f"exit_code=0\nwall_seconds={wall:.3f}\npeak_vram_mib={{'0': {torch.cuda.max_memory_allocated()//(1024*1024)}}}\n")
print(f"RUN {run_id}: wall={wall:.1f}s peak={torch.cuda.max_memory_allocated()//(1024*1024)}MiB")
