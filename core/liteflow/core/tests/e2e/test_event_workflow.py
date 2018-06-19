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
        self.result = None


class TestCounters:
    step1_counter = 0
    step2_counter = 0


class Step1(StepBody):
    def run(self, context: StepExecutionContext) -> ExecutionResult:
        TestCounters.step1_counter += 1
        return ExecutionResult.next()


class Step2(StepBody):
    def run(self, context: StepExecutionContext) -> ExecutionResult:
        TestCounters.step2_counter += 1
        return ExecutionResult.next()


class TestWorkflow(Workflow):

    def id(self):
        return "Test"

    def version(self):
        return 1

    def build(self, builder: WorkflowBuilder):
        builder\
            .start_with(Step1) \
            .wait_for('event1', lambda data, context: 'key1') \
                .output('result', lambda step: step.event_data) \
            .then(Step2)


class EventWorkflow(WorkflowScenario):
    def setUp(self):
        super().setUp()
        self.host.register_workflow(TestWorkflow())

    def test_scenario(self):
        wid = self.host.start_workflow("Test", 1, TestData())
        self.wait_for_subscription('event1', 'key1', timedelta(seconds=30))
        self.host.publish_event('event1', 'key1', "abc")
        self.wait_for_workflow_to_complete(wid, timedelta(seconds=30))

        status = self.get_workflow_status(wid)
        final_data = self.get_workflow_data(wid)
        self.assertEqual(status, WorkflowInstance.COMPLETE)
        self.assertEqual(TestCounters.step1_counter, 1)
        self.assertEqual(TestCounters.step2_counter, 1)
        self.assertEqual(final_data.result, "abc")

