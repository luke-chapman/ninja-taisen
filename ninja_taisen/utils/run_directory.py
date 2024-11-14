import datetime
from pathlib import Path


def timestamp() -> str:
    return datetime.datetime.now(datetime.UTC).strftime("%Y%m%d_%H%M%S")


def choose_run_directory() -> Path:
    return Path.home() / ".ninja-taisen" / f"ninja-taisen-{timestamp()}"


def setup_run_directory() -> Path:
    results_dir = choose_run_directory()
    results_dir.mkdir()
    return results_dir
