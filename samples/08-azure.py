import logging
from azure.storage.common import CloudStorageAccount
from liteflow.core import *
from liteflow.providers.mongo import MongoPersistenceProvider
from liteflow.providers.azure import AzureQueueProvider, AzureLockProvider


mongo = MongoPersistenceProvider('mongodb://localhost:27017/', 'liteflow')

azure_storage_account = CloudStorageAccount(is_emulated=True)
azure_queue_service = AzureQueueProvider(azure_storage_account)
azure_lock_service = AzureLockProvider(azure_storage_account)

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
            .then(Step2)


host = configure_workflow_host(persistence_service=mongo,
                               queue_service=azure_queue_service,
                               lock_service=azure_lock_service)
host.register_workflow(MyWorkflow())
host.start()

wid = host.start_workflow("MyWorkflow", 1, MyData())

input()
host.stop()

