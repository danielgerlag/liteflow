from interface import implements
from typing import List
import uuid
import threading
from liteflow.core.abstractions import IPersistenceProvider
from liteflow.core.models import WorkflowInstance, EventSubscription, Event


class MemoryPersistenceProvider(implements(IPersistenceProvider)):

    def __init__(self):
        self._workflows: List[WorkflowInstance] = []
        self._events: List[Event] = []
        self._subscriptions: List[EventSubscription] = []
        self.lock = threading.Lock()

    def create_workflow(self, workflow: WorkflowInstance):
        self.lock.acquire()
        try:
            workflow.id = str(uuid.uuid4())
            self._workflows.append(workflow)
            return workflow.id
        finally:
            self.lock.release()

    def persist_workflow(self, workflow: WorkflowInstance):
        self.lock.acquire()
        try:
            for old in [x for x in self._workflows if x.id == workflow.id]:
                self._workflows.remove(old)
            self._workflows.append(workflow)
        finally:
            self.lock.release()

    def get_workflow_instance(self, id) -> WorkflowInstance:
        self.lock.acquire()
        try:
            for wf in [x for x in self._workflows if x.id == id]:
                return wf
        finally:
            self.lock.release()

    def get_runnable_instances(self) -> []:
        result = []
        self.lock.acquire()
        try:
            for wf in [x for x in self._workflows if x.status == WorkflowInstance.RUNNABLE]:
                result.append(wf.id)
            return result
        finally:
            self.lock.release()

    def create_subscription(self, subscription: EventSubscription):
        subscription.id = str(uuid.uuid4())
        self._subscriptions.append(subscription)
        return subscription.id

    def get_subscriptions(self, event_name, event_key, effective_date) -> []:
        result = []
        for sub in [x for x in self._subscriptions if x.event_name == event_name and x.event_key == event_key and x.subscribe_as_of <= effective_date]:
            result.append(sub)
        return result

    def terminate_subscription(self, subscription_id):
        for sub in [x for x in self._subscriptions if x.id == subscription_id]:
            self._subscriptions.remove(sub)
            break

    def create_event(self, evt: Event):
        evt.id = str(uuid.uuid4())
        self._events.append(evt)
        return evt.id

    def get_event(self, event_id) -> Event:
        for evt in [x for x in self._events if x.id == event_id]:
            return evt

    def mark_event_processed(self, event_id):
        for evt in [x for x in self._events if x.id == event_id]:
            evt.is_processed = True
            break

    def mark_event_unprocessed(self, event_id):
        for evt in [x for x in self._events if x.id == event_id]:
            evt.is_processed = False
            break

    def get_runnable_events(self, effective_date) -> []:
        result = []
        for evt in [x for x in self._events if not x.is_processed and x.event_time <= effective_date]:
            result.append(evt.id)
        return result

    def get_events(self, event_name, event_key, effective_date) -> []:
        result = []
        for evt in [x for x in self._events if x.event_name == event_name and x.event_key == event_key and x.event_time >= effective_date]:
            result.append(evt.id)
        return result

    def persist_errors(self, errors: []):
        pass

