from __future__ import annotations

import argparse
import sys
import textwrap
from dataclasses import dataclass
from pathlib import Path
from typing import Any, ClassVar, Final

from loguru import logger

from schemas.dump_options.options import Option, Options, OptionValue

indent: Final[int] = 4
indent_str: Final[str] = " " * indent


@dataclass
class TypeInfo:
    type_name: str
    fields_count: int


def is_keyword(name: str) -> bool:
    return name in {"help", "version"}


class CodeCreator:
    @staticmethod
    def name(name: str) -> str:
        name_to_write = name.replace("-", "_")
        if is_keyword(name_to_write):
            name_to_write += "_"
        return name_to_write

    @staticmethod
    def default_name(name: str) -> str:
        content = "DEFAULT_" + CodeCreator.name(name)
        content = content.upper()
        return content.upper()

    @staticmethod
    def default_declaration(name: str) -> str:
        default_str = "BeekeeperDefaults." + CodeCreator.default_name(name)
        if is_keyword(name):
            default_str = f'field(name="{name}", default={default_str})'
        return default_str

    @staticmethod
    def custom_type(name: str) -> str:
        content = ""
        words = name.split("-")
        for word in words:
            content += word[0:1].upper() + word[1 : len(word)]
        content += "Params"
        return content

    @staticmethod
    def line(content: str) -> str:
        return indent_str + content + "\n"

    @staticmethod
    def custom_types(custom_parameters_types: list[TypeInfo]) -> str:
        content = ""
        for custom_type in custom_parameters_types:
            content += f"class {custom_type.type_name}(NamedTuple):\n"
            for i in range(custom_type.fields_count):
                content += CodeCreator.line(f"field_{i}: str")

        return content

    @staticmethod
    def default_value(default_values: list[str]) -> str:
        content = ""
        for default_value in default_values:
            content += CodeCreator.line(f"{default_value}")

        return content


