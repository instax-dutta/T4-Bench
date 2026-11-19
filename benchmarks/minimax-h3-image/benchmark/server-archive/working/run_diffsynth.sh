#!/bin/bash
export PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True
export CUPY_CACHE_DIR=/kaggle/working/bench/cupy
export TMPDIR=/kaggle/working/bench/tmp
export LD_LIBRARY_PATH=/usr/local/nvidia/lib64:${LD_LIBRARY_PATH:-}
id=$1; w=$2; h=$3; seed=$4
mkdir -p /kaggle/working/bench/results/$id
nvidia-smi --query-gpu=index,utilization.gpu,memory.used,memory.total --format=csv,noheader -l 1 > /kaggle/working/bench/results/$id/gpu.csv 2>/dev/null &
SM=$!
python3 /kaggle/working/bench/run_diffsynth.py "$id" "$w" "$h" "$seed" > /kaggle/working/bench/results/$id/ds.log 2>&1
RC=$?
kill $SM 2>/dev/null
echo "DIFFSYNTH $id rc=$RC"
tail -8 /kaggle/working/bench/results/$id/ds.log
