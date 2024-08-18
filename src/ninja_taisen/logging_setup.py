import logging
import time


class UTCFormatter(logging.Formatter):
    converter = time.gmtime


def setup_logging(verbosity: int) -> None:
    logging.basicConfig(
        level=verbosity, datefmt="%Y-%m-%d %H:%M:%S", format="%(asctime)s - %(levelname)s - %(module)s - %(message)s"
    )

    for handler in logging.getLogger().handlers:
        assert handler.formatter is not None
        handler.setFormatter(UTCFormatter(handler.formatter._fmt, handler.formatter.datefmt))
