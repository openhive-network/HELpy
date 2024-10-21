from __future__ import annotations

from beekeepy._executable.beekeeper_common import (
    BeekeeperCommon,
)
from helpy._executable.arguments import Arguments

from pathlib import Path
from pydantic import Field

# All config items are automatically generated
class BeekeeperArguments(BeekeeperCommon, Arguments):
    # Configuration file name relative to data-dir
    config: Path = Field(default_factory=lambda: Path("config.ini"))

    # Directory containing configuration file config.ini. Default location: $HOME/.beekeeper or CWD/. beekeeper
    data_dir: Path | None = None

    # Dump configuration and exit
    dump_config: bool = False

    # Dump information about all supported command line and config options in JSON format and exit
    dump_options: bool = False

    # Export explicitly private keys to a local file `wallet_name.keys`. Both [name, password] are required for every wallet. By default is empty.Two wallets example: --export-keys-wallet "["blue-wallet", "PW5JViFn5gd4rt6ohk7DQMgHzQN6Z9FuMRfKoE5Ysk25mkjy5AY1b"]" --export-keys-wallet "["green-wallet", "PW5KYF9Rt4ETnuP4uheHSCm9kLbCuunf6RqeKgQ8QRoxZmGeZUhhk"]"
    export_keys_wallet: list[str] = []

    # Generate bash auto-complete script (try: eval "$(hived --generate-completions)")
    generate_completions: bool = False

    # Print this help message and exit.
    help: bool = False

    # Print names of all available plugins and exit
    list_plugins: bool = False

    # Print version information.
    version: bool = False
