from __future__ import annotations

from pathlib import Path
from types import UnionType
from typing import TYPE_CHECKING, Any, ClassVar, get_args

from pydantic import BaseModel

from helpy._interfaces.url import Url
from helpy.exceptions import InvalidOptionError

if TYPE_CHECKING:
    from typing_extensions import Self


class Config(BaseModel):
    DEFAULT_FILE_NAME: ClassVar[str] = "config.ini"

    class Config:
        arbitrary_types_allowed = True

    def save(self, destination: Path) -> None:
        destination = destination / Config.DEFAULT_FILE_NAME if destination.is_dir() else destination
        with destination.open("wt", encoding="utf-8") as out_file:
            out_file.write("# config automatically generated by helpy\n")
            for member_name, member_value in self.__dict__.items():
                if member_value is not None:
                    if isinstance(member_value, list) and len(member_value) == 0:
                        continue
                    entry_name = self._convert_member_name_to_config_name(member_name)
                    entry_value = self._convert_member_value_to_config_value(member_name, member_value)
                    out_file.write(f"{entry_name}={entry_value}\n")

    @classmethod
    def load(cls, source: Path) -> Self:
        source = source / Config.DEFAULT_FILE_NAME if source.is_dir() else source
        assert source.exists(), "Given file does not exists."
        fields = cls.__fields__
        values_to_write = {}
        with source.open("rt", encoding="utf-8") as in_file:
            for line in in_file:
                if (line := line.strip("\n")) and not line.startswith("#"):
                    config_name, config_value = line.split("=")
                    member_name = cls._convert_config_name_to_member_name(config_name)
                    member_type = fields[member_name].annotation
                    if isinstance(member_type, UnionType) and get_args(member_type)[-1] == type(None):
                        member_type = get_args(member_type)[0]
                    values_to_write[member_name] = cls._convert_config_value_to_member_value(
                        config_value, expected=member_type
                    )
        return cls(**values_to_write)

    @classmethod
    def _convert_member_name_to_config_name(cls, member_name: str) -> str:
        return member_name.replace("_", "-")

    @classmethod
    def _convert_config_name_to_member_name(cls, config_name: str) -> str:
        return config_name.strip().replace("-", "_")

    @classmethod
    def _convert_member_value_to_config_value(cls, member_name: str, member_value: Any) -> str:  # noqa: ARG003
        if isinstance(member_value, list):
            return " ".join(member_value)

        if isinstance(member_value, bool):
            return "yes" if member_value else "no"

        if isinstance(member_value, Url):
            return member_value.as_string(with_protocol=False)

        if isinstance(member_value, Path):
            return member_value.as_posix()

        return str(member_value)

    @classmethod
    def _convert_config_value_to_member_value(  # noqa: PLR0911
        cls, config_value: str, *, expected: type[Any]
    ) -> Any | None:
        config_value = config_value.strip()
        if config_value is None:
            return None

        if expected == Path:
            return Path(config_value.replace('"', ""))

        if expected == list[str]:
            return config_value.split()

        if expected == Url:
            return Url(config_value)

        if expected == bool:
            cv_lower = config_value.lower()
            if cv_lower == "yes":
                return True

            if cv_lower == "no":
                return False

            raise InvalidOptionError(f"Expected `yes` or `no`, got: `{config_value}`")

        if "str" in str(expected):
            return config_value.strip('"')

        return expected(config_value) if expected is not None else None
