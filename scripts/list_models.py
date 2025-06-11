#!/usr/bin/env python3
"""List available Gemini models."""

import os
from dotenv import load_dotenv
import google.generativeai as genai

load_dotenv(os.path.join("secrets", ".env"))

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

print("[MODELS] Listing available models...")
for model in genai.list_models():
    if "generateContent" in getattr(model, "supported_generation_methods", []):
        print(f"- {model.name}")
