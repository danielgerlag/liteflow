from interface import Interface
from ..models import *

class IPersistenceProvider(Interface):

    def create_workflow(self, workflow: WorkflowInstance):
        pass

    def persist_workflow(self, workflow: WorkflowInstance):
        pass

    def get_workflow_instance(self, id) -> WorkflowInstance:
        pass

    def get_runnable_instances(self) -> []:
        pass

    def create_subscription(self, subscription: EventSubscription):
        pass

    def get_subscriptions(self, event_name, event_key, effective_date) -> []:
        pass

    def terminate_subscription(self, subscription_id):
        pass

    def create_event(self, evt: Event):
        pass

    def get_event(self, event_id) -> Event:
        pass

    def get_events(self, event_name, event_key, effective_date) -> []:
        pass

    def mark_event_processed(self, event_id):
        pass

    def mark_event_unprocessed(self, event_id):
        pass

    def get_runnable_events(self, effective_date) -> []:
        pass

    def persist_errors(self, errors: []):
        pass
