from __future__ import annotations

from pathlib import Path
from sys import argv

from beekeepy import Beekeeper, Settings, close_already_running_beekeeper

settings = Settings(working_directory=Path(argv[1]))
pid_file = settings.ensured_working_directory / "pid.txt"

if argv[2] == "start":
    bk = Beekeeper.factory(settings=settings)
    pid_file.write_text(str(bk.detach()))
elif argv[2] == "stop":
    close_already_running_beekeeper(pid=int(pid_file.read_text().strip()))
