from __future__ import annotations

from helpy._interfaces.key_pair import KeyPair
from helpy._interfaces.wax import calculate_public_key, generate_private_key


class AccountCredentials(KeyPair):
    name: str

    @classmethod
    def create(cls, name: str) -> AccountCredentials:
        pv_key = generate_private_key()
        pub_key = calculate_public_key(pv_key)
        return AccountCredentials(name=name, public_key=pub_key, private_key=pv_key)

    @classmethod
    def create_multiple(cls, number_of_accounts: int, *, name_base: str = "account") -> list[AccountCredentials]:
        return [AccountCredentials.create(f"{name_base}-{i}") for i in range(number_of_accounts)]
