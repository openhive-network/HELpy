from __future__ import annotations

import os
import signal
import subprocess
import time
from abc import ABC, abstractmethod
from contextlib import contextmanager
from typing import TYPE_CHECKING, Any, Generic, TypeVar

import psutil

from beekeepy._executable.abc.arguments import Arguments
from beekeepy._executable.abc.config import Config
from beekeepy._executable.abc.streams import StreamsHolder
from beekeepy._utilities.context import ContextSync
from beekeepy.exceptions import ExecutableIsNotRunningError, TimeoutReachWhileCloseError

if TYPE_CHECKING:
    from collections.abc import Iterator
    from pathlib import Path

    from loguru import Logger


class Closeable(ABC):
    @abstractmethod
    def close(self, timeout_secs: float = 10.0) -> None: ...


class AutoCloser(ContextSync[None]):
    def __init__(self, obj_to_close: Closeable | None, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self.__obj_to_close = obj_to_close

    def _enter(self) -> None:
        return None

    def _finally(self) -> None:
        if self.__obj_to_close is not None:
            self.__obj_to_close.close()


ConfigT = TypeVar("ConfigT", bound=Config)
ArgumentT = TypeVar("ArgumentT", bound=Arguments)


class Executable(Closeable, Generic[ConfigT, ArgumentT]):
    def __init__(self, executable_path: Path, working_directory: Path, logger: Logger) -> None:
        if working_directory.exists():
            assert working_directory.is_dir(), "Given path is not pointing to directory"
        else:
            working_directory.mkdir()
        assert executable_path.is_file(), "Given executable path is not pointing to file"
        self.__executable_path = executable_path.absolute()
        self.__process: subprocess.Popen[str] | None = None
        self.__working_directory = working_directory.absolute()
        self._logger = logger
        self.__files = StreamsHolder()
        self.__files.set_paths_for_dir(self.__working_directory)
        self.__config: ConfigT = self._construct_config()
        self.__arguments: ArgumentT = self._construct_arguments()

    @property
    def pid(self) -> int:
        assert self.__process is not None, "Process is not running, nothing to return"
        return self.__process.pid

    @property
    def working_directory(self) -> Path:
        return self.__working_directory

    @property
    def config(self) -> ConfigT:
        return self.__config

    @property
    def arguments(self) -> ArgumentT:
        return self.__arguments

    @property
    def executable_path(self) -> Path:
        return self.__executable_path

    def _run(
        self,
        *,
        blocking: bool,
        environ: dict[str, str] | None = None,
        propagate_sigint: bool = True,
        save_config: bool = True,
    ) -> AutoCloser:
        return self.__run(
            blocking=blocking,
            arguments=self.arguments,
            environ=environ,
            propagate_sigint=propagate_sigint,
            save_config=save_config,
        )

    def __run(
        self,
        *,
        blocking: bool,
        arguments: ArgumentT,
        environ: dict[str, str] | None = None,
        propagate_sigint: bool = True,
        save_config: bool = True,
    ) -> AutoCloser:
        command, environment_variables = self.__prepare(arguments=arguments, environ=environ, save_config=save_config)
        self._logger.info(f"starting `{self.__executable_path.stem}` as: `{command}`")

        if blocking:
            with self.__files.stdout as stdout, self.__files.stderr as stderr:
                subprocess.run(
                    command,
                    cwd=self.__working_directory,
                    env=environment_variables,
                    check=True,
                    stdout=stdout,
                    stderr=stderr,
                )
                return AutoCloser(None)

        # Process created here have to exist longer than current scope
        self.__process = subprocess.Popen(
            command,
            cwd=self.__working_directory,
            env=environment_variables,
            stdout=self.__files.stdout.open_stream(),
            stderr=self.__files.stderr.open_stream(),
            preexec_fn=(  # noqa: PLW1509
                os.setpgrp if not propagate_sigint else None
            ),  # create new process group, so signals won't be passed to child process
        )  # type: ignore[assignment]

        return AutoCloser(self)

    def run_and_get_output(
        self, arguments: ArgumentT, environ: dict[str, str] | None = None, timeout: float | None = None
    ) -> str:
        command, environment_variables = self.__prepare(arguments=arguments, environ=environ)
        result = subprocess.check_output(command, stderr=subprocess.STDOUT, env=environment_variables, timeout=timeout)
        return result.decode().strip()

    def __prepare(
        self,
        arguments: ArgumentT,
        environ: dict[str, str] | None,
        save_config: bool = True,  # noqa: FBT001, FBT002
    ) -> tuple[list[str], dict[str, str]]:
        environ = environ or {}

        self.__working_directory.mkdir(exist_ok=True)
        command: list[str] = [self.__executable_path.as_posix(), *(arguments.process())]
        self._logger.debug(
            f"Starting {self.__executable_path.name} in {self.working_directory} with arguments: {' '.join(command)}"
        )

        environment_variables = dict(os.environ)
        environment_variables.update(environ)
        if save_config:
            self.config.save(self.working_directory)

        return command, environment_variables

    def __raise_exception_if_timeout_on_close(self) -> None:
        raise TimeoutReachWhileCloseError

    def detach(self) -> int:
        if self.__process is None:
            raise ExecutableIsNotRunningError
        pid = self.pid
        self.__process = None
        self.__files.close()
        return pid

    def close(self, timeout_secs: float = 10.0) -> None:
        if self.__process is None:
            return

        self.__process.send_signal(signal.SIGINT)
        try:
            return_code = self.__process.wait(timeout=timeout_secs)
            self._logger.debug(f"Closed with {return_code} return code")
        except subprocess.TimeoutExpired:
            self.__process.kill()
            self.__process.wait()
            self.__raise_exception_if_timeout_on_close()
        finally:
            self.__process = None
            self.__files.close()

    def is_running(self) -> bool:
        if not self.__process:
            return False

        return self.__process.poll() is None

    def log_has_phrase(self, text: str) -> bool:
        return text in self.__files

    @contextmanager
    def restore_arguments(self, new_arguments: ArgumentT | None) -> Iterator[None]:
        __backup = self.__arguments
        self.__arguments = new_arguments or self.__arguments
        try:
            yield
        except:  # noqa: TRY302 # https://docs.python.org/3/library/contextlib.html#contextlib.contextmanager
            raise
        finally:
            self.__arguments = __backup

    @abstractmethod
    def _construct_config(self) -> ConfigT: ...

    @abstractmethod
    def _construct_arguments(self) -> ArgumentT: ...

    def generate_default_config(self) -> ConfigT:
        if not self.working_directory.exists():
            self.working_directory.mkdir(parents=True)
        orig_path_to_config: Path | None = None
        path_to_config = self.working_directory / Config.DEFAULT_FILE_NAME
        if path_to_config.exists():
            orig_path_to_config = path_to_config.rename(
                path_to_config.with_suffix(".ini.orig")
            )  # temporary move it to not interfere with config generation
        arguments = self._construct_arguments()
        arguments.dump_config = True
        self.__run(blocking=True, arguments=arguments, save_config=False)
        temp_path_to_file = path_to_config.rename(path_to_config.with_suffix(".ini.tmp"))
        if orig_path_to_config is not None:
            orig_path_to_config.rename(path_to_config)
        return self.config.load(temp_path_to_file)

    def get_help_text(self) -> str:
        return self.run_and_get_output(arguments=self.__arguments.just_get_help())

    def version(self) -> str:
        return self.run_and_get_output(arguments=self.__arguments.just_get_version())

    def reserved_ports(self, *, timeout_seconds: int = 10) -> list[int]:
        assert self.is_running(), "Cannot obtain reserved ports for not started executable"
        start = time.perf_counter()
        while start + timeout_seconds >= time.perf_counter():
            connections = psutil.net_connections("inet4")
            reserved_ports = [connection.laddr[1] for connection in connections if connection.pid == self.pid]  # type: ignore[misc]
            if reserved_ports:
                return reserved_ports
        raise TimeoutError
