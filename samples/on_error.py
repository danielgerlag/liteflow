import logging
from liteflow.core.models import *
from liteflow.core.builders import *
from liteflow.core import configure_workflow_host


class Hello(StepBody):
    def run(self, context: StepExecutionContext) -> ExecutionResult:
        print("Hello")
        return ExecutionResult.next()


class Explode(StepBody):
    def run(self, context: StepExecutionContext) -> ExecutionResult:
        print(f"exploding...")
        raise RuntimeError()


class Goodbye(StepBody):
    def run(self, context: StepExecutionContext) -> ExecutionResult:
        print("Goodbye")
        return ExecutionResult.next()


class MyWorkflow(Workflow):

    def id(self):
        return "MyWorkflow"

    def version(self):
        return 1

    def build(self, builder: WorkflowBuilder):
        builder\
            .start_with(Hello)\
            .then(Explode)\
                .on_error(WorkflowStep.RETRY, error_max_retry=1, error_retry_interval=3)\
            .then(Goodbye)


host = configure_workflow_host()
host.register_workflow(MyWorkflow())
host.start()

wid = host.start_workflow("MyWorkflow", 1, None)

input()
host.stop()

