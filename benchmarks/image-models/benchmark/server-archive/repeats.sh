#!/bin/bash
set -u
M=/kaggle/working/quadbench/models
CSV=/kaggle/working/quadbench/results.csv
row=$(/kaggle/working/quadbench/run_one.sh zimage_s42_repeat z-image-turbo $M/zimage/z_image_turbo-Q4_K.gguf $M/zimage/split_files/vae/ae.safetensors $M/shared/Qwen3-4B-Instruct-2507-Q4_K_M.gguf 8 1.0 "" 1024 1024 42 --max-vram 12); echo "$row" >> $CSV; echo "$row"
row=$(/kaggle/working/quadbench/run_one.sh flux_s42_repeat flux2-klein-4b $M/flux/flux-2-klein-4b-Q4_0.gguf $M/flux/split_files/vae/flux2-vae.safetensors $M/shared/Qwen3-4B-Instruct-2507-Q4_K_M.gguf 4 1.0 "" 1024 1024 42 --max-vram 12); echo "$row" >> $CSV; echo "$row"
row=$(/kaggle/working/quadbench/run_sdxl.sh sdxl_s42_repeat 42); echo "$row" >> $CSV; echo "$row"
