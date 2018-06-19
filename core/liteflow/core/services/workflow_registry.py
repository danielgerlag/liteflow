from typing import List
from interface import implements
from liteflow.core.models import WorkflowDefinition, Workflow
from liteflow.core.abstractions import IWorkflowRegistry
from liteflow.core.builders import WorkflowBuilder


class WorkflowRegistry(implements(IWorkflowRegistry)):

    def __init__(self):
        self.registry: List[WorkflowDefinition]= []

    def get_definition(self, id, version) -> WorkflowDefinition:
        return next(x for x in self.registry if x.id == id and x.version == version)

    def register_workflow(self, workflow: Workflow):
        builder = WorkflowBuilder()
        workflow.build(builder)
        definition = builder.build(workflow.id(), workflow.version())
        self.registry.append(definition)
