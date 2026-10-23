import os
import sys
from pathlib import Path
from dotenv import load_dotenv
import uvicorn

BASE_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(BASE_DIR))

# Load .env file
env_path = BASE_DIR / ".env"
if env_path.exists():
    load_dotenv(dotenv_path=env_path)
else:
    load_dotenv()


def main():
    raw_port = os.getenv("SERVER_PORT", "8000")
    try:
        port = int(raw_port)
    except (TypeError, ValueError):
        port = 8000

    uvicorn.run("main:app", host="0.0.0.0", port=port)


if __name__ == "__main__":
    main()
