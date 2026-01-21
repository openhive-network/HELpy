# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**Beekeepy** is a high-level Python interface for interacting with Beekeeper, a cryptographic key management service for the Hive blockchain. The package provides both synchronous and asynchronous APIs with full type hints.

- **Package name**: `hiveio-beekeepy`
- **Python requirement**: 3.12+ (currently targeting 3.14)
- **Linux only** - no Windows support planned

## Build and Development Commands

### Development Setup (Recommended)
```bash
cd tests/local-tools
poetry install
```
This installs Beekeepy in editable mode plus all dev tools (ruff, mypy, pytest).

### Run All Linters
```bash
pre-commit run --all
```

### Individual Tools
```bash
# Format with Ruff
poetry run ruff format --config tests/local-tools/pyproject.toml tests/ beekeepy/

# Lint with Ruff
poetry run ruff check --config tests/local-tools/pyproject.toml tests/ beekeepy/

# Type check with MyPy
poetry run mypy --config-file tests/local-tools/pyproject.toml tests/ beekeepy/
```

### Running Tests
```bash
# All beekeepy tests (parallel, from local-tools poetry env)
cd tests/local-tools
poetry run pytest --asyncio-mode auto -n auto tests/beekeepy_test

# Single test file
poetry run pytest tests/beekeepy_test/handle/basic/test_wallet.py

# Single test
poetry run pytest tests/beekeepy_test/handle/basic/test_wallet.py::test_name

# With Hive node endpoint (for integration tests)
poetry run pytest --hived-http-endpoint=https://api.hive.blog tests/beekeepy_test
```

## Dependency Management (Poetry)

The lockfile pins exact versions of all dependencies (direct and transitive). This prevents dependency mismatches between environments - if the lockfile is wrong or missing, builds may fail or behave differently. These rules keep it synchronized with pyproject.toml.

- **Dependency versions are specified in `pyproject.toml` and locked in `poetry.lock`**
- **Always use `poetry lock`** (without additional flags like `--regenerate`)
- **Always run `poetry lock` after changing `pyproject.toml`**
- **The `poetry.lock` file must be in the repository** - never add it to `.gitignore`
- **Never delete `poetry.lock`** - it ensures reproducible builds
- **Never edit `poetry.lock` manually** - always use poetry commands
- **Don't upgrade dependencies on your own** - only upgrade when explicitly requested

## Architecture

### Main API Classes (in `beekeepy/beekeepy/`)

**Async API** (`_interface/abc/asynchronous.py`):
- `AsyncBeekeeper` - Main entry point, use `.factory()` for local or `.remote_factory(url)` for remote
- `AsyncSession` - Created via `beekeeper.create_session()`
- `AsyncWallet` - Locked wallet, created via `session.create_wallet()`
- `AsyncUnlockedWallet` - Unlocked wallet with signing capabilities

**Sync API** (`_interface/abc/synchronous.py`):
- `Beekeeper`, `Session`, `Wallet`, `UnlockedWallet` - sync equivalents

All classes are context managers (use with `async with` / `with`).

### Internal Structure

- `_interface/` - Abstract base classes defining the public API
- `_apis/` - Low-level API communication (HTTP/JSON-RPC)
- `_communication/` - HTTP client implementations (aiohttp for async, requests for sync)
- `_executable/` - Beekeeper binary management (embedded in `beekeepy/beekeeper`)
- `_runnable_handle/` - Lifecycle management for local Beekeeper instances
- `_exceptions/` - 70+ exception types for detailed error handling
- `_utilities/` - Helpers (lazy imports, context managers, delay guards)
- `handle/` - High-level runnable/remote handle implementations

### Key Patterns

- **Factory methods**: Use `.factory()` for local instances, `.remote_factory(url)` for remote
- **Lazy imports**: Public API uses lazy loading to minimize startup time
- **Sync/async parity**: Both APIs mirror each other exactly
- **Context managers**: All resources clean up automatically with `with`/`async with`

## CI/CD

Pipeline stages: `static_code_analysis` → `build` → `tests` → `beekeepy`

Key jobs:
- `pre_commit_checks` - Pre-commit validation
- `formatting_with_ruff_check` / `lint_code_with_ruff` - Code style
- `type_check_with_mypy` - Type checking
- `fetch_beekeeper` - Downloads beekeeper binary from beekeeper repo
- `run_beekeepy_tests` - Runs pytest suite
- `build_beekeepy_wheel` / `deploy_*` - Package building and deployment

## Code Style

- Line length: 120
- All files require `from __future__ import annotations`
- MyPy strict mode enabled
- Ruff with `select = ["ALL"]` (most rules enabled, see `tests/local-tools/pyproject.toml` for ignores)
- `pytest.asyncio_mode = "auto"` - no need to decorate async tests
