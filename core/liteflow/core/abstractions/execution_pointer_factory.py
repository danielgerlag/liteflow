from interface import Interface
from liteflow.core.models import ExecutionPointer, WorkflowDefinition, StepOutcome


class IExecutionPointerFactory(Interface):

    def build_genesis_pointer(self, definition: WorkflowDefinition) -> ExecutionPointer:
        pass

    def build_next_pointer(self, definition: WorkflowDefinition, pointer: ExecutionPointer, outcome_target: StepOutcome) -> ExecutionPointer:
        pass

    def build_child_pointer(self, definition: WorkflowDefinition, pointer: ExecutionPointer, child_def_id: int, branch) -> ExecutionPointer:
        pass
