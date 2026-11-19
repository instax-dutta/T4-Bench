#!/bin/bash
set -u
export HF_HUB_ENABLE_HF_TRANSFER=0
cd /root/bench
log(){ echo "[$(date -u +%H:%M:%S)] $*" | tee -a /root/bench/logs/download.log; }
log "START downloads"
hf download unsloth/MiniMax-H3-Image-GGUF minimax_h3_image_pruned-Q3_K_M.gguf --local-dir /root/bench/models/unsloth-gguf >> /root/bench/logs/download.log 2>&1 && log "OK Q3_K_M"
hf download unsloth/MiniMax-H3-Image-GGUF minimax_h3_image_pruned-UD-Q4_K_XL.gguf --local-dir /root/bench/models/unsloth-gguf >> /root/bench/logs/download.log 2>&1 && log "OK UD-Q4_K_XL"
hf download unsloth/MiniMax-H3-Image-GGUF minimax_h3_image_pruned-Q5_K_M.gguf --local-dir /root/bench/models/unsloth-gguf >> /root/bench/logs/download.log 2>&1 && log "OK Q5_K_M"
hf download PrunaAI/P-H3-Image-Comfy text_encoders/p-h3-image_text_encoder_int8_convrot.safetensors --local-dir /root/bench/models/p-h3-te >> /root/bench/logs/download.log 2>&1 && log "OK P-H3 TE int8"
hf download leejet/MiniMax-H3-GGUF qwen3vl_32b_minimax_h3-Q4_K_M.gguf --local-dir /root/bench/models/qwen32b-te >> /root/bench/logs/download.log 2>&1 && log "OK Qwen32B TE Q4_K_M"
hf download Comfy-Org/MiniMax-H3-Image vae/minimax_h3_image_vae_fp16.safetensors --local-dir /root/bench/models/comfy >> /root/bench/logs/download.log 2>&1 && log "OK VAE fp16"
log "DONE downloads"
