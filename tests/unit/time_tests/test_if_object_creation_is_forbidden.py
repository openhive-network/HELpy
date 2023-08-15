from __future__ import annotations

import pytest

from hive_transfer_protocol import Time


def test_if_object_creation_is_forbidden() -> None:
    with pytest.raises(TypeError):
        Time()
