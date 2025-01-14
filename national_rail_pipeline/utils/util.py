import logging
import sys
import os


def configure_logging(logger, debug=False) -> None:
    if len(logger.handlers) > 0:
        return

    log_level = logging.INFO
    if debug:
        log_level = logging.DEBUG

    logger.setLevel(log_level)
    ch = logging.StreamHandler(sys.stdout)
    ch.setLevel(log_level)
    formatter = logging.Formatter("[%(name)s][%(levelname)s][%(asctime)s] %(message)s")
    ch.setFormatter(formatter)
    logger.addHandler(ch)


def create_directory_if_not_exists(directory: str) -> None:
    if not os.path.exists(directory):
        os.makedirs(directory)
