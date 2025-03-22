from __future__ import annotations

import json
import shutil
import tempfile
from pathlib import Path
from typing import TYPE_CHECKING

from beekeepy._executable.abc.executable import AutoCloser, Executable
from beekeepy._executable.beekeeper_arguments import BeekeeperArguments, ExportKeysWalletParams
from beekeepy._executable.beekeeper_config import BeekeeperConfig
from beekeepy._executable.beekeeper_executable_discovery import get_beekeeper_binary_path
from beekeepy._utilities.key_pair import KeyPair

if TYPE_CHECKING:
    from loguru import Logger


class BeekeeperExecutable(Executable[BeekeeperConfig, BeekeeperArguments]):
    def __init__(self, executable_path: Path | None, working_directory: Path, logger: Logger) -> None:
        super().__init__(executable_path or get_beekeeper_binary_path(), working_directory, logger)

    def _construct_config(self) -> BeekeeperConfig:
        config = BeekeeperConfig(wallet_dir=self.working_directory)
        config.plugin.append("app_status_api")
        return config

    def _construct_arguments(self) -> BeekeeperArguments:
        return BeekeeperArguments(data_dir=self.working_directory)

    def export_keys_wallet(
        self, wallet_name: str, wallet_password: str, extract_to: Path | None = None
    ) -> list[KeyPair]:
        with tempfile.TemporaryDirectory() as tempdir:
            tempdir_path = Path(tempdir)
            wallet_file_name = f"{wallet_name}.wallet"
            shutil.copyfile(self.working_directory / wallet_file_name, tempdir_path / wallet_file_name)
            bk = BeekeeperExecutable(
                executable_path=self.executable_path,
                working_directory=self.working_directory,
                logger=self._logger,
            )
            with bk.restore_arguments(
                BeekeeperArguments(
                    data_dir=tempdir_path,
                    export_keys_wallet=ExportKeysWalletParams(wallet_name=wallet_name, wallet_password=wallet_password),
                )
            ):
                bk.run(
                    blocking=True,
                )

        keys_path = bk.working_directory / f"{wallet_name}.keys"
        if extract_to is not None:
            shutil.move(keys_path, extract_to)
            keys_path = extract_to

        with keys_path.open("r") as file:
            return [KeyPair(**obj) for obj in json.load(file)]

    def run(
        self,
        *,
        blocking: bool,
        environ: dict[str, str] | None = None,
        propagate_sigint: bool = True,
    ) -> AutoCloser:
        return self._run(blocking=blocking, environ=environ, propagate_sigint=propagate_sigint)
