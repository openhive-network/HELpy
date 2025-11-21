from __future__ import annotations

from typing import Any

from beekeepy.handle.remote import (
    AbstractSyncApi,
    AbstractSyncApiCollection,
    AbstractSyncHandle,
    RemoteHandleSettings,
    SyncSendable,
)
from schemas._preconfigured_base_model import PreconfiguredBaseModel


class InputTypeSchema(PreconfiguredBaseModel):
    input_type: str
    input_value: list[str]


class VoterSchema(PreconfiguredBaseModel):
    voter_name: str
    vests: str
    account_vests: str
    proxied_vests: str
    timestamp: str


class WitnessesVotersResponseSchema(PreconfiguredBaseModel):
    total_votes: int
    total_pages: int
    voters: list[VoterSchema]


class TestApi(AbstractSyncApi):
    endpoint = AbstractSyncApi.endpoint_rest()

    def base_path(self) -> str:
        return "/hafbe-api"

    @classmethod
    def _register_api(cls) -> bool:
        """This is test api, no need to register it."""
        return False

    @endpoint.get("/last-synced-block")
    def last_synced_block(self) -> int:
        raise NotImplementedError

    @endpoint.get("/input-type/{input-value}")
    def input_type(self, /, input_value: str) -> InputTypeSchema:
        raise NotImplementedError

    @endpoint.get("/witnesses/{account-name}/voters")
    def witnesses_voters(self, /, account_name: str, *, page_size: int, page: int = 0) -> WitnessesVotersResponseSchema:
        raise NotImplementedError


class TestApiCollection(AbstractSyncApiCollection):
    def __init__(self, owner: SyncSendable) -> None:
        super().__init__(owner)

        self.test_api = TestApi(owner=self._owner)


class TestCaller(AbstractSyncHandle[RemoteHandleSettings, TestApiCollection]):
    def _construct_api(self) -> TestApiCollection:
        """Return api collection."""
        return TestApiCollection(owner=self)

    def _target_service(self) -> str:
        """Returns name of service that following handle is connecting to."""
        return "test_service"

    def batch(self, *, delay_error_on_data_access: bool = False) -> Any:
        raise NotImplementedError
