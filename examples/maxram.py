#!.venv/bin/python3


import os
import pwd
import shlex
import subprocess
import sys

from multiprocessd import NSProcess, nssandbox

SANDBOX_OPTIONS = dict(
    MemoryMax=1024 * 1024 * 10,
    MemorySwapMax=0,
)


@nssandbox(**SANDBOX_OPTIONS)
def run():
    print("we will run out of ram")
    x = "foo" * SANDBOX_OPTIONS["MemoryMax"]
    print("we run out of ram")


if __name__ == "__main__":
    if os.getuid() != 0:
        print("should be root to run this stuff", file=sys.stderr)
        sys.exit(-1)

    run()
