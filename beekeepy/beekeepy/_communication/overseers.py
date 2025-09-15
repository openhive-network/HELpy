from __future__ import annotations

from beekeepy._communication.abc.overseer import AbstractOverseer
from beekeepy._communication.abc.rules import RulesClassifier
from beekeepy._communication.rules import (
    ApiNotFound,
    DifferenceBetweenAmountOfRequestsAndResponses,
    ErrorInResponse,
    InvalidPassword,
    JussiResponse,
    NullResult,
    UnableToAcquireDatabaseLock,
    UnableToAcquireForkdbLock,
    UnableToOpenWallet,
    UnlockIsNotAccessible,
    UnparsableResponse,
    WalletIsAlreadyUnlocked,
)

__all__ = ["CommonOverseer", "StrictOverseer"]


class CommonOverseer(AbstractOverseer):
    """Dedicated for common usage."""

    def _rules(self) -> RulesClassifier:
        return RulesClassifier(
            preliminary=[
                ApiNotFound,
                WalletIsAlreadyUnlocked,
                UnableToOpenWallet,
                InvalidPassword,
                UnlockIsNotAccessible,
                ErrorInResponse,
            ],
            infinitely_repeatable=[
                UnableToAcquireDatabaseLock,
                UnableToAcquireForkdbLock,
            ],
            finitely_repeatable=[
                UnparsableResponse,
                JussiResponse,
                DifferenceBetweenAmountOfRequestsAndResponses,
                NullResult,
            ],
        )


class StrictOverseer(AbstractOverseer):
    """Dedicated for test usage."""

    def _rules(self) -> RulesClassifier:
        return RulesClassifier(
            preliminary=[
                UnparsableResponse,
                JussiResponse,
                DifferenceBetweenAmountOfRequestsAndResponses,
                ApiNotFound,
                NullResult,
                UnlockIsNotAccessible,
                WalletIsAlreadyUnlocked,
                UnableToOpenWallet,
                InvalidPassword,
                ErrorInResponse,
            ],
            infinitely_repeatable=[
                UnableToAcquireDatabaseLock,
                UnableToAcquireForkdbLock,
            ],
            finitely_repeatable=[],
        )
