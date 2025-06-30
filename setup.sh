bash#!/bin/bash

# Install Ollama
curl -fsSL https://ollama.ai/install.sh | sh

# Install Python dependencies
pip install -r requirements.txt

echo "Setup complete! Run: python app.py"
