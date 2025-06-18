# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

AI Proxy News is a transparent AI-assisted news workflow prototype that processes interview audio through Google Speech-to-Text and Gemini API to generate summarized articles with follow-up questions. The system is designed for transparency, storing all intermediate outputs and prompts publicly.

## Core Architecture

The system follows a linear pipeline:
1. Audio recording (manual) → `data/record.mp3`
2. Google Cloud Storage upload → Speech-to-Text API → `data/transcript.txt`
3. Gemini API processing with credo → summary + follow-up questions
4. Article generation → `docs/site/article.md`
5. Static site publication (manual)

## Development Commands

### Docker Compose Workflow (Primary)
```bash
# Start all services (web: port 12000, asr: port 12001)
docker-compose up --build

# Start in background
docker-compose up -d --build

# Stop services
docker-compose down

# Run main demo workflow
docker-compose run --rm demo bash scripts/run_demo.sh data/record.mp3

# View logs
docker-compose logs -f
```

### Local Development (Alternative)
```bash
# Install dependencies
pip install -r requirements.txt

# List available Gemini models
python3 scripts/list_models.py

# Run main workflow locally
bash scripts/run_demo.sh data/record.mp3

# Serve demo site locally (default port 12000)
bash scripts/serve_docs.sh [port]

# Run realtime transcription server (port 12001 by default)
python3 scripts/realtime_server.py

# Run realtime demo with both web server and ASR server
bash scripts/run_realtime_demo.sh [docs_port] [asr_port]
```

### Docker Workflow (Legacy - Use docker-compose instead)
```bash
# Build Docker image (uses secrets/.env for PROXY if set)
bash scripts/build_image.sh

# Run main demo workflow
docker run --rm -it \
  -v $(pwd):/app \
  --env-file secrets/.env \
  ai-proxy-news bash scripts/run_demo.sh data/record.mp3

# Run realtime demo with web server
docker run --rm -it \
  -p 12000:7000 -p 12001:7001 \
  -v $(pwd):/app \
  --env-file secrets/.env \
  ai-proxy-news bash scripts/run_realtime_demo.sh
```

## Configuration

All API keys and credentials are stored in `secrets/.env` (copy from `.env.example`):
- `GOOGLE_APPLICATION_CREDENTIALS`: Path to Google Cloud service account JSON
- `GEMINI_API_KEY`: Google Gemini API key
- `GCS_BUCKET`: Google Cloud Storage bucket for audio uploads
- `PROXY`: Optional proxy URL for Docker builds
- `ASR_PORT`: WebSocket port for realtime transcription (default 12001)
- `DOCS_PORT`: HTTP port for demo site (default 12000)

## Key Components

- **scripts/asr.py**: Handles audio upload to GCS and Speech-to-Text API calls
- **scripts/gpt_chain.py**: Processes transcripts through Gemini API using credo.json
- **scripts/realtime_server.py**: WebSocket server for live transcription demo
- **credo.json**: Editorial policy embedded in AI prompts
- **docs/site/**: Static site output directory with demo HTML/JS
- **output/**: Intermediate processing files for transparency

## File Structure

- Audio files go in `data/` (supports .mp3, .wav, .mp4)
- Generated transcripts saved to `data/transcript.txt`
- Processing outputs in `output/` (summary.md, follow_up.md, raw_gpt_output.md)
- Final article copied to `docs/site/article.md`
- Demo site assets in `docs/site/` with realtime transcription UI

## Important Notes

- The system requires Google Cloud credentials and Gemini API access
- Audio files are uploaded to GCS for Speech-to-Text processing
- All intermediate outputs are preserved for transparency
- The credo.json file defines the AI's editorial guidelines
- Default ports are 12000 (HTTP) and 12001 (WebSocket) to avoid conflicts

## Execution Methods

**Recommended:** Use `docker-compose up --build` for integrated development with automatic service orchestration.

**Alternative:** Use `bash scripts/run_realtime_demo.sh` for lightweight local development without Docker overhead.

**Legacy:** Single Docker container approach is maintained for compatibility but not recommended for new development.