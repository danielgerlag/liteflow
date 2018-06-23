import unittest
import logging
from datetime import datetime
from unittest.mock import MagicMock, Mock
from liteflow.core.models import *
from liteflow.core.services import *


class ProcessExecutionResultTestCase(unittest.TestCase):
    def setUp(self):
        self._pointer_factory = Mock()
        self._subject = ExecutionResultProcessor(self._pointer_factory, logging.root)

    def test_advance_workflow(self):
        definition = WorkflowDefinition()
        pointer1 = build_pointer(0, True, ExecutionPointer.RUNNING)
        pointer2 = build_pointer(1, False, ExecutionPointer.PENDING)
        outcome = StepOutcome()
        outcome.next_step = 1
        step = WorkflowStep(StepBody)
        step.outcomes = [outcome]
        self._pointer_factory.build_next_pointer.return_value = pointer2
        workflow = given_workflow([pointer1])
        wf_result = WorkflowExecutorResult()

        self._subject.process_execution_result(workflow, definition, pointer1, step, ExecutionResult.next(), wf_result)

        self.assertFalse(pointer1.active)
        self.assertEqual(pointer1.status, ExecutionPointer.COMPLETE)
        self.assertIsNotNone(pointer1.end_time)
        self.assertIn(pointer2, workflow.execution_pointers)
        self._pointer_factory.build_next_pointer.assert_called()

    def test_set_persistence_data(self):
        persistence_data = "abc"
        definition = WorkflowDefinition()
        pointer1 = build_pointer(0, True, ExecutionPointer.RUNNING)
        step = WorkflowStep(StepBody)
        workflow = given_workflow([pointer1])
        wf_result = WorkflowExecutorResult()

        self._subject.process_execution_result(workflow, definition, pointer1, step, ExecutionResult.persist(persistence_data), wf_result)

        self.assertEqual(pointer1.persistence_data, persistence_data)
        self.assertIsNone(pointer1.end_time)

    def test_subscribe_to_event(self):
        definition = WorkflowDefinition()
        pointer1 = build_pointer(0, True, ExecutionPointer.RUNNING)
        step = WorkflowStep(StepBody)
        workflow = given_workflow([pointer1])
        wf_result = WorkflowExecutorResult()

        self._subject.process_execution_result(workflow, definition, pointer1, step, ExecutionResult.wait_for_event("Event", "Key", datetime.utcnow()), wf_result)

        self.assertTrue(any(x for x in wf_result.subscriptions if x.step_id == pointer1.step_id and x.event_name == "Event" and x.event_key == "Key"))
        self.assertEqual(pointer1.status, ExecutionPointer.WAITING)
        self.assertEqual(pointer1.event_name, "Event")
        self.assertEqual(pointer1.event_key, "Key")
        self.assertFalse(pointer1.active)
        self.assertIsNone(pointer1.end_time)


def build_pointer(id, active, status):
    result = ExecutionPointer()
    result.id = id
    result.active = active
    result.status = status
    return result


def given_workflow(pointers):
    result = WorkflowInstance()
    result.status = WorkflowInstance.RUNNABLE
    result.execution_pointers.extend(pointers)
    return result
