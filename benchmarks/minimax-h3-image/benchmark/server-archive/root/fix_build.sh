#!/bin/bash
set -e
export CUDACXX=/usr/local/cuda/bin/nvcc
export PATH=/usr/local/cuda/bin:$PATH
export LD_LIBRARY_PATH=/usr/local/nvidia/lib64:${LD_LIBRARY_PATH:-}
cd /root/bench/repos/stable-diffusion.cpp/build
cmake -DSD_CUDA=ON -DCMAKE_CUDA_COMPILER=/usr/local/cuda/bin/nvcc -DCMAKE_CUDA_ARCHITECTURES=75 -DCMAKE_BUILD_TYPE=Release -DSD_CUDA_CUTLASS_PATH= -DGGML_CUDA_NO_VMM=ON -DCUDA_CUDA_LIBRARY=/usr/local/nvidia/lib64/libcuda.so -DCMAKE_LIBRARY_PATH=/usr/local/nvidia/lib64 .. >> /root/bench/logs/build.log 2>&1
cmake --build . -j4 >> /root/bench/logs/build.log 2>&1
echo "[$(date -u +%H:%M:%S)] BUILD DONE" | tee -a /root/bench/logs/build.log
