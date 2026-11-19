#!/bin/bash
set -u
export LD_LIBRARY_PATH=/usr/local/nvidia/lib64:${LD_LIBRARY_PATH:-}
RUN_ID=$1; DIFF=$2; LLM=$3; W=$4; H=$5; SEED=$6; shift 6
CLI=/root/bench/repos/stable-diffusion.cpp/build/bin/sd-cli
VAE=/root/bench/models/comfy/vae/minimax_h3_image_vae_fp16.safetensors
RUN=/kaggle/working/bench/results/$RUN_ID
mkdir -p "$RUN"
PROMPT=${PROMPT:-"A silver tabby kitten holding a sign reading 'sd.cpp', natural daylight"}
echo "$PROMPT" > "$RUN/prompt.txt"
nvidia-smi --query-gpu=index,utilization.gpu,memory.used,memory.total --format=csv,noheader -l 1 > "$RUN/gpu.csv" 2>/dev/null &
SMID=$!
START=$(date +%s.%N)
"$CLI" --diffusion-model "$DIFF" --vae "$VAE" --llm "$LLM" \
  -p "$PROMPT" -o "$RUN/out.png" \
  --cfg-scale 1.0 --steps 6 --sampling-method euler --sigmas minimax-h3-image \
  -W "$W" -H "$H" --rng cpu --seed "$SEED" \
  --offload-to-cpu --vae-tiling "$@" > "$RUN/sd.log" 2>&1
RC=$?
END=$(date +%s.%N)
kill $SMID 2>/dev/null || true
python3 - "$RUN" "$START" "$END" "$RC" <<'PY'
import sys, csv
run,start,end,rc=sys.argv[1],float(sys.argv[2]),float(sys.argv[3]),sys.argv[4]
peak={}
try:
  for row in csv.reader(open(f'{run}/gpu.csv')):
    if len(row)<4: continue
    try: v=int(row[2].split()[0])
    except ValueError: continue
    peak[row[0]]=max(peak.get(row[0],0),v)
except FileNotFoundError: pass
open(f'{run}/metrics.txt','w').write(f"exit_code={rc}\nwall_seconds={end-start:.3f}\npeak_vram_mib={peak}\n")
print(f"RUN {run}: rc={rc} wall={end-start:.1f}s peak_vram_mib={peak}")
PY
exit $RC
