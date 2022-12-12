#!.venv/bin/python3


import os
import pwd
import shlex
import time
import subprocess
import sys

from concurrentd.transient import TransientUnitProcess

SANDBOX_OPTIONS = dict(
    User="nobody", Group="nobody", PrivateTmp=True, PrivateNetwork=True
)


class Process(TransientUnitProcess):
    def __init__(self):
        super().__init__(properties=SANDBOX_OPTIONS)

    def run(self):
        print(pwd.getpwuid(os.getuid()))
        time.sleep(20)


if __name__ == "__main__":
    if os.getuid() != 0:
        print("should be root to run this stuff", file=sys.stderr)
        sys.exit(-1)

    p = Process()
    p.start()
    p.join()
