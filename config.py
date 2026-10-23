import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
_env_path = Path(__file__).resolve().parent / ".env"
if _env_path.exists():
    load_dotenv(dotenv_path=_env_path)
else:
    load_dotenv()

_raw_keys = os.getenv("GROQ_API_KEYS", "")
GROQ_API_KEYS = [k.strip() for k in _raw_keys.split(",") if k.strip()]

if not GROQ_API_KEYS:
    raise ValueError(
        "GROQ_API_KEYS environment variable is missing or empty. "
        "Please provide one or more comma-separated Groq API keys in your .env file or environment."
    )
