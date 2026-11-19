window.BENCH_DATA = {
  "generated": "2026-11-19",
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
  "limitations": [
    "The 0–100 quality score comes from an image-text model. It is not a human beauty rating.",
    "Image results are square 1024px pictures; video results are short clips at each model's usual size.",
    "The larger 13B video model could not be finished: the machine ran out of storage at 57 of 93 GB.",
    "Each result loads the model fresh unless the row says warm or batched."
  ]
};
