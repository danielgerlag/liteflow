import logging
from datetime import datetime
from typing import List
from interface import implements
from liteflow.core.models import WorkflowInstance, Workflow, Event
from liteflow.core.abstractions import *


class WorkflowHost(implements(IWorkflowHost)):

    def __init__(self, persistence_service: IPersistenceProvider, queue_service: IQueueProvider, lock_service: ILockProvider, pointer_factory: IExecutionPointerFactory, registry: IWorkflowRegistry, background_services: List[IBackgroundService]):
        self._pointer_factory = pointer_factory
        self._persistence_service = persistence_service
        self._queue_service = queue_service
        self._lock_service = lock_service
        self._background_services = background_services
        self._registry = registry
        self._logger = logging.getLogger(str(self.__class__))

    def start_workflow(self, workflow_id, version, data):
        definition = self._registry.get_definition(workflow_id, version)
        if definition is None:
            raise Exception("workflow not registered")

        instance = WorkflowInstance()
        instance.workflow_definition_id = workflow_id
        instance.version = version
        instance.data = data
        instance.description = definition.description
        instance.next_execution = 0
        instance.create_time = datetime.utcnow()
        instance.status = WorkflowInstance.RUNNABLE

        genesis = self._pointer_factory.build_genesis_pointer(definition)
        instance.execution_pointers.append(genesis)

        workflow_id = self._persistence_service.create_workflow(instance)
        self._queue_service.queue_work(WORKFLOW_QUEUE, workflow_id)

        return workflow_id

    def publish_event(self, event_name, event_key, event_data=object(), effective_date=None):
        self._logger.debug(f"Publishing event {event_name} {event_key}")

        if effective_date is None:
            effective_date = datetime.utcnow()

        evt = Event()
        evt.event_name = event_name
        evt.event_key = event_key
        evt.event_data = event_data
        evt.event_time = effective_date
        evt.is_processed = False
        evt_id = self._persistence_service.create_event(evt)
        self._queue_service.queue_work(EVENT_QUEUE, evt_id)

    def register_workflow(self, workflow: Workflow):
        self._registry.register_workflow(workflow)

    def start(self):
        self._logger.info("Starting workflow host")
        for svc in self._background_services:
            svc.start()

    def stop(self):
        self._logger.info("Stopping workflow host")
        for svc in self._background_services:
            svc.stop()
        self._lock_service.shutdown()
