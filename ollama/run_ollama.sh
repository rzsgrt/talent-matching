#!/bin/bash

# echo "Starting Ollama server..."
# ollama serve &
# ollama run llama3.2:1b


# echo "Waiting for Ollama server to be active..."
# while [ "$(ollama list | grep 'NAME')" == "" ]; do
    # sleep 1
# done

ollama create model -f ./Modelfile &
ollama run model