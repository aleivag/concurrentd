import os
import pwd
import shlex
import subprocess
import time

from multiprocessd import NSProcessPoolExecutor

SANDBOX_OPTIONS = dict(
    User="nobody", Group="nobody", PrivateTmp=True, PrivateNetwork=True
)


def run():
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
    time.sleep(10)

    return "Hey"


def main():
    with NSProcessPoolExecutor(ns_options=SANDBOX_OPTIONS) as pool:
        f = [pool.submit(run), pool.submit(run), pool.submit(run)]
        print(pool.unit.Unit.Id)
    print(f)
    print([u.result() for u in f])
    print(pool.unit.Unit.Id)


if __name__ == "__main__":
    main()
