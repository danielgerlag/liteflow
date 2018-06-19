from liteflow.core import *


class Hello(StepBody):
    def run(self, context: StepExecutionContext) -> ExecutionResult:
        print("Hello world")
        return ExecutionResult.next()


class Goodbye(StepBody):
    def run(self, context: StepExecutionContext) -> ExecutionResult:
        print("Goodbye")
        return ExecutionResult.next()


class AddNumbers(StepBody):
    def __init__(self):
        self.input1 = 0
        self.input2 = 0
        self.output = 0

    def run(self, context: StepExecutionContext) -> ExecutionResult:
        self.output = self.input1 + self.input2
        return ExecutionResult.next()


class MyData:
    def __init__(self):
        self.value1 = 0
        self.value2 = 0
        self.value3 = 0


class MyWorkflow(Workflow):

    def id(self):
        return "MyWorkflow"

    def version(self):
        return 1

    def build(self, builder: WorkflowBuilder):
        builder\
            .start_with(Hello)\
            .then(AddNumbers) \
                .input('input1', lambda data, context: data.value1) \
                .input('input2', lambda data, context: data.value2) \
                .output('value3', lambda step: step.output) \
            .then(Goodbye)


host = configure_workflow_host()
host.register_workflow(MyWorkflow())
host.start()

data = MyData()
data.value1 = 2
data.value2 = 3

wid = host.start_workflow("MyWorkflow", 1, data)

input()
host.stop()
