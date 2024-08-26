import datetime
from pathlib import Path


def setup_run_directory() -> Path:
    timestamp = datetime.datetime.now(datetime.UTC).strftime("%Y%m%d_%H%M%S")
    results_dir = Path.cwd() / f".ninja-taisen-{timestamp}"
    results_dir.mkdir()
    return results_dir
