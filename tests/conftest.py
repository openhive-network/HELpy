from __future__ import annotations

import pytest

from hive_transfer_protocol.__private.handles.abc.api import AbstractApi, RegisteredApisT


@pytest.fixture()
def registered_apis() -> RegisteredApisT:
    """Return registered methods."""
    return AbstractApi._get_registered_methods()
