import logging
from liteflow.core.models import *
from .container_step_body import *


class Foreach(StepBody, ContainerStepBody):

    def __init__(self):
        self.collection: List = []
        self._logger = logging.getLogger(str(self.__class__))

    def run(self, context: StepExecutionContext) -> ExecutionResult:
        if context.persistence_data is None:
            data = ControlPersistenceData()
            data.children_active = True
            return ExecutionResult.branch(self.collection, data)

        if isinstance(context.persistence_data, ControlPersistenceData):
            if context.persistence_data.children_active:
                complete = True
                for cid in context.execution_pointer.children:
                    complete = complete and self.is_branch_complete(context.workflow.execution_pointers, cid)

                if complete:
                    return ExecutionResult.next()

        return ExecutionResult.persist(context.persistence_data)
