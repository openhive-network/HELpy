from __future__ import annotations

from abc import ABC, abstractmethod
from contextlib import contextmanager
from typing import TYPE_CHECKING, Any

from beekeepy._interface.context_settings_updater import ContextSettingsUpdater, SettingsT

if TYPE_CHECKING:
    from collections.abc import Iterator

__all__ = ["SettingsT", "UniqueSettingsHolder", "SharedSettingsHolder"]


class _SettingsHolderBase(ABC, ContextSettingsUpdater[SettingsT]):
    def __init__(self, *args: Any, settings: SettingsT, **kwargs: Any) -> None:
        self.__settings = self._get_settings_for_storage(settings)
        self.__is_in_modify_settings_state: bool = False
        super().__init__(*args, **kwargs)

    @property
    def settings(self) -> SettingsT:
        """Obtain currently used settings.

        Note:
            If you want to have shared settings with other instance, use `_settings`, otherwise you will pass copy.
        """
        return self._settings if self.__is_in_modify_settings_state else self._get_copy_of_settings()

    @property
    def _settings(self) -> SettingsT:
        """Obtain original settings instance.

        Can be used for making shared settings between self and other instance of SharedSettingsHolder.

        Warning:
            Not intended for public usage.
        """
        return self.__settings

    def _get_copy_of_settings(self) -> SettingsT:
        return self._settings.copy()

    @abstractmethod
    def _get_settings_for_storage(self, settings: SettingsT) -> SettingsT: ...

    @contextmanager
    def _modify_settings_state(self) -> Iterator[None]:
        self.__is_in_modify_settings_state = True
        try:
            yield
        finally:
            self.__is_in_modify_settings_state = False

    @contextmanager
    def restore_settings(self) -> Iterator[None]:
        """
        On exit settings will be restored to original values.

        Example:
            ```
            with handle.restore_setting():
                handle.settings.timeout = timedelta(seconds=10)
                handle.some.api.call() # timeout 10 seconds
            handle.some.api.call() # timeout 3 seconds
            ```

        Yields:
            Iterator[None]: Nothing.
        """
        with self._modify_settings_state():
            before = self._get_copy_of_settings()
            yield
        self.__settings = before


class SharedSettingsHolder(_SettingsHolderBase[SettingsT]):
    """Deriving after this class will not perform copy of passed settings (object is shared)."""

    def _get_settings_for_storage(self, settings: SettingsT) -> SettingsT:
        return settings


class UniqueSettingsHolder(_SettingsHolderBase[SettingsT]):
    """Deriving after this class will perform copy of passed settings (object is not shared)."""

    def _get_settings_for_storage(self, settings: SettingsT) -> SettingsT:
        return settings.copy()
