from __future__ import annotations

from pathlib import Path  # noqa: TCH003

from beekeepy._executable.arguments import Arguments
from beekeepy._executable.beekeeper_common import (
    BeekeeperCommon,
)
from beekeepy._executable.beekeeper_defaults import BeekeeperDefaults
from beekeepy._executable.custom_parameters_types import ExportKeysWalletParams  # noqa: TCH001


# All config items are automatically generated
class BeekeeperArguments(BeekeeperCommon, Arguments):
    """Parameters used in command line."""

    config: Path = BeekeeperDefaults.DEFAULT_CONFIG
    """Configuration file name relative to data-dir"""

    data_dir: Path | None = BeekeeperDefaults.DEFAULT_DATA_DIR
    """Directory containing configuration file config.ini. Default location: $HOME/.beekeeper or CWD/. beekeeper"""

    dump_config: bool = BeekeeperDefaults.DEFAULT_DUMP_CONFIG
    """Dump configuration and exit"""

    dump_options: bool = BeekeeperDefaults.DEFAULT_DUMP_OPTIONS
    """Dump information about all supported command line and config options in JSON format and exit"""

    export_keys_wallet: list[ExportKeysWalletParams] = BeekeeperDefaults.DEFAULT_EXPORT_KEYS_WALLET
    """Export explicitly private keys to a local file `wallet_name.keys`. Both [name, password] are required for every
 By default is empty.Two wallets example: --export-keys-wallet "["blue-wallet",
 --export-keys-wallet "["green-wallet", "PW5KYF9Rt4ETnuP4uheHSCm9kLbCuunf6RqeKgQ8QRoxZmGeZUhhk"]"
    """

    generate_completions: bool = BeekeeperDefaults.DEFAULT_GENERATE_COMPLETIONS
    """Generate bash auto-complete script (try: eval "$(hived --generate-completions)")"""

    help: bool = BeekeeperDefaults.DEFAULT_HELP
    """Print this help message and exit."""

    list_plugins: bool = BeekeeperDefaults.DEFAULT_LIST_PLUGINS
    """Print names of all available plugins and exit"""

    version: bool = BeekeeperDefaults.DEFAULT_VERSION
    """Print version information."""
