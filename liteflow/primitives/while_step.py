import logging
from datetime import datetime
from liteflow.models import *
from .container_step_body import *


class While(StepBody, ContainerStepBody):

    def __init__(self):
        self.condition: bool = None
        self._logger = logging.getLogger(str(self.__class__))

    def run(self, context: StepExecutionContext) -> ExecutionResult:
        if context.persistence_data is None:
            if self.condition:
                data = ControlPersistenceData()
                data.children_active = True
                return ExecutionResult.branch([None], data)

            return ExecutionResult.next()

        if isinstance(context.persistence_data, ControlPersistenceData):
            if context.persistence_data.children_active:
                for cid in context.execution_pointer.children:
                    if not self.is_branch_complete(context.workflow.execution_pointers, cid):
                        return ExecutionResult.persist(context.persistence_data)

            return ExecutionResult.persist(None)

        raise CorruptPersistenceDataError()
