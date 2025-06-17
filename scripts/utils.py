#!/usr/bin/env python3
"""Utility functions for AI Proxy News."""

import json
import os
import socket
import sys
from typing import List


def check_port_available(port: int) -> bool:
    """Check if a port is available for binding."""
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind(("0.0.0.0", port))
        return True
    except OSError:
        return False


def validate_port_or_exit(port: int, service_name: str = "service") -> None:
    """Validate port availability or exit with error message."""
    if not check_port_available(port):
        print(f"Port {port} is already in use for {service_name}; specify another.", file=sys.stderr)
        sys.exit(1)


def generate_video_list(data_dir: str, output_path: str) -> None:
    """Generate JSON listing of available video files."""
    video_extensions = ('.mp4', '.mov', '.webm')
    
    try:
        videos = [
            f for f in os.listdir(data_dir)
            if f.lower().endswith(video_extensions)
        ]
        
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(videos, f)
            
    except (OSError, IOError) as e:
        print(f"Error generating video list: {e}", file=sys.stderr)
        sys.exit(1)


def create_symlink_if_missing(source: str, target: str) -> None:
    """Create symbolic link if it doesn't exist."""
    if not os.path.exists(target):
        try:
            os.symlink(source, target)
        except OSError as e:
            print(f"Error creating symlink {target} -> {source}: {e}", file=sys.stderr)


if __name__ == "__main__":
    if len(sys.argv) == 3 and sys.argv[1] == "check_port":
        port = int(sys.argv[2])
        sys.exit(0 if check_port_available(port) else 1)
    elif len(sys.argv) == 4 and sys.argv[1] == "generate_videos":
        generate_video_list(sys.argv[2], sys.argv[3])
    else:
        print("Usage:")
        print("  python3 utils.py check_port <port>")
        print("  python3 utils.py generate_videos <data_dir> <output_json>")
        sys.exit(1)