import unittest
import logging
from typing import Callable
from unittest.mock import MagicMock, Mock
from liteflow.core.models import *
from liteflow.core.services import *


class MockStep(StepBody):

    executions = []

    def run(self, context: StepExecutionContext):
        MockStep.executions.append(context.execution_pointer)
        return ExecutionResult.next()


class WorkflowExecutorTestCase(unittest.TestCase):
    def setUp(self):
        self._execution_result_processor = Mock()
        self._registry = Mock()
        self._subject = WorkflowExecutor(self._execution_result_processor, self._registry, logging.root)
        MockStep.executions = []

    def test_execute_active_step(self):

        step = WorkflowStep(MockStep)
        step.id = 0
        step.body = MockStep
        self.given_1_step_workflow(step, "Test", 1)
        pointer = ExecutionPointer()
        pointer.active = True
        pointer.step_id = 0
        instance = WorkflowInstance()
        instance.workflow_definition_id = "Test"
        instance.version = 1
        instance.status = WorkflowInstance.RUNNABLE
        instance.next_execution = 0
        instance.id = 1
        instance.execution_pointers = [pointer]
        self._execution_result_processor.process_execution_result.return_value = WorkflowExecutorResult()

        self._subject.execute(instance)

        #self._execution_result_processor.process_execution_result.assert_called_once_with(workflow=instance, pointer=pointer, step=step)
        self.assertIn(pointer, MockStep.executions)

    def test_not_execute_inactive_step(self):

        step = WorkflowStep(MockStep)
        step.id = 0
        step.body = MockStep
        self.given_1_step_workflow(step, "Test", 1)
        pointer = ExecutionPointer()
        pointer.active = False
        pointer.step_id = 0
        instance = WorkflowInstance()
        instance.workflow_definition_id = "Test"
        instance.version = 1
        instance.status = WorkflowInstance.RUNNABLE
        instance.next_execution = 0
        instance.id = 1
        instance.execution_pointers = [pointer]
        self._execution_result_processor.process_execution_result.return_value = WorkflowExecutorResult()

        self._subject.execute(instance)

        self.assertNotIn(pointer, MockStep.executions)

    def given_1_step_workflow(self, step, id, version):
        definition = WorkflowDefinition()
        definition.id = id
        definition.version = version
        definition.steps = [step]
        self._registry.get_definition.return_value = definition
