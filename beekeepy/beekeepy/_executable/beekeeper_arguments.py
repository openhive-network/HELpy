from __future__ import annotations

from typing import TYPE_CHECKING, Any

from msgspec import field

from beekeepy._executable.abc.arguments import Arguments
from beekeepy._executable.beekeeper_common import (
    BeekeeperCommon,
)
from beekeepy._executable.beekeeper_custom_parameters_types import ExportKeysWalletParams
from beekeepy._executable.beekeeper_defaults import BeekeeperDefaults

if TYPE_CHECKING:
    from pathlib import Path


# All config items are automatically generated
class BeekeeperArguments(BeekeeperCommon, Arguments):
    """Parameters used in command line."""

    def _convert_member_value_to_string(self, name: str, member_value: int | str | Path | Any) -> list[str]:
        if isinstance(member_value, ExportKeysWalletParams):
            return [name, f'["{member_value[0]}","{member_value[1]}"]']
        return super()._convert_member_value_to_string(name, member_value)

    config: Path = BeekeeperDefaults.DEFAULT_CONFIG
    """
    Configuration file name relative to data-dir
    """

    data_dir: Path | None = BeekeeperDefaults.DEFAULT_DATA_DIR
    """
    Directory containing configuration file config.ini. Default location: $HOME/.beekeeper or CWD/. beekeeper
    """

    dump_config: bool = BeekeeperDefaults.DEFAULT_DUMP_CONFIG
    """
    Dump configuration and exit
    """

    dump_options: bool = BeekeeperDefaults.DEFAULT_DUMP_OPTIONS
    """
    Dump information about all supported command line and config options in JSON format and exit
    """

    export_keys_wallet: list[ExportKeysWalletParams] = BeekeeperDefaults.DEFAULT_EXPORT_KEYS_WALLET
    """
    Export explicitly private keys to a local file `wallet_name.keys`. Both [name, password] are required for every
        wallet. By default is empty.Two wallets example: --export-keys-wallet "["blue-wallet",
        "PW5JViFn5gd4rt6ohk7DQMgHzQN6Z9FuMRfKoE5Ysk25mkjy5AY1b"]" --export-keys-wallet "["green-wallet",
        "PW5KYF9Rt4ETnuP4uheHSCm9kLbCuunf6RqeKgQ8QRoxZmGeZUhhk"]"
    """

    generate_completions: bool = BeekeeperDefaults.DEFAULT_GENERATE_COMPLETIONS
    """
    Generate bash auto-complete script (try: eval "$(hived --generate-completions)")
    """

    help_: bool = field(name="help", default=BeekeeperDefaults.DEFAULT_HELP_)
    """
    Print this help message and exit.
    """

    list_plugins: bool = BeekeeperDefaults.DEFAULT_LIST_PLUGINS
    """
    Print names of all available plugins and exit
    """

    version_: bool = field(name="version", default=BeekeeperDefaults.DEFAULT_VERSION_)
    """
    Print version information.
    """
