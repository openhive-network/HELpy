from __future__ import annotations

from functools import wraps
from typing import Iterator

import pytest
from local_tools.beekeepy.generators import (
    default_wallet_credentials,
    generate_account_name,
    generate_wallet_name,
    generate_wallet_password,
)
from local_tools.beekeepy.models import (
    SettingsLoggerFactory,
    WalletInfo,
    WalletInfoWithImportedAccounts,
    WalletsGeneratorT,
)

from beekeepy._handle import Beekeeper
from helpy import AccountCredentials


@pytest.fixture()
def beekeeper_not_started(settings_with_logger: SettingsLoggerFactory) -> Iterator[Beekeeper]:
    incoming_settings, logger = settings_with_logger()
    bk = Beekeeper(settings=incoming_settings, logger=logger)

    yield bk

    if bk.is_running:
        bk.teardown()


@pytest.fixture()
def beekeeper(beekeeper_not_started: Beekeeper) -> Iterator[Beekeeper]:
    with beekeeper_not_started as bk:
        yield bk


@pytest.fixture()
def wallet(beekeeper: Beekeeper) -> WalletInfo:
    name, password = default_wallet_credentials()
    beekeeper.api.create(wallet_name=name, password=password)
    return WalletInfo(name=name, password=password)


@pytest.fixture()
def account(beekeeper: Beekeeper, wallet: WalletInfo) -> AccountCredentials:
    acc = AccountCredentials.create(generate_account_name())
    beekeeper.api.import_key(wallet_name=wallet.name, wif_key=acc.private_key)
    return acc


@pytest.fixture(scope="session")
def keys_to_import() -> list[AccountCredentials]:
    return AccountCredentials.create_multiple(10)


@pytest.fixture()
def setup_wallets(beekeeper: Beekeeper) -> WalletsGeneratorT:
    @wraps(setup_wallets)
    def __setup_wallets(
        count: int, *, import_keys: bool = True, keys_per_wallet: int = 1
    ) -> list[WalletInfoWithImportedAccounts]:
        wallets = [
            WalletInfoWithImportedAccounts(
                name=generate_wallet_name(i),
                password=generate_wallet_password(i),
                accounts=(
                    AccountCredentials.create_multiple(keys_per_wallet, name_base=generate_account_name(i))
                    if keys_per_wallet
                    else []
                ),
            )
            for i in range(count)
        ]
        assert len(wallets) == count, "Incorrect number of created wallets"
        with beekeeper.batch() as bk:
            for wallet in wallets:
                bk.api.beekeeper.create(wallet_name=wallet.name, password=wallet.password)

                if import_keys:
                    for account in wallet.accounts:
                        bk.api.beekeeper.import_key(wallet_name=wallet.name, wif_key=account.private_key)
        return wallets

    return __setup_wallets
