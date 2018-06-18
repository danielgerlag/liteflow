import logging
from liteflow.models import *
from liteflow.builders import *
from liteflow import configure_workflow_host
from liteflowmongo.mongo_persistence_provider import MongoPersistenceProvider

mongo = MongoPersistenceProvider('mongodb://localhost:27017/', 'pyflow')


class Step1(StepBody):

    def __init__(self):
        self.my_value = 0
        self.your_value = 0

    def run(self, context: StepExecutionContext) -> ExecutionResult:
        print(f"step 1 - my value = {self.my_value}")
        self.your_value = self.my_value + 1
        return ExecutionResult.next()


class Step2(StepBody):
    def run(self, context: StepExecutionContext) -> ExecutionResult:
        print("step 2")
        return ExecutionResult.next()


class MyData:

    def __init__(self):
        self.value1 = 0


class MyWorkflow(Workflow):

    def id(self):
        return "MyWorkflow"

    def version(self):
        return 1

    def build(self, builder: WorkflowBuilder):
        builder\
            .start_with(Step1)\
                .input('my_value', lambda data, context: 5)\
                .output('value1', lambda step: step.your_value)\
            .wait_for('my_event', lambda data, context: 'my key')\
            .then(Step2)

# start


logging.basicConfig(level=logging.INFO)
host = configure_workflow_host(persistence_service=mongo)
host.register_workflow(MyWorkflow())
host.start()

wid = host.start_workflow("MyWorkflow", 1, MyData())
data = input("enter value to publish:")
host.publish_event("my_event", "my key")
input("Press enter to shutdown")
host.stop()

