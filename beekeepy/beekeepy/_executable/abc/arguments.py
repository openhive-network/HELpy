from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING, Any, TypeGuard

from beekeepy._communication import HttpUrl
from beekeepy._utilities.cli_parser import CliParser
from schemas._preconfigured_base_model import PreconfiguredBaseModel

if TYPE_CHECKING:
    from typing_extensions import Self


__all__ = ["Arguments"]


class Arguments:
    if TYPE_CHECKING:

        def __init__(self, *args: Any, **kwargs: Any) -> None:
            super().__init__(*args, **kwargs)

    @staticmethod
    def __validate_is_preconfigured_base_model(self_: Any) -> TypeGuard[PreconfiguredBaseModel]:
        assert isinstance(
            self_, PreconfiguredBaseModel
        ), "This is (phantom) abstract class, it should be composited with one that is PreconfiguredBaseModel"
        return True

    @staticmethod
    def __validate_is_self(self_: Any) -> TypeGuard[Arguments]:
        assert isinstance(
            self_, Arguments
        ), "This is (phantom) abstract class, it should be composited with one that is PreconfiguredBaseModel"
        return True

    def _convert_member_value_to_string(self, name: str, member_value: int | str | Path | Any) -> list[str]:
        response = []
        if isinstance(member_value, list):
            temp_response = []
            for item in member_value:
                temp_response.extend(self._convert_member_value_to_string(name, item))
            response = temp_response
        elif isinstance(member_value, bool):
            response = [name, ""]
        elif isinstance(member_value, str):
            response = [name, member_value]
        elif isinstance(member_value, int):
            response = [name, str(member_value)]
        elif isinstance(member_value, Path):
            response = [name, member_value.as_posix()]
        elif isinstance(member_value, HttpUrl):
            response = [name, member_value.as_string(with_protocol=False)]
        else:
            raise TypeError("Invalid type")

        return response

    def __convert_member_name_to_cli_value(self, member_name: str) -> str:
        return member_name.strip("_").replace("_", "-")

    def __prepare_arguments(self, pattern: str) -> list[str]:
        assert Arguments.__validate_is_preconfigured_base_model(self)

        data = self.dict(exclude_none=True, exclude_defaults=True)
        cli_arguments: list[str] = []

        assert Arguments.__validate_is_self(self)
        for k, v in data.items():
            if v is not None and v is not False:
                name = pattern.format(self.__convert_member_name_to_cli_value(k))
                cli_arguments.extend(self._convert_member_value_to_string(name, v))
        return cli_arguments

    def process(self, *, with_prefix: bool = True) -> list[str]:
        pattern = self._generate_argument_prefix(with_prefix=with_prefix)
        return self.__prepare_arguments(pattern)

    def _generate_argument_prefix(self, *, with_prefix: bool) -> str:
        return "--{0}" if with_prefix else "{0}"

    def update_with(self, other: Self | None) -> None:
        if other is None:
            return

        assert Arguments.__validate_is_preconfigured_base_model(self)
        assert Arguments.__validate_is_preconfigured_base_model(other)

        for other_name, other_value in other.dict(exclude_defaults=True, exclude_none=True).items():
            assert isinstance(other_name, str), "Member name has to be string"
            setattr(self, other_name, other_value)

    @classmethod
    def parse_cli_input(cls, cli: list[str]) -> Self:
        return cls(**CliParser.parse_cli_input(cli))

    @classmethod
    def just_get_help(cls) -> Self:
        return cls(help_=True)

    @classmethod
    def just_get_version(cls) -> Self:
        return cls(version_=True)

    @classmethod
    def just_dump_config(cls) -> Self:
        return cls(dump_config=True)
