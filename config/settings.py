"""
config/settings.py
------------------
All configuration lives here. Every other module imports from this file —
never reads os.environ directly.
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Load .env file from project root
_ROOT = Path(__file__).resolve().parent.parent
_ENV_FILE = _ROOT / ".env"

if not _ENV_FILE.exists():
    print(f"""
[CONFIG ERROR] .env file not found!

Expected location: {_ENV_FILE}

Steps to fix:
  1. Copy .env.example to .env  (same folder as main.py)
  2. Fill in your values
  3. Run again

On Windows:
  copy .env.example .env
""")
    sys.exit(1)

load_dotenv(_ENV_FILE)


def _require(key: str) -> str:
    """Get a required env var or print a helpful message and exit."""
    value = os.getenv(key)
    if not value:
        print(f"""
[CONFIG ERROR] Missing required variable: {key}

Open your .env file and make sure this line exists and is filled in:
  {key}=your_value_here

Location: {_ENV_FILE}
""")
        sys.exit(1)
    return value


# ── Telegram ──────────────────────────────────────────────────────────────────

TELEGRAM_BOT_TOKEN: str = _require("TELEGRAM_BOT_TOKEN")

# Only messages from this Telegram user ID are processed.
# Get yours: message @userinfobot on Telegram.
TELEGRAM_ALLOWED_USER_ID: int = int(_require("TELEGRAM_ALLOWED_USER_ID"))


# ── File system sandbox ────────────────────────────────────────────────────────

# The agent can ONLY read/write/delete files inside this directory.
# It will be created automatically if it doesn't exist.
AGENT_WORKSPACE_DIR: Path = Path(
    os.getenv("AGENT_WORKSPACE_DIR", str(_ROOT / "workspace"))
).resolve()

AGENT_WORKSPACE_DIR.mkdir(parents=True, exist_ok=True)
