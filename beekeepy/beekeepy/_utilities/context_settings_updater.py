from __future__ import annotations

from abc import abstractmethod
from contextlib import contextmanager
from typing import TYPE_CHECKING, Generic, TypeVar

from schemas._preconfigured_base_model import PreconfiguredBaseModel

if TYPE_CHECKING:
    from collections.abc import Iterator

SettingsT = TypeVar("SettingsT", bound=PreconfiguredBaseModel)


class ContextSettingsUpdater(Generic[SettingsT]):
    @abstractmethod
    def _get_copy_of_settings(self) -> SettingsT: ...

    @property
    @abstractmethod
    def _settings(self) -> SettingsT:
        """Obtain original settings instance.

        Can be used for making shared settings between self and other instance of SharedSettingsHolder.

        Warning:
            Not intended for public usage.
        """

    @contextmanager
    def update_settings(self) -> Iterator[SettingsT]:
        """
        Returns settings object, which can be freely modified. On exit saves it.

        Note:
            Modifying as:
            ```
            with handle.update_settings() as settings:
                handle.settings.some_value = new_value
            ```
            Does not affect state of settings, as `handle.settings` will return copy of current state.

        Example:
            ```
            with handle.update_settings() as settings:
                settings.timeout = timedelta(seconds=10)
                handle.some.api.call() # timeout 3 seconds
            handle.some.api.call() # timeout 10 seconds
            ```

        Yields:
            Iterator[SettingsT]: Stored settings instance
        """
        settings_to_update = self._get_copy_of_settings()

        yield settings_to_update

        # Simple override is not possible here because
        # SharedSettingsHolder won't work, as reference
        # to original settings will be lost
        for key, value in settings_to_update.dict().items():
            setattr(self._settings, key, value)
