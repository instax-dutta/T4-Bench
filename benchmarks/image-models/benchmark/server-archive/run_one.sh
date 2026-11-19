#!/bin/bash
# usage: run_one.sh RUN_ID MODEL_ID DIFF VAE LLM STEPS CFG SIGMAS W H SEED [extra]
set -u
export LD_LIBRARY_PATH=/usr/local/nvidia/lib64:${LD_LIBRARY_PATH:-}
R=$1; M=$2; DIFF=$3; VAE=$4; LLM=$5; STEPS=$6; CFG=$7; SIGMAS=$8; W=$9; H=${10}; SEED=${11}; shift 11
CLI=/root/bench/repos/stable-diffusion.cpp/build/bin/sd-cli
OUT=/kaggle/working/quadbench/results/$R
mkdir -p "$OUT"
PROMPT=${PROMPT:-"A silver tabby kitten holding a sign reading 'sd.cpp', natural daylight"}
echo "$PROMPT" > "$OUT/prompt.txt"
echo "model=$M steps=$STEPS cfg=$CFG sigmas=$SIGMAS size=${W}x${H} seed=$SEED" > "$OUT/meta.txt"
echo "prompt_sha256=$(sha256sum $OUT/prompt.txt | cut -d' ' -f1)" >> "$OUT/meta.txt"
nvidia-smi --query-gpu=index,utilization.gpu,memory.used,memory.total --format=csv,noheader -l 1 > "$OUT/gpu.csv" 2>/dev/null &
SM=$!
START=$(date +%s.%N)
"$CLI" --diffusion-model "$DIFF" --vae "$VAE" --llm "$LLM" \
  -p "$PROMPT" -o "$OUT/out.png" --cfg-scale "$CFG" --steps "$STEPS" \
  ${SIGMAS:+--sigmas "$SIGMAS"} --sampling-method euler -W "$W" -H "$H" \
  --rng cpu --seed "$SEED" --offload-to-cpu --vae-tiling "$@" \
  > "$OUT/sd.log" 2>&1
RC=$?
END=$(date +%s.%N)
kill $SM 2>/dev/null || true
python3 - "$OUT" "$START" "$END" "$RC" "$M" "$STEPS" "$CFG" "$SIGMAS" "$W" "$H" "$SEED" <<'PY'
import sys,csv
r=sys.argv[1]; st,en=float(sys.argv[2]),float(sys.argv[3]); rc=sys.argv[4]
m,steps,cfg,sig,w,h,seed=sys.argv[5:12]
peak={}
try:
  for row in csv.reader(open(r+'/gpu.csv')):
    if len(row)<4: continue
    try: v=int(row[2].split()[0])
    except ValueError: continue
    peak[row[0]]=max(peak.get(row[0],0),v)
except FileNotFoundError: pass
open(r+'/metrics.txt','w').write(f"exit_code={rc}\nwall_seconds={en-st:.3f}\npeak_vram_mib={peak}\n")
print(f"{m},{w}x{h},{seed},{steps},{cfg},{sig},{rc},{en-st:.3f},{peak.get('0',0)}")
PY
exit $RC
