import logging
from datetime import datetime
from concurrent.futures import Executor
from liteflow.core.services.queue_consumer import QueueConsumer
from liteflow.core.abstractions import *
from liteflow.core.models import *


class EventConsumer(QueueConsumer):

    def __init__(self, persistence_service: IPersistenceProvider, queue_service: IQueueProvider, lock_service: ILockProvider, thread_pool: Executor, idle_time: float):
        super(EventConsumer, self).__init__(queue_service, thread_pool, idle_time)
        self._lock_service = lock_service
        self._persistence_service = persistence_service
        self._logger = logging.getLogger(str(self.__class__))

    def get_queue(self):
        return EVENT_QUEUE

    def process_item(self, item):
        if not self._lock_service.acquire_lock(f"event:{item}"):
            self._logger.info(f"Event locked {item}")
            return
        try:
            evt = self._persistence_service.get_event(item)
            if evt.event_time <= datetime.utcnow():
                subs = self._persistence_service.get_subscriptions(evt.event_name, evt.event_key, evt.event_time)
                self._logger.info(f"got {len(subs)} subs")
                success = True
                for sub in subs:
                    success = success and self.seed_subscription(evt, sub)
                if success:
                    self._persistence_service.mark_event_processed(item)
        except Exception as ex:
            self._logger.error(str(ex))
        finally:
            self._lock_service.release_lock(f"event:{item}")

    def seed_subscription(self, evt: Event, subscription: EventSubscription) -> bool:
        if not self._lock_service.acquire_lock(f"workflow:{subscription.workflow_id}"):
            self._logger.info(f"workflow locked {subscription.workflow_id}")
            return False
        try:
            instance = self._persistence_service.get_workflow_instance(subscription.workflow_id)
            self._logger.info(f"seeding workflow {instance.id}")
            for pointer in (x for x in instance.execution_pointers if x.event_name == subscription.event_name and x.event_key == subscription.event_key and not x.event_published):
                pointer.event_data = evt.event_data
                pointer.event_published = True
                pointer.active = True
                self._logger.info(f"seeding pointer {pointer.id}")

            instance.next_execution = 0
            self._persistence_service.persist_workflow(instance)
            self._persistence_service.terminate_subscription(subscription.id)

            return True
        except Exception as ex:
            self._logger.error(str(ex))
        finally:
            self._lock_service.release_lock(f"workflow:{subscription.workflow_id}")
            self._queue_service.queue_work(WORKFLOW_QUEUE, subscription.workflow_id)