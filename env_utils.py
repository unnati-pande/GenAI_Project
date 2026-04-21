from __future__ import annotations

from pathlib import Path
import os
from dotenv import load_dotenv


def load_environment() -> None:
    """
    Load environment variables from .env and .env.example files.

    Priority:
    1. Existing OS environment variables (never overridden)
    2. .env file
    3. .env.example (fallback only)
    """

    project_root = Path(__file__).resolve().parent

    env_path = project_root / ".env"
    example_path = project_root / ".env.example"

    # Load .env
    if env_path.is_file():
        load_dotenv(dotenv_path=env_path, override=False)
        print(f"[INFO] Loaded .env from: {env_path}")
    else:
        print(f"[WARNING] Missing .env file at: {env_path}")

    # Load fallback .env.example
    if example_path.is_file():
        load_dotenv(dotenv_path=example_path, override=False)
        print(f"[INFO] Loaded .env.example from: {example_path}")
    else:
        print(f"[WARNING] Missing .env.example file at: {example_path}")

    # Validate critical variables
    required_vars = ["OPENAI_API_KEY"]

    missing_vars = [var for var in required_vars if not os.getenv(var)]

    if missing_vars:
        print(f"[ERROR] Missing required environment variables: {', '.join(missing_vars)}")
    else:
        print("[INFO] Environment variables loaded successfully")