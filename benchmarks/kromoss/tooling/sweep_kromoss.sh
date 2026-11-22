#!/bin/bash
# Kromoss (lodestones/Kromoss, MOSS-Image 5B DiT) benchmark on 2x T4.
# QUEUED: run only after the Inkling-2-Mini sweep completes on the VM.
#   nohup bash /workspace/sweep_kromoss.sh > /workspace/weights/logs/kromoss_sweep.log 2>&1 &
#
# Storage (writable overlay quota ~96 GB, disk_guard enforced):
#   diffusers set stays resident ~30 GB (DiT 10.2 + Qwen3.5-9B TE 16.8 + VAE
#   + LoRAs). ComfyUI single files are streamed and deleted after each config
#   (bf16 DiT 10.2, TE single 19.3, int8 DiT 5.4). Peak ~60 GB.
set -u
W=/workspace/weights
K=$W/kromoss
B=/workspace/bench_kromoss.py
CSV=$W/kromoss_results.csv
REPO=lodestones/Kromoss
mkdir -p $K $W/logs
touch $CSV

done_row() { grep -q "^$1," $CSV 2>/dev/null; }

disk_guard() {
  avail=$(df --output=avail -B1G / | tail -1)
  if [ "$avail" -lt 25 ]; then
    rm -rf $HOME/.cache/huggingface /root/.cache/pip 2>/dev/null
    sync
    avail=$(df --output=avail -B1G / | tail -1)
  fi
  if [ "$avail" -lt 25 ]; then
    echo "ABORT: only ${avail}G free on / - overlay quota risk" | tee -a $W/logs/sweep_abort.log
    exit 1
  fi
}

# ---------- stage 0: diffusers resident set ----------
disk_guard
for f in model_index.json pipeline_moss_image.py scheduler_config.json; do :; done
hf download $REPO --include "transformer/*" "text_encoder/*" "vae/config.json" "vae/diffusion_pytorch_model.safetensors" "scheduler/*" "tokenizer/*" "model_index.json" "pipeline_moss_image.py" "8-steps-dmd2-lora.safetensors" \
  --local-dir $K >> $W/logs/dl_kromoss.log 2>&1 || echo "download issue (check log; --include may be ignored by HF CLI 1.33 - fall back to explicit loop)" >> $W/logs/dl_kromoss.log
# explicit fallback loop if the include-pattern download misbehaved
if [ ! -f $K/transformer/diffusion_pytorch_model-00003-of-00003.safetensors ] || [ ! -f $K/text_encoder/model-00004-of-00004.safetensors ]; then
  for f in transformer/config.json \
    transformer/diffusion_pytorch_model-00001-of-00003.safetensors \
    transformer/diffusion_pytorch_model-00002-of-00003.safetensors \
    transformer/diffusion_pytorch_model-00003-of-00003.safetensors \
    text_encoder/config.json text_encoder/model.safetensors.index.json \
    text_encoder/model-00001-of-00004.safetensors \
    text_encoder/model-00002-of-00004.safetensors \
    text_encoder/model-00003-of-00004.safetensors \
    text_encoder/model-00004-of-00004.safetensors \
    vae/config.json vae/diffusion_pytorch_model.safetensors \
    scheduler/scheduler_config.json scheduler/pipeline_moss_image.py \
    tokenizer/tokenizer.json tokenizer/tokenizer_config.json tokenizer/chat_template.jinja \
    model_index.json pipeline_moss_image.py 8-steps-dmd2-lora.safetensors; do
    hf download $REPO "$f" --local-dir $K >> $W/logs/dl_kromoss.log 2>&1 || echo "FAILED: $f" >> $W/logs/dl_kromoss.log
  done
fi

# ---------- stage 1: diffusers configs (warm process, full pipe call) ----------
# K1: full-quality path, 50 steps CFG 3, TE on CPU
done_row "k1-diffusers-50steps" || python3 $B diffusers k1-diffusers-50steps 50 3 none cpu
# K2: headline config, 8 steps CFG 1 + DMD2 LoRA, TE on CPU
done_row "k2-diffusers-8steps-lora" || python3 $B diffusers k2-diffusers-8steps-lora 8 1 dmd2 cpu
# K3: encode-speed config, TE int8 on GPU 1 (falls back to cpu if bnb missing)
done_row "k3-diffusers-te-int8g1" || python3 $B diffusers k3-diffusers-te-int8g1 8 1 dmd2 int8g1
python3 $B clip $K/out

# ---------- stage 2: ComfyUI route (int8 W8A8 is ComfyUI-only) ----------
if [ ! -d /workspace/ComfyUI ]; then
  git clone --depth 1 https://github.com/comfyanonymous/ComfyUI.git /workspace/ComfyUI >> $W/logs/comfy_install.log 2>&1
  cd /workspace/ComfyUI && pip install -r requirements.txt >> $W/logs/comfy_install.log 2>&1; cd /
fi
mkdir -p /workspace/ComfyUI/models/diffusion_models /workspace/ComfyUI/models/text_encoders /workspace/ComfyUI/models/vae /workspace/ComfyUI/models/loras
hf download $REPO kromoss_simple_workflow.json --local-dir $K >> $W/logs/dl_kromoss.log 2>&1

# text encoder single file (ComfyUI loader format) - needed for both comfy configs
disk_guard
[ -f /workspace/ComfyUI/models/text_encoders/qwen3.5_9b_bf16.safetensors ] || \
  hf download $REPO text_encoders/qwen3.5_9b_bf16.safetensors --local-dir $K >> $W/logs/dl_kromoss.log 2>&1 && \
  ln -sf $K/text_encoders/qwen3.5_9b_bf16.safetensors /workspace/ComfyUI/models/text_encoders/
hf download $REPO vae/flux2-vae_small.safetensors --local-dir $K >> $W/logs/dl_kromoss.log 2>&1 && \
  ln -sf $K/vae/flux2-vae_small.safetensors /workspace/ComfyUI/models/vae/
ln -sf $K/8-steps-dmd2-lora.safetensors /workspace/ComfyUI/models/loras/

# K4: ComfyUI bf16 DiT, 8 steps + LoRA (delete after bench)
if ! done_row "k4-comfy-bf16"; then
  disk_guard
  hf download $REPO diffusion_models/kromoss_bf16.safetensors --local-dir $K >> $W/logs/dl_kromoss.log 2>&1 && \
    ln -sf $K/diffusion_models/kromoss_bf16.safetensors /workspace/ComfyUI/models/diffusion_models/
  python3 $B comfy k4-comfy-bf16 bf16 8 1
  rm -f $K/diffusion_models/kromoss_bf16.safetensors
fi
# K5: ComfyUI int8 W8A8 DiT (T4 int8 tensor cores), 8 steps + LoRA
if ! done_row "k5-comfy-int8"; then
  disk_guard
  hf download $REPO diffusion_models/kromoss_int8_convrot.safetensors --local-dir $K >> $W/logs/dl_kromoss.log 2>&1 && \
    ln -sf $K/diffusion_models/kromoss_int8_convrot.safetensors /workspace/ComfyUI/models/diffusion_models/
  python3 $B comfy k5-comfy-int8 int8 8 1
  rm -f $K/diffusion_models/kromoss_int8_convrot.safetensors
fi
python3 $B clip $K/out

echo "KROMOSS SWEEP COMPLETE"
