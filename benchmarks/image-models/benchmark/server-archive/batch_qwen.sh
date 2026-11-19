#!/bin/bash
set -u
export HF_HOME=/kaggle/working/quadbench/hf
M=/kaggle/working/quadbench/models
D=$M/qwen/qwen_image_2.1_turbo_Q4_K_M.gguf
V=$M/qwen/vae/qwen_image_2.1_vae_bf16.safetensors
L=$M/shared/Qwen3VL-8B-Instruct-Q4_K_M.gguf
CSV=/kaggle/working/quadbench/results.csv
for seed in 42 123 999; do
  echo "[$(date -u +%H:%M:%S)] START qwen $seed" | tee -a /kaggle/working/quadbench/logs/qwen.log
  row=$(/kaggle/working/quadbench/run_one.sh qwen_s${seed} qwen-image-2.1-viggle-4step "$D" "$V" "$L" 4 1.0 "" 1024 1024 $seed --max-vram 12)
  echo "$row" >> $CSV
  echo "[$(date -u +%H:%M:%S)] $row" | tee -a /kaggle/working/quadbench/logs/qwen.log
done
echo QWEN_BATCH_DONE
