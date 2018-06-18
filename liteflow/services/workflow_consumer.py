import logging
from concurrent.futures import Executor
from interface import implements
from liteflow.services.queue_consumer import QueueConsumer
from liteflow.abstractions import *
from liteflow.models import *


class WorkflowConsumer(QueueConsumer):

    def __init__(self, executor: IWorkflowExecutor, persistence_service: IPersistenceProvider, queue_service: IQueueProvider, lock_service: ILockProvider, thread_pool: Executor, idle_time: float):
        super(WorkflowConsumer, self).__init__(queue_service, thread_pool, idle_time)
        self._lock_service = lock_service
        self._persistence_service = persistence_service
        self._executor = executor
        self._logger = logging.getLogger(str(self.__class__))

    def get_queue(self):
        return WORKFLOW_QUEUE

    def process_item(self, item):
        if not self._lock_service.acquire_lock(f"workflow:{item}"):
            self._logger.info(f"Workflow locked {item}")
            return
        instance = self._persistence_service.get_workflow_instance(item)
        success = False
        result = None
        try:
            if instance.status == WorkflowInstance.RUNNABLE:
                result = self._executor.execute(instance)
                self._persistence_service.persist_workflow(instance)
                success = True

        except Exception as ex:
            self._logger.error(str(ex))
        finally:
            self._lock_service.release_lock(f"workflow:{item}")

            for sub in result.subscriptions:
                self._logger.info(f"Subscribing to event {sub.event_name} for {instance.id}")
                self._persistence_service.create_subscription(sub)
                events = self._persistence_service.get_events(sub.event_name, sub.event_key, sub.subscribe_as_of)
                for evt_id in events:
                    self._persistence_service.mark_event_unprocessed(evt_id)
                    self._queue_service.queue_work(EVENT_QUEUE, evt_id)

            self._persistence_service.persist_errors(result.errors)

            if success and instance.status == WorkflowInstance.RUNNABLE:
                self._queue_service.queue_work(WORKFLOW_QUEUE, item)
