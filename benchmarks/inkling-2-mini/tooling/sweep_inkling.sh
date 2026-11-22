#!/bin/bash
# Full engine x quant sweep for Inkling-2-Mini on 2x Tesla T4 (Kaggle VM).
# Run on the VM:  nohup bash /workspace/sweep_inkling.sh > /workspace/weights/logs/sweep.log 2>&1 &
#
# Engine note (measured 2026-11-22): llama.cpp b12633 prebuilt, CUDA 12.8
# flavor + bundled cudart. The CUDA 13.5 flavor lacks sm_75 SASS and its PTX
# is too new for the VM's CUDA 13.0 driver ("unsupported toolchain"). The
# unsloth repo-ROOT GGUFs are the obsolete PR #32695 layout (tensor error);
# use Mainline_Support/*.gguf_file (merged PR #32694 layout). AtomicChat
# AD-* files are merged-layout already (verified: loads and generates).
#
# Quota-aware: each quant file is downloaded, benched, then deleted. Peak
# disk ~24 GB against the ~96 GB writable quota. Safe to re-run; done rows
# are skipped and downloads resume.
set -u
W=/workspace/weights
B=/workspace/bench_inkling.py
CSV=$W/inkling_results.csv
PRE=/workspace/llama_prebuilt/llama-b12633
CUDART=/workspace/llama_prebuilt/cudart-llama-b12633-bin-ubuntu-cuda-12.8-x64
UNS=unsloth/Inkling-2-Mini-GGUF
UNC=AtomicChat/Inkling-2-Mini-Uncensored-GGUF
mkdir -p $W/logs $W/quants
touch $CSV

done_row() { grep -q "^$1," $CSV 2>/dev/null; }

disk_guard() {
  avail=$(df --output=avail -B1G / | tail -1)
  if [ "$avail" -lt 25 ]; then
    rm -rf $HOME/.cache/huggingface /root/.cache/pip 2>/dev/null
    ollama list 2>/dev/null | tail -n +2 | awk "{print \$1}" | xargs -r ollama rm >> $W/logs/cleanup.log 2>&1
    sync
    avail=$(df --output=avail -B1G / | tail -1)
  fi
  if [ "$avail" -lt 25 ]; then
    echo "ABORT: only ${avail}G free on / - overlay quota risk" | tee -a $W/logs/sweep_abort.log
    exit 1
  fi
}

