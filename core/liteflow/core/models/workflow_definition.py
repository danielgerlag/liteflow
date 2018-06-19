from typing import List
from .workflow_step import WorkflowStep


class WorkflowDefinition:
    def __init__(self):
        self.id = None
        self.version = 1
        self.description = None
        self.steps: List[WorkflowStep] = []
