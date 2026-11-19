#!/bin/bash
set -u
export HF_HOME=/kaggle/working/quadbench/hf
M=/kaggle/working/quadbench/models
D=$M/zimage/z_image_turbo-Q4_K.gguf
V=$M/zimage/split_files/vae/ae.safetensors
L=$M/shared/Qwen3-4B-Instruct-2507-Q4_K_M.gguf
CSV=/kaggle/working/quadbench/results.csv
echo "model_id,size,seed,steps,cfg,sigmas,exit_code,wall_s,peak_gpu0_mib" > $CSV
for seed in 42 123 999; do
  echo "[$(date -u +%H:%M:%S)] START zimage $seed" | tee -a /kaggle/working/quadbench/logs/zimage.log
  row=$(/kaggle/working/quadbench/run_one.sh zimage_s${seed} z-image-turbo "$D" "$V" "$L" 8 1.0 "" 1024 1024 $seed --max-vram 12)
  echo "$row" >> $CSV
  echo "[$(date -u +%H:%M:%S)] $row" | tee -a /kaggle/working/quadbench/logs/zimage.log
done
echo ZIMAGE_BATCH_DONE
