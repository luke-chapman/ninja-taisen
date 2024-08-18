import logging
import time
from pathlib import Path


class UTCFormatter(logging.Formatter):
    converter = time.gmtime


def setup_logging(verbosity: int, log_file: Path | None = None) -> None:
    # Set up the root logger
    logger = logging.getLogger()
    logger.setLevel(verbosity)

    # Create a console handler with the specified format, if it doesn't already exist
    if not any(isinstance(h, logging.StreamHandler) for h in logger.handlers):
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(
            UTCFormatter("%(asctime)s - %(levelname)s - %(module)s - %(message)s", "%Y-%m-%d %H:%M:%S")
        )
        logger.addHandler(console_handler)

    if log_file is not None:
        # Create a file handler with the specified format
        file_handler = logging.FileHandler(log_file)
        file_handler.setFormatter(
            UTCFormatter("%(asctime)s - %(levelname)s - %(module)s - %(message)s", "%Y-%m-%d %H:%M:%S")
        )
        logger.addHandler(file_handler)
