from __future__ import annotations

from schemas._preconfigured_base_model import PreconfiguredBaseModel
from schemas.fields.basic import PrivateKey, PublicKey  # noqa: TCH001


class KeyPair(PreconfiguredBaseModel):
    public_key: PublicKey
    private_key: PrivateKey

    def __hash__(self) -> int:
        return hash(self.private_key)

    def __eq__(self, value: object) -> bool:
        if isinstance(value, KeyPair):
            return self.private_key == value.private_key
        return super().__eq__(value)
