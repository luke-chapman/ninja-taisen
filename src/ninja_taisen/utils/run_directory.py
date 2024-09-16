import datetime
from pathlib import Path


def choose_run_directory() -> Path:
    timestamp = datetime.datetime.now(datetime.UTC).strftime("%Y%m%d_%H%M%S")
    return Path.cwd() / f"ninja-taisen-{timestamp}"


def setup_run_directory() -> Path:
    results_dir = choose_run_directory()
    results_dir.mkdir()
    return results_dir
