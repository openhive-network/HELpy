from __future__ import annotations

from beekeepy._utilities.options_generator.common import TypeInfo, indent_str, is_keyword


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
    def default_declaration(name: str, prefix: str) -> str:
        default_str = f"{prefix.capitalize()}Defaults." + CodeCreator.default_name(name)
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
