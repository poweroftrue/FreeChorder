#!/bin/bash
# Ultra-fast impulse mode launcher
# Bypasses virtual environment and runs minimal Python directly

PYTHON_PATH="/Users/mostafa/freechorder/venv/bin/python3"
SCRIPT_PATH="/Users/mostafa/freechorder/src/freechorder/cli/quick_impulse.py"

# Use system Python if venv not available (even faster)
if [ ! -f "$PYTHON_PATH" ]; then
    PYTHON_PATH="python3"
fi

# Run with minimal startup overhead
exec $PYTHON_PATH -S $SCRIPT_PATH
