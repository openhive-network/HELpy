from __future__ import annotations


class HiveTransferProtocolError(Exception):
    """Base class for all Hive Transfer Protocol Errors."""


class ParseError(HiveTransferProtocolError):
    """Raised if cannot parse given str, e.x. url, date, asset."""
