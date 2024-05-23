from __future__ import annotations

import pytest

from helpy import ContextAsync, ContextSync


class MyCustomError(Exception):
    pass


class SyncTestContext(ContextSync[None]):
    def __init__(self) -> None:
        super().__init__()
        self.test_variable = "invalid"

    def _enter(self) -> None:
        self.test_variable = "during-test"

    def _finally(self) -> None:
        self.test_variable = "correct"


class AsyncTestContext(ContextAsync[None]):
    def __init__(self) -> None:
        super().__init__()
        self.test_variable = "invalid"

    async def _aenter(self) -> None:
        self.test_variable = "during-test"

    async def _afinally(self) -> None:
        self.test_variable = "correct"


def test_finally_context_sync() -> None:
    # ARRANGE
    ctx = SyncTestContext()
    assert ctx.test_variable == "invalid"

    # ACT & ASSERT
    with ctx:
        assert ctx.test_variable == "during-test"
    assert ctx.test_variable == "correct"


async def test_finally_context_async() -> None:
    # ARRANGE
    ctx = AsyncTestContext()
    assert ctx.test_variable == "invalid"

    # ACT & ASSERT
    async with ctx:
        assert ctx.test_variable == "during-test"
    assert ctx.test_variable == "correct"


def test_exception_rethrow_sync() -> None:
    with pytest.raises(MyCustomError):  # noqa: PT012, SIM117
        with SyncTestContext():
            raise MyCustomError


async def test_exception_rethrow_async() -> None:
    with pytest.raises(MyCustomError):  # noqa: PT012
        async with AsyncTestContext():
            raise MyCustomError
