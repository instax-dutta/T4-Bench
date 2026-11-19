#!/bin/bash
set -u
log(){ echo "[$(date -u +%H:%M:%S)] $*" | tee -a /root/bench/logs/setup.log; }
log "START python deps"
pip install -q bitsandbytes torchao sentencepiece gguf >> /root/bench/logs/setup.log 2>&1 && log "OK python deps" || log "FAIL python deps"
log "START clone ComfyUI"
cd /root/bench/repos && git clone --depth 1 https://github.com/Comfy-Org/ComfyUI.git >> /root/bench/logs/setup.log 2>&1 && log "OK ComfyUI" || log "FAIL ComfyUI"
log "START clone ComfyUI-GGUF"
git clone --depth 1 https://github.com/city96/ComfyUI-GGUF.git /root/bench/repos/ComfyUI/custom_nodes/ComfyUI-GGUF >> /root/bench/logs/setup.log 2>&1 && log "OK ComfyUI-GGUF" || log "FAIL ComfyUI-GGUF"
log "START clone DiffSynth-Studio"
git clone --depth 1 https://github.com/modelscope/DiffSynth-Studio.git >> /root/bench/logs/setup.log 2>&1 && log "OK DiffSynth" || log "FAIL DiffSynth"
log "DONE setup"
