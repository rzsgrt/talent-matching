FROM ollama/ollama:latest

# Copy Modelfile
COPY Modelfile /tmp/Modelfile
COPY ./run_ollama.sh /tmp/run_ollama.sh
WORKDIR /tmp
RUN chmod +x run_ollama.sh

# Expose port
EXPOSE 11434

# Run Ollama
# CMD ["ollama", "serve"]
# CMD ollama create mymodel -f Modelfile