from __future__ import annotations

from helpy import Time, TimeFormats


def test_time_serialization_in_default_format() -> None:
    time = Time.parse("1970-01-01T00:00:00")
    assert Time.serialize(time) == "1970-01-01T00:00:00"


def test_time_serialization_in_custom_format() -> None:
    time = Time.parse("1970-01-01T00:00:00")
    assert Time.serialize(time, format_=TimeFormats.TIME_OFFSET_FORMAT) == "@1970-01-01 00:00:00"


def test_time_serialization_in_custom_format_with_mills() -> None:
    time = Time.parse("1970-01-01T00:00:00")
    assert Time.serialize(time, format_=TimeFormats.TIME_OFFSET_FORMAT_WITH_MILLIS) == "@1970-01-01 00:00:00.000000"
