#!/bin/bash
# usage: opt_run.sh RUN_ID MODE(single4|dual2) DIFF VAE LLM STEPS CFG [EXTRA...]
set -u
export LD_LIBRARY_PATH=/usr/local/nvidia/lib64:${LD_LIBRARY_PATH:-}
R=$1; MODE=$2; DIFF=$3; VAE=$4; LLM=$5; STEPS=$6; CFG=$7; shift 7
CLI=/root/bench/repos/stable-diffusion.cpp/build/bin/sd-cli
O=/kaggle/working/quadbench/results/$R
mkdir -p "$O"
PROMPT="A silver tabby kitten holding a sign reading 'sd.cpp', natural daylight"
printf '%s\n' "$PROMPT" > "$O/prompt.txt"
args=()
if [ -n "$DIFF" ]; then args+=(--diffusion-model "$DIFF"); else args+=(-m "$VAE"); fi
if [ -n "$DIFF" ]; then args+=(--vae "$VAE"); fi
if [ -n "$LLM" ]; then args+=(--llm "$LLM"); fi
args+=(-p "$PROMPT" --cfg-scale "$CFG" --steps "$STEPS" --sampling-method euler \
       -W 1024 -H 1024 --rng cpu --seed 42 --vae-tiling --max-vram 12 "$@")
S=$(date +%s.%N)
if [ "$MODE" = single4 ]; then
  CUDA_VISIBLE_DEVICES=0 "$CLI" "${args[@]}" -b 4 -o "$O/out.png" > "$O/sd.log" 2>&1
  RC=$?
else
  CUDA_VISIBLE_DEVICES=0 "$CLI" "${args[@]}" -b 2 -o "$O/g0.png" > "$O/g0.log" 2>&1 & P0=$!
  CUDA_VISIBLE_DEVICES=1 "$CLI" "${args[@]}" -b 2 -o "$O/g1.png" > "$O/g1.log" 2>&1 & P1=$!
  wait $P0; A=$?; wait $P1; B=$?; RC=$((A+B))
fi
E=$(date +%s.%N)
echo "$R,$MODE,$(python3 -c "print(f'{$E-$S:.3f}')"),$RC,$(find "$O" -name '*.png' | wc -l)"
