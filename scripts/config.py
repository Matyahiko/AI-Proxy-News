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
    return int(get_optional_env("ASR_PORT", "12001"))


def get_docs_port():
    """Get HTTP docs server port with default."""
    return int(get_optional_env("DOCS_PORT", "12000"))


def validate_port_usage():
    """Validate that required ports are available."""
    import socket
    
    def check_port_available(port: int) -> bool:
        """Check if a port is available for binding."""
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.bind(("0.0.0.0", port))
            return True
        except OSError:
            return False
    
    docs_port = get_docs_port()
    asr_port = get_asr_port()
    
    unavailable_ports = []
    if not check_port_available(docs_port):
        unavailable_ports.append(f"DOCS_PORT {docs_port}")
    if not check_port_available(asr_port):
        unavailable_ports.append(f"ASR_PORT {asr_port}")
    
    if unavailable_ports:
        print(f"Error: Ports already in use: {', '.join(unavailable_ports)}", file=sys.stderr)
        print("Specify different ports via environment variables.", file=sys.stderr)
        sys.exit(1)