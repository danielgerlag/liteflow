from interface import Interface
from liteflow.core.models import *


class IWorkflowExecutor(Interface):

    def execute(self, workflow: WorkflowInstance) -> WorkflowExecutorResult:
        pass
