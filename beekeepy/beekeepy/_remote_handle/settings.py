from __future__ import annotations

from typing import ClassVar

from beekeepy._communication import (
    AbstractCommunicator,
    AbstractOverseer,
    CommonOverseer,
    CommunicationSettings,
    HttpUrl,
)


class RemoteHandleSettings(CommunicationSettings):
    class Defaults(CommunicationSettings.Defaults):
        OVERSEER: ClassVar[type[AbstractOverseer]] = CommonOverseer

    http_endpoint: HttpUrl | None = None
    """
    Endpoint exposed by service to be connect to by handle.
    """

    communicator: type[AbstractCommunicator] | AbstractCommunicator | None = None
    """
    Defines class to be used for network handling. Can be given as class or instance.

    Note: If set to none, handles will use preferred communicators
    """

    overseer: type[AbstractOverseer] | AbstractOverseer = Defaults.OVERSEER
    """
    Defines class to be used for response validation and handling basic turbulence
    during communication
    """

    def try_get_communicator_instance(
        self, settings: CommunicationSettings | None = None
    ) -> AbstractCommunicator | None:
        """Tries to return instance of communicator.

        If communicator is given as class, such instance will be created,
        by passing keyword argument: settings=settings,
        where value of settings is get from function arguments.

        Args:
            settings: Used for communicator instance creation.
                When None is passed, settings will be filled with current instance of settings (self)

        Returns:
            Child of AbstractCommunicator instance if communicator is not None, otherwise None
        """
        if self.communicator is None:
            return None

        if isinstance(self.communicator, type):
            return self.communicator(settings=(settings or self))

        return self.communicator

    def get_overseer(self, *, communicator: AbstractCommunicator) -> AbstractOverseer:
        """Obtains overseer instance, by returning it (if exists) or by creating new instance.

        Args:
            communicator: will be passed to overseer.

        Notes:
            If settings.overseer is not a type, then communicator argument is not used.

        Returns:
            Overseer
        """
        if isinstance(self.overseer, AbstractOverseer):
            return self.overseer
        return self.overseer(communicator=communicator)
