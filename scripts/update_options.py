from __future__ import annotations

import argparse
import json
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from loguru import logger

from schemas.dump_options.options import Option, Options, OptionValue

indent = 4


@dataclass
class TypeInfo:
    type_name: str
    fields_count: int


custom_parameters_types = []
default_values = []


def create_name(name: str) -> str:
    return name.replace("-", "_")


def create_default_name(name: str) -> str:
    content = "DEFAULT_" + create_name(name)
    content = content.upper()
    return content.upper()


def create_default_declaration(name: str) -> str:
    return "BeekeeperDefaults." + create_default_name(name)


def create_custom_type(name: str) -> str:
    content = ""
    words = name.split("-")
    for word in words:
        content += word[0:1].upper() + word[1 : len(word)]
    content += "Params"
    return content


def create_line(content: str, *, last: bool) -> str:
    return "".join([" " for _ in range(indent)]) + content + ("" if last else "\n")


def search_endpoint(name: str, value: OptionValue) -> str:
    content = ""
    if name.find("endpoint") == -1:
        if value.fields_count is not None and value.fields_count > 1:
            custom_type_name = create_custom_type(name)
            custom_parameters_types.append(TypeInfo(custom_type_name, value.fields_count))
            content += custom_type_name
        else:
            content += "str"
    else:
        content += "HttpUrl" if name.find("ws-endpoint") == -1 else "WsUrl"
    return content


def find_type(name: str, value: OptionValue) -> str:
    current_type = ""
    match value.value_type:
        case "path":
            current_type = "Path"
        case "string":
            current_type = search_endpoint(name, value)
        case "ulong":
            current_type = "int"
        case "uint":
            current_type = "int"
        case "bool":
            current_type = "bool"
        case "string_array":
            current_type = "list[" + search_endpoint(name, value) + "]"
        case _:
            current_type = "str"
    return current_type


def read_path(path_default_value: Any) -> str:
    content = ""
    if str(path_default_value)[0] == '"':
        content += f" = Field(default_factory=lambda: Path({path_default_value}))"
    elif path_default_value == ".":
        content += " = Field(default_factory=lambda: Path())"
    else:
        content += f' = Field(default_factory=lambda: Path("{path_default_value}"))'
    return content


def read_value(name: str, value: OptionValue) -> tuple[str, str]:
    current_type = find_type(name, value)

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
                content += " = Field(default_factory=list)"
        elif current_type == "str":
            content += f' = "{value.default_value}"'
        elif current_type == "Path":
            content += read_path(value.default_value)
        elif current_type == "bool":
            content += f' = {"True" if value.default_value == "true" else "False"}'
        else:
            content += f" = {value.default_value}"

    return content_type + create_default_declaration(name), content_type_default + content


def prepare_description(description: str, *, last: bool) -> str:
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
        content = create_line(f'"""{content}', last=False)
        content += create_line('"""', last=last)
    else:
        content = create_line(f'"""{content}"""', last=last)
    return content


def read_option(option: Option, *, last: bool) -> str:
    content = ""
    tmp_value = None
    if option.value is not None:
        tmp_value = option.value
    else:
        tmp_value = OptionValue(
            required=True, multitoken=False, composed=False, value_type="bool", default_value="False", fields_count=None
        )

    values = read_value(option.name, tmp_value)
    values_size = 2
    assert len(values) == values_size

    declaration = create_name(option.name) + values[0]
    default_values.append(create_default_name(option.name) + values[1])

    content += create_line(declaration, last=False)

    content += prepare_description(option.description, last=last)

    if not last:
        content += "\n"

    return content


def read_options(options: list[Option] | None) -> str:
    content = ""

    if options is not None and len(options) > 0:
        content += "\n"
        for cnt, option in enumerate(options):
            content += read_option(option, last=(cnt + 1) == len(options))

    return content


def write_file(content: str, file_name: str) -> None:
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


def create_custom_types(custom_parameters_types: list[TypeInfo]) -> str:
    content = ""
    for custom_type in custom_parameters_types:
        content += f"class {custom_type.type_name}(NamedTuple):\n"
        for i in range(custom_type.fields_count):
            content += create_line(f"field_{i}: str", last=i == custom_type.fields_count - 1)

    return content


def create_default_value(default_values: list[str]) -> str:
    content = ""
    for cnt, default_value in enumerate(default_values):
        content += create_line(f"{default_value}", last=cnt == len(default_values) - 1)

    return content


def update_options(options_file: Path) -> None:
    with Path(options_file).open("r") as json_file:
        opts = Options(**json.load(json_file))

        content_common = read_options(opts.common)
        content_config_file = read_options(opts.config_file)
        content_command_line = read_options(opts.command_line)
        content_custom_types = create_custom_types(custom_parameters_types)
        content_default_values = create_default_value(default_values)

        write_file(content_common, "beekeeper_common")
        write_file(content_config_file, "beekeeper_config")
        write_file(content_command_line, "beekeeper_arguments")
        write_file(content_custom_types, "custom_parameters_types")
        write_file(content_default_values, "beekeeper_defaults")


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

    update_options(args.options_file)
