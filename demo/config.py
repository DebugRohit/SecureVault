"""Configuration for the SecureVault recruiter demonstration."""

from pathlib import Path


DEMO_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = DEMO_DIR.parent

TEMPLATES_DIR = DEMO_DIR / "templates"
STATIC_DIR = DEMO_DIR / "static"
BACKGROUND_IMAGE = STATIC_DIR / "images" / "spiderman.jpg"

HOST = "127.0.0.1"
PORT = 80
DEBUG = False