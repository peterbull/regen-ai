#!/bin/bash
# set -x
# Set git credentials config
git config --global credential.helper store

# Login to Hugging Face
huggingface-cli login --token $HUGGINGFACE_TOKEN --add-to-git-credential

# Download Model
if [ ! -d "/usr/share/downloads/$HUGGINGFACE_MODEL_NAME" ]; then
    huggingface-cli download $HUGGINGFACE_MODEL_DIR $HUGGINGFACE_MODEL_NAME --local-dir /usr/share/downloads   --local-dir-use-symlinks False
fi

# Start server
ollama serve