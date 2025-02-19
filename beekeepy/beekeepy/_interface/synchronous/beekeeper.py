from __future__ import annotations

from typing import TYPE_CHECKING, Any

from loguru import logger

from beekeepy._handle.beekeeper import Beekeeper as SynchronousBeekeeperHandle
from beekeepy._handle.beekeeper import SyncRemoteBeekeeper as SynchronousRemoteBeekeeperHandle
from beekeepy._interface.abc.packed_object import PackedSyncBeekeeper
from beekeepy._interface.abc.synchronous.beekeeper import Beekeeper as BeekeeperInterface
from beekeepy._interface.close_sessions_sync import close_sessions
from beekeepy._interface.delay_guard import SyncDelayGuard
from beekeepy._interface.settings import Settings
from beekeepy._interface.state_invalidator import StateInvalidator
from beekeepy._interface.synchronous.session import Session
from beekeepy.exceptions import DetachRemoteBeekeeperError, UnknownDecisionPathError
from beekeepy.exceptions.common import InvalidatedStateByClosingBeekeeperError

if TYPE_CHECKING:
    from beekeepy._handle.beekeeper import SyncRemoteBeekeeper
    from beekeepy._interface.abc.synchronous.session import (
        Session as SessionInterface,
    )
    from helpy import HttpUrl
    from helpy._communication.settings import CommunicationSettings


class Beekeeper(BeekeeperInterface, StateInvalidator):
    def __init__(self, *args: Any, handle: SyncRemoteBeekeeper, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self.__instance = handle
        self.__guard = SyncDelayGuard()
        self.__default_session: SessionInterface | None = None
        self.__owned_session_tokens: list[str] = []

    def create_session(self, *, salt: str | None = None) -> SessionInterface:  # noqa: ARG002
        session: SessionInterface | None = None
        while session is None or self.__guard.error_occured():
            with self.__guard:
                return self.__create_session()
        raise UnknownDecisionPathError

    @property
    def session(self) -> SessionInterface:
        if self.__default_session is None:
            session_token_from_handle = self._get_instance().session.token
            self.__default_session = self.__create_session(
                token=session_token_from_handle,
                default_session=(session_token_from_handle == self.settings.use_existing_session),
            )
        return self.__default_session

    def _get_instance(self) -> SyncRemoteBeekeeper:
        return self.__instance

    @StateInvalidator.empty_call_after_invalidation(None)
    def teardown(self) -> None:
        close_sessions(self.__instance.http_endpoint, self.__owned_session_tokens)
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
        session.get_info()
        self.register_invalidable(session)
        if not default_session:
            self.__owned_session_tokens.append(session.token)
        return session

    def __manage_closed_default_session(self) -> None:
        self.__default_session = None
        self._get_instance()._clear_session()

    def pack(self) -> PackedSyncBeekeeper:
        return PackedSyncBeekeeper(settings=self._get_instance().settings, unpack_factory=Beekeeper._remote_factory)

    @classmethod
    def _factory(cls, *, settings: Settings | None = None) -> BeekeeperInterface:
        settings = settings or Settings()
        handle = SynchronousBeekeeperHandle(settings=settings, logger=logger)
        handle.run()
        return cls(handle=handle)

    @classmethod
    def _remote_factory(cls, *, url_or_settings: Settings | HttpUrl) -> BeekeeperInterface:
        if isinstance(url_or_settings, Settings):
            assert (
                url_or_settings.http_endpoint is not None
            ), "Settings.http_endpoint has to be set when passing to remote_factory"
        settings = url_or_settings if isinstance(url_or_settings, Settings) else Settings(http_endpoint=url_or_settings)
        handle = SynchronousRemoteBeekeeperHandle(settings=settings)
        cls.__apply_existing_session_token(settings=settings, handle=handle)
        return cls(handle=handle)

    @classmethod
    def __apply_existing_session_token(cls, settings: Settings, handle: SynchronousRemoteBeekeeperHandle) -> None:
        if settings.use_existing_session:
            handle.set_session_token(settings.use_existing_session)

    def _enter(self) -> BeekeeperInterface:
        return self

    def _finally(self) -> None:
        self.teardown()

    def _get_copy_of_settings(self) -> CommunicationSettings:
        return self.__instance._get_copy_of_settings()

    @property
    def _settings(self) -> CommunicationSettings:
        return self.__instance._settings
