#!/bin/bash
set -u
log(){ echo "[$(date -u +%H:%M:%S)] $*" | tee -a /root/bench/logs/diffsynth_dl.log; }
pip install -q modelscope >> /root/bench/logs/diffsynth_dl.log 2>&1 && log "OK modelscope" || log "FAIL modelscope"
python3 - <<'PY' >> /root/bench/logs/diffsynth_dl.log 2>&1
from modelscope import snapshot_download
base='/root/bench/models/diffsynth'
for mid, pats in [
 ('DiffSynth-Studio/MiniMax-H3-Image-EntroPack', ['models/dit_8bit_int8.*','models/dit_extreme_3bpp.*','models/vae_int8.*']),
 ('DiffSynth-Studio/EntroPackPreQuants', ['models/MiniMax-H3/text_encoder_int8_convrot.*','models/MiniMax-H3/text_encoder_3bpp.*']),
 ('MiniMax/MiniMax-H3-Image', ['pdd_fused_heads.safetensors','processor/*']),
]:
    print('DOWNLOAD', mid, pats, flush=True)
    p=snapshot_download(mid, allow_patterns=pats, local_dir=base+'/'+mid.replace('/','__'))
    print('OK', p, flush=True)
PY
log "DONE diffsynth downloads"
