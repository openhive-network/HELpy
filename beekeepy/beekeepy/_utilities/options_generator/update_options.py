"""Usage from bash for beekeeper.

```bash
python3 -m beekeepy._utilities.options_generator.update_options \
    --options-file /path/to/options.json \
    --source-dir helpy/beekeepy/beekeepy/_utilities/options_generator/resources \
    --dest-dir helpy/beekeepy/beekeepy/_executable \
    --prefix beekeeper
```
"""

from __future__ import annotations

import argparse
from pathlib import Path

from beekeepy._utilities.options_generator.json_processor import JSONProcessor


def update_options(*, options_file: Path, source_dir: Path, dest_dir: Path, prefix: str) -> None:
    """
    Generates Arguments and Config classes from given options file.

    Arguments:
        options_file: Path to the JSON file that contains options retrieved from hived by `--dump-options`.
        source_dir: Path to the directory with templates for generated files. In that directory
            following files are expected: `common.in`, `config.in`, `arguments.in`, `defaults.in`,
            `custom_parameters_types.in`.
        dest_path: Path to the destination directory where generated files will be written.
        prefix: Prefix for generated files. E.g.: `beekeeper` will
            prodcue: `beekeeper_common.py`, `beekeeper_config.py`, etc...
    """
    assert dest_dir.exists(), f"Destination path {dest_dir} is not a directory."
    assert options_file.is_file(), f"Options file {options_file} does not exist."
    for in_file_type in (
        JSONProcessor.build_path_with_prefix(prefix, "common", source_dir, in_sufix=True),
        JSONProcessor.build_path_with_prefix(prefix, "config", source_dir, in_sufix=True),
        JSONProcessor.build_path_with_prefix(prefix, "arguments", source_dir, in_sufix=True),
        JSONProcessor.build_path_with_prefix(prefix, "defaults", source_dir, in_sufix=True),
        JSONProcessor.build_path_with_prefix(prefix, "custom_parameters_types", source_dir, in_sufix=True),
    ):
        assert in_file_type.is_file(), f"File {in_file_type} does not exist."

    JSONProcessor.update_options(options_file=options_file, source_dir=source_dir, dest_dir=dest_dir, prefix=prefix)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate CLI and CONFIG parameters.")
    parser.add_argument(
        "--options-file",
        required=True,
        type=str,
        default="",
        help="JSON file that contains options retrieved from hived by `--dump-options`",
    )
    parser.add_argument(
        "--source-dir",
        required=True,
        type=str,
        help="Source directory with templates for generated files. In that directory following files are expected: "
        "common.in, config.in, arguments.in, defaults.in, custom_parameters_types.in",
    )
    parser.add_argument(
        "--dest-dir",
        required=True,
        type=str,
        help="Destination directory where generated files will be written.",
    )
    parser.add_argument(
        "--prefix",
        required=True,
        type=str,
        help="Prefix for generated files. Default is empty. E.x: hive or beekeeper",
    )
    args = parser.parse_args()

    update_options(
        options_file=Path(args.options_file),
        source_dir=Path(args.source_dir),
        dest_dir=Path(args.dest_dir),
        prefix=args.prefix,
    )
