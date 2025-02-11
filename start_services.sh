#!/bin/sh

# Start Ollama serve in the background
ollama serve &

# Wait for a few seconds to ensure Ollama serve starts
sleep 10

# Pull the necessary models
ollama pull llama3:8b
#ollama pull llama3.3:70b
ollama pull nomic-embed-text

# Start Streamlit
cd /src
streamlit run main.py --server.port 5000
