#!/usr/bin/env bash
set -euo pipefail

if [[ -d /app ]]; then
    cd /app
fi

exec python -m streamlit run app.py --server.address 0.0.0.0 --server.port "${PORT:-8501}"
