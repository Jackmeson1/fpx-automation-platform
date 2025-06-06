#!/bin/bash
# Simple environment setup script for FPX Automation Platform
# Creates a Python virtual environment and installs dependencies.
set -e

ENV_DIR="${1:-.venv}"
PYTHON_BIN="${PYTHON:-python3}"

if ! command -v "$PYTHON_BIN" >/dev/null 2>&1; then
  echo "Python not found: $PYTHON_BIN" >&2
  exit 1
fi

$PYTHON_BIN -m venv "$ENV_DIR"
source "$ENV_DIR/bin/activate"

pip install --upgrade pip
pip install -r requirements.txt

echo "Virtual environment created in $ENV_DIR"
echo "Activate with: source $ENV_DIR/bin/activate"
