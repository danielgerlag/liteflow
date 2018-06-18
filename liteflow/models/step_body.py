from abc import ABCMeta, abstractmethod
from .execution_pointer import ExecutionPointer
from .execution_result import ExecutionResult
from .workflow_instance import WorkflowInstance


class StepExecutionContext:
    def __init__(self, workflow, step, persistence_data, execution_pointer):
        self.persistence_data = persistence_data
        self.step = step
        self.workflow: WorkflowInstance = workflow
        self.execution_pointer: ExecutionPointer = execution_pointer


class StepBody:
    __metaclass__ = ABCMeta

    @abstractmethod
    def run(self, context: StepExecutionContext) -> ExecutionResult:
        raise NotImplementedError
