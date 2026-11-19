#!/bin/bash
set -u
M=/kaggle/working/quadbench/models
D=$M/flux/flux-2-klein-4b-Q4_0.gguf
V=$M/flux/split_files/vae/flux2-vae.safetensors
L=$M/shared/Qwen3-4B-Instruct-2507-Q4_K_M.gguf
CSV=/kaggle/working/quadbench/results.csv
for seed in 42 123 999; do
  echo "[$(date -u +%H:%M:%S)] START flux $seed" | tee -a /kaggle/working/quadbench/logs/flux.log
  row=$(/kaggle/working/quadbench/run_one.sh flux_s${seed} flux2-klein-4b "$D" "$V" "$L" 4 1.0 "" 1024 1024 $seed --max-vram 12)
  echo "$row" >> $CSV
  echo "[$(date -u +%H:%M:%S)] $row" | tee -a /kaggle/working/quadbench/logs/flux.log
done
echo FLUX_BATCH_DONE
