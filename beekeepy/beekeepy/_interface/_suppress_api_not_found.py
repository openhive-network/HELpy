from __future__ import annotations

from typing import TYPE_CHECKING

from beekeepy._interface.context import SelfContextSync
from beekeepy.exceptions import ApiNotFoundError, GroupedErrorsError

if TYPE_CHECKING:
    from types import TracebackType


class SuppressApiNotFound(SelfContextSync):
    """Use to suppress ApiNotFoundError.

    Example:
    ```python

    with SuppressApiNotFound("database_api", "rc_api") as suppressed:
        node.api.database.get_config()
        with node.batch() as bnode:
            bnode.api.rc.get_resource_params()
            bnode.api.jsonrpc.get_methods()

    print("suppressed apis:", [x.api for x in suppressed.errors])
    # suppressed apis: ['database_api', 'rc_api']
    ```
    """

    def __init__(self, *apis: str) -> None:
        super().__init__()
        self.__apis = list(apis)
        self.__suppressed_errors: list[ApiNotFoundError] = []

    def _finally(self) -> None:
        return

    @property
    def errors(self) -> list[ApiNotFoundError]:
        return self.__suppressed_errors

    def _handle_exception(self, exception: BaseException, __: TracebackType | None) -> bool:
        if not isinstance(exception, ApiNotFoundError):
            return False

        cause = exception.cause
        if (cause is None) or (not isinstance(cause, GroupedErrorsError)):
            raise ValueError("Cannot access cause of exception to retrieve all information")

        for ex in cause.exceptions:
            if not isinstance(ex, ApiNotFoundError):
                return False

            if ex.api not in self.__apis:
                return False

            self.__suppressed_errors.append(ex)

        return True
