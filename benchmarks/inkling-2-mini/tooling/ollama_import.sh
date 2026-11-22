#!/bin/bash
# Import a local GGUF into Ollama for same-file engine comparison.
# Usage: bash /workspace/ollama_import.sh <tag> <gguf-path>
cat <<EOF > /workspace/inkling_modelfile
FROM $2
EOF
ollama create "$1" -f /workspace/inkling_modelfile >> /workspace/weights/logs/ollama_import.log 2>&1
