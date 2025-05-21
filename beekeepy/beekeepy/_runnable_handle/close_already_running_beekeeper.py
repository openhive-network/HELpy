from __future__ import annotations

import contextlib
import os
import signal
from pathlib import Path
from typing import Callable

import psutil
from loguru import logger

from beekeepy._executable.beekeeper_executable_discovery import (
    get_beekeeper_binary_path,
)
from beekeepy.exceptions import (
    FailedToDetectRunningBeekeeperError,
    UndistinguishableBeekeeperInstancesError,
)

__all__ = ["close_already_running_beekeeper"]


ProcessFilter = Callable[[psutil.Process], bool]


def _wait_for_pid_to_die(pid: int, *, timeout_secs: float = 5.0) -> None:
    """Monitors process with given pid, until it is no longer reachable (killed)."""
    with contextlib.suppress(psutil.NoSuchProcess):
        psutil.wait_procs([psutil.Process(pid)], timeout=timeout_secs)


def _kill_by_pid(*, pid: int) -> None:
    sig = signal.SIGINT  # signal type which will be used to kill beekeeper
    os.kill(pid, sig)  # try to kill it

    try:
        _wait_for_pid_to_die(pid, timeout_secs=10)  # check is process actually dead
        logger.debug(f"Process {pid} was closed with SIGINT")
    except TimeoutError:
        sig = signal.SIGKILL  # in case of no reaction to ^C, kill process hard way
        os.kill(pid, sig)
        _wait_for_pid_to_die(pid)  # confirm is hard way take effect
        logger.debug(f"Process {pid} was force-closed with SIGKILL")


def _prepare_path_to_compare(path: Path | str) -> str:
    if not isinstance(path, Path):
        path = Path(path)
    return path.resolve().absolute().as_posix()


def _filter_processes(procs: list[psutil.Process], callback: Callable[[psutil.Process], bool]) -> list[psutil.Process]:
    result = []
    for p in procs:
        with contextlib.suppress(psutil.Error):
            if callback(p):
                result.append(p)
    return result


def _filter_proc_preliminary_factory(binary_path: Path | None) -> ProcessFilter:
    username = psutil.Process().username()
    current_beekeeper_path = _prepare_path_to_compare(binary_path or get_beekeeper_binary_path())

    def impl(p: psutil.Process) -> bool:
        if p.username() != username:
            return False
        return _prepare_path_to_compare(p.exe()) == current_beekeeper_path

    return impl


def _filter_proc_by_cwd_factory(cwd: Path) -> ProcessFilter:
    cwd_for_lookup = _prepare_path_to_compare(cwd)

    def impl(p: psutil.Process) -> bool:
        return _prepare_path_to_compare(p.cwd()) == cwd_for_lookup

    return impl


def _filter_proc_by_reserved_port_factory(port: int) -> ProcessFilter:
    found_pid: int | None = None
    for conn in psutil.net_connections("inet4"):
        addr = conn.laddr
        assert len(addr) == 2, f"Expected 2 elements in addr, got {addr}"  # noqa: PLR2004
        if conn.pid is None or not bool(addr):
            continue
        if int(addr[1]) == port:
            found_pid = conn.pid
            break

    def impl(p: psutil.Process) -> bool:
        return found_pid is not None and p.pid == found_pid

    return impl


def _handle_beekeeper_killing(process: psutil.Process) -> None:
    pid = process.pid
    logger.info(f"Killing beekeeper with pid={pid} started in {process.cwd()}...")
    _kill_by_pid(pid=pid)
    logger.info(f"Killed beekeeper with pid={pid}")


def close_already_running_beekeeper(
    *,
    pid: int | None = None,
    binary_path: Path | None = None,
    cwd: Path | None = None,
    port: int | None = None,
    on_multiple_match_kill_all: bool = False,
) -> None:
    """
    AIO function to find and kill detached beekeeper instance.

    Args:
        pid: if given, instantly kills process with given pid
        binary_path: if given, filters out all beekeepers that are not started using this binary
                    (by default it takes binary from package)
        cwd: if given, filters out all beekeepers that have working directory set in other directories
        port: if given, selects beekeeper with such reserved port
        on_multiple_match_kill_all: if set to True, kills all beekeepers that matches given criteria

    Returns:
        None
    """
    if pid is not None:
        _handle_beekeeper_killing(psutil.Process(pid=pid))
        return

    processes = _filter_processes(list(psutil.process_iter()), _filter_proc_preliminary_factory(binary_path))

    if cwd is not None:
        processes = _filter_processes(processes, _filter_proc_by_cwd_factory(cwd))

    if port is not None:
        processes = _filter_processes(processes, _filter_proc_by_reserved_port_factory(port))

    if len(processes) == 0:
        raise FailedToDetectRunningBeekeeperError

    if len(processes) > 1 and not on_multiple_match_kill_all:
        raise UndistinguishableBeekeeperInstancesError

    for proc in processes:
        _handle_beekeeper_killing(proc)
