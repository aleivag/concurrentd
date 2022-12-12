#!../.venv/bin/python3

import os
import shlex
import subprocess
import sys
from pathlib import Path

from multiprocessd import NSProcessPoolExecutor

###
# asuming you have a debian root (it could be a docker/oci image), in the path
# defined by ROOT_PATH then
###

ROOT_PATH = Path(__file__).absolute().parent.parent / ".debian"


def run():
    """
    runs like it where in a debian os.. a la container...
    """
    print(Path("/etc/os-release").read_text())
    subprocess.run(shlex.split("whoami"))
    subprocess.run(shlex.split("ps auxf"))
    subprocess.run(shlex.split("apt install sl"))
    subprocess.run(shlex.split("/usr/games/sl"))


if __name__ == "__main__":
    if os.getuid() != 0:
        print("should be root to run this stuff", file=sys.stderr)
        sys.exit(-1)
    print(ROOT_PATH)
    assert ROOT_PATH.exists(), f"{ROOT_PATH} must exists"
    with NSProcessPoolExecutor(
        ns_options=dict(RootDirectory=ROOT_PATH, MountAPIVFS=True, User="root")
    ) as pool:
        pool.submit(run)
