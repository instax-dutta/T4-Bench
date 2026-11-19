#!/bin/bash
cd /root/bench/repos/DiffSynth-Studio
pip install -q -e . >> /root/bench/logs/diffsynth_install.log 2>&1
pip install -q diffsynth==2.2.2 cupy-cuda13x >> /root/bench/logs/diffsynth_install.log 2>&1
echo "[$(date -u +%H:%M:%S)] DIFFSYNTH INSTALL DONE" | tee -a /root/bench/logs/diffsynth_install.log
