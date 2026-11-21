#!/usr/bin/env python3
"""Benchmark driver for LongCat-Video-Avatar-1.6 on 2x Tesla T4.

Usage:
  python3 benchmark_avatar.py <resolution 480p|720p> <segments> <runs> \
      <warmup y|n> <compile y|n> <model_type> [quant int8|fp16] [nproc 1|2] [tag]

Each timed run is a fresh torchrun process (cold load, warm inductor caches
after the first). VRAM is sampled at 1 Hz for the whole process lifetime.
Rows append to /workspace/weights/benchmark_results.csv:
  tag,resolution,segments,run,wall_s,exit_code,gpu0_peak_mib,gpu1_peak_mib,frames,duration_s,fps,video
Warm-up run is recorded with run=0 and excluded from medians.
"""
import csv
import glob
import os
import subprocess
import sys
import threading
import time

REPO = "/workspace/LongCat-Video"
WEIGHTS = "/workspace/weights"
CKPT = f"{WEIGHTS}/LongCat-Video-Avatar-1.6"
CSV_PATH = f"{WEIGHTS}/benchmark_results.csv"
LOG_DIR = f"{WEIGHTS}/logs"
HEADER = ["tag", "resolution", "segments", "run", "wall_s", "exit_code",
          "gpu0_peak_mib", "gpu1_peak_mib", "frames", "duration_s", "fps", "video"]

ENV = dict(os.environ)
ENV["LD_LIBRARY_PATH"] = "/usr/local/nvidia/lib64:/usr/local/cuda-13.0/lib64"
ENV["TORCHINDUCTOR_CACHE_DIR"] = f"{WEIGHTS}/inductor_cache"
ENV.setdefault("TOKENIZERS_PARALLELISM", "false")


def gpu_sampler(stop, peaks):
    """Sample per-GPU memory.used at 1 Hz until stop is set."""
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


def ffprobe(path):
    """Return (frames, duration_s, fps) or (None, None, None)."""
    try:
        out = subprocess.run(
            ["ffprobe", "-v", "error", "-select_streams", "v:0",
             "-count_frames", "-show_entries",
             "stream=nb_read_frames,duration,avg_frame_rate",
             "-of", "default=nw=1", path],
            capture_output=True, text=True, env=ENV, timeout=120)
        d = dict(kv.split("=", 1) for kv in out.stdout.strip().splitlines() if "=" in kv)
        frames = int(d.get("nb_read_frames", 0)) or None
        dur = float(d["duration"]) if d.get("duration") else None
        fps = None
        if d.get("avg_frame_rate") and d["avg_frame_rate"] != "0/0":
            n, _, den = d["avg_frame_rate"].partition("/")
            den = int(den or 1)
            fps = round(int(n) / den, 3) if den else None
        return frames, dur, fps
    except Exception:
        return None, None, None


def run_once(tag, resolution, segments, model_type, quant, nproc,
             compile_flag, run_id, warmup):
    out_dir = f"{WEIGHTS}/out_{tag}_run{run_id}"
    log_path = f"{LOG_DIR}/{tag}_run{run_id}.log"
    cmd = ["torchrun", f"--nproc_per_node={nproc}",
           f"{REPO}/run_demo_avatar_single_audio_to_video.py",
           f"--stage_1=ai2v",
           f"--checkpoint_dir={CKPT}",
           f"--input_json=assets/avatar/single_example_1.json",
           f"--resolution={resolution}",
           f"--num_segments={segments}",
           f"--model_type={model_type}",
           f"--context_parallel_size={nproc}",
           "--use_distill", "--mix_steps=4", "--mix_alpha=1.0",
           "--lora_path=loraB/lora.safetensors"]
    if quant == "int8":
        cmd.append("--use_int8")
    if compile_flag:
        cmd += ["--compile_dit", "--compile_vae"]
    cmd.append(f"--output_dir={out_dir}")

    stop = threading.Event()
    peaks = {}
    t = threading.Thread(target=gpu_sampler, args=(stop, peaks), daemon=True)
    t.start()
    t0 = time.time()
    with open(log_path, "w") as log:
        proc = subprocess.run(cmd, cwd=REPO, env=ENV, stdout=log,
                              stderr=subprocess.STDOUT)
    wall = time.time() - t0
    stop.set()
    t.join(timeout=5)

    frames = dur = fps = None
    video = ""
    mp4s = sorted(glob.glob(f"{out_dir}/**/*.mp4", recursive=True),
                  key=os.path.getmtime)
    if mp4s:
        video = mp4s[-1]
        frames, dur, fps = ffprobe(video)

    row = [tag, resolution, segments, run_id, f"{wall:.1f}", proc.returncode,
           peaks.get(0, 0), peaks.get(1, 0), frames, dur, fps, video]
    with open(CSV_PATH, "a", newline="") as f:
        csv.writer(f).writerow(row)
    print(f"[run] tag={tag} run={run_id} wall={wall:.1f}s exit={proc.returncode} "
          f"peaks={peaks.get(0,0)}/{peaks.get(1,0)} MiB frames={frames} "
          f"dur={dur} fps={fps}", flush=True)
    return proc.returncode, wall


def main():
    if len(sys.argv) < 7:
        sys.exit(__doc__)
    resolution = sys.argv[1]
    segments = int(sys.argv[2])
    runs = int(sys.argv[3])
    warmup = sys.argv[4].lower().startswith("y")
    compile_flag = sys.argv[5].lower().startswith("y")
    model_type = sys.argv[6]
    quant = sys.argv[7] if len(sys.argv) > 7 else "int8"
    nproc = int(sys.argv[8]) if len(sys.argv) > 8 else 2
    tag = sys.argv[9] if len(sys.argv) > 9 else "A"

    os.makedirs(LOG_DIR, exist_ok=True)
    if not os.path.exists(CSV_PATH):
        with open(CSV_PATH, "w", newline="") as f:
            csv.writer(f).writerow(HEADER)

    if warmup:
        print(f"[warmup] {tag}: compile={compile_flag} starting", flush=True)
        run_once(tag, resolution, segments, model_type, quant, nproc,
                 compile_flag, 0, warmup=True)

    walls = []
    for i in range(1, runs + 1):
        print(f"[run] {tag} {i}/{runs} starting", flush=True)
        code, wall = run_once(tag, resolution, segments, model_type, quant,
                              nproc, compile_flag, i, warmup=False)
        if code == 0:
            walls.append(wall)
    if walls:
        walls.sort()
        med = walls[len(walls) // 2]
        print(f"[summary] tag={tag} n={len(walls)} median_wall_s={med:.1f} "
              f"all={walls}", flush=True)
    else:
        print(f"[summary] tag={tag} no successful runs", flush=True)


if __name__ == "__main__":
    main()
