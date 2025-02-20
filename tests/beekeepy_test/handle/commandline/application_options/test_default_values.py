from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from beekeepy._executable.beekeeper_config import (
    BeekeeperConfig,
    http_webserver_default,
)
from beekeepy._executable.defaults import BeekeeperDefaults

if TYPE_CHECKING:
    from beekeepy._executable.beekeeper_executable import BeekeeperExecutable


def check_default_values_from_config(default_config: BeekeeperConfig) -> None:
    assert default_config.unlock_timeout == BeekeeperDefaults.DEFAULT_UNLOCK_TIMEOUT
    assert default_config.unlock_interval == BeekeeperDefaults.DEFAULT_UNLOCK_INTERVAL
    assert default_config.log_json_rpc == BeekeeperDefaults.DEFAULT_LOG_JSON_RPC
    assert default_config.webserver_http_endpoint == http_webserver_default()
    assert default_config.webserver_thread_pool_size == BeekeeperDefaults.DEFAULT_WEBSERVER_THREAD_POOL_SIZE
    assert default_config.notifications_endpoint == BeekeeperDefaults.DEFAULT_NOTIFICATIONS_ENDPOINT
    assert default_config.backtrace == BeekeeperDefaults.DEFAULT_BACKTRACE
    assert default_config.export_keys_wallet == BeekeeperDefaults.DEFAULT_EXPORT_KEYS_WALLET


def test_default_values(beekeeper_exe: BeekeeperExecutable) -> None:
    """Test will check default values of Beekeeper."""
    # ARRANGE & ACT
    default_config = beekeeper_exe.generate_default_config()

    # ASSERT
    check_default_values_from_config(default_config)


async def test_config_fields_coverege(beekeeper_exe: BeekeeperExecutable) -> None:
    """Test will check for the differences between config.ini file and BeekeeperConfig class."""
    # ARRANGE
    beekeeper_config = beekeeper_exe.generate_default_config()

    with (beekeeper_exe.working_directory / (BeekeeperConfig.DEFAULT_FILE_NAME + ".tmp")).open() as config:
        config_class_fields = set(beekeeper_config.__dict__.keys())
        in_config_fields = set()

        comment_line_start = "# "
        separator_mark = "="

        # ACT
        for line in config:
            if (line := line.strip("\n")) and separator_mark in line:
                field_name = (
                    line[2:].split(separator_mark)[0]
                    if line.startswith(comment_line_start)
                    else line.split(separator_mark)[0]
                )
                in_config_fields.add(field_name.replace("-", "_"))

        differences_in_config = in_config_fields - config_class_fields
        differences_in_class = config_class_fields - in_config_fields

        # ASSERT
        for diff_in_config in differences_in_config:
            pytest.fail(
                f"Field `{diff_in_config}` exists in config.ini file, but does not have representation in"
                " BeekeeperConfig class."
            )

        for diff_in_class in differences_in_class:
            if diff_in_class in [
                "notifications_endpoint",
                "export_keys_wallet",
                "log_json_rpc",
                "webserver_unix_endpoint",
                "webserver_ws_endpoint",
            ]:
                # notifications_endpoint - When running not via handle, this is not set
                # export_keys_wallet - set only when dumping keys, not this case
                # log_json_rpc - using default logging config

                # Not supported or not used
                # webserver_unix_endpoint
                # webserver_ws_endpoint
                continue
            pytest.fail(
                f"Field `{diff_in_class}` exists in BeekeeperConfig class, but does not have representation in"
                " config.ini file."
            )
