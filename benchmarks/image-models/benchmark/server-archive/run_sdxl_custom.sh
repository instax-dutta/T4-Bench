#!/bin/bash
set -u
export LD_LIBRARY_PATH=/usr/local/nvidia/lib64:${LD_LIBRARY_PATH:-}
R=$1; P=$2; SEED=$3
CLI=/root/bench/repos/stable-diffusion.cpp/build/bin/sd-cli
CK=/kaggle/working/quadbench/models/sdxl/sd_xl_base_1.0.safetensors
VAE=/kaggle/working/quadbench/models/sdxl/sdxl_vae.safetensors
O=/kaggle/working/quadbench/results/$R
mkdir -p "$O"
printf '%s\n' "$P" > "$O/prompt.txt"
S=$(date +%s.%N)
"$CLI" -m "$CK" --vae "$VAE" -p "$P" -o "$O/out.png" --cfg-scale 7.0 --steps 30 \
 --sampling-method euler -W 1024 -H 1024 --rng cpu --seed "$SEED" --vae-tiling --max-vram 12 > "$O/sd.log" 2>&1
RC=$?; E=$(date +%s.%N)
echo "$R,sdxl,$SEED,$RC,$(python3 -c "print(f'{$E-$S:.3f}')")"
