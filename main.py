"""
main.py
-------
Entry point.  Run with:

    python main.py

Make sure .env is present and filled in first.
"""

from core import Agent
from utils import get_logger

log = get_logger("main")


if __name__ == "__main__":
    try:
        agent = Agent()
        agent.run()
    except KeyboardInterrupt:
        log.info("Stopped by user.")
    except Exception as exc:
        log.exception("Fatal error: %s", exc)
        raise
