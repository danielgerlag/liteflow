from liteflow.core import *


class Hello(StepBody):
    def run(self, context: StepExecutionContext) -> ExecutionResult:
        print("Hello")
        return ExecutionResult.next()


class DoStuff(StepBody):

    def run(self, context: StepExecutionContext) -> ExecutionResult:
        print(f"doing stuff")
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
            .if_(lambda data, context: data.value1 > 3)\
                .do(lambda x:\
                    x.start_with(DoStuff))\
            .then(Goodbye)


host = configure_workflow_host()
host.register_workflow(MyWorkflow())
host.start()

data = MyData()
data.value1 = 4
wid = host.start_workflow("MyWorkflow", 1, data)

input()
host.stop()

