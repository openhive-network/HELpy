from __future__ import annotations

from typing import TYPE_CHECKING, Any

from loguru import logger

from beekeepy._interface.abc.packed_object import PackedSyncBeekeeper
from beekeepy._interface.abc.synchronous.beekeeper import Beekeeper as BeekeeperInterface
from beekeepy._interface.settings import InterfaceSettings
from beekeepy._interface.synchronous.session import Session
from beekeepy._remote_handle import BeekeeperTemplate as SynchronousRemoteBeekeeperHandle
from beekeepy._runnable_handle import BeekeeperTemplate as SynchronousBeekeeperHandle
from beekeepy._utilities.delay_guard import SyncDelayGuard
from beekeepy._utilities.state_invalidator import StateInvalidator
from beekeepy.exceptions import (
    DetachRemoteBeekeeperError,
    InvalidatedStateByClosingBeekeeperError,
    UnknownDecisionPathError,
)

if TYPE_CHECKING:
    from beekeepy._communication import CommunicationSettings, HttpUrl
    from beekeepy._interface.abc.synchronous.session import (
        Session as SessionInterface,
    )


class Beekeeper(BeekeeperInterface, StateInvalidator):
    def __init__(self, *args: Any, handle: SynchronousRemoteBeekeeperHandle[InterfaceSettings], **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self.__instance = handle
        self.__guard = SyncDelayGuard()
        self.__default_session: SessionInterface | None = None

    def create_session(self, *, salt: str | None = None) -> SessionInterface:  # noqa: ARG002
        session: SessionInterface | None = None
        while session is None or self.__guard.error_occured():
            with self.__guard:
                session = self.__create_session()
                session.get_info()
                return session
        raise UnknownDecisionPathError

    @property
    def session(self) -> SessionInterface:
        if self.__default_session is None:
            self.__default_session = self.__create_session(self._get_instance().session.token, default_session=True)
        return self.__default_session

    def _get_instance(self) -> SynchronousRemoteBeekeeperHandle[InterfaceSettings]:
        return self.__instance

    @StateInvalidator.empty_call_after_invalidation(None)
    def teardown(self) -> None:
        if isinstance(self.__instance, SynchronousBeekeeperHandle):
            self.__instance.teardown()
        self.invalidate(InvalidatedStateByClosingBeekeeperError())

    def detach(self) -> int:
        if not isinstance(self.__instance, SynchronousBeekeeperHandle):
            raise DetachRemoteBeekeeperError
        return self.__instance.detach()

    def __create_session(self, token: str | None = None, *, default_session: bool = False) -> SessionInterface:
        session = Session(
            beekeeper=self._get_instance(),
            use_session_token=token,
            guard=self.__guard,
            default_session_close_callback=(self.__manage_closed_default_session if default_session else None),
        )
        self.register_invalidable(session)
        return session

    def __manage_closed_default_session(self) -> None:
        self.__default_session = None
        self._get_instance()._clear_session()

    def pack(self) -> PackedSyncBeekeeper:
        return PackedSyncBeekeeper(settings=self.settings, unpack_factory=Beekeeper._remote_factory)

    @classmethod
    def _factory(cls, *, settings: InterfaceSettings | None = None) -> BeekeeperInterface:
        settings = settings or InterfaceSettings()
        handle = cls.__create_local_handle(settings=settings)
        handle.run()
        return cls(handle=handle)

    @classmethod
    def _remote_factory(cls, *, url_or_settings: InterfaceSettings | HttpUrl) -> BeekeeperInterface:
        if isinstance(url_or_settings, InterfaceSettings):
            assert (
                url_or_settings.http_endpoint is not None
            ), "Settings.http_endpoint has to be set when passing to remote_factory"
        settings = (
            url_or_settings
            if isinstance(url_or_settings, InterfaceSettings)
            else InterfaceSettings(http_endpoint=url_or_settings)
        )
        handle = SynchronousRemoteBeekeeperHandle(settings=settings)
        cls.__apply_existing_session_token(settings=settings, handle=handle)
        return cls(handle=handle)

    @classmethod
    def __apply_existing_session_token(
        cls, settings: InterfaceSettings, handle: SynchronousRemoteBeekeeperHandle[InterfaceSettings]
    ) -> None:
        if settings.use_existing_session:
            handle.set_session_token(settings.use_existing_session)

    @classmethod
    def __create_local_handle(cls, settings: InterfaceSettings) -> SynchronousBeekeeperHandle[InterfaceSettings]:
        return SynchronousBeekeeperHandle(settings=settings, logger=logger)

    def _enter(self) -> BeekeeperInterface:
        return self

    def _finally(self) -> None:
        self.teardown()

    def _get_copy_of_settings(self) -> CommunicationSettings:
        return self.__instance._get_copy_of_settings()

    @property
    def _settings(self) -> CommunicationSettings:
        return self.__instance._settings
