#!/bin/bash
set -u
export LD_LIBRARY_PATH=/usr/local/nvidia/lib64:${LD_LIBRARY_PATH:-}
R=$1; SEED=$2; M=SDXL_XL
CLI=/root/bench/repos/stable-diffusion.cpp/build/bin/sd-cli
CK=/kaggle/working/quadbench/models/sdxl/sd_xl_base_1.0.safetensors
VAE=/kaggle/working/quadbench/models/sdxl/sdxl_vae.safetensors
OUT=/kaggle/working/quadbench/results/$R
mkdir -p "$OUT"
PROMPT=${PROMPT:-"A silver tabby kitten holding a sign reading 'sd.cpp', natural daylight"}
echo "$PROMPT" > "$OUT/prompt.txt"
echo "model=$M steps=30 cfg=7.0 size=1024x1024 seed=$SEED" > "$OUT/meta.txt"
nvidia-smi --query-gpu=index,utilization.gpu,memory.used,memory.total --format=csv,noheader -l 1 > "$OUT/gpu.csv" 2>/dev/null &
SM=$!
START=$(date +%s.%N)
"$CLI" -m "$CK" --vae "$VAE" -p "$PROMPT" -o "$OUT/out.png" \
  --cfg-scale 7.0 --steps 30 --sampling-method euler -W 1024 -H 1024 \
  --rng cpu --seed "$SEED" --vae-tiling --max-vram 12 > "$OUT/sd.log" 2>&1
RC=$?
END=$(date +%s.%N)
kill $SM 2>/dev/null || true
python3 - "$OUT" "$START" "$END" "$RC" "$SEED" <<'PY'
import sys,csv
r=sys.argv[1]; st,en=float(sys.argv[2]),float(sys.argv[3]); rc=sys.argv[4]; seed=sys.argv[5]
peak={}
try:
  for row in csv.reader(open(r+'/gpu.csv')):
    if len(row)<4: continue
    try: v=int(row[2].split()[0])
    except ValueError: continue
    peak[row[0]]=max(peak.get(row[0],0),v)
except FileNotFoundError: pass
open(r+'/metrics.txt','w').write(f"exit_code={rc}\nwall_seconds={en-st:.3f}\npeak_vram_mib={peak}\n")
print(f"sdxl,1024x1024,{seed},30,7.0,,{rc},{en-st:.3f},{peak.get('0',0)}")
PY
exit $RC
