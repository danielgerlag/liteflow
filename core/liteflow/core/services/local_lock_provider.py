from interface import implements
import threading
from typing import List
from liteflow.core.abstractions import ILockProvider


class LocalLockProvider(implements(ILockProvider)):

    def __init__(self):
        self._locks: List[str] = []
        self.lock = threading.Lock()

    def acquire_lock(self, resource) -> bool:
        self.lock.acquire()
        try:
            if self._locks.__contains__(resource):
                return False
            else:
                self._locks.append(resource)
                return True
        finally:
            self.lock.release()

    def release_lock(self, resource):
        self.lock.acquire()
        try:
            if self._locks.__contains__(resource):
                self._locks.remove(resource)
        finally:
            self.lock.release()

    def shutdown(self):
        pass
