from __future__ import annotations

from abc import ABC, abstractmethod
from contextlib import contextmanager
from typing import TYPE_CHECKING, Any, Generic, TypeVar

from helpy._communication.settings import CommunicationSettings

if TYPE_CHECKING:
    from collections.abc import Iterator

__all__ = ["SettingsT", "UniqueSettingsHolder", "SharedSettingsHolder"]

SettingsT = TypeVar("SettingsT", bound=CommunicationSettings)


class _SettingsHolderBase(ABC, Generic[SettingsT]):
    def __init__(self, *args: Any, settings: SettingsT, **kwargs: Any) -> None:
        self.__settings = self._get_settings_for_storage(settings)
        self.__is_in_modify_settings_state: bool = False
        super().__init__(*args, **kwargs)

    @property
    def settings(self) -> SettingsT:
        """Obtain currently used settings."""
        return self.__settings if self.__is_in_modify_settings_state else self._get_copy_of_settings()

    def _get_copy_of_settings(self) -> SettingsT:
        return self.__settings.copy()

    def _settings_updated(self, old_settings: SettingsT, new_settings: SettingsT) -> None:
        """
        Override this method if there are any action required after settings were updated.

        Args:
            old_settings: settings instance before change
            new_settings: settings instance after change
        """

    @abstractmethod
    def _get_settings_for_storage(self, settings: SettingsT) -> SettingsT:
        ...

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

    @contextmanager
    def update_settings(self) -> Iterator[SettingsT]:
        """
        Returns settings object, which can be freely modified. On exit saves it.

        Yields:
            Iterator[SettingsT]: Stored settings instance
        """
        with self._modify_settings_state():
            original_settings = self._get_copy_of_settings()
            settings_to_update = self._get_copy_of_settings()
            yield settings_to_update
            self.__settings = settings_to_update
            self._settings_updated(old_settings=original_settings, new_settings=self.__settings)


class SharedSettingsHolder(_SettingsHolderBase[SettingsT]):
    """Deriving after this class will not perform copy of passed settings (object is shared)."""

    def _get_settings_for_storage(self, settings: SettingsT) -> SettingsT:
        return settings


class UniqueSettingsHolder(_SettingsHolderBase[SettingsT]):
    """Deriving after this class will perform copy of passed settings (object is not shared)."""

    def _get_settings_for_storage(self, settings: SettingsT) -> SettingsT:
        return settings.copy()
