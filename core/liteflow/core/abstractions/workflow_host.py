from datetime import datetime
from interface import Interface
from liteflow.core.models import Workflow

class IWorkflowHost(Interface):

    def register_workflow(self, workflow: Workflow):
        pass

    def start_workflow(self, workflow_id, version, data):
        pass

    def publish_event(self, event_name, event_key, event_data=object(), effective_date=None):
        pass

    def start(self):
        pass

    def stop(self):
        pass