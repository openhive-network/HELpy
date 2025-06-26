from __future__ import annotations


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
