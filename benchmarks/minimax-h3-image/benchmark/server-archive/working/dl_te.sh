#!/bin/bash
set -u
U="https://www.modelscope.cn/models/DiffSynth-Studio/EntroPackPreQuants/resolve/master/models/MiniMax-H3/text_encoder_3bpp.safetensors"
F=/kaggle/working/bench/models/diffsynth/text_encoder/text_encoder_3bpp.safetensors
echo "[$(date -u +%H:%M:%S)] START TE" | tee -a /kaggle/working/bench/logs/te_dl.log
curl -L -C - --retry 5 --retry-delay 5 -o "$F" "$U" >> /kaggle/working/bench/logs/te_dl.log 2>&1
echo "[$(date -u +%H:%M:%S)] TE DONE size=$(stat -c%s $F)" | tee -a /kaggle/working/bench/logs/te_dl.log
hf download MiniMaxAI/MiniMax-H3-Image pdd_fused_heads.safetensors --local-dir /kaggle/working/bench/models/diffsynth/base >> /kaggle/working/bench/logs/te_dl.log 2>&1
hf download MiniMaxAI/MiniMax-H3-Image --include "processor/*" --local-dir /kaggle/working/bench/models/diffsynth/base >> /kaggle/working/bench/logs/te_dl.log 2>&1
echo "[$(date -u +%H:%M:%S)] SMALL FILES DONE" | tee -a /kaggle/working/bench/logs/te_dl.log
