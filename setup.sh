#!/bin/bash

# Create virtual environment if it doesn't exist
if [ ! -d ".venv" ]; then
  python3 -m venv .venv
fi

# Install dependencies
.venv/bin/pip install -r requirements.txt

echo "\nSetup complete! Run your app with:"
echo ".venv/bin/python main.py" 