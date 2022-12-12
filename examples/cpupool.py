import os
import pwd
import shlex
import subprocess
import time
from concurrent.futures import as_completed

from concurrentd.transient import TransientUnitPoolExecutor

SANDBOX_OPTIONS = {"CPUQuota": 0.5}


def run(timeout):
    print(f"start with {timeout=}")
    t0 = time.time()
    while time.time() - t0 < timeout:
        2**64 - 1


def main():
    with TransientUnitPoolExecutor(ns_options=SANDBOX_OPTIONS) as pool:
        print(pool.unit.Id)
        for _ in as_completed(
            [
                pool.submit(run, 5),
                pool.submit(run, 10),
                pool.submit(run, 15),
                pool.submit(run, 20),
                pool.submit(run, 25),
            ]
        ):
            print("finish one")


if __name__ == "__main__":
    print("hi")
    main()
