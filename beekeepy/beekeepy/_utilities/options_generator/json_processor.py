from __future__ import annotations

import textwrap
from pathlib import Path
from typing import Any, ClassVar

from beekeepy._utilities.options_generator.code_creator import CodeCreator
from beekeepy._utilities.options_generator.common import TypeInfo, indent_str
from schemas.dump_options.options import Option, Options, OptionValue


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
    def __read_value(name: str, value: OptionValue, prefix: str) -> tuple[str, str]:
        current_type = JSONProcessor.__find_type(name, value)

        none_is_allowed = len(str(value.default_value)) == 0 and not value.required

        content_type = f": {current_type}" + (" | None" if none_is_allowed else "") + " = "
        content_type_default = f": ClassVar[{current_type}" + (" | None] = None" if none_is_allowed else "]")
        content = ""

        if not none_is_allowed:
            if isinstance(value.default_value, list):
                if len(value.default_value) > 0:
                    content += (
                        f" = field(default_factory=lambda: [\n{indent_str*2}"
                        + f",\n{indent_str*2}".join(
                            [JSONProcessor.__prepare_string_value(item) for item in value.default_value]
                        )
                        + f"\n{indent_str}])"
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

        return content_type + CodeCreator.default_declaration(name, prefix=prefix), content_type_default + content

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
    def __read_option(option: Option, prefix: str) -> str:
        content = ""
        value = option.value or OptionValue(
            required=True,
            multitoken=False,
            composed=False,
            value_type="bool",
            default_value="False",
            fields_count=None,
        )

        values = JSONProcessor.__read_value(option.name, value, prefix=prefix)
        values_size = 2
        assert len(values) == values_size

        declaration = CodeCreator.name(option.name) + values[0]
        JSONProcessor.default_values.append(CodeCreator.default_name(option.name) + values[1])

        content += CodeCreator.line(declaration)

        content += JSONProcessor.__prepare_description(option.description)

        return content

    @staticmethod
    def __read_options(options: list[Option] | None, prefix: str) -> str:
        content = ""

        if options is not None and len(options) > 0:
            content += "\n"
            for option in options:
                content += JSONProcessor.__read_option(option, prefix=prefix)

        return content

    @staticmethod
    def __write_file(  # noqa: PLR0913
        content: str,
        file_name: str,
        dest_dir: Path,
        src_dir: Path,
        prefix: str,
        *,
        force_generate: bool = False,
    ) -> None:
        if (not force_generate) and not content.strip():
            return

        marker = "{GENERATED-ITEMS}"

        src_path_file = JSONProcessor.build_path_with_prefix(prefix, file_name, src_dir, in_sufix=True)
        dst_path_file = JSONProcessor.build_path_with_prefix(prefix, file_name, dest_dir, in_sufix=False)

        src_file_content = src_path_file.read_text()
        src_file_content = src_file_content.replace(marker, content)
        Path(dst_path_file).write_text(src_file_content.strip("\n \t") + "\n")

    @staticmethod
    def build_path_with_prefix(prefix: str, filename: str, path: Path, *, in_sufix: bool) -> Path:
        path = path.absolute()
        return path / (f"{prefix}_{filename}." + ("in" if in_sufix else "py"))

    @staticmethod
    def update_options(*, options_file: Path, source_dir: Path, dest_dir: Path, prefix: str) -> None:
        opts = Options.parse_file(options_file)

        content_common = JSONProcessor.__read_options(opts.common, prefix)
        content_config_file = JSONProcessor.__read_options(opts.config_file, prefix)
        content_command_line = JSONProcessor.__read_options(opts.command_line, prefix)
        content_custom_types = CodeCreator.custom_types(JSONProcessor.custom_parameters_types)
        content_default_values = CodeCreator.default_value(JSONProcessor.default_values)

        JSONProcessor.__write_file(content_common, "common", dest_dir, source_dir, prefix)
        JSONProcessor.__write_file(content_config_file, "config", dest_dir, source_dir, prefix, force_generate=True)
        JSONProcessor.__write_file(content_command_line, "arguments", dest_dir, source_dir, prefix, force_generate=True)
        JSONProcessor.__write_file(content_custom_types, "custom_parameters_types", dest_dir, source_dir, prefix)
        JSONProcessor.__write_file(content_default_values, "defaults", dest_dir, source_dir, prefix)
