from typing import List, TypeVar, Generic
from .step_outcome import StepOutcome
from .execution_pointer import ExecutionPointer


T = TypeVar('T')


class WorkflowStep(Generic[T]):
    RETRY = 0
    SUSPEND = 1
    TERMINATE = 2
    COMPENSATE = 3

    def __init__(self, body: T):
        self.id = None
        self.body = body
        self.name = None
        self.error_behavior = WorkflowStep.RETRY
        self.outcomes: List[StepOutcome] = []
        self.children = []
        self.inputs: List[IOMapping] = []
        self.outputs: List[IOMapping] = []

    def prime_for_retry(self, pointer: ExecutionPointer):
        pass


class IOMapping:
    def __init__(self):
        self.property: property = None
        self.value: function = None
