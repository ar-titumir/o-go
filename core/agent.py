"""
core/agent.py
-------------
The central Agent class.

Today it is a thin coordinator — its only job is to start the
Telegram gateway.  Future days will add:
  - AI brain (Day N)
  - Memory / context (Day N+1)
  - Skill plugins (Day N+2)
  - Scheduler / cron (Day N+3)
  - …

Nothing else should ever import from gateway directly;
they go through Agent instead.
"""

from utils import get_logger
from gateway import run_telegram

log = get_logger(__name__)


class Agent:
    def __init__(self) -> None:
        log.info("Agent initialised.")

    def run(self) -> None:
        """Start the agent. Blocks until interrupted."""
        log.info("Agent starting…")
        run_telegram()
