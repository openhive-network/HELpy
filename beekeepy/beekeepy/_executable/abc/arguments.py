from __future__ import annotations

from abc import abstractmethod
from pathlib import Path
from typing import TYPE_CHECKING, Any

from msgspec import field

from schemas._preconfigured_base_model import PreconfiguredBaseModel

if TYPE_CHECKING:
    from typing_extensions import Self


__all__ = ["Arguments"]


class CliParser:
    @classmethod
    def parse_cli_input(cls, cli: list[str]) -> dict[str, str | list[str] | bool]:
        ordered_cli: dict[str, str | set[str] | None] = {}
        previous_key: str | None = None
        for item in cli:
            key, value = cls._preprocess_option(item)
            if key.startswith("__"):
                previous_key = key[2:]
                ordered_cli[previous_key] = value
                continue
            if key.startswith("_"):
                previous_key = key[1:]
                ordered_cli[previous_key] = value
                continue

            if key in ordered_cli:
                if isinstance((dict_value := ordered_cli[key]), set):
                    dict_value.add(item)
                elif ordered_cli[key] is None:
                    assert isinstance(item, str), "parsing failed, item is not string"  # mypy check
                    ordered_cli[key] = item
                else:  # if ordered_cli[key] is not None and is not set
                    assert isinstance(item, str), "parsing failed, item is not string"  # mypy check
                    dict_value = ordered_cli[key]
                    assert isinstance(dict_value, str), "parsing failed, dict_value is not string"  # mypy check
                    ordered_cli[key] = {dict_value, item}
                continue

            assert (
                previous_key is not None
            ), "parsing failed, previous_key was not set and following argument is not prefixed"
            ordered_cli[previous_key] = item
            previous_key = None

        return cls._convert_sets_to_lists_and_none_to_boolean(ordered_cli)

    @classmethod
    def _convert_sets_to_lists_and_none_to_boolean(
        cls, ordered_cli: dict[str, str | set[str] | None]
    ) -> dict[str, str | list[str] | bool]:
        result: dict[str, str | list[str] | bool] = {}
        for key, value in ordered_cli.items():
            if isinstance(value, set):
                result[key] = list(value)
            elif value is None:
                result[key] = True
            else:
                result[key] = value
        return result

    @classmethod
    def _preprocess_option(cls, item: str) -> tuple[str, str | None]:
        key = item
        value = None
        if "=" in item:
            key, value = item.split("=")

        key = key.replace("-", "_")
        return key, value


class Arguments(PreconfiguredBaseModel):
    help: bool = False
    version: bool = False
    dump_config: bool = False

    class Config:
        arbitrary_types_allowed = True

    def __convert_member_name_to_cli_value(self, member_name: str) -> str:
        return member_name.replace("_", "-")

    def __convert_member_value_to_string(self, member_value: int | str | Path | Any) -> str:
        if isinstance(member_value, bool):
            return ""
        if isinstance(member_value, str):
            return member_value
        if isinstance(member_value, int):
            return str(member_value)
        if isinstance(member_value, Path):
            return member_value.as_posix()
        if isinstance(result := self._convert_member_value_to_string_default(member_value=member_value), str):
            return result
        raise TypeError("Invalid type")

    @abstractmethod
    def _convert_member_value_to_string_default(self, member_value: Any) -> str | Any: ...

    def __prepare_arguments(self, pattern: str) -> list[str]:
        data = self.dict(exclude_none=True, exclude_defaults=True)
        cli_arguments: list[str] = []
        for k, v in data.items():
            if isinstance(v, list) and len(v) == 0:
                continue
            cli_arguments.append(pattern.format(self.__convert_member_name_to_cli_value(k)))
            cli_arguments.append(self.__convert_member_value_to_string(v))
        return cli_arguments

    def process(self, *, with_prefix: bool = True) -> list[str]:
        pattern = self._generate_argument_prefix(with_prefix=with_prefix)
        return self.__prepare_arguments(pattern)

    def _generate_argument_prefix(self, *, with_prefix: bool) -> str:
        return "--{0}" if with_prefix else "{0}"

    def update_with(self, other: Self | None) -> None:
        if other is None:
            return

        for other_name, other_value in other.dict(exclude_defaults=True, exclude_none=True).items():
            assert isinstance(other_name, str), "Member name has to be string"
            setattr(self, other_name, other_value)

    @classmethod
    def parse_cli_input(cls, cli: list[str]) -> Self:
        return cls(**CliParser.parse_cli_input(cli))  # type: ignore[arg-type]

    @classmethod
    def just_get_help(cls) -> Self:
        return cls(help=True)

    @classmethod
    def just_get_version(cls) -> Self:
        return cls(version=True)

    @classmethod
    def just_dump_config(cls) -> Self:
        return cls(dump_config=True)
