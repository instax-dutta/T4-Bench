#!/bin/bash
# Full engine x quant sweep for Inkling-2-Mini on 2x Tesla T4 (Kaggle VM).
# Run on the VM:  nohup bash /workspace/sweep_inkling.sh > /workspace/weights/logs/sweep.log 2>&1 &
#
# Quota-aware: quants total ~139 GB, the writable overlay quota is ~96 GB.
# Each quant file is downloaded, benched by every engine that can use it,
# then deleted before the next one. Peak disk ~24 GB.
#
# Safe to re-run: every stage checks whether it already succeeded (CSV row
# exists) and skips; downloads resume.
set -u
W=/workspace/weights
B=/workspace/bench_inkling.py
REPO=unsloth/Inkling-2-Mini-GGUF
UNC=AtomicChat/Inkling-2-Mini-Uncensored-GGUF
CSV=$W/inkling_results.csv
mkdir -p $W/logs
touch $CSV

done_row() { grep -q "^$1," $CSV 2>/dev/null; }

# ---------- stage 0: build llama.cpp (>= b12600 merged loop arch) ----------
if [ ! -x /workspace/llama.cpp/build/bin/llama-bench ]; then
  if [ ! -d /workspace/llama.cpp ]; then
    git clone --depth 1 https://github.com/ggml-org/llama.cpp.git /workspace/llama.cpp \
      >> $W/logs/build.log 2>&1
  fi
  cd /workspace/llama.cpp
  cmake -B build -DGGML_CUDA=ON >> $W/logs/build.log 2>&1
  cmake --build build -j 4 --target llama-bench llama-server >> $W/logs/build.log 2>&1
fi
/workspace/llama.cpp/build/bin/llama-bench --version >> $W/logs/build.log 2>&1 \
  || echo "WARN llama-bench not functional" >> $W/logs/build.log

# benchmark image (fixed across all vision runs)
if [ ! -f $W/bench_image.b64 ]; then
  curl -sL "https://huggingface.co/datasets/huggingface/documentation-images/resolve/main/p-blog/candy.JPG" \
    -o $W/bench_image.jpg
  base64 -w0 $W/bench_image.jpg > $W/bench_image.b64
fi

# ---------- stage 1: llama.cpp quant sweep ----------
# order: small -> large; single-GPU first, then 2-GPU splits
#   file | repo | gpus | note
SWEEP="
UD-IQ1_M.gguf|$REPO|1|1-bit floor
Inkling-2-Mini-Uncensored-AD-IQ2_M.gguf|$UNC|1|uncensored 2-bit
UD-Q2_K_XL.gguf|$REPO|1|
UD-IQ3_XXS.gguf|$REPO|1|
Inkling-2-Mini-Uncensored-AD-IQ3_S.gguf|$UNC|1|uncensored single-card target
UD-Q3_K_XL.gguf|$REPO|1|tight, expect OOM at 8k
Inkling-2-Mini-Uncensored-AD-Q4_K.gguf|$UNC|2|uncensored split
UD-Q4_K_M.gguf|$REPO|2|
UD-Q4_K_XL.gguf|$REPO|2|
UD-Q8_K_XL.gguf|$REPO|2|reference
"
while IFS='|' read -r f repo gpus note; do
  [ -z "$f" ] && continue
  tag=$(echo "$f" | sed "s/\.gguf$//")
  if done_row "llama.cpp,$tag"; then echo "skip $tag (done)"; continue; fi
  echo "=== $f ($gpus GPU) $note"
  hf download "$repo" "$f" --local-dir $W/quants >> $W/logs/dl.log 2>&1 || { echo "download failed $f"; continue; }
  python3 $B llamacpp $W/quants/$f $gpus 8192
  # Ollama comparison on two representative single-card quants
  if [ "$gpus" = "1" ] && { [ "$f" = "UD-Q3_K_XL.gguf" ] || [ "$f" = "Inkling-2-Mini-Uncensored-AD-IQ3_S.gguf" ]; }; then
    bash /workspace/ollama_import.sh "$tag" "$W/quants/$f" || true
    python3 $B ollama "$tag" 1 8192
  fi
  rm -f $W/quants/$f
done <<EOF
$SWEEP
EOF

# ---------- stage 2: Ollama official tag, 2-GPU layer split ----------
if ! done_row "ollama,inkling-2-mini"; then
  curl -fsSL https://ollama.com/install.sh | sh >> $W/logs/ollama_install.log 2>&1
  systemctl start ollama 2>/dev/null || (ollama serve > $W/logs/ollama_serve.log 2>&1 &) ; sleep 5
  ollama pull inkling-2-mini >> $W/logs/ollama_pull.log 2>&1 || echo "pull failed" >> $W/logs/ollama_pull.log
  python3 $B ollama inkling-2-mini 2 8192
fi

# ---------- stage 3: vision (one single-card + one split) ----------
MMPROJ=mmproj-F16.gguf
hf download $REPO "$MMPROJ" --local-dir $W/quants >> $W/logs/dl.log 2>&1
for combo in "Inkling-2-Mini-Uncensored-AD-IQ3_S.gguf|$UNC|1" "UD-Q4_K_XL.gguf|$REPO|2"; do
  IFS='|' read -r f repo gpus <<< "$combo"
  tag=$(echo "$f" | sed "s/\.gguf$//")
  done_row "llama.cpp-vision,$tag" && continue
  hf download "$repo" "$f" --local-dir $W/quants >> $W/logs/dl.log 2>&1 || continue
  python3 $B vision $W/quants/$f $W/quants/$MMPROJ $gpus 8192
  rm -f $W/quants/$f
done
rm -f $W/quants/$MMPROJ

# ---------- stage 4: attempt engines (expected failures, documented) ----------
if ! done_row "vllm"; then
  pip install vllm >> $W/logs/vllm_install.log 2>&1 || true
  hf download $UNC Inkling-2-Mini-Uncensored-AD-IQ2_M.gguf --local-dir $W/quants >> $W/logs/dl.log 2>&1
  python3 $B attempt vllm "timeout 600 vllm serve $W/quants/Inkling-2-Mini-Uncensored-AD-IQ2_M.gguf --max-model-len 4096"
  rm -f $W/quants/Inkling-2-Mini-Uncensored-AD-IQ2_M.gguf
fi
if ! done_row "sglang"; then
  pip install sglang >> $W/logs/sglang_install.log 2>&1 || true
  python3 $B attempt sglang "timeout 600 python3 -m sglang.launch_server --model-path thinkingmachines/Inkling-2-Mini --host 127.0.0.1 --port 30000"
fi
if ! done_row "transformers-native"; then
  python3 $B attempt transformers-native "python3 /workspace/transformers_attempt.py"
fi

echo "SWEEP COMPLETE"
