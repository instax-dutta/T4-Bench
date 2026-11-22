#!/usr/bin/env python3
"""Documented-infeasibility check: load the native NVFP4/MXFP8 Inkling-2-Mini
checkpoint with transformers on one T4. Expected outcome: the modelopt
checkpoint must dequantize to bf16 (~53 GB) which exceeds both the 15 GB GPU
and the 31 GB host RAM, so this fails during from_pretrained shard loading.
The failure row is the measurement.
"""
import subprocess
import sys

cmd = [sys.executable, "-c", """
import torch
from transformers import AutoModelForMultimodalLM
try:
    m = AutoModelForMultimodalLM.from_pretrained(
        "thinkingmachines/Inkling-2-Mini", device_map="auto")
    print("UNEXPECTED: loaded", sum(p.numel() for p in m.parameters()))
except Exception as e:
    print("EXPECTED-FAIL:", type(e).__name__, str(e)[:300])
    raise SystemExit(3)
"""]
raise SystemExit(subprocess.run(cmd).returncode)
