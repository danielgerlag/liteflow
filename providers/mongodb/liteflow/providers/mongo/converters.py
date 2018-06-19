import pickle
from typing import Dict
from bson.objectid import ObjectId
from liteflow.core.models import WorkflowInstance, EventSubscription, Event, ExecutionPointer


def dump_execution_pointer(source: ExecutionPointer):
    return {
        'id': source.id,
        'step_id': source.step_id,
        'active': source.active,
        'sleep_until': source.sleep_until,
        'persistence_data': pickle.dumps(source.persistence_data),
        'start_time': source.start_time,
        'end_time': source.end_time,
        'event_name': source.event_name,
        'event_key': source.event_key,
        'event_published': source.event_published,
        'event_data': pickle.dumps(source.event_data),
        'context_item': pickle.dumps(source.context_item),
        'predecessor_id': source.predecessor_id,
        'outcome': source.outcome,
        'status': source.status,
        'retry_count': source.retry_count,
        'children': pickle.dumps(source.children),
        'scope': pickle.dumps(source.scope)
    }


def dump_workflow_instance(source: WorkflowInstance):
    result = {
        'workflow_definition_id': source.workflow_definition_id,
        'version': source.version,
        'description': source.description,
        'next_execution': source.next_execution,
        'status': source.status,
        'data': pickle.dumps(source.data),
        'create_time': source.create_time,
        'complete_time': source.complete_time,
        'execution_pointers': [dump_execution_pointer(x) for x in source.execution_pointers]
    }

    if source.id is not None:
        result['_id'] = ObjectId(source.id)

    return result


def dump_subscription(source: EventSubscription):
    result = {
        'event_name': source.event_name,
        'event_key': source.event_key,
        'step_id': source.step_id,
        'workflow_id': source.workflow_id,
        'subscribe_as_of': source.subscribe_as_of
    }

    if source.id is not None:
        result['_id'] = ObjectId(source.id)

    return result


def dump_event(source: Event):
    result = {
        'event_name': source.event_name,
        'event_key': source.event_key,
        'event_data': pickle.dumps(source.event_data),
        'event_time': source.event_time,
        'is_processed': source.is_processed
    }

    if source.id is not None:
        result['_id'] = ObjectId(source.id)

    return result


def load_execution_pointer(source: Dict) -> ExecutionPointer:
    result = ExecutionPointer()
    result.id = source['id']
    result.step_id = source['step_id']
    result.active = source['active']
    result.sleep_until = source['sleep_until']
    result.persistence_data = pickle.loads(source['persistence_data'])
    result.start_time = source['start_time']
    result.end_time = source['end_time']
    result.event_name = source['event_name']
    result.event_key = source['event_key']
    result.event_published = source['event_published']
    result.event_data = pickle.loads(source['event_data'])
    result.context_item = pickle.loads(source['context_item'])
    result.predecessor_id = source['predecessor_id']
    result.outcome = source['outcome']
    result.status = source['status']
    result.retry_count = source['retry_count']
    result.children = pickle.loads(source['children'])
    result.scope = pickle.loads(source['scope'])

    return result


def load_workflow_instance(source: Dict) -> WorkflowInstance:
    result = WorkflowInstance()
    result.id = str(source['_id'])
    result.workflow_definition_id = source['workflow_definition_id']
    result.version = source['version']
    result.description = source['description']
    result.data = pickle.loads(source['data'])
    result.next_execution = source['next_execution']
    result.status = source['status']
    result.create_time = source['create_time']
    result.complete_time = source['complete_time']
    result.execution_pointers = [load_execution_pointer(x) for x in source['execution_pointers']]

    return result


def load_subscription(source: Dict) -> EventSubscription:
    result = EventSubscription()
    result.id = str(source['_id'])
    result.event_name = source['event_name']
    result.event_key = source['event_key']
    result.step_id = source['step_id']
    result.workflow_id = source['workflow_id']
    result.subscribe_as_of = source['subscribe_as_of']

    return result


def load_event(source: Dict) -> Event:
    result = Event()
    result.id = str(source['_id'])
    result.event_name = source['event_name']
    result.event_key = source['event_key']
    result.event_data = pickle.loads(source['event_data'])
    result.event_time = source['event_time']
    result.is_processed = source['is_processed']

    return result
