from interface import Interface
from liteflow.models import *


class IWorkflowExecutor(Interface):

    def execute(self, workflow: WorkflowInstance) -> WorkflowExecutorResult:
        pass
