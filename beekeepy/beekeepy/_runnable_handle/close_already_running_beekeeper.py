from __future__ import annotations

import errno
import os
import signal
import time

from loguru import logger


def _is_running(pid: int) -> bool:
    """
    Check whether pid exists in the current process table.

    Source: https://stackoverflow.com/a/7654102

    Args:
    ----
    pid: The Process ID to check.

    Returns:
    -------
    True if process with the given pid is running else False.
    """
    try:
        os.kill(pid, 0)
    except OSError as err:
        if err.errno == errno.ESRCH:
            return False
    return True


def _wait_for_pid_to_die(pid: int, *, timeout_secs: float = 5.0) -> None:
    sleep_time = min(1.0, timeout_secs)
    already_waited = 0.0
    while not _is_running(pid):
        if timeout_secs - already_waited <= 0:
            raise TimeoutError(f"Process with pid {pid} didn't die in {timeout_secs} seconds.")

        time.sleep(sleep_time)
        already_waited += sleep_time


def close_already_running_beekeeper(*, pid: int) -> None:
    """If beekeeper has been started and explicitly not closed, this function allows to close it basing on workdir."""
    sig = signal.SIGINT  # signal type which will be used to kill beekeeper
    os.kill(pid, sig)  # try to kill it

    try:
        _wait_for_pid_to_die(pid, timeout_secs=10)  # check is process actually dead
        logger.debug("Process was closed with SIGINT")
    except TimeoutError:
        sig = signal.SIGKILL  # in case of no reaction to ^C, kill process hard way
        os.kill(pid, sig)
        _wait_for_pid_to_die(pid)  # confirm is hard way take effect
        logger.debug("Process was force-closed with SIGKILL")
