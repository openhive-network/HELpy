from __future__ import annotations

from typing import TYPE_CHECKING

from pydantic import validator

from schemas._preconfigured_base_model import PreconfiguredBaseModel
from schemas.fields.basic import PrivateKey, PublicKey

if TYPE_CHECKING:
    from typing import Any

    from pydantic.typing import CallableGenerator


class KeyPair(PreconfiguredBaseModel):
    public_key: PublicKey | str
    private_key: PrivateKey | str

    def __hash__(self) -> int:
        return hash(self.private_key)

    def __eq__(self, value: object) -> bool:
        if isinstance(value, KeyPair):
            return self.private_key == value.private_key
        return super().__eq__(value)

    @validator("private_key")
    @classmethod
    def _use_private_key_class(cls, value: Any) -> PrivateKey:
        assert isinstance(value, str), "given value is not string, cannot be converted to private key"
        PrivateKey.validate(value)
        return PrivateKey(value)

    @validator("public_key")
    @classmethod
    def _use_public_key_class(cls, value: Any) -> PublicKey:
        assert isinstance(value, str), "given value is not string, cannot be converted to public key"
        PublicKey.validate(value)
        return PublicKey(value)

    @classmethod
    def __get_validators__(cls) -> CallableGenerator:
        yield from super().__get_validators__()
        yield cls._use_private_key_class
        yield cls._use_public_key_class
