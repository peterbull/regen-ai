#!/bin/bash
# set -x
# Set git credentials config
git config --global credential.helper store

# Login to Hugging Face
huggingface-cli login --token $HUGGINGFACE_TOKEN --add-to-git-credential

# Set HF_HOME to the mapped volume to prevent extra downloads during development
export HF_HOME=/usr/share/downloads

# # Download Model
# if [ ! -d "/usr/share/downloads/$HUGGINGFACE_MODEL_NAME" ]; then
#     huggingface-cli download $HUGGINGFACE_MODEL_DIR $HUGGINGFACE_MODEL_NAME --local-dir /usr/share/downloads   --local-dir-use-symlinks False
# fi

# # Config model from Modelfile
# ollama create $OLLAMA_MODEL_ALIAS -f /usr/share/modelfiles/$OLLAMA_MODEL_ALIAS/Modelfile

# Start server
ollama serve
