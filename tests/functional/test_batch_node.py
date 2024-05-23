from __future__ import annotations

from typing import TYPE_CHECKING, Literal

import pytest

from helpy.exceptions import CommunicationError, NothingToSendError, ResponseNotReadyError

if TYPE_CHECKING:
    from helpy._handles.hived.async_handle import AsyncHived
    from helpy._handles.hived.sync_handle import Hived


def test_batch_node(sync_node: Hived) -> None:
    with sync_node.batch() as node:
        dynamic_properties = node.api.database.get_dynamic_global_properties()
        config = node.api.database.get_config()

    assert len(dynamic_properties.dict(by_alias=True)) != 0
    assert len(config.dict(by_alias=True)) != 0


async def test_async_batch_node(async_node: AsyncHived) -> None:
    async with await async_node.batch() as node:
        dynamic_properties = await node.api.database.get_dynamic_global_properties()
        config = await node.api.database.get_config()

    assert len(dynamic_properties.dict(by_alias=True)) != 0
    assert len(config.dict(by_alias=True)) != 0


def test_batch_node_response_not_ready(sync_node: Hived) -> None:
    with sync_node.batch() as node:
        dynamic_properties = node.api.database.get_dynamic_global_properties()

        with pytest.raises(ResponseNotReadyError):
            _ = dynamic_properties.head_block_id


def test_batch_node_error_response(sync_node: Hived) -> None:
    with pytest.raises(CommunicationError, match="Invalid cast"):  # noqa: PT012, SIM117
        with sync_node.batch() as node:
            node.api.database.find_accounts(accounts=123)


def test_batch_node_error_response_delayed(sync_node: Hived) -> None:
    with sync_node.batch(delay_error_on_data_access=True) as node:
        response = node.api.database.find_accounts(accounts=123)

    with pytest.raises(CommunicationError, match="Invalid cast"):
        _ = response.accounts[0].name


async def test_async_batch_node_error_response_delayed(async_node: AsyncHived) -> None:
    async with await async_node.batch(delay_error_on_data_access=True) as node:
        response = await node.api.database.find_accounts(accounts=123)

    with pytest.raises(CommunicationError, match="Invalid cast"):
        _ = response.accounts[0].name


@pytest.mark.parametrize("order", ["first_good", "first_bad"])
def test_batch_node_mixed_request_delayed(sync_node: Hived, order: Literal["first_good", "first_bad"]) -> None:
    with sync_node.batch(delay_error_on_data_access=True) as node:
        if order == "first_good":
            good_response = node.api.database.get_dynamic_global_properties()
            bad_response = node.api.database.find_accounts(accounts=123)
        else:
            bad_response = node.api.database.find_accounts(accounts=123)
            good_response = node.api.database.get_dynamic_global_properties()

    assert good_response.head_block_number > 0
    with pytest.raises(CommunicationError, match="Invalid cast"):
        _ = bad_response.accounts[0].name


async def test_batch_node_nothing_to_send(sync_node: Hived) -> None:
    with pytest.raises(NothingToSendError):  # noqa: SIM117
        with sync_node.batch():
            pass
