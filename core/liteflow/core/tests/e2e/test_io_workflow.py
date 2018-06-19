import unittest
from datetime import timedelta
from unittest.mock import MagicMock, Mock

from liteflow.core import configure_workflow_host
from liteflow.core.builders import WorkflowBuilder
from liteflow.core.abstractions import *
from liteflow.core.models import *
from .scenario_test import WorkflowScenario


class TestData:
    def __init__(self):
        self.value1 = 0
        self.value2 = 0
        self.value3 = 0


class Step1(StepBody):

    def __init__(self):
        self.input1 = 0
        self.input2 = 0
        self.output = 0

    def run(self, context: StepExecutionContext) -> ExecutionResult:
        self.output = self.input1 + self.input2
        return ExecutionResult.next()


class TestWorkflow(Workflow):

    def id(self):
        return "Test"

    def version(self):
        return 1

    def build(self, builder: WorkflowBuilder):
        builder\
            .start_with(Step1) \
                .input('input1', lambda data, context: data.value1) \
                .input('input2', lambda data, context: data.value2) \
                .output('value3', lambda step: step.output)


class IOWorkflow(WorkflowScenario):
    def setUp(self):
        super().setUp()
        self.host.register_workflow(TestWorkflow())

    def test_scenario(self):
        initial_data = TestData()
        initial_data.value1 = 2
        initial_data.value2 = 3
        wid = self.host.start_workflow("Test", 1, initial_data)
        self.wait_for_workflow_to_complete(wid, timedelta(seconds=30))

        final_data = self.get_workflow_data(wid)
        self.assertEqual(final_data.value3, 5)
