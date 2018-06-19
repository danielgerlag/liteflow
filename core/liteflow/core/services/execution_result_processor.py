from datetime import datetime, timedelta
import logging
from interface import implements
from liteflow.core.models import WorkflowInstance, WorkflowDefinition, ExecutionPointer, WorkflowStep, ExecutionResult,\
    WorkflowExecutorResult, EventSubscription
from liteflow.core.abstractions import IExecutionResultProcessor, IExecutionPointerFactory


class ExecutionResultProcessor(implements(IExecutionResultProcessor)):

    def __init__(self, pointer_factory: IExecutionPointerFactory):
        self._pointer_factory = pointer_factory
        self._logger = logging.getLogger(str(self.__class__))

    def process_execution_result(self, workflow: WorkflowInstance, definition: WorkflowDefinition, pointer: ExecutionPointer, step: WorkflowStep, result: ExecutionResult, workflow_result: WorkflowExecutorResult):
        pointer.persistence_data = result.persistence_data
        pointer.outcome = result.outcome_value

        if result.sleep_for is None:
            pointer.status = ExecutionPointer.SLEEPING
            pointer.sleep_until = datetime.utcnow()

        if result.event_name is not None:
            pointer.event_name = result.event_name
            pointer.event_key = result.event_key
            pointer.active = False
            pointer.status = ExecutionPointer.WAITING

            subscription = EventSubscription()
            subscription.workflow_id = workflow.id
            subscription.step_id = pointer.step_id
            subscription.event_name = pointer.event_name
            subscription.event_key = pointer.event_key
            subscription.subscribe_as_of = result.event_as_of

            workflow_result.subscriptions.append(subscription)

        if result.proceed:
            pointer.active = False
            pointer.end_time = datetime.utcnow()
            pointer.status = ExecutionPointer.COMPLETE

            for target in (x for x in step.outcomes if ((x.get_value(workflow.data) == result.outcome_value) or (x.get_value(workflow.data) is None) )):
                new_pointer = self._pointer_factory.build_next_pointer(definition, pointer, target)
                workflow.execution_pointers.append(new_pointer)

        else:
            for branch in result.branch_values:
                for child_id in step.children:
                    new_pointer = self._pointer_factory.build_child_pointer(definition, pointer, child_id, branch)
                    workflow.execution_pointers.append(new_pointer)

    def handle_step_exception(self, workflow: WorkflowInstance, definition: WorkflowDefinition, pointer: ExecutionPointer, step: WorkflowStep):
        pointer.status = ExecutionPointer.FAILED

        if step.error_behavior == WorkflowStep.RETRY:
            pointer.retry_count += 1
            pointer.sleep_until = datetime.utcnow() + timedelta(seconds=10) #TODO: make confiurable
            step.prime_for_retry(pointer)
        elif step.error_behavior == WorkflowStep.SUSPEND:
            workflow.status = WorkflowInstance.SUSPENDED
        elif step.error_behavior == WorkflowStep.TERMINATE:
            workflow.status = WorkflowInstance.TERMINATED
