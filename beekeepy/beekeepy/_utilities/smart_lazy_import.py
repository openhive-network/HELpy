"""
Rozwiązanie dla lazy importów z automatycznym wykrywaniem struktury modułów.

Wymaga tylko nazwy atrybutu i referencji na aktualny moduł.

Użycie:
```python
    import sys

    def __getattr__(name: str) -> Any:
        return smart_lazy_getattr(name, sys.modules[__name__])
```
"""

from __future__ import annotations

import importlib
from typing import TYPE_CHECKING, Any, Callable

if TYPE_CHECKING:
    from types import ModuleType

__all__ = [
    "smart_lazy_getattr",
    "lazy_module_factory",
    "aggregate_same_import",
]


ModuleInterfaceMapping = dict[str, str]
ModuleInterface = list[str]
GetattrProtocol = Callable[[str], Any]
AliasMapping = dict[str, str]


def smart_lazy_getattr(
    name: str, current_module: ModuleType, name_module_translation: ModuleInterfaceMapping, aliases: AliasMapping
) -> Any:
    """
    Intelligent lazy loading with automatic module detection.

    Args:
        name: Name of the attribute to import
        current_module: Reference to the current module (sys.modules[__name__])
        aliases: Mapping of alias names to target names

    Returns:
        Imported attribute

    Raises:
        AttributeError: If the attribute was not found

    Example:
    ```python
    # In __init__.py
    import sys

    def __getattr__(name: str) -> Any:
        return smart_lazy_getattr(name, sys.modules[__name__])
    ```
    """
    if name in ("__path__", "__file__"):
        return current_module.__file__

    if name not in name_module_translation:
        if name in aliases:
            name = aliases[name]
        else:
            raise ImportError(f"Module '{current_module.__name__}' has no attribute '{name}'")

    return importlib.import_module(name_module_translation[name]).__getattribute__(name)


def lazy_module_factory(
    current_module: ModuleType,
    type_checking_all: ModuleInterface,
    /,
    aliases: AliasMapping | None = None,
    **translations: str,
) -> GetattrProtocol:
    """
    Factory function for creating __getattr__ with lazy loading.

    Args:
        current_module: Reference to the current module (sys.modules[__name__])
        type_checking_all: List of all attribute names for TYPE_CHECKING validation
        aliases: Optional mapping of alias names to target names
        **translations: Mapping of attribute names to their respective modules
    Usage:
    ```python
    import sys

    __getattr__, __all__ = create_smart_getattr(
        sys.modules[__name__],

        # Translations
        Beekeeper="beekeepy._interface.abc.synchronous",
        Session="beekeepy._interface.abc.synchronous",
        Settings="beekeepy._interface.settings",
        aliases={ # alias_name -> target
            "AsyncBeekeeper": "Beekeeper",  # Alias example
        },
    )
    ```
    """
    aliases = aliases or {}
    _validate_all_in_translations(type_checking_all, translations, aliases)

    def new_getattr(name: str) -> Any:
        return smart_lazy_getattr(name, current_module, translations, aliases)

    return new_getattr


def aggregate_same_import(*attributes: str, module: str) -> ModuleInterfaceMapping:
    """
    Helper function to aggregate multiple attributes from the same module.

    Args:
        module: Module path
        *attributes: Attribute names to import from the module

    Returns:
        A mapping of attribute names to their module paths
    """
    return {attr: module for attr in attributes}


def _validate_all_in_translations(
    all_names: ModuleInterface, translations: ModuleInterfaceMapping, aliases: AliasMapping
) -> None:
    missing = set(all_names) - (set(translations.keys()) | set(aliases.keys()))
    if missing:
        raise ImportError(f"Missing translations for: {', '.join(missing)}")
