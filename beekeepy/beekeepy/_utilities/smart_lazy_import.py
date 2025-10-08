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
from typing import Any, Callable, get_args

__all__ = [
    "smart_lazy_getattr",
    "lazy_module_factory",
    "aggregate_same_import",
]


ModuleComponent = str
ModulePath = str
Alias = str

ImportInput = tuple[ModulePath, ModuleComponent]
AliasedImportInput = tuple[ModulePath, ModuleComponent, Alias]
AggregatedAliasedImportInput = tuple[ModuleComponent, Alias]

ModuleInterfaceMappingInput = ImportInput | AliasedImportInput
AggregatedModuleInterfaceMappingInput = ModuleComponent | AggregatedAliasedImportInput

ModuleInterfaceMapping = dict[ModuleComponent, ModulePath]
AliasMapping = dict[Alias, ModuleComponent]

ModuleGlobals = dict[str, Any]
GetattrProtocol = Callable[[str], Any]


def smart_lazy_getattr(
    name: str, module_globals: ModuleGlobals, name_module_translation: ModuleInterfaceMapping, aliases: AliasMapping
) -> Any:
    """
    Intelligent lazy loading with automatic module detection.

    Args:
        name: Name of the attribute to import
        module_globals: Reference to the current module (use: `globals()`)
        aliases: Mapping of alias names to target names

    Returns:
        Imported attribute

    Raises:
        AttributeError: If the attribute was not found
    """
    if name in ("__path__", "__file__", "__all__", "__name__"):
        if name == "__path__":
            name = "__file__"
        return module_globals[name]

    if name not in name_module_translation:
        if name in aliases:
            name = aliases[name]
        else:
            raise ImportError(f"Module '{module_globals['__name__']}' has no attribute '{name}'")

    return importlib.import_module(name_module_translation[name]).__getattribute__(name)


def lazy_module_factory(
    module_globals: ModuleGlobals, /, *translations: ModuleInterfaceMappingInput
) -> GetattrProtocol:
    """
    Factory function for creating __getattr__ with lazy loading.

    Args:
        module_globals: Reference to the current module (pass `globals()`)
        *translations: Mapping of attribute names to their respective modules
    Usage:
    ```python
    import sys

    __getattr__ = create_smart_getattr(
        globals(),

        # Translations
        # ("module.path", "AttributeName"),
        ("beekeepy._interface.abc.synchronous", "Session"),
        ("beekeepy._interface.settings", "Settings")

        # Aliasing
        # ("module.path", "AttributeName", "AliasName"),
        ("beekeepy._interface.abc.synchronous", "Beekeeper", "AsyncBeekeeper"),
    )
    ```
    """
    translations_no_alias, aliases = _extract_aliases(translations)
    _validate_all_in_translations(module_globals, translations_no_alias, aliases)

    def new_getattr(name: str) -> Any:
        return smart_lazy_getattr(name, module_globals, translations_no_alias, aliases)

    return new_getattr


def aggregate_same_import(
    *attributes: AggregatedModuleInterfaceMappingInput, module: ModulePath
) -> tuple[ModuleInterfaceMappingInput, ...]:
    """
    Helper function to aggregate multiple attributes from the same module.

    Args:
        module: Module path
        *attributes: Attribute names to import from the module

    Returns:
        A mapping of attribute names to their module paths
    """
    result: list[ModuleInterfaceMappingInput] = []
    for attribute in attributes:
        if isinstance(attribute, str):
            result.append((module, attribute))
        else:
            result.append((module, *attribute))
    return tuple(result)


def _validate_all_in_translations(
    module_globals: ModuleGlobals, translations: ModuleInterfaceMapping, aliases: AliasMapping
) -> None:
    missing = set(module_globals["__all__"]) - (set(translations.keys()) | set(aliases.keys()))
    if missing:
        raise ImportError(f"Missing translations for: {', '.join(missing)}")


def _extract_aliases(
    translation: tuple[ModuleInterfaceMappingInput, ...],
) -> tuple[ModuleInterfaceMapping, AliasMapping]:
    translations: ModuleInterfaceMapping = {}
    aliases: AliasMapping = {}

    for item in translation:
        if len(item) == len(get_args(ImportInput)):  # simple import
            translations[item[1]] = item[0]
        elif len(item) == len(get_args(AliasedImportInput)):  # aliased import
            translations[item[1]] = item[0]
            aliases[item[2]] = item[1]  # type: ignore[misc]
        else:
            raise ImportError(f"Invalid input during lazy import definition: {item}")

    return translations, aliases