# ---------- stage 0: install the prebuilt engine ----------
mkdir -p /workspace/llama.cpp/build/bin
cp -n $PRE/* /workspace/llama.cpp/build/bin/ 2>/dev/null
export LD_LIBRARY_PATH=/usr/local/nvidia/lib64:$CUDART:/workspace/llama.cpp/build/bin
/workspace/llama.cpp/build/bin/llama-bench --version >> $W/logs/engine.log 2>&1 \
  || echo "WARN llama-bench not functional" >> $W/logs/engine.log

if [ ! -f $W/bench_image.b64 ]; then
  curl -sL "https://huggingface.co/datasets/huggingface/documentation-images/resolve/main/p-blog/candy.JPG" \
    -o $W/bench_image.jpg
  base64 -w0 $W/bench_image.jpg > $W/bench_image.b64
fi

# obsolete-layout pre-downloads from the first attempt: delete
rm -f $W/quants/Inkling-2-Mini-UD-Q2_K_XL.gguf $W/quants/Inkling-2-Mini-UD-IQ3_XXS.gguf

# ---------- stage 1: llama.cpp quant sweep ----------
SWEEP="
Inkling-2-Mini-UD-IQ1_M.gguf_file|$UNS|MS|1|1-bit floor
Inkling-2-Mini-Uncensored-AD-IQ2_M.gguf|$UNC|.|1|uncensored 2-bit
Inkling-2-Mini-UD-Q2_K_XL.gguf_file|$UNS|MS|1|
Inkling-2-Mini-UD-IQ3_XXS.gguf_file|$UNS|MS|1|
Inkling-2-Mini-Uncensored-AD-IQ3_S.gguf|$UNC|.|1|uncensored single-card target
Inkling-2-Mini-UD-Q3_K_XL.gguf_file|$UNS|MS|1|tight at 8k, expect OOM
Inkling-2-Mini-Uncensored-AD-Q4_K.gguf|$UNC|.|2|uncensored split
Inkling-2-Mini-UD-Q4_K_M.gguf_file|$UNS|MS|2|
Inkling-2-Mini-UD-Q4_K_XL.gguf_file|$UNS|MS|2|
Inkling-2-Mini-UD-Q8_K_XL.gguf_file|$UNS|MS|2|reference
"
while IFS='|' read -r f repo sub gpus note; do
  [ -z "$f" ] && continue
  tag=$(echo "$f" | sed "s/\.gguf_file$//; s/\.gguf$//")
  if [ "$sub" = "MS" ]; then repopath="Mainline_Support/$f"; else repopath="$f"; fi
  if done_row "llama.cpp,$tag"; then echo "skip $tag (done)"; continue; fi
  echo "=== $f ($gpus GPU) $note"
  disk_guard
  hf download "$repo" "$repopath" --local-dir $W/quants >> $W/logs/dl.log 2>&1 || { echo "download failed $f"; continue; }
  python3 $B llamacpp $W/quants/$repopath $gpus 8192
  rm -f $W/quants/$repopath
  rm -rf $HOME/.cache/huggingface 2>/dev/null
done <<EOF
$SWEEP
EOF

# ---------- stage 2: Ollama ----------
# Already measured and recorded: official tag is MLX-only; local GGUF import
# fails with unknown architecture inkling2_loop in Ollama's bundled runner.
# Rows are in the CSV; nothing to run here.

# ---------- stage 3: vision (one single-card + one split) ----------
MMPROJ=mmproj-Inkling-2-Mini-Uncensored-F16.gguf
disk_guard
hf download $UNC "$MMPROJ" --local-dir $W/quants >> $W/logs/dl.log 2>&1
for combo in "Inkling-2-Mini-Uncensored-AD-IQ3_S.gguf|$UNC|.|1" "Inkling-2-Mini-UD-Q4_K_XL.gguf_file|$UNS|MS|2"; do
  IFS='|' read -r f repo sub gpus <<< "$combo"
  tag=$(echo "$f" | sed "s/\.gguf_file$//; s/\.gguf$//")
  done_row "llama.cpp-vision,$tag" && continue
  if [ "$sub" = "MS" ]; then repopath="Mainline_Support/$f"; else repopath="$f"; fi
  disk_guard
  hf download "$repo" "$repopath" --local-dir $W/quants >> $W/logs/dl.log 2>&1 || continue
  python3 $B vision $W/quants/$repopath $W/quants/$MMPROJ $gpus 8192
  rm -f $W/quants/$repopath
done
rm -f $W/quants/$MMPROJ

# ---------- stage 4: attempt engines (expected failures, documented) ----------
if ! done_row "vllm"; then
  disk_guard
  pip install vllm >> $W/logs/vllm_install.log 2>&1 || true
  hf download $UNC Inkling-2-Mini-Uncensored-AD-IQ2_M.gguf --local-dir $W/quants >> $W/logs/dl.log 2>&1
  python3 $B attempt vllm "timeout 600 vllm serve $W/quants/Inkling-2-Mini-Uncensored-AD-IQ2_M.gguf --max-model-len 4096"
  rm -f $W/quants/Inkling-2-Mini-Uncensored-AD-IQ2_M.gguf
  pip uninstall -y vllm >> $W/logs/cleanup.log 2>&1 || true
fi
if ! done_row "sglang"; then
  disk_guard
  pip install sglang >> $W/logs/sglang_install.log 2>&1 || true
  python3 $B attempt sglang "timeout 600 python3 -m sglang.launch_server --model-path thinkingmachines/Inkling-2-Mini --host 127.0.0.1 --port 30000"
  pip uninstall -y sglang >> $W/logs/cleanup.log 2>&1 || true
fi
if ! done_row "transformers-native"; then
  python3 $B attempt transformers-native "python3 /workspace/transformers_attempt.py"
fi

echo "SWEEP COMPLETE"
