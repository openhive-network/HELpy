from __future__ import annotations

import asyncio
import math
import re
import time
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from enum import Enum
from typing import TYPE_CHECKING, Any, Literal

from dateutil.relativedelta import relativedelta

from helpy.exceptions import ParseError

if TYPE_CHECKING:
    from collections.abc import Awaitable, Callable


class TimeFormats(Enum):
    DEFAULT_FORMAT = "%Y-%m-%dT%H:%M:%S"
    DEFAULT_FORMAT_WITH_MILLIS = "%Y-%m-%dT%H:%M:%S.%f"
    FAKETIME_FORMAT = "@%Y-%m-%d %H:%M:%S"
    FAKETIME_FORMAT_WITH_MILLIS = "@%Y-%m-%d %H:%M:%S.%f"


@dataclass
class TimeControl:
    speed_up_rate: float | int | None = None

    def __post_init__(self) -> None:
        if (
            self.speed_up_rate is not None
            and not isinstance(self.speed_up_rate, float)
            and not isinstance(self.speed_up_rate, int)
        ):
            raise ValueError(f"Incorrect format of 'speed_up_rate' argument, given: `{self.speed_up_rate}`")

    def as_string(self) -> str:
        if self.speed_up_rate:
            return f"+0 x{self.speed_up_rate :.1f}"
        return "+0"

    def apply_head_block_time(self, head_block_time: datetime) -> None:
        pass


@dataclass
class OffsetTimeControl(TimeControl):
    r"""
    Represents a control mechanism for time-related parameters.

    Args:
        offset: The offset value specifying a relative time.
            Format: '[+-]N[mhdy\s]', where 'N' is any positive floating-point number. The letter at the end denotes
            the unit of time (y: year d: day, h: hour, m: minute). Default without any letter means second.
            (e.g. "+10h")
        speed_up_rate (float): An speed-up rate
            Format: positive floating-point number.
            (e.g. "10.0")

    Raises:
        ValueError:
        if `offset` has an incorrect format,
        if `speed_up_rate` has an incorrect format.

    Methods:
        as_string(): Returns a string representation of the time control parameters.
    """

    offset: str = "+0"

    def __post_init__(self) -> None:
        super().__post_init__()
        if self.offset is not None and not re.match(r"^[+\-]?\d+([mhdy])?", self.offset):
            raise ValueError(f"Incorrect format of 'offset' argument, given: `{self.offset}`")

    def as_string(self) -> str:
        if self.speed_up_rate:
            return f"{self.offset} x{self.speed_up_rate}"
        return self.offset


@dataclass
class StartTimeControl(TimeControl):
    r"""
    Represents a control mechanism for time-related parameters.

    Args:
        start_time: The starting time specifying an absolute time.
            Format: "@%Y-%m-%d %H:%M:%S" or "@%Y-%m-%d %H:%M:%S.%f"
            (e.g. "@1970-01-01 00:00:00")
        speed_up_rate: An speed-up rate
            Format: positive floating-point number.
            (e.g. "10.0")

    Raises:
        ValueError:
            if `start_time` has an incorrect format,
            if `speed_up_rate` has an incorrect format.

    Methods:
        as_string(): Returns a string representation of the time control parameters.
    """

    start_time: Literal["head_block_time"] | datetime = field(default_factory=datetime.now)

    def apply_head_block_time(self, head_block_time: datetime) -> None:
        if self.start_time == "head_block_time":
            self.start_time = head_block_time

    def as_string(self) -> str:
        if self.start_time == "head_block_time":
            raise ValueError("You probably forgot to call `apply_head_block_time` to specify time")
        assert isinstance(self.start_time, datetime), "start_time have to be datetime type"
        serialized_start_time = Time.serialize(self.start_time, format_=TimeFormats.FAKETIME_FORMAT)
        if self.speed_up_rate:
            return f"{serialized_start_time} x{self.speed_up_rate}"
        return serialized_start_time

    def is_start_time_equal_to(self, value: str) -> bool:
        return self.start_time == value


@dataclass
class SpeedUpRateTimeControl(TimeControl):
    r"""
    Represents a control mechanism for time-related parameters.

    Args:
        speed_up_rate: An speed-up rate
            Format: positive floating-point number.
            (e.g. "10.0")

    Raises:
        ValueError: if `speed_up_rate` has an incorrect format.

    Methods:
        as_string(): Returns a string representation of the time control parameters.
    """


