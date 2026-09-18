"""
logger_config.py
-----------------
Central logging setup. Every module gets its logger via
``get_logger(__name__)`` so log lines are traceable to their source
module. Logs rotate at 1 MB to keep disk usage bounded (addresses the
Resource Efficiency non-functional requirement) and are written both to
a file (for audit/reporting) and the console (for live feedback).
"""

import logging
from logging.handlers import RotatingFileHandler

from src.config import LOG_FILE

_LOG_FORMAT = "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s"
_configured = False


def _configure_root():
    global _configured
    if _configured:
        return

    root = logging.getLogger("anpr")
    root.setLevel(logging.DEBUG)

    file_handler = RotatingFileHandler(
        LOG_FILE, maxBytes=1_000_000, backupCount=3, encoding="utf-8"
    )
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(logging.Formatter(_LOG_FORMAT))

    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(logging.Formatter("%(levelname)s: %(message)s"))

    root.addHandler(file_handler)
    root.addHandler(console_handler)
    _configured = True


def get_logger(name: str) -> logging.Logger:
    """Return a namespaced logger under the shared 'anpr' root logger."""
    _configure_root()
    return logging.getLogger(f"anpr.{name}")
