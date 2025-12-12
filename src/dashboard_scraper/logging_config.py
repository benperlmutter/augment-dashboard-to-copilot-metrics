from __future__ import annotations

import logging
import os


def setup_logging(level: str = "INFO") -> None:
    lvl = getattr(logging, level.upper(), logging.INFO)
    fmt = "%(asctime)s %(levelname)s %(name)s %(message)s"
    datefmt = "%Y-%m-%dT%H:%M:%S%z"
    logging.basicConfig(level=lvl, format=fmt, datefmt=datefmt)

    # Reduce noise from third-party libs if needed
    logging.getLogger("urllib3.connectionpool").setLevel(logging.WARNING)
    logging.getLogger("requests").setLevel(logging.WARNING)

