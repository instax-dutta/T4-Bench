#!/bin/bash
set -u
export LD_LIBRARY_PATH=/usr/local/nvidia/lib64:${LD_LIBRARY_PATH:-}
M=/root/bench/models
Q3=$M/unsloth-gguf/minimax_h3_image_pruned-Q3_K_M.gguf
Q4=$M/unsloth-gguf/minimax_h3_image_pruned-UD-Q4_K_XL.gguf
Q5=$M/unsloth-gguf/minimax_h3_image_pruned-Q5_K_M.gguf
P3=$M/p-h3-te/text_encoders/p-h3-image_text_encoder_int8_convrot.safetensors
QW=$M/qwen32b-te/qwen3vl_32b_minimax_h3-Q4_K_M.gguf
SUMMARY=/root/bench/results/summary.csv
echo "run_id,diffusion,llm,w,h,seed,exit_code,wall_s,peak_gpu0_mib" > $SUMMARY
run(){
  id=$1; diff=$2; llm=$3; w=$4; h=$5; seed=$6
  echo "[$(date -u +%H:%M:%S)] START $id" | tee -a /root/bench/logs/batch.log
  /root/bench/run_sdcpp.sh "$id" "$diff" "$llm" "$w" "$h" "$seed" --max-vram 12 > /root/bench/logs/$id.nohup 2>&1
  rc=$?
  wall=$(grep wall_seconds /root/bench/results/$id/metrics.txt 2>/dev/null | cut -d= -f2)
  peak=$(grep peak_vram_mib /root/bench/results/$id/metrics.txt 2>/dev/null | sed "s/.*'0': \([0-9]*\).*/\1/")
  echo "$id,$(basename $diff),$(basename $llm),$w,$h,$seed,$rc,$wall,$peak" >> $SUMMARY
  echo "[$(date -u +%H:%M:%S)] DONE $id rc=$rc wall=$wall peak=$peak" | tee -a /root/bench/logs/batch.log
}
run B2_s1024_s123 "$Q3" "$P3" 1024 1024 123
run B2_s1024_s999 "$Q3" "$P3" 1024 1024 999
run B2_s1024_s42_repeat "$Q3" "$P3" 1024 1024 42
run B_s1024_s42 "$Q4" "$P3" 1024 1024 42
run B_s1024_s123 "$Q4" "$P3" 1024 1024 123
run B_s1024_s999 "$Q4" "$P3" 1024 1024 999
run B3_s1024_s42 "$Q5" "$P3" 1024 1024 42
run B_qwen32b_s1024_s42 "$Q4" "$QW" 1024 1024 42
run B2_s2048_s42 "$Q3" "$P3" 2048 2048 42
run B_s2048_s42 "$Q4" "$P3" 2048 2048 42
echo "[$(date -u +%H:%M:%S)] BATCH DONE" | tee -a /root/bench/logs/batch.log
