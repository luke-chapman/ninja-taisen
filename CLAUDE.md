# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Common Commands

All dev tasks go through `dev.py`:

```bash
uv run python dev.py test      # cargo test + maturin develop + pytest
uv run python dev.py lint      # ruff check + mypy
uv run python dev.py format    # black + ruff --fix
uv run python dev.py check     # format + lint + test
uv run python dev.py regen     # regenerate regression test fixtures
```

Run a single pytest test:
```bash
uv run maturin develop && uv run pytest tests/test_api.py::test_name
```

Run batch simulations for strategy benchmarking:
```bash
uv run python analysis/batch_simulate.py
```

## Architecture

This is a hybrid **Python + Rust** project using [maturin](https://www.maturin.rs/) to build a Python extension from Rust code. The Rust implementation is several hundred times faster than the pure-Python equivalent.

### Rust (`src/`)

The Rust crate compiles to a Python extension module (`ninja_taisen_rust`) and provides one public function exposed to Python: `simulate_instructions_from_csv_file()`. Internally this fans out to a thread pool where each thread runs `simulate_one()` — the main game loop: roll dice → gather moves → choose move (per strategy) → execute move → check victory.

Key modules:
- `card.rs` — cards are single `u8` bytes: `[non-null(1) | team(1) | category(2) | strength(4)]`
- `board.rs` — board state as two 110-byte arrays (monkey/wolf piles)
- `battle.rs` — rock-paper-scissors battle resolution including joker mechanics
- `strategy.rs` — strategy dispatch (random, random_spot_win, metric_count, metric_position, metric_strength)
- `dto.rs` — serialisable structs for Rust↔Python data exchange

Type stubs for the Rust module live in `typing/ninja_taisen_rust/__init__.py`.

### Python (`ninja_taisen/`)

The Python layer mirrors the Rust game logic and provides the public API, Flask server, and strategy framework.

- **`api.py`** — public entry points: `simulate()`, `choose_move()`, `execute_move()`. Pass `rust=True` to delegate to the Rust backend.
- **`dtos.py`** — Pydantic models shared by Python and Rust paths (`BoardDto`, `MoveDto`, `ResultDto`, etc.). Uses camelCase JSON serialisation.
- **`flask_entrypoint.py`** — REST API with `/choose` and `/execute` POST endpoints.
- **`algos/`** — pure-Python game engine (game_runner, move_gatherer, card_mover, card_battle, board_builder, board_inspector).
- **`strategy/`** — pluggable strategy implementations behind the `IStrategy` interface.
- **`objects/types.py`** — core Python types: `Card`, `Board` (defaultdict piles), `Move`, `DiceRoll`, `BattleResult`.

### Test structure (`tests/`)

- `test_api.py` / `test_api_rust.py` — API-level tests for Python and Rust paths
- `test_flask_entrypoint.py` — Flask endpoint tests
- `regression/` — JSON fixtures for turn-by-turn move validation and batch simulation results; regenerated with `dev.py regen`

### Data flow (batch simulation)

```
analysis/batch_simulate.py  →  api.simulate(rust=True)
  →  Rust: simulate_instructions_from_csv_file()  [thread pool]
    →  per thread: simulate_one()  →  gather_all_moves → choose_move → execute_move
  →  output: Parquet files in timestamped directory under analysis/
```
