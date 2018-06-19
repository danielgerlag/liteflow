from pymongo import MongoClient
from interface import implements
from typing import List
from liteflow.core.abstractions import IPersistenceProvider
from liteflow.core.models import WorkflowInstance, EventSubscription, Event
from .converters import *


class MongoPersistenceProvider(implements(IPersistenceProvider)):

    def __init__(self, connection_string, database):
        self._client = MongoClient(connection_string)
        self._database = self._client[database]
        self._workflow_collection = self._database['workflows']
        self._subscription_collection = self._database['subscriptions']
        self._event_collection = self._database['events']

    def create_workflow(self, workflow: WorkflowInstance):
        data = dump_workflow_instance(workflow)
        workflow.id = str(self._workflow_collection.insert_one(data).inserted_id)
        return workflow.id

    def persist_workflow(self, workflow: WorkflowInstance):
        data = dump_workflow_instance(workflow)
        self._workflow_collection.replace_one({ '_id': ObjectId(workflow.id) }, data)

    def get_workflow_instance(self, id) -> WorkflowInstance:
        data = self._workflow_collection.find_one({ "_id": ObjectId(id)})
        return load_workflow_instance(data)

    def get_runnable_instances(self) -> []:
        result = []
        for item in self._workflow_collection.find(filter={"status": WorkflowInstance.RUNNABLE}, projection={"_id": True}):
            result.append(item["_id"])
        return result

    def create_subscription(self, subscription: EventSubscription):
        data = dump_subscription(subscription)
        subscription.id = str(self._subscription_collection.insert_one(data).inserted_id)
        return subscription.id

    def get_subscriptions(self, event_name, event_key, effective_date) -> []:
        result = []
        for item in self._subscription_collection.find(filter={
            "event_name": event_name,
            "event_key": event_key,
            "subscribe_as_of": {"$lte": effective_date}
        }):
            result.append(load_subscription(item))
        return result

    def terminate_subscription(self, subscription_id):
        self._subscription_collection.delete_one({"_id": subscription_id})

    def create_event(self, evt: Event):
        data = dump_event(evt)
        evt.id = str(self._event_collection.insert_one(data).inserted_id)
        return evt.id

    def get_event(self, event_id) -> Event:
        data = self._event_collection.find_one({"_id": ObjectId(event_id)})
        return load_event(data)

    def mark_event_processed(self, event_id):
        self._event_collection.update_one({"_id": event_id}, {"$set": {"is_processed": True}})

    def mark_event_unprocessed(self, event_id):
        self._event_collection.update_one({"_id": event_id}, {"$set": {"is_processed": False}})

    def get_runnable_events(self, effective_date) -> []:
        result = []
        for item in self._event_collection.find(filter={
            "is_processed": False,
            "event_time": {"$lte": effective_date}
        }, projection={"_id": True}):
            result.append(item["_id"])
        return result

    def get_events(self, event_name, event_key, effective_date) -> []:
        result = []
        for item in self._event_collection.find(filter={
            "event_name": event_name,
            "event_key": event_key,
            "event_time": {"$gte": effective_date}
        }, projection={"_id": True}):
            result.append(item["_id"])
        return result

    def persist_errors(self, errors: []):
        pass

