FROM python:3.11-slim

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

COPY . .

CMD ["bash"]
