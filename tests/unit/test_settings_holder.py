from __future__ import annotations

from typing import Any, cast

import pytest

from helpy._communication.settings import CommunicationSettings
from helpy._interfaces.settings_holder import SharedSettingsHolder, UniqueSettingsHolder

TestSharedSettingsHolder = SharedSettingsHolder[CommunicationSettings]
TestUniqueSettingsHolder = UniqueSettingsHolder[CommunicationSettings]
AnySettingsHolder = TestSharedSettingsHolder | TestUniqueSettingsHolder


def get_shared_settings() -> TestSharedSettingsHolder:
    return SharedSettingsHolder(settings=CommunicationSettings())


def get_unique_settings() -> TestUniqueSettingsHolder:
    return UniqueSettingsHolder(settings=CommunicationSettings())


@pytest.mark.parametrize("holder", [get_shared_settings(), get_unique_settings()])
def test_copy_in_getter(holder: AnySettingsHolder) -> None:
    # ARRANGE
    previous_value = holder.settings.max_retries

    # ACT
    holder.settings.max_retries = 10

    # ASSERT
    assert holder.settings.max_retries == previous_value


@pytest.mark.parametrize("holder", [get_shared_settings(), get_unique_settings()])
def test_modify_settings(holder: AnySettingsHolder) -> None:
    # ARRANGE
    new_value = holder.settings.max_retries + 1

    # ACT
    with holder.update_settings() as settings:
        settings.max_retries = new_value

    # ASSERT
    assert holder.settings.max_retries == new_value


@pytest.mark.parametrize("holder", [get_shared_settings(), get_unique_settings()])
def test_restore_settings(holder: AnySettingsHolder) -> None:
    # ARRANGE
    previous_value = holder.settings.max_retries

    # ACT
    with holder.restore_settings():
        holder.settings.max_retries = 10

    # ASSERT
    assert holder.settings.max_retries == previous_value


def test_shared_settings() -> None:
    # ARRANGE
    parent = get_shared_settings()
    child = SharedSettingsHolder(settings=parent._settings)
    new_value = parent.settings.max_retries + 1

    # ACT
    with parent.update_settings() as settings:
        settings.max_retries = new_value

    # ASSERT
    assert parent.settings.max_retries == child.settings.max_retries


def test_unique_settings() -> None:
    # ARRANGE
    parent = get_unique_settings()
    child = UniqueSettingsHolder(settings=parent._settings)
    old_value = parent.settings.max_retries
    new_value = parent.settings.max_retries + 1

    # ACT
    with parent.update_settings() as settings:
        settings.max_retries = new_value

    # ASSERT
    assert parent.settings.max_retries == new_value
    assert child.settings.max_retries == old_value


def test_is_shared_has_same_addresses() -> None:
    # ARRANGE
    parent = get_shared_settings()

    # ACT
    child = SharedSettingsHolder(settings=parent._settings)

    # ASSERT
    assert id(parent._settings) == id(child._settings)


def test_is_unique_has_different_addresses() -> None:
    # ARRANGE
    parent = get_unique_settings()

    # ACT
    child = UniqueSettingsHolder(settings=parent._settings)

    # ASSERT
    assert id(parent._settings) != id(child._settings)


@pytest.mark.parametrize("holder_cls", [SharedSettingsHolder, UniqueSettingsHolder])
def test_is_update_event_works(holder_cls: type[AnySettingsHolder]) -> None:
    # ARRANGE
    class HolderTestClass(holder_cls):  # type: ignore[valid-type, misc]
        def __init__(self) -> None:
            super().__init__(settings=CommunicationSettings())
            self.event_happened = False

        def _settings_updated(self, old_settings: Any, new_settings: Any) -> None:  # noqa: ARG002
            self.event_happened = True

    test_obj = cast(AnySettingsHolder, HolderTestClass())
    new_value = test_obj.settings.max_retries + 1

    # ACT
    with test_obj.update_settings() as settings:
        settings.max_retries = new_value

    # ASSERT
    assert test_obj.settings.max_retries == new_value
    assert cast(HolderTestClass, test_obj).event_happened


@pytest.mark.parametrize("holder", [get_shared_settings(), get_unique_settings()])
def test_is_update_event_not_happens_on_error(holder: AnySettingsHolder) -> None:
    # ARRANGE
    old_value = holder.settings.max_retries

    class TestError(Exception):
        pass

    # ACT
    with pytest.raises(TestError):  # noqa: PT012, SIM117
        with holder.update_settings() as settings:
            settings.max_retries = 10
            raise TestError

    # ASSERT
    assert holder.settings.max_retries == old_value


@pytest.mark.parametrize("holder", [get_shared_settings(), get_unique_settings()])
def test_is_update_happens_after_exit_from_with_statement(holder: AnySettingsHolder) -> None:
    # ARRANGE
    old_value = holder.settings.max_retries
    new_value = old_value + 1

    # ACT & ASSERT
    with holder.update_settings() as settings:
        settings.max_retries = new_value
        assert holder.settings.max_retries == old_value
    assert holder.settings.max_retries == new_value


@pytest.mark.parametrize("holder", [get_shared_settings(), get_unique_settings()])
def test_is_update_settings_does_not_affect_settings_accessor(holder: AnySettingsHolder) -> None:
    # ARRANGE
    old_value = holder.settings.max_retries
    new_value = old_value + 1

    # ACT & ASSERT
    with holder.update_settings() as _:
        holder.settings.max_retries = new_value
        assert holder.settings.max_retries == old_value
    assert holder.settings.max_retries == old_value
