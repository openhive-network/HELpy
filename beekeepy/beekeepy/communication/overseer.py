from __future__ import annotations

from typing import TYPE_CHECKING

__all__ = [
    "rules",
    "AbstractOverseer",
    "CommonOverseer",
    "StrictOverseer",
]

if TYPE_CHECKING:
    from beekeepy._communication import rules
    from beekeepy._communication.abc.overseer import AbstractOverseer
    from beekeepy._communication.overseers import CommonOverseer, StrictOverseer
else:
    from sys import modules

    from beekeepy._utilities.smart_lazy_import import aggregate_same_import, lazy_module_factory

    __getattr__ = lazy_module_factory(
        modules[__name__],
        __all__,
        # Translations
        **aggregate_same_import(
            "CommonOverseer",
            "StrictOverseer",
            module="beekeepy._communication.overseers",
        ),
        rules="beekeepy._communication",
        AbstractOverseer="beekeepy._communication.abc.overseer",
    )
