import logging
import datetime
from interface import implements
from liteflow.core.models import *
from liteflow.core.abstractions import *


class WorkflowExecutor(implements(IWorkflowExecutor)):

    def __init__(self, result_processor: IExecutionResultProcessor, registry: IWorkflowRegistry):
        self._registry = registry
        self._result_processor = result_processor
        self._logger = logging.getLogger(str(self.__class__))

    def execute(self, workflow: WorkflowInstance) -> WorkflowExecutorResult:
        self._logger.log(logging.DEBUG, f"Executing workflow {workflow.id}")
        wf_result = WorkflowExecutorResult()

        exe_pointers = [x for x in workflow.execution_pointers if x.active and (x.sleep_until is None or x.sleep_until < datetime.datetime.utcnow())]

        definition = self._registry.get_definition(workflow.workflow_definition_id, workflow.version)

        if definition is None:
            logging.log(logging.ERROR, "Workflow {0} version {1} is not registered".format(workflow.workflow_definition_id, workflow.version))
            return

        for pointer in exe_pointers:
            step: WorkflowStep = ([x for x in definition.steps if x.id == pointer.step_id][:1] or [None])[0]
            if step is not None:
                try:
                    pointer.status = ExecutionPointer.RUNNING
                    if pointer.start_time is None:
                        pointer.start_time = datetime.datetime.utcnow()

                    logging.log(logging.DEBUG, "Starting step {0} on workflow {1}".format(step.name, workflow.id))

                    context = StepExecutionContext(workflow, step, pointer.persistence_data, pointer)
                    body: StepBody = step.body()
                    process_inputs(workflow, step, body, context)
                    result = body.run(context)

                    if result.proceed:
                        process_outputs(workflow, step, body)

                    self._result_processor.process_execution_result(workflow, definition, pointer, step, result, wf_result)

                except Exception as err:
                    logging.log(logging.ERROR, str(err))
                    errEx = ExecutionError()
                    errEx.workflow_id = workflow.id
                    errEx.execution_pointer_id = pointer.id
                    errEx.error_time = datetime.datetime.utcnow()
                    errEx.message = str(err)
                    self._result_processor.handle_step_exception(workflow, definition,pointer, step)

            else:
                logging.log(logging.ERROR, f"Unable to find step {pointer.step_id} in workflow definition")
                pointer.sleep_until = datetime.datetime.utcnow() + datetime.timedelta(minutes=1) #TODO: make configurable

        #TODO: ProcessAfterExecutionIteration
        determine_next_execution_time(workflow)
        return wf_result


def process_inputs(workflow: WorkflowInstance, step: WorkflowStep, body: StepBody, context: StepExecutionContext):
    for step_input in step.inputs:
        setattr(body, step_input.property, step_input.value(workflow.data, context))


def process_outputs(workflow: WorkflowInstance, step: WorkflowStep, body: StepBody):
    for step_output in step.outputs:
        setattr(workflow.data, step_output.property, step_output.value(body))


def determine_next_execution_time(workflow: WorkflowInstance):
    workflow.next_execution = None

    if workflow.status == WorkflowInstance.COMPLETE:
        return

    for pointer in [x for x in workflow.execution_pointers if x.active and len(x.children) == 0]:
        if pointer.sleep_until is None:
            workflow.next_execution = 0
            return

    if workflow.next_execution is None:
        for pointer in [x for x in workflow.execution_pointers if x.active and len(x.children) > 0]:
            children = []
            for ep in workflow.execution_pointers:
                if any(c == ep.id for c in pointer.children):
                    children.append(ep)

            if all(c.end_time is not None for c in children):
                if pointer.sleep_until is None:
                    workflow.next_execution = 0
                    return
                workflow.next_execution = min(pointer.sleep_until, workflow.next_execution or pointer.sleep_until)

    if workflow.next_execution is None and all(x.end_time is not None for x in workflow.execution_pointers):
        workflow.status = WorkflowInstance.COMPLETE
        workflow.complete_time = datetime.datetime.utcnow()
