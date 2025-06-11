FROM python:3.11-slim

# Optional proxy for network access during build
ARG PROXY
ENV http_proxy=${PROXY} \
    https_proxy=${PROXY}

# Install system dependencies
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
       ffmpeg curl \
    && rm -rf /var/lib/apt/lists/*

# Install c2patool (binary release)
RUN curl -L https://github.com/contentauth/c2patool/releases/latest/download/c2patool-linux-x64 \
        -o /usr/local/bin/c2patool \
    && chmod +x /usr/local/bin/c2patool

WORKDIR /app
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Clear proxy settings for runtime image
ENV http_proxy= \
    https_proxy=

COPY . .

CMD ["bash"]
