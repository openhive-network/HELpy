from __future__ import annotations

import json

import msgspec

from schemas._preconfigured_base_model import PreconfiguredBaseModel
from schemas.fields.basic import PrivateKey, PublicKey


class KeyPair(PreconfiguredBaseModel):
    public_key: PublicKey
    private_key: PrivateKey

    def __post_init__(self) -> None:
        msgspec.json.decode(json.dumps(self.public_key).encode(), type=PublicKey)
        msgspec.json.decode(json.dumps(self.private_key).encode(), type=PrivateKey)

    def __hash__(self) -> int:
        return hash(self.private_key)

    def __eq__(self, value: object) -> bool:
        if isinstance(value, KeyPair):
            return self.private_key == value.private_key
        return super().__eq__(value)
