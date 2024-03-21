from __future__ import annotations

import helpy


def test_test() -> None:
    helpy.Hived(settings=helpy.Settings(http_endpoint=helpy.HttpUrl("https://api.hive.blog")))
