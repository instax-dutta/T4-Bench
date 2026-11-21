#!/bin/bash
# VM prep for LongCat-Video-Avatar-1.6 benchmark on 2x T4 (Kaggle VM).
# Run on a FRESH VM:  bash /workspace/prepare.sh phase0
#   phase0: INT8 DiT only (15.9 GB) + patches + measured load test
#           -> /workspace/weights/int8_load_test.json
#   phase1: remaining sweep weights (~32 GB more) - only if phase0 fits
#   phase2: fp16 base_model (31.7 GB, config C) - only if phase0 fits
# Safe to re-run; hf resumes partial files.
#
# Why selective: full both-repo download is ~112 GB, the writable overlay
# quota is ~96 GB (the 2026-11-21 session died this way; whisper ships
# ~15 GB of fp32/bin/flax duplicates, base repo dit/ is 27 GB and unused
# by the avatar pipeline). Explicit file loops because HF CLI 1.33 ignores
# --include (repo gotcha from the video-gen project).
set -u
W=/workspace/weights
REPO=/workspace/LongCat-Video
mkdir -p $W/logs

BASE=meituan-longcat/LongCat-Video
AVATAR=meituan-longcat/LongCat-Video-Avatar-1.6

INT8_FILES="base_model_int8/config.json base_model_int8/quantization_config.json \
base_model_int8/quantized_model.safetensors.index.json \
base_model_int8/quantized_model-00001-of-00004.safetensors \
base_model_int8/quantized_model-00002-of-00004.safetensors \
base_model_int8/quantized_model-00003-of-00004.safetensors \
base_model_int8/quantized_model-00004-of-00004.safetensors"

REST_FILES="scheduler/scheduler_config.json \
loraA/lora.safetensors loraB/lora.safetensors \
whisper-large-v3/model.safetensors whisper-large-v3/config.json \
whisper-large-v3/generation_config.json whisper-large-v3/merges.txt \
whisper-large-v3/normalizer.json whisper-large-v3/preprocessor_config.json \
whisper-large-v3/special_tokens_map.json whisper-large-v3/tokenizer.json \
whisper-large-v3/tokenizer_config.json whisper-large-v3/vocab.json \
whisper-large-v3/added_tokens.json \
vocal_separator/Kim_Vocal_2.onnx vocal_separator/download_checks.json \
vocal_separator/mdx_model_data.json vocal_separator/vr_model_data.json"

BASE_FILES="scheduler/scheduler_config.json \
text_encoder/config.json text_encoder/model.safetensors.index.json \
text_encoder/model-00001-of-00005.safetensors \
text_encoder/model-00002-of-00005.safetensors \
text_encoder/model-00003-of-00005.safetensors \
text_encoder/model-00004-of-00005.safetensors \
text_encoder/model-00005-of-00005.safetensors \
tokenizer/special_tokens_map.json tokenizer/spiece.model \
tokenizer/tokenizer.json tokenizer/tokenizer_config.json \
vae/config.json vae/diffusion_pytorch_model.safetensors"

FP16_FILES="base_model/config.json \
base_model/diffusion_pytorch_model.safetensors.index.json \
base_model/diffusion_pytorch_model-00001-of-00006.safetensors \
base_model/diffusion_pytorch_model-00002-of-00006.safetensors \
base_model/diffusion_pytorch_model-00003-of-00006.safetensors \
base_model/diffusion_pytorch_model-00004-of-00006.safetensors \
base_model/diffusion_pytorch_model-00005-of-00006.safetensors \
base_model/diffusion_pytorch_model-00006-of-00006.safetensors"

dl() {
  hf download "$1" "$3" --local-dir "$2" >> $W/logs/dl.log 2>&1 \
    || echo "DOWNLOAD_FAILED: $1/$3" >> $W/logs/dl_failures.log
}

download_set() {
  for f in $3; do dl "$1" "$2" "$f"; done
  echo "done downloading $1" >> $W/logs/dl.log
}

# --- repo + T4 patches (idempotent) ---
setup_repo() {
  if [ ! -d $REPO ]; then
    git clone --depth 1 https://github.com/meituan-longcat/LongCat-Video.git $REPO \
      >> $W/logs/clone.log 2>&1
  fi
  pip install xformers >> $W/logs/pip_xformers.log 2>&1

  cd $REPO
  # P1: bf16 -> fp16 (T4 sm_75 has no native bfloat16; audited: these two
  #     files hold every hardcode)
  sed -i "s/torch\.bfloat16/torch.float16/g" \
    run_demo_avatar_single_audio_to_video.py \
    longcat_video/modules/quantization.py
  # P2: whisper loads fp16 (default from_pretrained upcasts to fp32 = 6.2 GB/GPU)
  sed -i "s/WhisperModel\.from_pretrained(checkpoint_path)/WhisperModel.from_pretrained(checkpoint_path, torch_dtype=\"float16\")/" \
    longcat_video/audio_process/__init__.py
  # P3: keep umT5 text encoder on CPU (11.35 GB fp16 does not fit a 15 GB T4
  #     next to the DiT); pipeline encodes on CPU and moves embeds to device
  sed -i "s/    pipe\.to(local_rank)/    pipe.vae.to(local_rank)\n    pipe.text_encoder.to(\"cpu\")/" \
    run_demo_avatar_single_audio_to_video.py
  sed -i "s/prompt_embeds = self\.text_encoder(text_input_ids\.to(device), mask\.to(device))\.last_hidden_state/prompt_embeds = self.text_encoder(text_input_ids, mask).last_hidden_state/" \
    longcat_video/pipeline_longcat_video_avatar.py
  # P4: attention backend in checkpoint configs: flash-attn2 does not build
  #     on CUDA 13; use xformers
  for f in $W/LongCat-Video-Avatar-1.6/base_model_int8/config.json \
           $W/LongCat-Video-Avatar-1.6/base_model/config.json; do
    [ -f "$f" ] && sed -i \
      -e "s/\"enable_flashattn2\": true/\"enable_flashattn2\": false/" \
      -e "s/\"enable_xformers\": false/\"enable_xformers\": true/" "$f"
  done
}

case "${1:-phase0}" in
phase0)
  download_set "$AVATAR" "$W/LongCat-Video-Avatar-1.6" "$INT8_FILES"
  setup_repo
  echo "=== inventory ==="; du -sh $W/LongCat-Video-Avatar-1.6
  [ -f $W/logs/dl_failures.log ] && { echo "FAILED DOWNLOADS:"; cat $W/logs/dl_failures.log; exit 1; }
  export LD_LIBRARY_PATH=/usr/local/nvidia/lib64:/usr/local/cuda-13.0/lib64
  python3 /workspace/int8_load_test.py
  ;;
phase1)
  download_set "$BASE" "$W/LongCat-Video" "$BASE_FILES" &
  P1=$!
  download_set "$AVATAR" "$W/LongCat-Video-Avatar-1.6" "$REST_FILES" &
  P2=$!
  wait $P1 $P2
  setup_repo
  echo "=== inventory ==="; du -sh $W/LongCat-Video $W/LongCat-Video-Avatar-1.6
  [ -f $W/logs/dl_failures.log ] && { echo "FAILED DOWNLOADS:"; cat $W/logs/dl_failures.log; exit 1; }
  python3 -m py_compile /workspace/benchmark_avatar.py && echo "phase1 OK"
  ;;
phase2)
  download_set "$AVATAR" "$W/LongCat-Video-Avatar-1.6" "$FP16_FILES"
  echo "=== inventory ==="; du -sh $W/LongCat-Video-Avatar-1.6
  ;;
esac
