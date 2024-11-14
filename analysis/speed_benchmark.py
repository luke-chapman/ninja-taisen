import datetime
import json
import os
import subprocess
import sys
from collections import defaultdict
from pathlib import Path
from typing import Any

import polars as pl
import psutil

from ninja_taisen.dtos import Strategy
from ninja_taisen.utils.run_directory import setup_run_directory

# TODO 2024-11-13 - work out why the import of ninja_taisen fails. Maturin docs are confusing!
try:
    import ninja_taisen  # noqa
except ImportError:
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))


STRATEGIES = [Strategy.random, Strategy.random_spot_win, Strategy.metric_count, Strategy.metric_strength]
COMMAND_PREFIX = [
    sys.executable,
    str(Path(__file__).resolve().parent / "batch_simulate.py"),
    "--strategies",
] + STRATEGIES


def launch_benchmark_process(
    multiplier: int,
    parallelism: int,
    chunk_size: int,
    rust: bool,
    overall_run_dir: Path,
) -> float:
    name = "rust" if rust else "python"
    run_dir = overall_run_dir / f"dry_run_{name}_{16 * multiplier}"
    run_dir.mkdir()
    command = COMMAND_PREFIX + [
        "--run-dir",
        str(run_dir),
        "--multiplier",
        str(multiplier),
        "--max-processes",
        str(parallelism),
        "--per-process",
        str(chunk_size),
    ]
    if rust:
        command.append("--rust")

    print(f"Launching {name} benchmark with {16 * multiplier} simulations")
    print(subprocess.list2cmdline(command))
    subprocess.check_output(command)
    print("Benchmark subprocess complete")
    time_taken_txt = run_dir / "time_taken.txt"
    return float(time_taken_txt.read_text())


def choose_chunk_sizes(overall_run_dir: Path) -> tuple[int, int]:
    multiplier = 10
    python_dry_run_time = launch_benchmark_process(
        multiplier=multiplier,
        parallelism=1,
        chunk_size=multiplier * 16,
        rust=False,
        overall_run_dir=overall_run_dir,
    )
    rust_dry_run_time = launch_benchmark_process(
        multiplier=multiplier,
        parallelism=1,
        chunk_size=multiplier * 16,
        rust=True,
        overall_run_dir=overall_run_dir,
    )

    python_s_per_run = python_dry_run_time / (16 * multiplier)
    rust_s_per_run = rust_dry_run_time / (16 * multiplier)

    python_chunk_size = int(1 / python_s_per_run) * 10
    rust_chunk_size = int(1 / rust_s_per_run) * 10
    print("Choosing chunk sizes to aim for about 10s per chunk")
    print(f"Python: {python_chunk_size}, Rust: {rust_chunk_size}")
    return python_chunk_size, rust_chunk_size


def run() -> None:
    logical_cpus = psutil.cpu_count(logical=True)
    assert logical_cpus is not None, "Could not determine logical_cpus"

    total_ram_gb = psutil.virtual_memory().total / (1024**3)
    cpu_freq_ghz = psutil.cpu_freq().max / 1000

    overall_run_dir = setup_run_directory()
    python_chunk_size, rust_chunk_size = choose_chunk_sizes(overall_run_dir)
    run_python, run_rust = True, True

    simulation_counts = [2000, 4000, 10000, 20000, 40000, 100000, 200000, 400000, 1000000]

    results: dict[str, list[Any]] = defaultdict(list)

    for simulation_count in simulation_counts:
        if not run_python and not run_rust:
            print("Stopping all simulations because we've taken up too much time")
            break

        results["simulation_count"].append(simulation_count)
        assert simulation_count % 16 == 0
        multiplier = int(simulation_count / 16)
        if run_python:
            python_s = launch_benchmark_process(
                multiplier=multiplier,
                parallelism=logical_cpus - 1,
                chunk_size=python_chunk_size,
                rust=False,
                overall_run_dir=overall_run_dir,
            )
            results["python_s"].append(round(python_s, 3))
            if python_s > 100.0:
                run_python = False
        else:
            results["python_s"].append(None)

        if run_rust:
            rust_s = launch_benchmark_process(
                multiplier=multiplier,
                parallelism=logical_cpus - 1,
                chunk_size=rust_chunk_size,
                rust=True,
                overall_run_dir=overall_run_dir,
            )
            results["rust_s"].append(round(rust_s, 3))
            if rust_s > 100.0:
                run_rust = False
        else:
            results["rust_s"].append(None)

        if run_rust and run_python:
            results["speed_differential"].append(int(results["python_s"][-1] / results["rust_s"][-1]))
        else:
            results["speed_differential"].append(None)

    pl.DataFrame(data=results).write_csv(overall_run_dir / "benchmark_results.csv")
    metadata = {
        "date": datetime.datetime.today().strftime("%Y-%m-%d"),
        "user": os.getlogin(),
        "logical_cpus": logical_cpus,
        "total_ram_gb": total_ram_gb,
        "cpu_freq_ghz": cpu_freq_ghz,
    }
    metadata_json = overall_run_dir / "benchmark_metadata.json"
    metadata_json.write_text(json.dumps(metadata, indent=2))
    print("Benchmark exercise complete")


if __name__ == "__main__":
    run()
