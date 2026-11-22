window.BENCH_DATA = {
  "generated": "2026-11-22",
  "server": {
    "gpus": 2,
    "gpu": "Tesla T4 15360 MiB",
    "arch": "sm_75 Turing",
    "ramGiB": 31,
    "cuda": "13.0",
    "torch": "2.11.0+cu130"
  },
  "imageModels": [
    {
      "id": "flux2-klein-4b",
      "name": "FLUX.2 klein 4B",
      "steps": 4,
      "coldMedian": 23.7,
      "coldMin": 22.9,
      "coldMax": 30.4,
      "peakVramMiB": 3677,
      "bestThroughput": 374,
      "bestMode": "batch4_per_gpu_dual",
      "clip": 0.3924,
      "qualityScore": 39,
      "clipN": 14
    },
    {
      "id": "qwen-image-2.1-viggle-4step",
      "name": "Qwen-Image 2.1 Viggle 4-step",
      "steps": 4,
      "coldMedian": 64.0,
      "coldMin": 46.4,
      "coldMax": 69.3,
      "peakVramMiB": 5867,
      "bestThroughput": 150,
      "bestMode": "batch2_per_gpu_dual",
      "clip": 0.3839,
      "qualityScore": 38,
      "clipN": 11
    },
    {
      "id": "z-image-turbo",
      "name": "Z-Image-Turbo",
      "steps": 8,
      "coldMedian": 47.6,
      "coldMin": 46.9,
      "coldMax": 49.5,
      "peakVramMiB": 4651,
      "bestThroughput": 147,
      "bestMode": "batch2_per_gpu_dual",
      "clip": 0.3814,
      "qualityScore": 38,
      "clipN": 12
    },
    {
      "id": "sdxl",
      "name": "SDXL 1.0",
      "steps": 30,
      "coldMedian": 63.5,
      "coldMin": 63.4,
      "coldMax": 67.5,
      "peakVramMiB": 7313,
      "bestThroughput": 107,
      "bestMode": "batch2_per_gpu_dual",
      "clip": 0.3894,
      "qualityScore": 39,
      "clipN": 14
    }
  ],
  "imageOptimization": [
    {
      "model": "flux2-klein-4b",
      "mode": "baseline_cold_1",
      "imagesPerHour": 152,
      "wall": 23.693,
      "images": 1,
      "peak": 3677
    },
    {
      "model": "flux2-klein-4b",
      "mode": "batch4_single_gpu",
      "imagesPerHour": 167,
      "wall": 86.298,
      "images": 4,
      "peak": 3677
    },
    {
      "model": "flux2-klein-4b",
      "mode": "batch2_per_gpu_dual",
      "imagesPerHour": 349,
      "wall": 41.281,
      "images": 4,
      "peak": 3677
    },
    {
      "model": "flux2-klein-4b",
      "mode": "batch8_single_gpu",
      "imagesPerHour": 197,
      "wall": 146.258,
      "images": 8,
      "peak": 3677
    },
    {
      "model": "flux2-klein-4b",
      "mode": "batch4_per_gpu_dual",
      "imagesPerHour": 374,
      "wall": 77.02,
      "images": 8,
      "peak": 3677
    },
    {
      "model": "z-image-turbo",
      "mode": "baseline_cold_1",
      "imagesPerHour": 76,
      "wall": 47.609,
      "images": 1,
      "peak": 4651
    },
    {
      "model": "z-image-turbo",
      "mode": "batch4_single_gpu",
      "imagesPerHour": 81,
      "wall": 177.977,
      "images": 4,
      "peak": 4651
    },
    {
      "model": "z-image-turbo",
      "mode": "batch2_per_gpu_dual",
      "imagesPerHour": 147,
      "wall": 97.734,
      "images": 4,
      "peak": 4651
    },
    {
      "model": "qwen-image-2.1-viggle-4step",
      "mode": "baseline_cold_1",
      "imagesPerHour": 56,
      "wall": 64.004,
      "images": 1,
      "peak": 5867
    },
    {
      "model": "qwen-image-2.1-viggle-4step",
      "mode": "batch4_single_gpu",
      "imagesPerHour": 90,
      "wall": 160.195,
      "images": 4,
      "peak": 5867
    },
    {
      "model": "qwen-image-2.1-viggle-4step",
      "mode": "batch2_per_gpu_dual",
      "imagesPerHour": 150,
      "wall": 96.066,
      "images": 4,
      "peak": 5867
    },
    {
      "model": "sdxl",
      "mode": "baseline_cold_1",
      "imagesPerHour": 57,
      "wall": 63.523,
      "images": 1,
      "peak": 7313
    },
    {
      "model": "sdxl",
      "mode": "batch4_single_gpu",
      "imagesPerHour": 58,
      "wall": 248.739,
      "images": 4,
      "peak": 7313
    },
    {
      "model": "sdxl",
      "mode": "batch2_per_gpu_dual",
      "imagesPerHour": 107,
      "wall": 134.794,
      "images": 4,
      "peak": 7313
    }
  ],
  "videoModels": [
    {
      "id": "cog_s50_f49",
      "model": "cogvideox-2b",
      "steps": 50,
      "frames": 49,
      "size": "720x480",
      "wall": 1053.0,
      "clips": 1,
      "perClip": 1053.0,
      "perClipAll": [],
      "fpsGenerated": 0.0465,
      "peakVramMiB": 11301,
      "clip": 0.2645,
      "qualityScore": 26
    },
    {
      "id": "ltx2b_s8_f121",
      "model": "ltx2b-distilled",
      "steps": 8,
      "frames": 121,
      "size": "768x512",
      "wall": 131.4,
      "clips": 1,
      "perClip": 131.4,
      "perClipAll": [],
      "fpsGenerated": 0.9209,
      "peakVramMiB": 11032,
      "clip": 0.2329,
      "qualityScore": 23
    },
    {
      "id": "ltx_multi3",
      "model": "ltx2b-warm3",
      "steps": 8,
      "frames": 121,
      "size": "768x512",
      "wall": 270.4,
      "clips": 3,
      "perClip": 49.2,
      "perClipAll": [
        73.63,
        49.245,
        47.99
      ],
      "fpsGenerated": 2.4593,
      "peakVramMiB": 11033,
      "clip": 0.2006,
      "qualityScore": 20
    },
    {
      "id": "ltx_multi3_s4_f49",
      "model": "ltx2b-warm3-s4",
      "steps": 4,
      "frames": 49,
      "size": "768x512",
      "wall": 207.7,
      "clips": 3,
      "perClip": 27.6,
      "perClipAll": [
        51.518,
        27.569,
        27.357
      ],
      "fpsGenerated": 1.7754,
      "peakVramMiB": 11033,
      "clip": 0.2139,
      "qualityScore": 21
    }
  ],
  "h3": {
    "quants": [
      {
        "quant": "Q3_K_M",
        "median": 100.5,
        "runs": 10
      },
      {
        "quant": "Q5_K_M",
        "median": 126.9,
        "runs": 4
      },
      {
        "quant": "UD-Q4_K_XL",
        "median": 175.5,
        "runs": 7
      }
    ],
    "weightsGiB": [
      {
        "name": "All BF16",
        "gib": 126.0
      },
      {
        "name": "All FP8",
        "gib": 64.1
      },
      {
        "name": "All 4-bit",
        "gib": 33.1
      },
      {
        "name": "One T4 VRAM",
        "gib": 15.0
      }
    ],
    "native4096": [
      {
        "quant": "Q3_K_M",
        "wall": 659.7,
        "peak": 14653
      },
      {
        "quant": "UD-Q4_K_XL",
        "wall": 672.0,
        "peak": 14493
      }
    ]
  },
  "winners": {
    "image": "FLUX.2 klein 4B",
    "imageThroughput": 374,
    "imageClip": 0.3924,
    "video": "LTX-Video 2B 0.9.8 distilled",
    "videoClipBest": 0.2645,
    "videoClipName": "CogVideoX-2b",
    "steadyClipSeconds": 27.6,
    "cogSeconds": 1053.0
  },
  "llm": [
    {
      "model": "LiquidAI LFM2.5-8B-A1B",
      "sizeGB": 4.9,
      "vramGB": 5.7,
      "decodeTokS": 119.0,
      "prefillTokS": 800.0,
      "gpus": "1x T4"
    },
    {
      "model": "XHToken Spark-X2.5-1.7B",
      "sizeGB": 1.1,
      "vramGB": 1.3,
      "decodeTokS": 100.0,
      "prefillTokS": null,
      "gpus": "1x T4"
    },
    {
      "model": "XHToken Spark-X2.5-4B",
      "sizeGB": 2.5,
      "vramGB": 3.7,
      "decodeTokS": 54.0,
      "prefillTokS": 1385.0,
      "gpus": "1x T4"
    },
    {
      "model": "Qwen3-Coder-30B-A3B",
      "sizeGB": 18.0,
      "vramGB": 22.0,
      "decodeTokS": 71.0,
      "prefillTokS": 165.0,
      "gpus": "2x T4 split"
    },
    {
      "model": "google Gemma 4 12B IT",
      "sizeGB": 6.7,
      "vramGB": 8.1,
      "decodeTokS": 21.0,
      "prefillTokS": 144.0,
      "gpus": "1x T4"
    },
    {
      "model": "Qwen3.8-27B",
      "sizeGB": 16.0,
      "vramGB": 17.7,
      "decodeTokS": 13.0,
      "prefillTokS": 52.0,
      "gpus": "2x T4 split"
    }
  ],
  "inkling": {
    "single": [
      {
        "id": "Inkling-2-Mini-UD-IQ1_M",
        "name": "UD-IQ1_M (1-bit)",
        "sizeGiB": 7.46,
        "pp": 312.5,
        "tg": 26.5,
        "peakVramMiB": 8635
      },
      {
        "id": "Inkling-2-Mini-Uncensored-AD-IQ2_M",
        "name": "AD-IQ2_M (uncens.)",
        "sizeGiB": 8.06,
        "pp": 341.8,
        "tg": 26.1,
        "peakVramMiB": 9233
      },
      {
        "id": "Inkling-2-Mini-UD-Q2_K_XL",
        "name": "UD-Q2_K_XL",
        "sizeGiB": 8.51,
        "pp": 314.6,
        "tg": 25.1,
        "peakVramMiB": 9699
      },
      {
        "id": "Inkling-2-Mini-UD-Q3_K_XL",
        "name": "UD-Q3_K_XL",
        "sizeGiB": 12.69,
        "pp": 312.3,
        "tg": 24.3,
        "peakVramMiB": 13913
      },
      {
        "id": "Inkling-2-Mini-UD-IQ3_XXS",
        "name": "UD-IQ3_XXS",
        "sizeGiB": 10.86,
        "pp": 310.3,
        "tg": 23.0,
        "peakVramMiB": 12091
      },
      {
        "id": "Inkling-2-Mini-Uncensored-AD-IQ3_S",
        "name": "AD-IQ3_S (uncens.)",
        "sizeGiB": 12.43,
        "pp": 319.9,
        "tg": 22.3,
        "peakVramMiB": 13471
      }
    ],
    "sizes": [
      {
        "name": "UD-IQ1_M (1-bit)",
        "sizeGiB": 7.46,
        "fits": true,
        "tg": 26.5
      },
      {
        "name": "AD-IQ2_M (uncens.)",
        "sizeGiB": 8.06,
        "fits": true,
        "tg": 26.1
      },
      {
        "name": "UD-Q2_K_XL",
        "sizeGiB": 8.51,
        "fits": true,
        "tg": 25.1
      },
      {
        "name": "UD-IQ3_XXS",
        "sizeGiB": 10.86,
        "fits": true,
        "tg": 23.0
      },
      {
        "name": "AD-IQ3_S (uncens.)",
        "sizeGiB": 12.43,
        "fits": true,
        "tg": 22.3
      },
      {
        "name": "UD-Q3_K_XL",
        "sizeGiB": 12.69,
        "fits": true,
        "tg": 24.3
      },
      {
        "name": "AD-Q4_K (uncens.)",
        "sizeGiB": 15.46,
        "fits": false,
        "tg": 2.4
      },
      {
        "name": "UD-Q4_K_M",
        "sizeGiB": 15.46,
        "fits": false,
        "tg": 2.1
      },
      {
        "name": "UD-Q4_K_XL",
        "sizeGiB": 16.42,
        "fits": false,
        "tg": 2.1
      },
      {
        "name": "UD-Q8_K_XL",
        "sizeGiB": 21.3,
        "fits": false,
        "tg": 1.9
      }
    ],
    "t4GiB": 15.0,
    "hybridNote": "4-bit quants (15.5-21.3 GiB) do not fit one T4 and have no cross-GPU split; a GPU+CPU hybrid manages only 1.9-2.4 tok/s.",
    "vision": [
      {
        "config": "AD-IQ2_M + vision, one T4",
        "wallS": 37.3,
        "peakVramMiB": 14533,
        "result": "works"
      },
      {
        "config": "AD-IQ3_S + vision, one T4",
        "wallS": "",
        "peakVramMiB": 14565,
        "result": "out of memory during image encode"
      },
      {
        "config": "UD-Q4_K_XL hybrid + vision",
        "wallS": "",
        "peakVramMiB": 513,
        "result": "context creation out of memory"
      }
    ],
    "negatives": [
      [
        "ollama",
        "official tag is MLX-only; MLX runtime unavailable on CUDA"
      ],
      [
        "ollama",
        "local GGUF import fails: unknown architecture inkling2_loop in Ollama bundled llama.cpp"
      ],
      [
        "ollama",
        "arch inkling2_loop unsupported in Ollama bundled runner"
      ],
      [
        "vllm",
        "    For further information visit https://errors.pydantic.dev/2.14/v/value_error"
      ],
      [
        "sglang",
        "/usr/bin/python3: Error while finding module specification for 'sglang.launch_se"
      ],
      [
        "transformers-native",
        "You can update Transformers with the command `pip install --upgr"
      ]
    ],
    "engine": "llama.cpp b12633 (CUDA 12.8 prebuilt) is the only engine that runs Inkling-2-Mini on T4"
  },
  "agentConcurrency": [
    {
      "agents": 1.0,
      "perAgent": "71 tok/s",
      "aggregate": "11 tok/s (load-dominated wall)"
    },
    {
      "agents": 2.0,
      "perAgent": "56 + 52 tok/s",
      "aggregate": "**92 tok/s** over 2.3s wall"
    }
  ],
  "toolEval": [
    {
      "metric": "Passed / partial / failed",
      "score": "9 / 4 / 2"
    },
    {
      "metric": "Points",
      "score": "22/30"
    },
    {
      "metric": "Quality",
      "score": "73/100"
    },
    {
      "metric": "Responsiveness",
      "score": "74/100 (median turn 1.5s)"
    },
    {
      "metric": "Deployability",
      "score": "73/100"
    },
    {
      "metric": "Weakest category",
      "score": "Multi-Step Chains (33%)"
    },
    {
      "metric": "Safety",
      "score": "1 warning (TC-08: batched tools before reading results)"
    }
  ],
  "fineTuning": {
    "results": [
      {
        "arm": "`unsloth_native`",
        "result": "completed",
        "peakMiB": 7111.0,
        "loss": 0.829
      },
      {
        "arm": "`soup` `backend: unsloth`",
        "result": "completed",
        "peakMiB": 7109.0,
        "loss": 0.8044
      },
      {
        "arm": "`soup` `backend: transformers` (unsloth installed)",
        "result": "completed",
        "peakMiB": 14867.0,
        "loss": 0.8058
      },
      {
        "arm": "`soup` `backend: transformers` (unsloth blocked)",
        "result": "**OOM**",
        "peakMiB": 14817.0,
        "loss": null
      }
    ],
    "quality": [
      {
        "adapter": "unsloth",
        "loss": 1.03731
      },
      {
        "adapter": "soup transformers",
        "loss": 1.0405
      }
    ],
    "steps": [
      {
        "arm": "`unsloth_native`",
        "step": "**8.65 s**",
        "note": "precise, via TrainerCallback"
      },
      {
        "arm": "`soup` arms",
        "step": "~9-10 s (upper bound)",
        "note": "whole-process span / 50, includes ~36 s model load"
      }
    ]
  },
  "spark": {
    "inference": [
      {
        "metric": "Load time (safetensors → CUDA)",
        "small": "20s",
        "large": "8.5s"
      },
      {
        "metric": "VRAM, BF16, idle",
        "small": "3.4GB",
        "large": "8.2GB"
      },
      {
        "metric": "VRAM under agentic load",
        "small": "~4.8GB, stable",
        "large": "~10-12GB, OOMs in long sessions"
      },
      {
        "metric": "Throughput (thinking on, T4)",
        "small": "~16 tok/s",
        "large": "~12 tok/s"
      },
      {
        "metric": "Trivial-Q thinking length",
        "small": "179 tokens (verbose)",
        "large": "54 tokens (decisive)"
      }
    ],
    "tasks": [
      {
        "task": "**T1** implement `median()` to pass 5 pytest tests",
        "small": "PASS — 5 steps, 1 tool error, ran tests",
        "large": "PASS — 4 steps, 0 errors, ran tests"
      },
      {
        "task": "**T2** debug repo (binary-search off-by-one across 2 files), 7 tests",
        "small": "PASS — 3 steps, 5 errors, ran tests",
        "large": "PASS — 14 steps, 9 errors, **never ran the suite itself** (final state correct at step limit — verification gap)"
      },
      {
        "task": "**T3** implement LRU cache from spec from scratch, 5 tests",
        "small": "**FAIL** — 3 tool steps + 17 no-call turns, never wrote a working file",
        "large": "PASS — 5 steps, 1 error, ran tests"
      },
      {
        "task": "Agentic score",
        "small": "**2/3**",
        "large": "**3/3**"
      }
    ]
  },
  "ternary": {
    "singleT4": [
      {
        "packing": "PQ2_0",
        "pp512": 293.9,
        "tg128": 15.1
      },
      {
        "packing": "PTQ1_0",
        "pp512": 200.3,
        "tg128": 15.4
      }
    ],
    "dualT4": [
      {
        "packing": "PQ2_0",
        "pp512": 313.0,
        "tg128": 22.9
      }
    ],
    "context": [
      {
        "context": "4k",
        "vram": "~7.2 GB (single T4)",
        "notes": "weights only + tiny KV"
      },
      {
        "context": "64k",
        "vram": "**12.4 GB** (6.15 + 6.29 split)",
        "notes": "opencode server config"
      },
      {
        "context": "262144 (full)",
        "vram": "**26.2 GB** (13.0 + 13.2 split)",
        "notes": "loads and serves on 2xT4"
      }
    ]
  },
  "sourceFiles": [
    "2x Tesla T4 Kaggle Benchmarks.md",
    "Soup vs Unsloth Fine-Tuning Benchmark Tesla T4 2026.md",
    "Spark X2.5 Agentic Benchmark Report.md",
    "Ternary Bonsai 2 27B Benchmark Report.md"
  ],
  "limitations": [
    "These notes describe how we measured. They are not limits of the T4 GPUs themselves.",
    "Our 0 to 100 quality score is a similarity check against the prompt. It tells you whether the output followed the words, not whether people like it.",
    "Images were tested at 1024x1024. Video clips were kept short and used each model's normal preset.",
    "We stopped the 13B video run halfway through its download. The Kaggle session ran out of writable space at 57 of 93 GB, so this says nothing about the model itself.",
    "Most timings include a fresh model load. Rows marked warm or batched reuse a model that is already loaded.",
    "Inkling speeds are token generation with a 512-token prompt and 256 generated tokens. The looped model cannot fully disable its reasoning, so per-answer time is longer than tokens-per-second suggests.",
    "Inkling 4-bit quants were only measured in a GPU-plus-CPU hybrid at 1.9-2.4 tokens per second, because llama.cpp has no way to split this architecture across both T4s."
  ]
};
