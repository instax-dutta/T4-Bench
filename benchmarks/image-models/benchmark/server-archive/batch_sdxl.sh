#!/bin/bash
set -u
CSV=/kaggle/working/quadbench/results.csv
for seed in 42 123 999; do
  echo "[$(date -u +%H:%M:%S)] START sdxl $seed" | tee -a /kaggle/working/quadbench/logs/sdxl.log
  row=$(/kaggle/working/quadbench/run_sdxl.sh sdxl_s${seed} $seed)
  echo "$row" >> $CSV
  echo "[$(date -u +%H:%M:%S)] $row" | tee -a /kaggle/working/quadbench/logs/sdxl.log
done
echo SDXL_BATCH_DONE
