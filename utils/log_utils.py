import io
import sys
import re
import logging


def setup_logger(name, log_level=logging.INFO):
    """로거를 리턴한다.
    """
    formatter = logging.Formatter("[{asctime}] [{levelname:<8}] {name}: {message}", "%Y-%m-%d %H:%M:%S", style="{")
    handler = logging.StreamHandler()
    handler.setFormatter(formatter)
    logger = logging.getLogger(name)
    logger.addHandler(handler)
    logger.setLevel(log_level)
    return logger
