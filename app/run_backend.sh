#!/bin/bash
# Arranca el backend FastAPI con uv
cd "$(dirname "$0")/backend"
echo "🚀 Iniciando backend en http://localhost:8000"
echo "   Docs: http://localhost:8000/docs"
~/.local/bin/uv run --with fastapi --with "uvicorn[standard]" --with pandas \
  --with numpy --with pyarrow --with strands-agents --with boto3 \
  uvicorn main:app --reload --host 0.0.0.0 --port 8000
