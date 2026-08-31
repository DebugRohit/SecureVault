"""Configuration for the SecureVault recruiter demonstration."""

from __future__ import annotations

import os
from pathlib import Path


DEMO_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = DEMO_DIR.parent

TEMPLATES_DIR = DEMO_DIR / "templates"
STATIC_DIR = DEMO_DIR / "static"
BACKGROUND_IMAGE = STATIC_DIR / "images" / "spiderman.jpg"

HOST = os.environ.get("HOST", "127.0.0.1")
PORT = int(os.environ.get("PORT", "5000"))
DEBUG = os.environ.get("FLASK_DEBUG", "false").lower() == "true"