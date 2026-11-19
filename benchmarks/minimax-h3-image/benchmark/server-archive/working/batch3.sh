#!/bin/bash
set -u
export LD_LIBRARY_PATH=/usr/local/nvidia/lib64:${LD_LIBRARY_PATH:-}
M=/root/bench/models
Q3=$M/unsloth-gguf/minimax_h3_image_pruned-Q3_K_M.gguf
Q4=$M/unsloth-gguf/minimax_h3_image_pruned-UD-Q4_K_XL.gguf
Q5=$M/unsloth-gguf/minimax_h3_image_pruned-Q5_K_M.gguf
P3=$M/p-h3-te/text_encoders/p-h3-image_text_encoder_int8_convrot.safetensors
SUMMARY=/kaggle/working/bench/results/summary.csv
cp /root/bench/results/summary.csv $SUMMARY 2>/dev/null || true
run(){
  id=$1; diff=$2; w=$3; h=$4; seed=$5
  echo "[$(date -u +%H:%M:%S)] START $id" | tee -a /kaggle/working/bench/logs/batch3.log
  /kaggle/working/bench/run_sdcpp.sh "$id" "$diff" "$P3" "$w" "$h" "$seed" --max-vram 12 > /kaggle/working/bench/logs/$id.nohup 2>&1
  rc=$?
  wall=$(grep wall_seconds /kaggle/working/bench/results/$id/metrics.txt 2>/dev/null | cut -d= -f2)
  peak=$(grep peak_vram_mib /kaggle/working/bench/results/$id/metrics.txt 2>/dev/null | sed "s/.*'0': \([0-9]*\).*/\1/")
  echo "$id,$(basename $diff),$(basename $P3),$w,$h,$seed,$rc,$wall,$peak" >> $SUMMARY
  echo "[$(date -u +%H:%M:%S)] DONE $id rc=$rc wall=$wall peak=$peak" | tee -a /kaggle/working/bench/logs/batch3.log
}
run B_s2048_s123 "$Q4" 2048 2048 123
run B_s2048_s999 "$Q4" 2048 2048 999
run B3_s1024_s123 "$Q5" 1024 1024 123
run B3_s1024_s999 "$Q5" 1024 1024 999
run B2_s4096_s42 "$Q3" 4096 4096 42
echo "[$(date -u +%H:%M:%S)] BATCH3 DONE" | tee -a /kaggle/working/bench/logs/batch3.log
