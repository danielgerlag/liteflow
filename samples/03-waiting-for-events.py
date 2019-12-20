import time
from liteflow.core import *
from liteflow.providers.mongo import MongoPersistenceProvider


# mongo = MongoPersistenceProvider('mongodb://localhost:27017/', 'liteflow')


class Hello(StepBody):
    def run(self, context: StepExecutionContext) -> ExecutionResult:
        print("Hello")
        return ExecutionResult.next()


class PrintMessage(StepBody):
    def __init__(self):
        self.message = ""

    def run(self, context: StepExecutionContext) -> ExecutionResult:
        print(self.message)
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
            .then(PrintMessage) \
                .input('message', lambda data, context: "The response is %s" % data.event_result)


host = configure_workflow_host()
host.register_workflow(MyWorkflow())
host.start()

wid = host.start_workflow("MyWorkflow", 1, MyData())

time.sleep(1)

event_data = input("Enter value to publish: ")

host.publish_event('event1', 'key1', event_data)
input()
host.stop()
