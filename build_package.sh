#!/bin/bash
# Build wheel distribution.
set -e
python -m pip install --upgrade build >/dev/null
python -m build
