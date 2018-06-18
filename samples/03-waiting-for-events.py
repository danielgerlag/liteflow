import logging
from liteflow.models import *
from liteflow.builders import *
from liteflow import configure_workflow_host


class Hello(StepBody):
    def run(self, context: StepExecutionContext) -> ExecutionResult:
        print("Hello world")
        return ExecutionResult.next()


class Goodbye(StepBody):
    def run(self, context: StepExecutionContext) -> ExecutionResult:
        print("Goodbye")
        return ExecutionResult.next()


class MyData:
    def __init__(self):
        self.event_result = None


class MyWorkflow(Workflow):

    def id(self):
        return "MyWorkflow"

    def version(self):
        return 1

    def build(self, builder: WorkflowBuilder):
        builder\
            .start_with(Hello) \
            .wait_for('event1', lambda data, context: 'key1') \
                .output('event_result', lambda step: step.event_data) \
            .then(Goodbye)


host = configure_workflow_host()
host.register_workflow(MyWorkflow())
host.start()

wid = host.start_workflow("MyWorkflow", 1, MyData())

event_data = input("Enter value to publish")

host.publish_event('event1', 'key1', event_data)
input()
host.stop()
