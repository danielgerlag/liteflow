import logging
from datetime import datetime
from liteflow.core.models import *
from .container_step_body import *


class SchedulePersistenceData:
    def __init__(self):
        self.elapsed = False


class Schedule(StepBody, ContainerStepBody):

    def __init__(self):
        self.interval = None
        self._logger = logging.getLogger(str(self.__class__))

    def run(self, context: StepExecutionContext) -> ExecutionResult:
        if context.persistence_data is None:
            data = SchedulePersistenceData()
            data.elapsed = False
            return ExecutionResult.sleep(self.interval, data)

        if isinstance(context.persistence_data, SchedulePersistenceData):
            if not context.persistence_data.elapsed:
                data = SchedulePersistenceData()
                data.elapsed = True
                return ExecutionResult.branch([None], self.interval, data)

            complete = True
            for cid in context.execution_pointer.children:
                complete = complete and self.is_branch_complete(context.workflow.execution_pointers, cid)

            if complete:
                return ExecutionResult.next()

            return ExecutionResult.persist(context.persistence_data)

        raise CorruptPersistenceDataError()
