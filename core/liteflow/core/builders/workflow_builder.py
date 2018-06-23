from typing import List
from typing import TypeVar, Generic
from liteflow.core.models import WorkflowStep, WorkflowDefinition
from liteflow.core.builders.step_builder import StepBuilder

TStep = TypeVar('T', WorkflowStep, WorkflowStep)


class WorkflowBuilder:
    def __init__(self):
        self.steps: List[WorkflowStep] = []

    def build(self, id, version) -> WorkflowDefinition:
        result = WorkflowDefinition()
        result.id = id
        result.version = version
        result.steps = self.steps
        return result

    def add_step(self, step: WorkflowStep):
        step.id = len(self.steps)
        self.steps.append(step)

    def start_with(self, body: TStep) -> StepBuilder[TStep]:
        new_step = WorkflowStep(body)
        new_step.body = body
        self.add_step(new_step)
        return StepBuilder[TStep](new_step, self)