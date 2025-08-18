# ophishal/common/logging.py
import logging
import os
from datetime import datetime


LOG_LEVEL = logging.WARNING
LOG_COLOR = True
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
        level_name = record.levelname.upper().strip()[0:4] if record.levelno != logging.DEBUG else "DBUG"
        levelname_centered = level_color + level_name + COLOR_END if LOG_COLOR else level_name
        return f"[{levelname_centered}][{timestamp}][ophishal:{record.filename}:{record.lineno}]{log_message}"

def setLogLevel(level:int):
    global LOG_LEVEL
    LOG_LEVEL = level

def setLogColor(colored:bool):
    global LOG_COLOR
    LOG_COLOR = colored

def create_logger(title:str) -> Formatter:
    # note that getLogger will interpret periods as hierarchical structures
    # https://docs.python.org/3/library/logging.html#logger-objects
    logger = logging.getLogger(title)
    logger.setLevel(LOG_LEVEL)
    handler = logging.StreamHandler()
    handler.setFormatter(Formatter(f'[{title}] %(message)s'))
    logger.addHandler(handler)
    return logger
