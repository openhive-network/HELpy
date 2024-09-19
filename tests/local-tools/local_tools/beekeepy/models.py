from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Protocol

from schemas.fields.basic import PublicKey

if TYPE_CHECKING:
    from loguru import Logger

    from beekeepy import Settings
    from helpy import AccountCredentials


@dataclass
class WalletInfo:
    name: str
    password: str


@dataclass
class WalletInfoWithImportedAccounts(WalletInfo):
    accounts: list[AccountCredentials]

    def get_all_public_keys(self) -> list[PublicKey]:
        return sorted([PublicKey(acc.public_key) for acc in self.accounts])


class WalletsGeneratorT(Protocol):
    def __call__(
        self, count: int, *, import_keys: bool = True, keys_per_wallet: int = 1
    ) -> list[WalletInfoWithImportedAccounts]: ...


class SettingsFactory(Protocol):
    def __call__(self, settings_update: Settings | None = None) -> Settings: ...


class SettingsLoggerFactory(Protocol):
    def __call__(self, settings_update: Settings | None = None) -> tuple[Settings, Logger]: ...