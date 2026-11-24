#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
if [[ -x "$ROOT_DIR/.venv/bin/python" ]]; then
    PYTHON="$ROOT_DIR/.venv/bin/python"
else
    PYTHON="${PYTHON:-python3}"
fi

export PYTHONPATH="$ROOT_DIR/src${PYTHONPATH:+:${PYTHONPATH}}"
exec "$PYTHON" -m config_converter "$@"
