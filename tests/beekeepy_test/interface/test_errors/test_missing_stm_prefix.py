from __future__ import annotations

import pytest

from beekeepy.exceptions.detectable import MissingSTMPrefixError
from helpy.exceptions import ErrorInResponseError


def test_basic_detection() -> None:
    # ARRANGE, ACT & ASSERT
    with pytest.raises(MissingSTMPrefixError), MissingSTMPrefixError(
        public_key="8Ya14mz5HiZ3JiEhoad4uoSjuK17fMJgJVVuY4991qrf6tbNdH"
    ):
        raise ErrorInResponseError(
            url="",
            request="",
            request_id=None,
            response=(
                "Assert Exception:source.substr( 0, prefix.size() ) == prefix: "
                "public key requires STM prefix, but was given "
                "`8Ya14mz5HiZ3JiEhoad4uoSjuK17fMJgJVVuY4991qrf6tbNdH`"
            ),
        )
