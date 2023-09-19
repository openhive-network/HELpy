from __future__ import annotations

import pytest

from helpy import Time


def test_if_object_creation_is_forbidden() -> None:
    with pytest.raises(TypeError):
        Time()
