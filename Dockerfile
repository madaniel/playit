# Dockerfile for Playit with 1Password Integration
FROM ghcr.io/playit-cloud/playit-agent:0.16

# Install dependencies: Python3 and 1Password CLI
USER root

# Install Python3 and curl (Alpine Linux)
RUN apk add --no-cache \
    python3 \
    py3-pip \
    curl \
    ca-certificates \
    unzip \
    bash

# Install 1Password CLI
RUN curl -sSfo op.zip https://cache.agilebits.com/dist/1P/op2/pkg/v2.30.0/op_linux_amd64_v2.30.0.zip && \
    unzip -od /usr/local/bin/ op.zip && \
    rm op.zip && \
    chmod +x /usr/local/bin/op

# Create app directory
RUN mkdir -p /app

# Copy scripts
COPY fetch_secret.py /app/fetch_secret.py
COPY web_server.py /app/web_server.py
COPY entrypoint.sh /app/entrypoint.sh

# Make scripts executable
RUN chmod +x /app/fetch_secret.py /app/entrypoint.sh

# Create directory for playit data
RUN mkdir -p /root/.playit

# Verify installations
RUN op --version && python3 --version

# Set the entrypoint
ENTRYPOINT ["/app/entrypoint.sh"]
