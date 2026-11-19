#!/bin/bash
set -u
export LD_LIBRARY_PATH=/usr/local/nvidia/lib64:${LD_LIBRARY_PATH:-}
M=/root/bench/models
Q3=$M/unsloth-gguf/minimax_h3_image_pruned-Q3_K_M.gguf
P3=$M/p-h3-te/text_encoders/p-h3-image_text_encoder_int8_convrot.safetensors
SUMMARY=/kaggle/working/bench/results/summary.csv
run(){
  id=$1; cap=$2
  echo "[$(date -u +%H:%M:%S)] START $id" | tee -a /kaggle/working/bench/logs/batch5.log
  /kaggle/working/bench/run_sdcpp.sh "$id" "$Q3" "$P3" 1024 1024 42 --max-vram "$cap" > /kaggle/working/bench/logs/$id.nohup 2>&1
  rc=$?
  wall=$(grep wall_seconds /kaggle/working/bench/results/$id/metrics.txt 2>/dev/null | cut -d= -f2)
  peak=$(grep peak_vram_mib /kaggle/working/bench/results/$id/metrics.txt 2>/dev/null | sed "s/.*'0': \([0-9]*\).*/\1/")
  echo "$id,$(basename $Q3),$(basename $P3),1024,1024,42,$rc,$wall,$peak" >> $SUMMARY
  echo "[$(date -u +%H:%M:%S)] DONE $id cap=$cap rc=$rc wall=$wall peak=$peak" | tee -a /kaggle/working/bench/logs/batch5.log
}
run B2_s1024_s42_cap10 10
run B2_s1024_s42_cap8 8
echo "[$(date -u +%H:%M:%S)] BATCH5 DONE" | tee -a /kaggle/working/bench/logs/batch5.log
