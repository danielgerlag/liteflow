from typing import List
from interface import Interface
from liteflow.core.models import WorkflowDefinition, Workflow


class IWorkflowRegistry(Interface):

    def get_definition(self, id, version) -> WorkflowDefinition:
        pass

    def register_workflow(self, workflow: Workflow):
        pass
