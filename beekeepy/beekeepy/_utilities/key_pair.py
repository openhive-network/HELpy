from __future__ import annotations

from typing import TYPE_CHECKING

from schemas._preconfigured_base_model import PreconfiguredBaseModel

if TYPE_CHECKING:
    from schemas.fields.basic import PrivateKey, PublicKey


class KeyPair(PreconfiguredBaseModel):
    public_key: PublicKey
    private_key: PrivateKey

    def __hash__(self) -> int:
        return hash(self.private_key)

    def __eq__(self, value: object) -> bool:
        if isinstance(value, KeyPair):
            return self.private_key == value.private_key
        return super().__eq__(value)
