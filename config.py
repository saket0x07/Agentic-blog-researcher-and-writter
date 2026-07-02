import os
from pathlib import Path
from dotenv import load_dotenv

# Try loading from the current directory, or parent directory where the main .env sits
current_dir = Path(__file__).resolve().parent
parent_dir = current_dir.parent

# Load .env files if they exist
load_dotenv(dotenv_path=current_dir / ".env")
load_dotenv(dotenv_path=parent_dir / ".env")

# API Keys Configuration
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")
HF_TOKEN = os.getenv("HF_TOKEN")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")

# Check which LLM API provider to use
USE_OPENROUTER = True if OPENROUTER_API_KEY else False

# Outputs config
OUTPUT_DIR = current_dir / "output"
IMAGE_DIR = OUTPUT_DIR / "images"

# Ensure directories exist
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
IMAGE_DIR.mkdir(parents=True, exist_ok=True)
