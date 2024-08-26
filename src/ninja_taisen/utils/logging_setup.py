import logging
import time
from pathlib import Path


class UTCFormatter(logging.Formatter):
    converter = time.gmtime


def setup_logging(verbosity: int = logging.INFO, log_file: Path | None = None) -> None:
    # Set up the root logger
    logger = logging.getLogger()
    logger.setLevel(verbosity)

    # Create a console handler with the specified format, if it doesn't already exist
    if not any(isinstance(h, logging.StreamHandler) for h in logger.handlers):
        logger.addHandler(logging.StreamHandler())

    if log_file is not None and not any(isinstance(h, logging.FileHandler) for h in logger.handlers):
        logger.addHandler(logging.FileHandler(log_file))

    for handler in logger.handlers:
        handler.setLevel(verbosity)
        handler.setFormatter(
            UTCFormatter("%(asctime)s - %(levelname)s - %(module)s - %(message)s", "%Y-%m-%d %H:%M:%S")
        )
