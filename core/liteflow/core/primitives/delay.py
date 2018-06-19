import logging
from datetime import datetime
from liteflow.core.models import *


class Delay(StepBody):

    def __init__(self):
        self.duration = None
        self._logger = logging.getLogger(str(self.__class__))

    def run(self, context: StepExecutionContext) -> ExecutionResult:
        if context.persistence_data is not None:
            return ExecutionResult.next()

        return ExecutionResult.sleep_for(self.duration, True)
