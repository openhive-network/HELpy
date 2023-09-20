from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any


class Observer(ABC):
    @abstractmethod
    async def data_received(self, data: dict[str, Any]) -> None:
        """Called when any data is received via PUT method.

        Arguments:
            data -- data received as body

        Returns:
            Nothing.
        """
