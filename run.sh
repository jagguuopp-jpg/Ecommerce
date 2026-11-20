#!/bin/bash
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

PYTHON_BIN="$SCRIPT_DIR/.venv/bin/python"
if [ ! -f "$PYTHON_BIN" ]; then
    PYTHON_BIN="python3"
fi

# Release port 8000 if another lingering instance is running
PID=$(lsof -ti:8000 2>/dev/null || true)
if [ -n "$PID" ]; then
    echo "Releasing port 8000 (occupied by PID $PID)..."
    kill -9 $PID 2>/dev/null || true
    sleep 1
fi

echo "Starting NEXORIG development server at http://127.0.0.1:8000/ ..."
exec "$PYTHON_BIN" Pc_store/manage.py runserver 127.0.0.1:8000
