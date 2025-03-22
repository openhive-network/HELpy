from __future__ import annotations

from typing import TYPE_CHECKING, Any

from loguru import logger

from beekeepy._interface.abc.asynchronous.beekeeper import Beekeeper as BeekeeperInterface
from beekeepy._interface.abc.packed_object import PackedAsyncBeekeeper
from beekeepy._interface.asynchronous.session import Session
from beekeepy._interface.delay_guard import AsyncDelayGuard
from beekeepy._interface.state_invalidator import StateInvalidator
from beekeepy._remote_handle.beekeeper import AsyncBeekeeper as AsynchronousRemoteBeekeeperHandle
from beekeepy._utilities.delay_guard import AsyncDelayGuard
from beekeepy._utilities.state_invalidator import StateInvalidator
from beekeepy.exceptions import (
    DetachRemoteBeekeeperError,
    InvalidatedStateByClosingBeekeeperError,
    UnknownDecisionPathError,
)

if TYPE_CHECKING:
    from beekeepy._communication import CommunicationSettings, HttpUrl
    from beekeepy._interface.abc.asynchronous.session import (
        Session as SessionInterface,
    )


class Beekeeper(BeekeeperInterface, StateInvalidator):
    def __init__(self, *args: Any, handle: AsynchronousRemoteBeekeeperHandle, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self.__instance = handle
        self.__guard = AsyncDelayGuard()
        self.__default_session: None | SessionInterface = None

    async def create_session(self, *, salt: str | None = None) -> SessionInterface:  # noqa: ARG002
        session: SessionInterface | None = None
        while session is None or self.__guard.error_occured():
            async with self.__guard:
                session = self.__create_session()
                await session.get_info()
                return session
        raise UnknownDecisionPathError

    @property
    async def session(self) -> SessionInterface:
        if self.__default_session is None:
            self.__default_session = self.__create_session((await self._get_instance().session).token)
        return self.__default_session

    def _get_instance(self) -> AsynchronousRemoteBeekeeperHandle:
        return self.__instance

    @StateInvalidator.empty_call_after_invalidation(None)
    def teardown(self) -> None:
        if isinstance(self.__instance, AsynchronousBeekeeperHandle):
            self.__instance.teardown()
        self.invalidate(InvalidatedStateByClosingBeekeeperError())

    def detach(self) -> int:
        if not isinstance(self.__instance, AsynchronousBeekeeperHandle):
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

    def pack(self) -> PackedAsyncBeekeeper:
        return PackedAsyncBeekeeper(settings=self.settings, unpack_factory=Beekeeper._remote_factory)

    @classmethod
    async def _factory(cls, *, settings: Settings | None = None) -> BeekeeperInterface:
        settings = settings or Settings()
        handle = AsynchronousBeekeeperHandle(settings=settings, logger=logger)
        handle.run()
        return cls(handle=handle)

    @classmethod
    async def _remote_factory(cls, *, url_or_settings: Settings | HttpUrl) -> BeekeeperInterface:
        if isinstance(url_or_settings, Settings):
            assert (
                url_or_settings.http_endpoint is not None
            ), "Settings.http_endpoint has to be set when passing to remote_factory"
        settings = url_or_settings if isinstance(url_or_settings, Settings) else Settings(http_endpoint=url_or_settings)
        handle = AsynchronousRemoteBeekeeperHandle(settings=settings)
        cls.__apply_existing_session_token(settings=settings, handle=handle)
        return cls(handle=handle)

    @classmethod
    def __apply_existing_session_token(cls, settings: Settings, handle: AsynchronousRemoteBeekeeperHandle) -> None:
        if settings.use_existing_session:
            handle.set_session_token(settings.use_existing_session)

    async def _aenter(self) -> BeekeeperInterface:
        return self

    async def _afinally(self) -> None:
        self.teardown()

    def _get_copy_of_settings(self) -> CommunicationSettings:
        return self.__instance._get_copy_of_settings()

    @property
    def _settings(self) -> CommunicationSettings:
        return self.__instance._settings
