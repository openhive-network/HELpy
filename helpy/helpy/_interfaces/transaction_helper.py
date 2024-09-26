from __future__ import annotations

from datetime import datetime, timedelta
from typing import TYPE_CHECKING, cast

from helpy._interfaces.wax import calculate_sig_digest, calculate_tapos_data
from schemas.fields.hive_datetime import HiveDateTime
from schemas.fields.hive_int import HiveInt
from schemas.operations.representations import HF26Representation
from schemas.transaction import Transaction as SchemasTransaction

if TYPE_CHECKING:
    from typing_extensions import Self

    from schemas.operations import AnyOperation


class Transaction(SchemasTransaction):
    def get_sig_digest(self, chain_id: str) -> str:
        """
        Calculates signature digest (sig_digest) for any chain basing on chain_id.

        Note:
            This digest is used as data to sign with private key and such signature should be appended to signatures member

        Args:
            chain_id: chain id of chain for which signature is calculated

        Returns:
            str: signature digest
        """  # noqa: E501
        return calculate_sig_digest(transaction=self, chain_id=chain_id)

    def recalculate_tapos(self, block_id: str) -> None:
        """
        Recalculates tapos basing on given block_id.

        Example:
            ```
            dgpo = node.api.database_api.get_dynamic_global_properties()
            transaction.recalculate_tapos(dgpo.head_block_id)
            ```

            or

            ```
            block = node.api.block_api.get_block(block_num=2137)
            transaction.recalculate_tapos(block.block.block_id)
            ```

        Args:
            block_id: Block id used for tapos calculation
        """
        tapos = calculate_tapos_data(block_id=block_id)
        self.ref_block_num = HiveInt(tapos.ref_block_num)
        self.ref_block_prefix = HiveInt(tapos.ref_block_prefix)

    def set_expiration(self, block_time: datetime, *, extra_time: timedelta = timedelta(minutes=30)) -> None:
        """
        Sets expiration basing on given block_time.

        Example:
            ```
            dgpo = node.api.database_api.get_dynamic_global_properties()
            transaction.set_expiration(dgpo.time)
            ```

        Args:
            block_time: time of block for reference (but can be any time).
            extra_time: length of expiration. Current default is maximum expiration time measuring from current
                        head block number.
        """
        self.expiration = cast(HiveDateTime, block_time + extra_time)

    def add_operation(self, operation: AnyOperation) -> None:
        """
        Adds operation to operations member with `Hf26Representation` wrapper.

        Example:
            operation = transaction.operations[0].value

        Args:
            operation: operation to add to operations member with proper wrapper.
        """
        self.operations.append(HF26Representation(type=operation.get_name_with_suffix(), value=operation))

    @classmethod
    def defaults(cls, block_id: str | None = None) -> Self:
        """
        Creates empty transaction object with default values.

        Args:
            block_id: If given, tapos is automatically calculated.

        Returns:
            TransactionHelper: Empty transaction.
        """
        trx = cls(
            ref_block_num=HiveInt(0),
            ref_block_prefix=HiveInt(0),
            expiration=HiveDateTime.now(),
            extensions=[],
            signatures=[],
            operations=[],
        )

        if block_id is not None:
            trx.recalculate_tapos(block_id=block_id)

        return trx
