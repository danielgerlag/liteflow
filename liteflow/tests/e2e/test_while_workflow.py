import unittest
from datetime import timedelta
from unittest.mock import MagicMock, Mock

from liteflow import configure_workflow_host
from liteflow.builders import WorkflowBuilder
from liteflow.abstractions import *
from liteflow.models import *
from .scenario_test import WorkflowScenario


class TestCounters:
    step1_counter = 0
    step2_counter = 0
    step3_counter = 0
    iterations = 0


class Step1(StepBody):
    def run(self, context: StepExecutionContext) -> ExecutionResult:
        TestCounters.step1_counter += 1
        return ExecutionResult.next()


class Step2(StepBody):
    def run(self, context: StepExecutionContext) -> ExecutionResult:
        TestCounters.step2_counter += 1
        TestCounters.iterations += 1
        return ExecutionResult.next()


class Step3(StepBody):
    def run(self, context: StepExecutionContext) -> ExecutionResult:
        TestCounters.step3_counter += 1
        return ExecutionResult.next()


class TestWorkflow(Workflow):

    def id(self):
        return "Test"

    def version(self):
        return 1

    def build(self, builder: WorkflowBuilder):
        builder\
            .start_with(Step1)\
                .while_(lambda data, context: TestCounters.iterations < 3)\
                    .do(lambda do:
                        do.start_with(Step2))\
            .then(Step3)


class WhileWorkflow(WorkflowScenario):
    def setUp(self):
        super().setUp()
        self.host.register_workflow(TestWorkflow())

    def test_scenario(self):
        wid = self.host.start_workflow("Test", 1, None)
        self.wait_for_workflow_to_complete(wid, timedelta(seconds=30))

        status = self.get_workflow_status(wid)
        self.assertEqual(status, WorkflowInstance.COMPLETE)
        self.assertEqual(TestCounters.step1_counter, 1)
        self.assertEqual(TestCounters.step2_counter, 3)
        self.assertEqual(TestCounters.step3_counter, 1)
