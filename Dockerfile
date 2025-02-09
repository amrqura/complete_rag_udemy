# Use a newer CUDA-enabled base image
FROM nvidia/cuda:11.8.0-cudnn8-runtime-ubuntu22.04

# Update and install necessary packages
RUN apt-get update -y && \
    apt-get install -y python3-pip python3-dev curl wget build-essential

# Install SQLite3 from source
RUN wget https://www.sqlite.org/2023/sqlite-autoconf-3410200.tar.gz && \
    tar -xvf sqlite-autoconf-3410200.tar.gz && \
    cd sqlite-autoconf-3410200 && \
    ./configure && \
    make && \
    make install && \
    cd .. && \
    rm -rf sqlite-autoconf-3410200 sqlite-autoconf-3410200.tar.gz

# Verify the installation of SQLite3
RUN sqlite3 --version

# Copy application files
COPY . /src
WORKDIR /src

# Install Python dependencies
RUN pip3 install -r requirements.txt --default-timeout=1000 --no-cache-dir

# Install Ollama
RUN curl -fsSL https://ollama.com/install.sh | sh

# Expose the desired port
EXPOSE 5000

# Start Ollama serve and Streamlit in a script to ensure proper execution order
COPY start_services.sh /src/start_services.sh
RUN chmod +x /src/start_services.sh
CMD ["/src/start_services.sh"]
