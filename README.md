multiprocessd
-------------

Ever wanted to run a peace of code in a "more restricted environment"?, _a la container_... for instance, ever wanted tp run a method, but
not allow it to access the internet, or to not be able to write data, or to limit the amount of cpu a single python
method can take?... well I have... and I made multiprocessd just for that


show don't tell
================
In coding as in screenplay writing, the logix is show not tell. so here are a couple of practical examples

let's assume you want to execute a method, but want that method to run as a different user, using only 20% of CPU,
with no network access, and having the entire filesystem as read only (except for tmp), then this code will get you there


```python
import time
from multiprocessd import NSProcessPoolExecutor


def busy_cpu(timeout):
    # doing redistricted stuff...
    t0 = time.time()
    while time.time() - t0 < timeout: 
        2**64 -1
    
if __name__ == "__main__":
    with NSProcessPoolExecutor(ns_options={
        "PrivateTmp": True, # mounts /tmp unique to the process
        "PrivateNetwork": True, # disable network
        "CPUQuota": 0.2, # only use 20% of CPU
        "ProtectSystem": "strict", # mount filesystem as read only
        "User": "nobody" # runs code a nobody
    }) as pool:
        print('bootstrap unit', pool.unit.Id.decode())
        pool.submit(busy_cpu, timeout=2)
        pool.submit(busy_cpu, timeout=3)

```

with this, restricted_method will be executed on an environment that cant use more than 20% of CPU 
([CPUQuota](https://www.freedesktop.org/software/systemd/man/systemd.resource-control.html#CPUQuota=)=0.2), 
with no network ([PrivateNetwork](https://www.freedesktop.org/software/systemd/man/systemd.exec.html#PrivateNetwork=)=True
executes the code with only the loopback network interface), with the os mounted as read only
([ProtectSystem](https://www.freedesktop.org/software/systemd/man/systemd.exec.html#ProtectSystem=)=strict) 


How does this works?
====================

very simple we use systemd, namespaces and cgroups to execute your code... `NSProcessPoolExecutor` works the same as
concurrent.futures.ProcessPoolExecutor, with the only difference that when you start NSProcessPoolExecutor, it wil create 
a systemd transient unit with the ns_options you pass. Then every time you submit work to the pool executor, it will work 
as a regular process, except that after been fork, the code is moved into the namespaces of the transient unit, the cgroup
and the user and group of the process will be set to the user and group of the transient unit.