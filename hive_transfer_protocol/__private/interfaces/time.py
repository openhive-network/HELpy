from __future__ import annotations

import asyncio
import math
import time
from datetime import datetime, timedelta, timezone
from typing import TYPE_CHECKING, Any, ClassVar, Literal, TypeAlias

from dateutil.relativedelta import relativedelta

from hive_transfer_protocol.exceptions import ParseError

if TYPE_CHECKING:
    from collections.abc import Awaitable, Callable


class TimeFormats:
    DEFAULT_FORMAT = "%Y-%m-%dT%H:%M:%S"
    DEFAULT_FORMAT_WITH_MILLIS = "%Y-%m-%dT%H:%M:%S.%f"
    TIME_OFFSET_FORMAT = "@%Y-%m-%d %H:%M:%S.%f"


def _get_avail_formats() -> TypeAlias:
    return Literal[TimeFormats.DEFAULT_FORMAT, TimeFormats.DEFAULT_FORMAT_WITH_MILLIS, TimeFormats.TIME_OFFSET_FORMAT]


class Time:
    _AVAIL_FORMATS: ClassVar[TypeAlias] = _get_avail_formats()

    def __new__(cls, *_: Any, **__: Any) -> Time:
        raise TypeError(f"Creation object of {Time.__name__} class is forbidden.")

    @classmethod
    def parse(
        cls,
        time: str,
        *,
        format_: _AVAIL_FORMATS | None = None,
        time_zone: timezone | None = timezone.utc,
    ) -> datetime:
        """Parses given string with given format in given timezone.

        Note:
            By default, when `format_` parameter is specified as None - the ISO format (Time.DEFAULT_FORMAT)
            and ISO format including milliseconds (Time.DEFAULT_FORMAT_WITH_MILLIS) could be parsed.

        Arguments:
            time -- time string to parse

        Keyword Arguments:
            format_ -- format of given time string (default: {Time.DEFAULT_FORMAT})
            time_zone -- timezone to set after parsing (default: {timezone.utc})

        Raises:
            ParseError: if parsing is not possible

        Returns:
            datetime.datetime object
        """
        if isinstance(time, datetime):
            return time

        def __parse_in_specified_format(_format: str) -> datetime:
            try:
                parsed = datetime.strptime(time, _format)
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
    def serialize(time: datetime, *, format_: str = TimeFormats.DEFAULT_FORMAT) -> str:
        return datetime.strftime(time, format_)

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
        serialize_format: str = TimeFormats.DEFAULT_FORMAT,
    ) -> str | datetime:
        time = datetime.now(time_zone)
        return cls.serialize(time, format_=serialize_format) if serialize else time

    @classmethod
    def from_now(
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
        serialize_format: str = TimeFormats.DEFAULT_FORMAT,
    ) -> str | datetime:
        """Adds to current time given time periods.

        Keyword Arguments:
            milliseconds -- milliseconds to add (default: {0})
            seconds -- seconds to add (default: {0})
            minutes -- minutes to add (default: {0})
            hours -- hours to add (default: {0})
            days -- days to add (default: {0})
            weeks -- weeks to add (default: {0})
            months -- months to add (default: {0})
            years -- years to add (default: {0})
            time_zone -- time zone to set (default: {timezone.utc})
            serialize -- return serialized time or as datetime (default: {True})
            serialize_format -- if serialize, this determines format (default: {DEFAULT_FORMAT})

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

        Arguments:
            predicate -- Callable that returns boolean value.

        Keyword Arguments:
            timeout -- Timeout in seconds or preferably timedelta (default: {math.inf})
            timeout_error_message -- Message that will be displayed if timeout is reached. (default: {None})
            poll_time -- Time between predicate calls. (default: {1.0})

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

        Arguments:
            predicate -- Callable that returns boolean value.

        Keyword Arguments:
            timeout -- Timeout in seconds or preferably timedelta (default: {math.inf})
            timeout_error_message -- Message that will be displayed if timeout is reached. (default: {None})
            poll_time -- Time between predicate calls. (default: {1.0})

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
