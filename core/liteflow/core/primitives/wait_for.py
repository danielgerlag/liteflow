import logging
from datetime import datetime
from liteflow.core.models import *


class WaitFor(StepBody):

    def __init__(self):
        self.event_name = None
        self.event_key = None
        self.effective_date = None
        self.event_data = None
        self._logger = logging.getLogger(str(self.__class__))

    def run(self, context: StepExecutionContext) -> ExecutionResult:
        if not context.execution_pointer.event_published:
            effective_date = datetime.min
            if self.effective_date is not None:
                effective_date = self.effective_date

            return ExecutionResult.wait_for_event(self.event_name, self.event_key, effective_date)

        self.event_data = context.execution_pointer.event_data
        return ExecutionResult.next()
