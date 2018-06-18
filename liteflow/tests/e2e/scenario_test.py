import unittest
import time
from datetime import timedelta, datetime
from liteflow import configure_workflow_host
from liteflow.abstractions import *
from liteflow.models import *


class WorkflowScenario(unittest.TestCase):
    def setUp(self):
        self.host: IWorkflowHost = configure_workflow_host()
        self.persistence_service: IPersistenceProvider = self.host._persistence_service
        self.host.start()

    def tearDown(self):
        self.host.stop()

    def wait_for_workflow_to_complete(self, workflow_id, time_out: timedelta):
        status = self.get_workflow_status(workflow_id)
        counter = 0
        while status == WorkflowInstance.RUNNABLE and counter < (time_out.total_seconds() * 10):
            time.sleep(0.1)
            counter += 1
            status = self.get_workflow_status(workflow_id)

    def wait_for_subscription(self, event_name, event_key, time_out: timedelta):
        counter = 0
        while len(self.get_active_subscriptions(event_name, event_key)) == 0 and counter < (time_out.total_seconds() * 10):
            time.sleep(0.1)
            counter += 1

    def get_workflow_status(self, workflow_id):
        instance = self.persistence_service.get_workflow_instance(workflow_id)
        return instance.status

    def get_workflow_data(self, workflow_id):
        instance = self.persistence_service.get_workflow_instance(workflow_id)
        return instance.data

    def get_active_subscriptions(self, event_name, event_key):
        return self.persistence_service.get_subscriptions(event_name, event_key, datetime.max)
