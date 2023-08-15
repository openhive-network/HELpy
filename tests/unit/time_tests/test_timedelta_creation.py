from __future__ import annotations

from datetime import timedelta

import pytest
from dateutil.relativedelta import relativedelta

from hive_transfer_protocol import Time


@pytest.mark.parametrize(
    ("created", "expected"),
    [
        pytest.param((Time.milliseconds(5)), timedelta(milliseconds=5), id="milliseconds"),
        pytest.param(Time.seconds(5), timedelta(seconds=5), id="seconds"),
        pytest.param(Time.minutes(1), timedelta(minutes=1), id="minutes"),
        pytest.param(Time.hours(100), timedelta(hours=100), id="hours"),
        pytest.param(Time.days(1000), timedelta(days=1000), id="days"),
        pytest.param(Time.weeks(1000), timedelta(weeks=1000), id="weeks"),
        pytest.param(Time.months(1000), relativedelta(months=1000), id="months"),
        pytest.param(Time.years(1000), relativedelta(years=1000), id="years"),
    ],
)
def test_timedelta_creation(created: timedelta, expected: timedelta | relativedelta) -> None:
    assert created == expected
