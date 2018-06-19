from typing import List
from liteflow.core.models.execution_pointer import ExecutionPointer


class WorkflowInstance:

    RUNNABLE = 0
    SUSPENDED = 1
    COMPLETE = 2
    TERMINATED = 3

    def __init__(self):
        self.id = None
        self.workflow_definition_id = None
        self.version = None
        self.description = None
        self.next_execution = None
        self.status = None
        self.data = None
        self.create_time = None
        self.complete_time = None
        self.execution_pointers: List[ExecutionPointer] = []


