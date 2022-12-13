concurrentd
-------------

Ever wanted to run a section of your code in a "more restricted environment"?, maybe _a la container_... for instance, ever wanted to run a method, but
not allow it to access the internet, or to not be able to write data, or to limit the amount of cpu a single python
method can take?... well I have... so I made concurrentd just for that


show don't tell
================
In coding as in screenplay writing, the logic is show not tell. So here are a couple of practical examples

let's assume you want to execute a method, but want that method to run as a different user, using only 20% of CPU,
with no network access, and having the entire filesystem as read only (except for tmp), then this code will get you there


```python
import time
from concurrentd.transient import TransientUnitPoolExecutor


def busy_cpu(timeout):
    # doing redistricted stuff...
    t0 = time.time()
    while time.time() - t0 < timeout: 
        2**64 -1
    
if __name__ == "__main__":
    with TransientUnitPoolExecutor(ns_options={
        "PrivateTmp": True, # mounts /tmp unique to the process
        "PrivateNetwork": True, # disable network
        "CPUQuota": 0.2, # only use 20% of CPU
        "ProtectSystem": "strict", # mount filesystem as read only
        "User": "nobody" # runs code a nobody
    }) as pool:
        print('bootstrap unit', pool.unit.Id.decode())
        pool.submit(busy_cpu, timeout=5)
        pool.submit(busy_cpu, timeout=10)
        pool.submit(busy_cpu, timeout=15)

```

with this, restricted_method will be executed by the user nobody ([User](https://www.freedesktop.org/software/systemd/man/systemd.exec.html#User=)="nobody") on an environment that can't use more than 20% of CPU 
([CPUQuota](https://www.freedesktop.org/software/systemd/man/systemd.resource-control.html#CPUQuota=)=0.2), 
with no network ([PrivateNetwork](https://www.freedesktop.org/software/systemd/man/systemd.exec.html#PrivateNetwork=)=True
executes the code with only the loopback network interface), with root mounted as read only
([ProtectSystem](https://www.freedesktop.org/software/systemd/man/systemd.exec.html#ProtectSystem=)=strict) and a private view /tmp ([PrivateTmp](https://www.freedesktop.org/software/systemd/man/systemd.exec.html#PrivateTmp=)=True)that will get clean as soon as the executor has finish 


How does this works?
====================

very simple we use systemd, namespaces and cgroups to execute your code... `TransientUnitPoolExecutor` works the same as
concurrent.futures.ProcessPoolExecutor, with the only difference that when you start TransientUnitPoolExecutor, it wil create 
a systemd transient unit with the ns_options you pass. Then every time you submit work to the pool executor, it will work 
as a regular subprocess, except that after been fork, the code is moved into the namespaces of the transient unit, the cgroup
and the user and group of the process will be set to the user and group of the transient unit.

you can specify most options in [systemd.directives](https://www.freedesktop.org/software/systemd/man/systemd.directives.html).

What u need:
============
* Run as root
* Systemd
