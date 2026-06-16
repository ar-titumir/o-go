"""
utils/logger.py
---------------
Central logging setup. Every module imports get_logger() from here.
"""

import logging
import sys
from pathlib import Path

LOG_DIR = Path(__file__).resolve().parent.parent / "logs"
LOG_DIR.mkdir(exist_ok=True)

_FMT = "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s"
_DATE_FMT = "%Y-%m-%d %H:%M:%S"


def get_logger(name: str) -> logging.Logger:
    """Return a named logger that writes to stdout AND a rotating log file."""
    logger = logging.getLogger(name)

    if logger.handlers:          # already configured — don't add duplicate handlers
        return logger

    logger.setLevel(logging.DEBUG)

    # --- stdout handler ---
    sh = logging.StreamHandler(sys.stdout)
    sh.setLevel(logging.INFO)
    sh.setFormatter(logging.Formatter(_FMT, _DATE_FMT))
    logger.addHandler(sh)

    # --- file handler ---
    fh = logging.FileHandler(LOG_DIR / "agent.log", encoding="utf-8")
    fh.setLevel(logging.DEBUG)
    fh.setFormatter(logging.Formatter(_FMT, _DATE_FMT))
    logger.addHandler(fh)

    return logger
