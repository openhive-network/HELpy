from __future__ import annotations

from hive_transfer_protocol import Time, TimeFormats


def test_time_serialization_in_default_format() -> None:
    time = Time.parse("1970-01-01T00:00:00")
    assert Time.serialize(time) == "1970-01-01T00:00:00"


def test_time_serialization_in_custom_format() -> None:
    time = Time.parse("1970-01-01T00:00:00")
    assert Time.serialize(time, format_=TimeFormats.TIME_OFFSET_FORMAT) == "@1970-01-01 00:00:00.000000"
