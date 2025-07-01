from __future__ import annotations

import re
from re import Pattern
from typing import Final

from beekeepy.exceptions import (
    InvalidAccountNameError,
    InvalidSchemaHexError,
    InvalidSchemaPrivateKeyError,
    InvalidSchemaPublicKeyError,
    NotPositiveTimeError,
    SchemaDetectableError,
    TimeTooBigError,
)
from schemas.errors import ValidationError
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
        for _arg_name, arg_value in arguments.items():
            validator(arg_value)
    except ValidationError as error:
        raise exception(_arg_name, arg_value) from error


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
