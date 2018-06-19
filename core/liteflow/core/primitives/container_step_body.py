from collections import deque
from typing import List
from liteflow.core.models import *


class ControlPersistenceData:
    def __init__(self):
        self.children_active = False


class CorruptPersistenceDataError(RuntimeError):
    pass


class ContainerStepBody:
    def is_branch_complete(self, pointers: List[ExecutionPointer], root_id) -> bool:
        root = next(x for x in pointers if x.id == root_id)
        if root.end_time is None:
            return False

        queue = deque(x for x in pointers if x.predecessor_id == root_id)

        while len(queue) > 0:
            item = queue.pop()
            if item.end_time is None:
                return False

            for child in (x for x in pointers if x.predecessor_id == item.id):
                queue.appendleft(child)

        return True
