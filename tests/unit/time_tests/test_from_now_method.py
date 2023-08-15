from __future__ import annotations

import random

import pytest

from hive_transfer_protocol import Time, TimeFormats


@pytest.mark.parametrize(
    "interval", ["milliseconds", "seconds", "minutes", "hours", "days", "weeks", "months", "years"]
)
def test_from_now_with_parameters(interval: str) -> None:
    # ARRANGE
    value = random.randint(-1000, 1000)
    interval_container = {interval: value}
    delta = getattr(Time, interval)(value)

    # ACT
    shifted_time = Time.from_now(**interval_container, serialize_format=TimeFormats.DEFAULT_FORMAT_WITH_MILLIS)  # type: ignore[arg-type]

    # ASSERT
    assert isinstance(shifted_time, str)
    reference_time_in_from_now = Time.parse(shifted_time, format_=TimeFormats.DEFAULT_FORMAT_WITH_MILLIS) - delta
    assert reference_time_in_from_now < Time.now(serialize=False)


def test_from_now_without_argument() -> None:
    with pytest.raises(ValueError):  # noqa: PT011
        Time.from_now()
