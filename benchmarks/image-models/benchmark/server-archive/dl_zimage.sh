#!/bin/bash
set -u
L=/kaggle/working/quadbench/logs/dl_zimage.log
echo "[$(date -u +%H:%M:%S)] START Z-Image download" | tee -a $L
hf download leejet/Z-Image-Turbo-GGUF z_image_turbo-Q4_K.gguf --local-dir /kaggle/working/quadbench/models/zimage >> $L 2>&1 && echo "OK dit" | tee -a $L
hf download Comfy-Org/z_image_turbo split_files/vae/ae.safetensors --local-dir /kaggle/working/quadbench/models/zimage >> $L 2>&1 && echo "OK vae" | tee -a $L
hf download unsloth/Qwen3-4B-Instruct-2507-GGUF Qwen3-4B-Instruct-2507-Q4_K_M.gguf --local-dir /kaggle/working/quadbench/models/shared >> $L 2>&1 && echo "OK qwen3-4b" | tee -a $L
echo "[$(date -u +%H:%M:%S)] DONE" | tee -a $L
