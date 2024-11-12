FROM ollama/ollama:latest

# Copy Modelfile
COPY Modelfile /Modelfile

# Expose port
EXPOSE 11434

# Run Ollama
CMD ["ollama", "serve"]