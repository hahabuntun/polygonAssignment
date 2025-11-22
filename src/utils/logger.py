import logging
import sys
from typing import Optional

from config import AppConfig

_cfg = AppConfig()


def setup_logger(name: str, level: Optional[str] = None) -> logging.Logger:
    logger = logging.getLogger(name)
    if logger.handlers:
        return logger
    lvl = (level or _cfg.log_level).upper()
    logger.setLevel(getattr(logging, lvl, logging.INFO))
    handler = logging.StreamHandler(sys.stdout)
    fmt = "%(asctime)s %(name)s %(levelname)s %(message)s"
    handler.setFormatter(logging.Formatter(fmt))
    logger.addHandler(handler)
    logger.propagate = False
    return logger
