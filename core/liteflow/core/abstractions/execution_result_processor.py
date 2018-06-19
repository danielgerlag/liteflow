from interface import Interface
from liteflow.core.models import WorkflowInstance, WorkflowDefinition, ExecutionPointer, WorkflowStep, ExecutionResult, WorkflowExecutorResult, EventSubscription


class IExecutionResultProcessor(Interface):

    def process_execution_result(self, workflow: WorkflowInstance, definition: WorkflowDefinition, pointer: ExecutionPointer, step: WorkflowStep, result: ExecutionResult, workflow_result: WorkflowExecutorResult):
        pass

    def handle_step_exception(self, workflow: WorkflowInstance, definition: WorkflowDefinition, pointer: ExecutionPointer, step: WorkflowStep):
        pass
