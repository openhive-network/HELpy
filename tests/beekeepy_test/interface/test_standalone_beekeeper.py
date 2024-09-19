from __future__ import annotations

import json
import os
import sys
import time
from pathlib import Path
from subprocess import run


def run_python_script(path_to_script: Path, args: list[str], cwd: Path) -> None:
    run(check=True, args=[sys.executable, path_to_script.as_posix(), *args], cwd=cwd)
    time.sleep(1.0)  # time to start script, evaluate it and leave some time for reaction of beekeeper


def is_alive(pid: int) -> bool:
    """Check For the existence of a unix pid.

    Source: https://stackoverflow.com/a/568285
    """
    try:
        os.kill(pid, 0)
    except OSError:
        return False
    else:
        return True


def verify_beekeeper_status(path_or_pid: Path | int, alive: bool) -> int:
    pid: int | None = None
    if isinstance(path_or_pid, Path):
        assert path_or_pid.exists(), f"Beekeeper started too slow, missing file: {path_or_pid.as_posix()}"
        with path_or_pid.open("r") as rfile:
            pid = int(json.load(rfile).get("pid", -1))
    else:
        pid = path_or_pid

    assert pid is not None or pid == -1, "File was empty or invalid, no pid to check"
    assert is_alive(pid) == alive, f"pid {pid} was {'still there' if not alive else 'missing'} on check"
    return pid


def test_standalone_beekeeper(working_directory: Path) -> None:
    # ARRANGE
    path_to_resource_directory = Path(__file__).resolve().parent / "resources"
    path_to_script = path_to_resource_directory / "standalone_beekeeper_by_args.py"
    path_to_working_directory = working_directory / "wdir"
    path_to_pid_file = path_to_working_directory / "beekeeper.pid"

    # ACT & ASSERT
    run_python_script(
        path_to_script=path_to_script, args=[path_to_working_directory.as_posix(), "start"], cwd=working_directory
    )

    pid = verify_beekeeper_status(path_or_pid=path_to_pid_file, alive=True)

    run_python_script(
        path_to_script=path_to_script, args=[path_to_working_directory.as_posix(), "stop"], cwd=working_directory
    )

    verify_beekeeper_status(path_or_pid=pid, alive=False)
