from __future__ import annotations

import argparse
import json
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any, ClassVar

from loguru import logger

from schemas.dump_options.options import Option, Options, OptionValue

indent = 4


@dataclass
class TypeInfo:
    type_name: str
    fields_count: int


class CodeCreator:
    @staticmethod
    def name(name: str) -> str:
        return name.replace("-", "_")

    @staticmethod
    def default_name(name: str) -> str:
        content = "DEFAULT_" + CodeCreator.name(name)
        content = content.upper()
        return content.upper()

    @staticmethod
    def default_declaration(name: str) -> str:
        return "BeekeeperDefaults." + CodeCreator.default_name(name)

    @staticmethod
    def custom_type(name: str) -> str:
        content = ""
        words = name.split("-")
        for word in words:
            content += word[0:1].upper() + word[1 : len(word)]
        content += "Params"
        return content

    @staticmethod
    def line(content: str, *, last: bool) -> str:
        return "".join([" " for _ in range(indent)]) + content + ("" if last else "\n")

    @staticmethod
    def custom_types(custom_parameters_types: list[TypeInfo]) -> str:
        content = ""
        for custom_type in custom_parameters_types:
            content += f"class {custom_type.type_name}(NamedTuple):\n"
            for i in range(custom_type.fields_count):
                content += CodeCreator.line(f"field_{i}: str", last=i == custom_type.fields_count - 1)

        return content

    @staticmethod
    def default_value(default_values: list[str]) -> str:
        content = ""
        for cnt, default_value in enumerate(default_values):
            content += CodeCreator.line(f"{default_value}", last=cnt == len(default_values) - 1)

        return content


class JSONProcessor:
    custom_parameters_types: ClassVar[list[TypeInfo]] = []
    default_values: ClassVar[list[str]] = []

    @staticmethod
    def __search_endpoint(name: str, value: OptionValue) -> str:
        content = ""
        if name.find("endpoint") == -1:
            if value.fields_count is not None and value.fields_count > 1:
                custom_type_name = CodeCreator.custom_type(name)
                JSONProcessor.custom_parameters_types.append(TypeInfo(custom_type_name, value.fields_count))
                content += custom_type_name
            else:
                content += "str"
        else:
            content += "HttpUrl" if name.find("ws-endpoint") == -1 else "WsUrl"
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
            content += f" = Field(default_factory=lambda: Path({path_default_value}))"
        elif path_default_value == ".":
            content += " = Field(default_factory=lambda: Path())"
        else:
            content += f' = Field(default_factory=lambda: Path("{path_default_value}"))'
        return content

    @staticmethod
    def __read_value(name: str, value: OptionValue) -> tuple[str, str]:
        current_type = JSONProcessor.__find_type(name, value)

        none_is_allowed = len(str(value.default_value)) == 0 and not value.required

        content_type = f": {current_type}{' | None' if none_is_allowed else ''} = "
        content_type_default = f": ClassVar[{current_type}{' | None] = None' if none_is_allowed else ']'}"
        content = ""

        if not none_is_allowed:
            if isinstance(value.default_value, list):
                if len(value.default_value) > 0:
                    for item in value.default_value:
                        content += f' = "{item}"'
                else:
                    content += " = []"
            elif current_type == "str":
                content += f' = "{value.default_value}"'
            elif current_type == "Path":
                content += JSONProcessor.__read_path(value.default_value)
            elif current_type == "bool":
                content += f' = {"True" if value.default_value == "true" else "False"}'
            else:
                content += f" = {value.default_value}"

        return content_type + CodeCreator.default_declaration(name), content_type_default + content

    @staticmethod
    def __prepare_description(description: str, *, last: bool) -> str:
        content = ""
        words = description.split(" ")
        limit = 120
        line = ""
        first = True
        was_split = False
        one_space_and_quotes = 4
        for word in words:
            if len(line) + len(word) + one_space_and_quotes + indent < limit:
                line += ("" if first else " ") + word
            else:
                content += line + "\n"
                line = ""
                was_split = True
            first = False

        content += line

        if was_split:
            content = CodeCreator.line(f'"""{content}', last=False)
            content += CodeCreator.line('"""', last=last)
        else:
            content = CodeCreator.line(f'"""{content}"""', last=last)
        return content

    @staticmethod
    def __read_option(option: Option, *, last: bool) -> str:
        content = ""
        tmp_value = None
        if option.value is not None:
            tmp_value = option.value
        else:
            tmp_value = OptionValue(
                required=True,
                multitoken=False,
                composed=False,
                value_type="bool",
                default_value="False",
                fields_count=None,
            )

        values = JSONProcessor.__read_value(option.name, tmp_value)
        values_size = 2
        assert len(values) == values_size

        declaration = CodeCreator.name(option.name) + values[0]
        JSONProcessor.default_values.append(CodeCreator.default_name(option.name) + values[1])

        content += CodeCreator.line(declaration, last=False)

        content += JSONProcessor.__prepare_description(option.description, last=last)

        if not last:
            content += "\n"

        return content

    @staticmethod
    def __read_options(options: list[Option] | None) -> str:
        content = ""

        if options is not None and len(options) > 0:
            content += "\n"
            for cnt, option in enumerate(options):
                content += JSONProcessor.__read_option(option, last=(cnt + 1) == len(options))

        return content

    @staticmethod
    def __write_file(content: str, file_name: str) -> None:
        marker = "{GENERATED-ITEMS}"

        src_path_file = f"{file_name}.in"
        dst_path_file = f"../beekeepy/beekeepy/_executable/{file_name}.py"

        with Path(src_path_file).open("r") as src_file:
            src_file_content = src_file.read()

            with Path(dst_path_file).open("w") as dst_file:
                src_file_content = src_file_content.replace(marker, content)

                # When is lack of parameters, remove last empty line otherwise ruff fails.
                if len(content) == 0 and len(src_file_content) > 0:
                    src_file_content = src_file_content[0 : len(src_file_content) - 1]

                dst_file.write(src_file_content)
                dst_file.close()

    @staticmethod
    def update_options(options_file: Path) -> None:
        with Path(options_file).open("r") as json_file:
            opts = Options(**json.load(json_file))

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
