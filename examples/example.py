#!.venv/bin/python3


import os
import pwd
import shlex
import subprocess
import sys

from multiprocessd import NSProcess, nssandbox

SANDBOX_OPTIONS = dict(
    User="nobody", Group="nobody", PrivateTmp=True, PrivateNetwork=True
)


def run():
    """ """
    print("we are going to ping 8.8.8.8, but network its turn off. so it will fail")
    subprocess.run(shlex.split("ping -Dc 2 8.8.8.8"))
    print("since we dont have network, lets check our ip, with `ip addr`")
    subprocess.run(shlex.split("ip addr"))
    print("ok, so .... who are we")
    print(pwd.getpwuid(os.getuid()))
    subprocess.run(shlex.split("whoami"))
    print("===>")
    print("lets check what we have in tmp")
    subprocess.run(shlex.split("df  /tmp"))
    print("ls -ll /tmp")
    subprocess.run(shlex.split("ls -ll  /tmp"))


@nssandbox(**SANDBOX_OPTIONS)
def sandbox_run():
    return run()


if __name__ == "__main__":
    if os.getuid() != 0:
        print("should be root to run this stuff", file=sys.stderr)
        sys.exit(-1)

    p = NSProcess(target=run, options=SANDBOX_OPTIONS)
    p.start()
    p.join()
    print("SANBOXING THIS")
    sandbox_run()