class JSONProcessor:
    custom_parameters_types: ClassVar[list[TypeInfo]] = []
    default_values: ClassVar[list[str]] = []

    @staticmethod
    def __search_endpoint(name: str, value: OptionValue) -> str:
        content = ""
        if "endpoint" not in name:
            if value.fields_count is not None and value.fields_count > 1:
                custom_type_name = CodeCreator.custom_type(name)
                JSONProcessor.custom_parameters_types.append(TypeInfo(custom_type_name, value.fields_count))
                content += custom_type_name
            else:
                content += "str"
        elif "ws-" in name:
            content += "WsUrl"
        elif "http" in name:
            content += "HttpUrl"
        else:
            content += "P2PUrl"
        return content

    @staticmethod
    def __find_type(name: str, value: OptionValue) -> str:
        current_type = ""
        match value.value_type:
            case "path":
                current_type = "Path"
            case "string":
                current_type = JSONProcessor.__search_endpoint(name, value)
            case "ulong":
                current_type = "int"
            case "uint":
                current_type = "int"
            case "bool":
                current_type = "bool"
            case "string_array":
                current_type = "list[" + JSONProcessor.__search_endpoint(name, value) + "]"
            case _:
                current_type = "str"
        return current_type

    @staticmethod
    def __read_path(path_default_value: Any) -> str:
        content = ""
        if str(path_default_value)[0] == '"':
            content += f" = field(default_factory=lambda: Path({path_default_value}))"
        elif path_default_value == ".":
            content += " = field(default_factory=lambda: Path())"
        else:
            content += f' = field(default_factory=lambda: Path("{path_default_value}"))'
        return content

    @staticmethod
    def __prepare_string_value(value: str) -> str:
        if '"' in value:
            return f'"""{value}"""'
        return f'"{value}"'

    @staticmethod
    def __read_value(name: str, value: OptionValue) -> tuple[str, str]:
        current_type = JSONProcessor.__find_type(name, value)

        none_is_allowed = len(str(value.default_value)) == 0 and not value.required

        content_type = f": {current_type}" + (" | None" if none_is_allowed else "") + " = "
        content_type_default = f": ClassVar[{current_type}" + (" | None] = None" if none_is_allowed else "]")
        content = ""

        if not none_is_allowed:
            if isinstance(value.default_value, list):
                if len(value.default_value) > 0:
                    content += (
                        " = ["
                        + ", ".join([JSONProcessor.__prepare_string_value(item) for item in value.default_value])
                        + "]"
                    )
                else:
                    content += " = []"
            elif current_type == "str" and isinstance(value.default_value, str):
                content += f" = {JSONProcessor.__prepare_string_value(value.default_value)}"
            elif current_type == "Path":
                content += JSONProcessor.__read_path(value.default_value)
            elif current_type == "bool":
                content += " = " + ("True" if value.default_value == "true" else "False")
            else:
                content += f" = {value.default_value}"

        return content_type + CodeCreator.default_declaration(name), content_type_default + content

    @staticmethod
    def __prepare_description(description: str) -> str:
        return (
            indent_str
            + '"""\n'
            + f"\n{indent_str}".join(
                textwrap.wrap(
                    description.strip(),
                    width=120,
                    initial_indent=indent_str,
                    subsequent_indent=indent_str,
                )
            )
            + f'\n{indent_str}"""\n\n'
        )

    @staticmethod
    def __read_option(option: Option) -> str:
        content = ""
        value = option.value or OptionValue(
            required=True,
            multitoken=False,
            composed=False,
            value_type="bool",
            default_value="False",
            fields_count=None,
        )

        values = JSONProcessor.__read_value(option.name, value)
        values_size = 2
        assert len(values) == values_size

        declaration = CodeCreator.name(option.name) + values[0]
        JSONProcessor.default_values.append(CodeCreator.default_name(option.name) + values[1])

        content += CodeCreator.line(declaration)

        content += JSONProcessor.__prepare_description(option.description)

        return content

    @staticmethod
    def __read_options(options: list[Option] | None) -> str:
        content = ""

        if options is not None and len(options) > 0:
            content += "\n"
            for option in options:
                content += JSONProcessor.__read_option(option)

        return content

    @staticmethod
    def __write_file(content: str, file_name: str) -> None:
        marker = "{GENERATED-ITEMS}"

        src_path_file = f"{file_name}.in"
        dst_path_file = f"../beekeepy/beekeepy/_executable/{file_name}.py"

        src_file_content = Path(src_path_file).read_text()
        src_file_content = src_file_content.replace(marker, content).strip("\n \t")

        Path(dst_path_file).write_text(src_file_content + "\n")

    @staticmethod
    def update_options(options_file: str) -> None:
        opts = Options.parse_file(Path(options_file))

        content_common = JSONProcessor.__read_options(opts.common)
        content_config_file = JSONProcessor.__read_options(opts.config_file)
        content_command_line = JSONProcessor.__read_options(opts.command_line)
        content_custom_types = CodeCreator.custom_types(JSONProcessor.custom_parameters_types)
        content_default_values = CodeCreator.default_value(JSONProcessor.default_values)

        JSONProcessor.__write_file(content_common, "beekeeper_common")
        JSONProcessor.__write_file(content_config_file, "beekeeper_config")
        JSONProcessor.__write_file(content_command_line, "beekeeper_arguments")
        JSONProcessor.__write_file(content_custom_types, "custom_parameters_types")
        JSONProcessor.__write_file(content_default_values, "beekeeper_defaults")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate CLI and CONFIG parameters.")
    parser.add_argument(
        "--options-file",
        required=True,
        type=str,
        default="",
        help="JSON file that contains options retrieved from hived by `--dump-options`",
    )
    args = parser.parse_args()

    if len(args.options_file) == 0:
        logger.error("JSON file is required. Aborting.")
        sys.exit(-1)

    JSONProcessor.update_options(args.options_file)
