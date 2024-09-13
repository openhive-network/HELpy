from __future__ import annotations

from helpy._communication.abc.communicator import AbstractCommunicator  # noqa: TCH001
from helpy._communication.settings import CommunicationSettings
from helpy._interfaces.url import HttpUrl  # noqa: TCH001


class Settings(CommunicationSettings):
    http_endpoint: HttpUrl
    """
    Endpoint exposed by service to be connect to by handle.
    """

    communicator: type[AbstractCommunicator] | AbstractCommunicator | None = None
    """
    Defines class to be used for network handling. Can be given as class or instance.

    Note: If set to none, handles will use preferred communicators
    """

    def try_get_communicator_instance(
        self, settings: CommunicationSettings | None = None
    ) -> AbstractCommunicator | None:
        """Tries to return instance of communicator. If communicator is given as class, such instance will be created, by passing keyword argument: settings=settings, where value of settings is get from function arguments.

        Args:
            settings: Used for communicator instance creation. When None is passed settings will be filled with current instance of settings (self)

        Returns:
            Child of AbstractCommunicator instance if communicator is not None, otherwise None
        """  # noqa: E501
        if self.communicator is None:
            return None

        if isinstance(self.communicator, type):
            return self.communicator(settings=(settings or self))

        return self.communicator
