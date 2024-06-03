#!/bin/bash

curl http://localhost:11434/api/generate -d '{"model": "open-hermes-2-4_0", "prompt": "Hello, how are you?"}'
