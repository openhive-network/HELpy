from __future__ import annotations


class HelpyError(Exception):
    """Base class for all helpy Errors."""


class ParseError(HelpyError):
    """Raised if cannot parse given str, e.x. url, date, asset."""


class BlockWaitTimeoutError(HelpyError):
    """Raised if reached not expected block number."""

    def __init__(
        self,
        last_block_number: int,
        block_number: int,
        last_irreversible_block_number: int,
    ) -> None:
        """Creates exception.

        Args:
            last_block_number: last fetched block number
            block_number: block that was expected to be irreversible
            last_irreversible_block_number: last fetched irreversible block number
        """
        super().__init__(
            f"Block with number `{last_block_number}` was just reached but expected `{block_number}` is still not"
            " irreversible.\n"
            f"Last irreversible block number is `{last_irreversible_block_number}`."
        )
