import ctypes
import os
from concurrent.futures import ProcessPoolExecutor
from functools import cached_property
from multiprocessing import Process
from multiprocessing.context import BaseContext
from pathlib import Path
from threading import Thread

import psutil
import pystemd
import pystemd.run

# resolve this better
LIBC = ctypes.CDLL("libc.so.6")

class ServiceUnitContext(BaseContext):
    _name = "fork"

    def __init__(self):
        self.unit = None
        super().__init__()

    def start_unit(self, properties):
        self.unit = pystemd.run(
            ["/bin/bash", "-c", f"exec sleep infinity"],
            user_mode=False,  # must run as root for most stuff to work... maybe not ... who knows
            extra={
                **properties,
                "Delegate": True,
            },
        )
        return self.unit

    def Process(self, **kwargs):
        return TransientUnitProcess(**kwargs, unit=self.unit)




class TransientUnitProcess(Process):
    def __init__(self, *, properties=None, unit=None, **kwargs):
        if unit:
            assert (
                not properties
            ), f"cant pass properties and unit to {self.__class__.__name__}"

        super().__init__(**kwargs)
        self.properties = properties or {}
        self.unit = unit
        self.terminate_unit_on_exit = False
        self.close_manager = False

    def _stop_unit_when_close(self):
        if not self.terminate_unit_on_exit:
            return

        self.join()
        self.unit.Unit.Stop(b"replace")

    def start(self):
        if not self.unit:
            self.unit = ServiceUnitContext().start_unit(self.properties)
            self.terminate_unit_on_exit = True

        super().start()

        # we need a better way of doing this... but, this one its good
        self.close_manager = Thread(target=self._stop_unit_when_close)
        self.close_manager.start()

    def _after_fork(self):
        # let's get the data from the unit

        unit_name = self.unit.Unit.Id
        main_pid = self.unit.Service.MainPID
        p = psutil.Process(main_pid)
        uid = p.uids().real
        gid = p.gids().real

        # attach ourselves to the cgroup
        with pystemd.SDManager() as manager:
            manager.AttachProcessesToUnit(unit_name, "/", [os.getpid()])

        # attach ourselves to the namespace
        for ns in Path(f"/proc/{main_pid}/ns").iterdir():
            LIBC.setns(os.open(ns, os.O_RDONLY), 0)

        # change the user
        os.setgid(gid)
        os.setuid(uid)

        Process._after_fork()


class TransientUnitPoolExecutor(ProcessPoolExecutor):
    def __init__(self, ns_options=None, **kwargs):
        self.ns_options = ns_options or {}
        self.pool_transient_context = ServiceUnitContext()
        super().__init__(**{**kwargs, "mp_context": self.pool_transient_context})

    def __enter__(self):
        self.unit = self.pool_transient_context.start_unit(self.ns_options)

        self.unit_name = self.unit.Unit.Names[0]
        self.main_pid = self.unit.Service.MainPID

        p = psutil.Process(self.main_pid)
        self.uid = p.uids().real
        self.gid = p.gids().real

        return super().__enter__()

    def __exit__(self, exc_type, exc_val, exc_tb):
        try:
            return super().__exit__(exc_type, exc_val, exc_tb)
        finally:
            self.unit.Unit.Stop(b"replace")