class Time:
    def __new__(cls, *_: Any, **__: Any) -> Time:  # noqa: PYI034  # it's creation prevention
        raise TypeError(f"Creation object of {Time.__name__} class is forbidden.")

    @classmethod
    def parse(
        cls,
        time: str,
        *,
        format_: TimeFormats | str | None = None,
        time_zone: timezone | None = timezone.utc,
    ) -> datetime:
        """Parses given string with given format in given timezone.

        Note:
            By default, when `format_` parameter is specified as None - the ISO format (Time.DEFAULT_FORMAT)
            and ISO format including milliseconds (Time.DEFAULT_FORMAT_WITH_MILLIS) could be parsed.

        Args:
            time: time string to parse
            format_: format of given time string
            time_zone: timezone to set after parsing

        Raises:
            ParseError: if parsing is not possible

        Returns:
            datetime.datetime object
        """
        if isinstance(time, datetime):
            return time

        def __parse_in_specified_format(_format: TimeFormats | str) -> datetime:
            if isinstance(_format, str):
                _format = TimeFormats(_format)
            try:
                parsed = datetime.strptime(time, _format.value)  # noqa: DTZ007 # in hive project %z is unused because all timestamps are utc
                return parsed.replace(tzinfo=time_zone) if time_zone else parsed
            except ValueError as exception:
                format_info = (
                    f"`{_format}` custom format."
                    if _format not in (TimeFormats.DEFAULT_FORMAT_WITH_MILLIS, TimeFormats.DEFAULT_FORMAT)
                    else (
                        f"`{TimeFormats.DEFAULT_FORMAT}` or `{TimeFormats.DEFAULT_FORMAT_WITH_MILLIS}` default formats."
                    )
                )
                raise ParseError(f"Could not be parse the `{time}` string using the {format_info}") from exception

        if format_ is not None:
            return __parse_in_specified_format(format_)

        try:
            return __parse_in_specified_format(TimeFormats.DEFAULT_FORMAT)
        except ParseError:
            return __parse_in_specified_format(TimeFormats.DEFAULT_FORMAT_WITH_MILLIS)

    @staticmethod
    def serialize(time: datetime, *, format_: TimeFormats | str = TimeFormats.DEFAULT_FORMAT) -> str:
        return datetime.strftime(time, TimeFormats(format_).value)

    @staticmethod
    def milliseconds(milliseconds: float) -> timedelta:
        return timedelta(milliseconds=milliseconds)

    @staticmethod
    def seconds(amount: float) -> timedelta:
        return timedelta(seconds=amount)

    @staticmethod
    def minutes(amount: float) -> timedelta:
        return timedelta(minutes=amount)

    @staticmethod
    def hours(amount: float) -> timedelta:
        return timedelta(hours=amount)

    @staticmethod
    def days(amount: float) -> timedelta:
        return timedelta(days=amount)

    @staticmethod
    def weeks(amount: float) -> timedelta:
        return timedelta(days=amount * 7)

    @staticmethod
    def months(amount: int) -> relativedelta:
        return relativedelta(months=amount)

    @staticmethod
    def years(amount: int) -> relativedelta:
        return relativedelta(years=amount)

    @classmethod
    def are_close(cls, first: datetime, second: datetime, *, absolute_tolerance: timedelta | None = None) -> bool:
        if absolute_tolerance is None:
            absolute_tolerance = cls.seconds(0)

        try:
            return abs(first - second) <= absolute_tolerance
        except TypeError as exception:
            raise ValueError(
                "The time zones of the two dates differ.\n"
                "Note, that time zones can be modified (e.g.: `.replace(tzinfo=datetime.timezone.utc)`)."
            ) from exception

    @classmethod
    def now(
        cls,
        *,
        serialize: bool = True,
        time_zone: timezone | None = timezone.utc,
        serialize_format: TimeFormats | str = TimeFormats.DEFAULT_FORMAT,
    ) -> str | datetime:
        time = datetime.now(time_zone)
        return cls.serialize(time, format_=serialize_format) if serialize else time

    @classmethod
    def from_now(  # noqa: PLR0913 # it is mirroring timedelta interface
        cls,
        *,
        milliseconds: int = 0,
        seconds: int = 0,
        minutes: int = 0,
        hours: int = 0,
        days: int = 0,
        weeks: int = 0,
        months: int = 0,
        years: int = 0,
        time_zone: timezone | None = timezone.utc,
        serialize: bool = True,
        serialize_format: TimeFormats | str = TimeFormats.DEFAULT_FORMAT,
    ) -> str | datetime:
        """Adds to current time given time periods.

        Args:
            milliseconds: milliseconds to add.
            seconds: seconds to add.
            minutes: minutes to add.
            hours: hours to add.
            days: days to add.
            weeks: weeks to add.
            months: months to add.
            years: years to add.
            time_zone: time zone to set.
            serialize: return serialized time or as datetime.
            serialize_format: if serialize, this determines format.

        Raises:
            ValueError: no periods has been given

        Returns:
            serialized or as datetime, shifted time with given time periods.
        """
        if not any([milliseconds, seconds, minutes, hours, days, weeks, months, years]):
            raise ValueError(
                "At least one keyword argument is required.\n"
                "If you want to get the current datetime, please use `Time.now()` instead."
            )

        delta = relativedelta(
            microseconds=milliseconds * 10**3,
            seconds=seconds,
            minutes=minutes,
            hours=hours,
            days=days,
            weeks=weeks,
            months=months,
            years=years,
        )

        now = cls.now(time_zone=time_zone, serialize=False)
        assert isinstance(now, datetime)  # just because of mypy
        time = now + delta
        return cls.serialize(time, format_=serialize_format) if serialize else time

    @classmethod
    def sync_wait_for(
        cls,
        predicate: Callable[[], bool],
        *,
        timeout: float | timedelta = math.inf,
        timeout_error_message: str | None = None,
        poll_time: float = 1.0,
    ) -> float:
        """Waits synchronously for the predicate to return True.

        Args:
            predicate: Callable that returns boolean value.
            timeout: Timeout in seconds or preferably timedelta.
            timeout_error_message: Message that will be displayed if timeout is reached.
            poll_time: Time between predicate calls.

        Raises:
            TimeoutError: if given timeout exceeds

        Returns:
            Time it took to wait for predicate return True.
        """
        timeout_secs = cls.__calculate_timeout_secs_and_validate_it(timeout=timeout)
        already_waited = 0.0
        while not predicate():
            if timeout_secs - already_waited <= 0:
                raise TimeoutError(timeout_error_message or "Waited too long, timeout was reached")

            sleep_time = min(poll_time, timeout_secs)
            time.sleep(sleep_time)
            already_waited += sleep_time

        return already_waited

    @classmethod
    async def async_wait_for(
        cls,
        predicate: Callable[[], bool] | Callable[[], Awaitable[bool]],
        *,
        timeout: float | timedelta = math.inf,
        timeout_error_message: str | None = None,
        poll_time: float = 1.0,
    ) -> float:
        """Waits asynchronously for the predicate to return True.

        Args:
            predicate: Callable that returns boolean value.
            timeout: Timeout in seconds or preferably timedelta.
            timeout_error_message: Message that will be displayed if timeout is reached.
            poll_time: Time between predicate calls.

        Raises:
            TimeoutError: if given timeout exceeds

        Returns:
            Time it took to wait for predicate return True.
        """
        timeout_secs = cls.__calculate_timeout_secs_and_validate_it(timeout=timeout)
        already_waited = 0.0

        async def __run_asynchronously_predicate() -> bool:
            result = predicate()
            if isinstance(result, bool):
                return result
            return await result

        while not await __run_asynchronously_predicate():
            cls.__check_is_timeout_exceeded(
                timeout_secs=timeout_secs, already_waited=already_waited, timeout_error_message=timeout_error_message
            )

            sleep_time = min(poll_time, timeout_secs)
            await asyncio.sleep(sleep_time)
            already_waited += sleep_time

        return already_waited

    @classmethod
    def __calculate_timeout_secs_and_validate_it(cls, timeout: float | timedelta) -> float:
        timeout_secs: float = timeout.total_seconds() if isinstance(timeout, timedelta) else timeout
        assert timeout_secs >= 0, "The `timeout` argument must be non-negative value."
        return timeout_secs

    @classmethod
    def __check_is_timeout_exceeded(
        cls, timeout_secs: float, already_waited: float, timeout_error_message: str | None
    ) -> None:
        if timeout_secs - already_waited <= 0:
            raise TimeoutError(timeout_error_message or "Waited too long, timeout was reached")

    @staticmethod
    def wait_for(
        predicate: Callable[[], bool],
        *,
        timeout: float | timedelta = math.inf,
        timeout_error_message: str | None = None,
        poll_time: float = 1.0,
    ) -> float:
        """
        Waits for the predicate to return True in the given timeout and raises TimeoutError if it was exceeded.

        Args:
            predicate: Callable that returns boolean value.
            timeout: Timeout in seconds or preferably timedelta (e.g. tt.Time.minutes(1)).
            timeout_error_message: Message that will be displayed if timeout is reached.
            poll_time: Time between predicate calls.

        Returns:
            Time in seconds that was spent on waiting.
        """
        timeout_secs: float = timeout.total_seconds() if isinstance(timeout, timedelta) else timeout
        assert timeout_secs >= 0, "The `timeout` argument must be non-negative value."

        already_waited = 0.0
        while not predicate():
            if timeout_secs - already_waited <= 0:
                raise TimeoutError(timeout_error_message or "Waited too long, timeout was reached")

            sleep_time = min(poll_time, timeout_secs)
            time.sleep(sleep_time)
            already_waited += sleep_time

        return already_waited
