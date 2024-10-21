from __future__ import annotations

import json
from pathlib import Path

from schemas.dump_options.options import Option, Options, OptionValue

indent = 4


def createLine(content: str, last: bool = False):
    return "".join([" " for _ in range(indent)]) + content + ("" if last else "\n")


def searchEndpoint(name: str):
    content = ""
    if name.find("endpoint") == -1:
        content += "str"
    else:
        content += "HttpUrl" if name.find("ws-endpoint") == -1 else "WsUrl"
    return content


def readValue(name: str, value: OptionValue):
    content = ": "
    current_type = None
    match value.value_type:
        case "path":
            current_type = "Path"
        case "string":
            current_type = searchEndpoint(name)
        case "ulong":
            current_type = "int"
        case "uint":
            current_type = "int"
        case "bool":
            current_type = "bool"
        case "string_array":
            current_type = "list[" + searchEndpoint(name) + "]"
        case _:
            current_type = "str"

    content += current_type

    if len(str(value.default_value)) == 0:
        if not value.required:
            content += " | None = None"
    elif isinstance(value.default_value, list):
        if len(value.default_value) > 0:
          for item in value.default_value:
              content += f' = "{item}"'
        else:
            content += " = []"
    elif current_type == "str":
          content += f' = "{value.default_value}"'
    elif current_type == "Path":
        if str(value.default_value)[0] == "\"":
          content += f' = Field(default_factory=lambda: Path({value.default_value}))'
        else:
          content += f' = Field(default_factory=lambda: Path("{value.default_value}"))'
    elif current_type == "bool":
        content += f' = {"True" if value.default_value == "true" else "False"}'
    else:
        content += f" = {value.default_value}"
    return content


def readOption(option: Option, last: bool):
    content = ""
    content += createLine("# " + option.description)
    tmpValue = None
    if option.value is not None:
        tmpValue = option.value
    else:
        tmpValue = OptionValue(required=True, multitoken=False, composed=False, value_type="bool", default_value="False")
    content += createLine(option.name.replace("-", "_") + readValue(option.name, tmpValue), last)

    if not last:
        content += "\n"

    return content


def readOptions(options: list[Option]):
    content = ""

    if options is not None and len(options) > 0:
        cnt = 0
        for option in options:
            cnt += 1
            content += readOption(option, cnt == len(options))
    else:
        content += createLine("pass", True)

    return content


def writeFile(content: str, partialFileName: str):
    marker = "{GENERATED-ITEMS}"

    srcPathFile = f"beekeeper_{partialFileName}.in"
    dstPathFile = f"../beekeepy/beekeepy/_executable/beekeeper_{partialFileName}.py"

    with Path(srcPathFile).open("r") as srcFile:
        srcFileContent = srcFile.read()

        with Path(dstPathFile).open("w") as dstFile:
            srcFileContent = srcFileContent.replace(marker, content)

            dstFile.write(srcFileContent)
            dstFile.close()


def updateOptions():
    with Path("/home/mario/src/options.json").open("r") as jsonFile:
        opts = Options(**json.load(jsonFile))

        contentCommon = readOptions(opts.common)
        contentConfigFile = readOptions(opts.config_file)
        contentCommandLine = readOptions(opts.command_line)

        writeFile(contentCommon, "common")
        writeFile(contentConfigFile, "config")
        writeFile(contentCommandLine, "arguments")


updateOptions()
