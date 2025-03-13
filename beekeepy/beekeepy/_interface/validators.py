from __future__ import annotations

import json
import re
from re import Pattern
from typing import Final

import msgspec

from beekeepy.exceptions import (
    InvalidAccountNameError,
    InvalidSchemaHexError,
    InvalidSchemaPrivateKeyError,
    InvalidSchemaPublicKeyError,
    NotPositiveTimeError,
    SchemaDetectableError,
    TimeTooBigError,
)
from schemas.fields.basic import AccountName, PrivateKey, PublicKey
from schemas.fields.hex import Hex

__all__ = [
    "validate_account_names",
    "validate_private_keys",
    "validate_public_keys",
    "validate_timeout",
    "validate_digest",
]

wallet_name_regex: Final[Pattern[str]] = re.compile(r"^[a-zA-Z0-9_\._\-\@]+$")


def _generic_kwargs_validator(
    arguments: dict[str, str], exception: type[SchemaDetectableError], validator: type[str]
) -> None:
    try:
        for arg_value in arguments.values():
            msgspec.json.decode(json.dumps(arg_value), type=validator)
    except msgspec.ValidationError as error:
        raise exception from error


def validate_account_names(**kwargs: str) -> None:
    _generic_kwargs_validator(kwargs, InvalidAccountNameError, AccountName)


def validate_private_keys(**kwargs: str) -> None:
    _generic_kwargs_validator(kwargs, InvalidSchemaPrivateKeyError, PrivateKey)


def validate_public_keys(**kwargs: str) -> None:
    _generic_kwargs_validator(kwargs, InvalidSchemaPublicKeyError, PublicKey)


def validate_digest(**kwargs: str) -> None:
    _generic_kwargs_validator(kwargs, InvalidSchemaHexError, Hex)


def validate_timeout(time: int) -> None:
    if time <= 0:
        raise NotPositiveTimeError(time=time)

    if time >= TimeTooBigError.MAX_VALUE:
        raise TimeTooBigError(time=time)
