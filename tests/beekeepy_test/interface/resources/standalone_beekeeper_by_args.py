from __future__ import annotations

import json
from pathlib import Path
from sys import argv

from local_tools.beekeepy.get_pid_of_running_beekeeper import get_pid_of_running_beekeeper

from beekeepy import Beekeeper, Settings, close_already_running_beekeeper

settings = Settings(working_directory=Path(argv[1]))

if argv[2] == "start":
    bk = Beekeeper.factory(settings=settings)
    (settings.working_directory / "beekeeper.pid").write_text(json.dumps({"pid": get_pid_of_running_beekeeper(bk)}))
    bk.detach()
elif argv[2] == "stop":
    close_already_running_beekeeper(working_directory=settings.working_directory)
