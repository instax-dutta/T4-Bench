#!/usr/bin/env python3
"""Measured feasibility test: can the INT8 LongCat-Video-Avatar-1.6 DiT
fit on one Tesla T4 (15360 MiB, sm_75)?

Loads the quantized DiT on CPU, then moves it to GPU 0 while sampling
per-GPU memory at 1 Hz. Writes /workspace/weights/int8_load_test.json.

Context parallelism in this repo splits activations, not weights, so each
rank must hold the full 14.78 GiB INT8 DiT - this test measures whether even
that alone fits.
"""
import json
import os
import subprocess
import sys
import threading
import time

sys.path.insert(0, "/workspace/LongCat-Video")
CKPT = "/workspace/weights/LongCat-Video-Avatar-1.6"
OUT = "/workspace/weights/int8_load_test.json"

ENV = dict(os.environ)
ENV["LD_LIBRARY_PATH"] = "/usr/local/nvidia/lib64:/usr/local/cuda-13.0/lib64"

peaks = {}
stop = threading.Event()

def sample():
    cmd = ["nvidia-smi", "--query-gpu=index,memory.used",
           "--format=csv,noheader,nounits"]
    while not stop.is_set():
        try:
            out = subprocess.run(cmd, capture_output=True, text=True,
                                 env=ENV, timeout=5)
            for line in out.stdout.strip().splitlines():
                idx, used = [x.strip() for x in line.split(",")]
                i = int(idx)
                peaks[i] = max(peaks.get(i, 0), int(used))
        except Exception:
            pass
        stop.wait(1.0)

t = threading.Thread(target=sample, daemon=True)
t.start()

import torch  # noqa: E402
from longcat_video.modules.quantization import load_quantized_dit  # noqa: E402

res = {"int8_shard_bytes": 15880383936,
       "t4_total_mib": 15360,
       "cp_split_hw": [2, 1]}

t0 = time.time()
dit = load_quantized_dit(CKPT, subfolder="base_model_int8",
                         cp_split_hw=[2, 1])
res["cpu_load_s"] = round(time.time() - t0, 1)
res["param_count"] = sum(p.numel() for p in dit.parameters())
res["int8_param_bytes"] = sum(
    b.numel() * b.element_size()
    for b in dit.buffers() if b.dtype == torch.int8)

try:
    dit = dit.to(0)
    torch.cuda.synchronize()
    res["to_gpu"] = "OK"
    res["torch_peak_alloc_mib"] = round(
        torch.cuda.max_memory_allocated(0) / 2**20, 1)
except Exception as e:
    res["to_gpu"] = f"OOM: {type(e).__name__}: {str(e)[:300]}"
res["nvidia_smi_peak_mib"] = dict(peaks)
res["free_before_mib"] = peaks.get(0, 0)

stop.set()
t.join(timeout=5)
with open(OUT, "w") as f:
    json.dump(res, f, indent=2)
print(json.dumps(res, indent=2))
