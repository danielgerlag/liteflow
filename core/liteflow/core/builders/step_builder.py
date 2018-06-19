from datetime import datetime
from typing import TypeVar, Generic, Callable, Any, List
from liteflow.core.models import WorkflowStep, StepOutcome, IOMapping, StepExecutionContext
from liteflow.core.primitives import *

TStep = TypeVar('T', WorkflowStep, WorkflowStep)
TNewStep = TypeVar('T', WorkflowStep, WorkflowStep)


class StepBuilder(Generic[TStep]):
    def __init__(self, step: TStep, workflow_builder):
        self.step = step
        self.workflow_builder = workflow_builder

    def then(self, body: TNewStep) -> 'StepBuilder[TNewStep]':
        new_step = WorkflowStep(body)
        new_step.body = body
        self.workflow_builder.add_step(new_step)

        outcome = StepOutcome()
        outcome.next_step = new_step.id
        self.step.outcomes.append(outcome)

        return StepBuilder[TStep](new_step, self.workflow_builder)

    def input(self, property_name: str, value: Callable[[Any, StepExecutionContext], Any]) -> 'StepBuilder[TStep]':
        mapping = IOMapping()
        mapping.property = property_name
        mapping.value = value
        self.step.inputs.append(mapping)
        return self

    def output(self, property_name: str, value: Callable[[TStep], Any]) -> 'StepBuilder[TStep]':
        mapping = IOMapping()
        mapping.property = property_name
        mapping.value = value
        self.step.outputs.append(mapping)
        return self

    def if_(self, condition: Callable[[Any, StepExecutionContext], bool]):
        new_step = WorkflowStep(If)
        new_step.body = If
        self.workflow_builder.add_step(new_step)
        step_builder = StepBuilder[TStep](new_step, self.workflow_builder)
        step_builder.input('condition', condition)
        outcome = StepOutcome()
        outcome.next_step = new_step.id
        self.step.outcomes.append(outcome)

        return step_builder

    def wait_for(self, event_name: str, event_key: Callable[[Any, StepExecutionContext], Any], effective_date=lambda data, context: datetime.utcnow()) -> 'StepBuilder[WaitFor]':
        new_step = WorkflowStep(WaitFor)
        new_step.body = WaitFor
        self.workflow_builder.add_step(new_step)

        step_builder = StepBuilder[TStep](new_step, self.workflow_builder)
        step_builder.input('event_name', lambda data, context: event_name)
        step_builder.input('event_key', event_key)
        step_builder.input('effective_date', effective_date)

        outcome = StepOutcome()
        outcome.next_step = new_step.id
        self.step.outcomes.append(outcome)

        return step_builder

    def while_(self, condition: Callable[[Any, StepExecutionContext], bool]):
        new_step = WorkflowStep(While)
        new_step.body = While
        self.workflow_builder.add_step(new_step)
        step_builder = StepBuilder[TStep](new_step, self.workflow_builder)
        step_builder.input('condition', condition)
        outcome = StepOutcome()
        outcome.next_step = new_step.id
        self.step.outcomes.append(outcome)

        return step_builder

    def for_each(self, collection: Callable[[Any, StepExecutionContext], List]):
        new_step = WorkflowStep(Foreach)
        new_step.body = Foreach
        self.workflow_builder.add_step(new_step)
        step_builder = StepBuilder[TStep](new_step, self.workflow_builder)
        step_builder.input('collection', collection)
        outcome = StepOutcome()
        outcome.next_step = new_step.id
        self.step.outcomes.append(outcome)

        return step_builder

    def on_error(self, error_behavior):
        self.step.error_behavior = error_behavior
        return self

    def do(self, builder: Callable):
        builder(self.workflow_builder)
        self.step.children.append(self.step.id + 1)
        return self
