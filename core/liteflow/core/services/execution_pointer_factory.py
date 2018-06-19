from interface import implements
import uuid
from liteflow.core.abstractions import IExecutionPointerFactory
from liteflow.core.models import ExecutionPointer, WorkflowDefinition, StepOutcome


class ExecutionPointerFactory(implements(IExecutionPointerFactory)):

    def build_genesis_pointer(self, definition: WorkflowDefinition) -> ExecutionPointer:
        result = ExecutionPointer()
        result.id = uuid.uuid4()
        result.step_id = 0
        result.active = True
        result.status = ExecutionPointer.PENDING
        return result

    def build_next_pointer(self, definition: WorkflowDefinition, pointer: ExecutionPointer, outcome_target: StepOutcome) -> ExecutionPointer:
        result = ExecutionPointer()
        result.id = uuid.uuid4()
        result.step_id = outcome_target.next_step
        result.active = True
        result.status = ExecutionPointer.PENDING
        result.context_item = pointer.context_item
        result.predecessor_id = pointer.id
        result.scope.extend(pointer.scope)
        return result

    def build_child_pointer(self, definition: WorkflowDefinition, pointer: ExecutionPointer, child_def_id: int, branch) -> ExecutionPointer:
        child_pointer_id = uuid.uuid4()
        child_scope = []
        child_scope.extend(pointer.scope)
        child_scope.append(pointer.id)
        pointer.children.append(child_pointer_id)

        result = ExecutionPointer()
        result.id = child_pointer_id
        result.predecessor_id = pointer.id
        result.step_id = child_def_id
        result.active = True
        result.status = ExecutionPointer.PENDING
        result.context_item = branch
        result.scope = child_scope
        return result
