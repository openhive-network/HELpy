from __future__ import annotations

from hive_transfer_protocol import Time


def test_comparison_without_tolerance() -> None:
    time = Time.parse("1970-01-01T00:00:00")

    assert Time.are_close(time, time)
    assert not Time.are_close(time, time + Time.seconds(1))


def test_comparison_with_absolute_tolerance() -> None:
    time = Time.parse("1970-01-01T00:00:00")

    assert Time.are_close(time, time - Time.seconds(6), absolute_tolerance=Time.seconds(5)) is False
    assert Time.are_close(time, time - Time.seconds(5), absolute_tolerance=Time.seconds(5)) is True
    assert Time.are_close(time, time - Time.seconds(4), absolute_tolerance=Time.seconds(5)) is True

    assert Time.are_close(time, time + Time.seconds(4), absolute_tolerance=Time.seconds(5)) is True
    assert Time.are_close(time, time + Time.seconds(5), absolute_tolerance=Time.seconds(5)) is True
    assert Time.are_close(time, time + Time.seconds(6), absolute_tolerance=Time.seconds(5)) is False
