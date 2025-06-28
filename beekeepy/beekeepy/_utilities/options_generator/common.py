from __future__ import annotations

from dataclasses import dataclass
from typing import Final

indent: Final[int] = 4
indent_str: Final[str] = " " * indent


@dataclass
class TypeInfo:
    type_name: str
    fields_count: int


def is_keyword(name: str) -> bool:
    return name in {"help", "version"}
