#!/usr/bin/env python3
"""Centralized configuration management for AI Proxy News."""

import os
import sys
from dotenv import load_dotenv


def load_config():
    """Load environment variables from secrets/.env file."""
    load_dotenv(os.path.join("secrets", ".env"))


def get_required_env(key: str) -> str:
    """Get required environment variable or exit with error."""
    value = os.getenv(key)
    if not value:
        print(f"Error: {key} not set in environment", file=sys.stderr)
        sys.exit(1)
    return value


def get_optional_env(key: str, default: str = "") -> str:
    """Get optional environment variable with default value."""
    return os.getenv(key, default)


def validate_gcs_config():
    """Validate Google Cloud Storage configuration."""
    load_config()
    bucket_name = get_required_env("GCS_BUCKET")
    return bucket_name


def validate_gemini_config():
    """Validate Gemini API configuration."""
    load_config()
    api_key = get_required_env("GEMINI_API_KEY")
    return api_key


def get_asr_port():
    """Get ASR WebSocket port with default."""
    return int(get_optional_env("ASR_PORT", "7001"))