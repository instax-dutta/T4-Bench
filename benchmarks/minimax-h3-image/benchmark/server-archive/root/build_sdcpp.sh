#!/bin/bash
set -e
export CUDACXX=/usr/local/cuda/bin/nvcc
export PATH=/usr/local/cuda/bin:$PATH
cd /root/bench/repos/stable-diffusion.cpp/build
cmake -DSD_CUDA=ON -DCMAKE_CUDA_COMPILER=/usr/local/cuda/bin/nvcc -DCMAKE_CUDA_ARCHITECTURES=75 -DCMAKE_BUILD_TYPE=Release -DSD_CUDA_CUTLASS_PATH= .. >> /root/bench/logs/build.log 2>&1
cmake --build . -j4 >> /root/bench/logs/build.log 2>&1
echo "[$(date -u +%H:%M:%S)] BUILD DONE" | tee -a /root/bench/logs/build.log
