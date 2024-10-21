from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING, Any

from pydantic import Field

from beekeepy._executable.custom_parameters_types import ExportKeysWalletParams
from helpy import HttpUrl
from schemas._preconfigured_base_model import PreconfiguredBaseModel

if TYPE_CHECKING:
    from typing_extensions import Self


class Arguments(PreconfiguredBaseModel):
    help_: bool = Field(alias="help", default=False)
    version: bool = False
    dump_config: bool = False

    def __convert_member_name_to_cli_value(self, member_name: str) -> str:
        return member_name.replace("_", "-")

    def __convert_member_value_to_string(self, name: str, member_value: int | str | Path | Any) -> list[str]:
        response = []
        if isinstance(member_value, list):
            temp_response = []
            for item in member_value:
                temp_response.extend(self.__convert_member_value_to_string(name, item))
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
        elif isinstance(member_value, ExportKeysWalletParams):
            response = [name, f'["{member_value[0]}","{member_value[1]}"]']
        else:
            raise TypeError("Invalid type")

        return response

    def __prepare_arguments(self, pattern: str) -> list[str]:
        data = self.dict(by_alias=True, exclude_none=True, exclude_unset=True, exclude_defaults=True)
        cli_arguments: list[str] = []
        for k, v in data.items():
            name = pattern.format(self.__convert_member_name_to_cli_value(k))
            cli_arguments.extend(self.__convert_member_value_to_string(name, v))
        return cli_arguments

    def process(self, *, with_prefix: bool = True) -> list[str]:
        pattern = self._generate_argument_prefix(with_prefix=with_prefix)
        return self.__prepare_arguments(pattern)

    def _generate_argument_prefix(self, *, with_prefix: bool) -> str:
        return "--{0}" if with_prefix else "{0}"

    def update_with(self, other: Self | None) -> None:
        if other is None:
            return

        for other_name, other_value in other.dict(exclude_unset=True, exclude_defaults=True, exclude_none=True).items():
            assert isinstance(other_name, str), "Member name has to be string"
            setattr(self, other_name, other_value)

    @classmethod
    def just_get_help(cls) -> Self:
        return cls(help_=True)

    @classmethod
    def just_get_version(cls) -> Self:
        return cls(version=True)

    @classmethod
    def just_dump_config(cls) -> Self:
        return cls(dump_config=True)
