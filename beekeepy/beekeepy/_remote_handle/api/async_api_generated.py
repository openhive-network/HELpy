from beekeepy._remote_handle.abc.api import AbstractAsyncApi
from beekeepy._remote_handle.api.api_description import CloseResponse
from beekeepy._remote_handle.api.api_description import CloseSessionResponse
from beekeepy._remote_handle.api.api_description import CreateResponse
from beekeepy._remote_handle.api.api_description import CreateSessionResponse
from beekeepy._remote_handle.api.api_description import DecryptDataResponse
from beekeepy._remote_handle.api.api_description import EncryptDataResponse
from beekeepy._remote_handle.api.api_description import GetInfoResponse
from beekeepy._remote_handle.api.api_description import GetPublicKeysResponseItem
from beekeepy._remote_handle.api.api_description import GetVersionResponse
from beekeepy._remote_handle.api.api_description import HasMatchingPrivateKeyResponse
from beekeepy._remote_handle.api.api_description import HasWalletResponse
from beekeepy._remote_handle.api.api_description import ImportKeyResponse
from beekeepy._remote_handle.api.api_description import IsWalletUnlockedResponse
from beekeepy._remote_handle.api.api_description import ListCreatedWalletsResponseItem
from beekeepy._remote_handle.api.api_description import ListWalletsResponseItem
from beekeepy._remote_handle.api.api_description import LockResponse
from beekeepy._remote_handle.api.api_description import LockAllResponse
from beekeepy._remote_handle.api.api_description import OpenResponse
from beekeepy._remote_handle.api.api_description import RemoveKeyResponse
from beekeepy._remote_handle.api.api_description import SetTimeoutResponse
from beekeepy._remote_handle.api.api_description import SignDigestResponse
from beekeepy._remote_handle.api.api_description import UnlockResponse
from typing import Optional
from typing import List


class BeekeeperApi(AbstractAsyncApi):
    endpoint = AbstractAsyncApi.endpoint

    @endpoint
    async def close(self, *, token: str, wallet_name: str) -> CloseResponse:
        """Closing implicitly locks the wallet"""

    @endpoint
    async def close_session(self, *, token: str) -> CloseSessionResponse:
        """In case when all sessions are closed, the beekeeper is closed as well"""

    @endpoint
    async def create(
        self,
        *,
        token: str,
        wallet_name: str,
        is_temporary: Optional[bool] = None,
        password: Optional[str] = None
    ) -> CreateResponse:
        """A new wallet is created in file dir/{wallet_name}.wallet. The new wallet is unlocked after creation and is implictly opened"""

    @endpoint
    async def create_session(
        self,
        *,
        notifications_endpoint: Optional[str] = None,
        salt: Optional[str] = None
    ) -> CreateSessionResponse:
        """An unique token is generated. The token represents current session."""

    @endpoint
    async def decrypt_data(
        self,
        *,
        encrypted_content: str,
        from_public_key: str,
        to_public_key: str,
        token: str,
        wallet_name: str
    ) -> DecryptDataResponse:
        """Decrypt given content. Using creator's and receivers's public keys, content is decrypted. Private keys must exist in given wallet"""

    @endpoint
    async def encrypt_data(
        self,
        *,
        content: str,
        from_public_key: str,
        to_public_key: str,
        token: str,
        wallet_name: str,
        nonce: Optional[int] = None
    ) -> EncryptDataResponse:
        """Encrypt given content. Using creator's and receivers's public keys, content is encrypted"""

    @endpoint
    async def get_info(self, *, token: str) -> GetInfoResponse:
        """Get current and timeout time connected with current session"""

    @endpoint
    async def get_public_keys(
        self, *, token: str, wallet_name: Optional[str] = None
    ) -> list[GetPublicKeysResponseItem]:
        """List all public keys from one wallet if a wallet_name is given otherwise all public keys from all unlocked wallets."""

    @endpoint
    async def get_version(self) -> GetVersionResponse:
        """Get current version. The version is based on git hash."""

    @endpoint
    async def has_matching_private_key(
        self, *, public_key: str, token: str, wallet_name: str
    ) -> HasMatchingPrivateKeyResponse:
        """Tests if a private key corresponding to a public key exists in a wallet"""

    @endpoint
    async def has_wallet(self, *, token: str, wallet_name: str) -> HasWalletResponse:
        """Tests if a wallet exists"""

    @endpoint
    async def import_key(
        self, *, token: str, wallet_name: str, wif_key: str
    ) -> ImportKeyResponse:
        """Import a private key into specified wallet"""

    @endpoint
    async def import_keys(
        self, *, token: str, wallet_name: str, wif_keys: List[str]
    ) -> list[str]:
        """Import private keys into specified wallet"""

    @endpoint
    async def is_wallet_unlocked(
        self, *, token: str, wallet_name: str
    ) -> IsWalletUnlockedResponse:
        """Display information if given wallet is locked or not"""

    @endpoint
    async def list_created_wallets(
        self, *, token: str
    ) -> list[ListCreatedWalletsResponseItem]:
        """List all created wallets stored physically in a directory pointed by the beekeeper. It doesn't matter if these wallets are opened/unlocked"""

    @endpoint
    async def list_wallets(self, *, token: str) -> list[ListWalletsResponseItem]:
        """List all opened wallets with information if given wallet is locked or not"""

    @endpoint
    async def lock(self, *, token: str, wallet_name: str) -> LockResponse:
        """A wallet is locked and it is not possible to execute any operations related to the wallet. Signing a transaction is blocked"""

    @endpoint
    async def lock_all(self, *, token: str) -> LockAllResponse:
        """All unlocked wallets are locked and implicitly closed"""

    @endpoint
    async def open(self, *, token: str, wallet_name: str) -> OpenResponse:
        """Open an existing wallet. Opening does not unlock the wallet"""

    @endpoint
    async def remove_key(
        self, *, public_key: str, token: str, wallet_name: str
    ) -> RemoveKeyResponse:
        """Remove a private key. Important! It is highly recommended to backup the key earlier. This operation can be reverted."""

    @endpoint
    async def set_timeout(self, *, seconds: int, token: str) -> SetTimeoutResponse:
        """Set a timeout in order to lock all wallets when time passes"""

    @endpoint
    async def sign_digest(
        self,
        *,
        public_key: str,
        sig_digest: str,
        token: str,
        wallet_name: Optional[str] = None
    ) -> SignDigestResponse:
        """Sign a transaction presented as a sig_digest using a private key corresponding to a public key"""

    @endpoint
    async def unlock(
        self, *, password: str, token: str, wallet_name: str
    ) -> UnlockResponse:
        """A wallet is unlocked and it is possible to execute some operations related to the wallet including a transaction signing. Unlocking implicitly opens the wallet"""
