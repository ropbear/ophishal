# ophishal/common/logging.py
import logging
import os
from datetime import datetime


DEFAULT_LOG_LEVEL = logging.WARNING
LOG_COLORS = {
    logging.DEBUG: "\033[1;37m",
    logging.INFO: "\033[1;32m",
    logging.WARNING: "\033[1;33m",
    logging.ERROR: "\033[1;31m",
    logging.CRITICAL: "\033[1;31m"
}
COLOR_END = "\033[0m"
COLOR_BASE = "\033[97m"


class Formatter(logging.Formatter):
    def format(self, record):
        timestamp = datetime.now().strftime("%Y-%m-%d-%H:%M:%S.%f")[:-3]
        log_message = super().format(record)
        level_color = LOG_COLORS.get(record.levelno, COLOR_BASE)
        levelname_centered = level_color + record.levelname.center(10) + COLOR_END
        return f"[{levelname_centered}][{timestamp}][{record.filename}:{record.lineno}] {log_message}"

def create_logger(title:str) -> Formatter:
    logger = logging.getLogger(title)
    logger.setLevel(DEFAULT_LOG_LEVEL)
    handler = logging.StreamHandler()
    handler.setFormatter(Formatter('%(message)s'))
    logger.addHandler(handler)
    return logger
