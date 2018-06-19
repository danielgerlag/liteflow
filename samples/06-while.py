from liteflow.core import *


class Hello(StepBody):
    def run(self, context: StepExecutionContext) -> ExecutionResult:
        print("Hello")
        return ExecutionResult.next()


class DoStuff(StepBody):

    def __init__(self):
        self.my_value = 0
        self.your_value = 0

    def run(self, context: StepExecutionContext) -> ExecutionResult:
        print(f"doing stuff - my value = {self.my_value}")
        self.your_value = self.my_value + 1
        return ExecutionResult.next()


class Goodbye(StepBody):
    def run(self, context: StepExecutionContext) -> ExecutionResult:
        print("goodbye")
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
            .start_with(Hello)\
            .while_(lambda data, context: data.value1 < 3)\
                .do(lambda do:\
                    do.start_with(DoStuff)\
                        .input('my_value', lambda data, context: data.value1)\
                        .output('value1', lambda step: step.your_value))\
            .then(Goodbye)


host = configure_workflow_host()
host.register_workflow(MyWorkflow())
host.start()

wid = host.start_workflow("MyWorkflow", 1, MyData())

input()
host.stop()

