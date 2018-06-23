import logging
from typing import Dict
from interface import implements
from azure.storage.queue import QueueService
from azure.storage.common import CloudStorageAccount
from liteflow.core.abstractions import IQueueProvider, EVENT_QUEUE, WORKFLOW_QUEUE


class AzureQueueProvider(implements(IQueueProvider)):

    def __init__(self, account: CloudStorageAccount):
        self._logger = logging.getLogger("liteflow.providers.azure")
        self._service = account.create_queue_service()
        self._queues: Dict[str] = {WORKFLOW_QUEUE: "workflow", EVENT_QUEUE: "event"}
        for queue in self._queues:
            try:
                self._logger.log(logging.DEBUG, f"Creating queue {self._queues[queue]}")
                self._service.create_queue(self._queues[queue])
            except:
                pass

    def queue_work(self, queue, data):
        try:
            self._logger.log(logging.DEBUG, f"Enqueueing {data} on {self._queues[queue]}")
            msg = self._service.put_message(self._queues[queue], str(data))
            self._logger.log(logging.DEBUG, f"Enqueued {data} on {self._queues[queue]} with msg id {msg.id}")
        except Exception as ex:
            self._logger.log(logging.ERROR, f"Failed to queue work - {ex}")

    def dequeue_work(self, queue):
        try:
            messages = self._service.get_messages(self._queues[queue], num_messages=1)
            for message in messages:
                self._service.delete_message(self._queues[queue], message.id, message.pop_receipt)
                self._logger.log(logging.DEBUG, f"Dequeued {message.content} from {self._queues[queue]}")
                return message.content
        except Exception as ex:
            self._logger.log(logging.ERROR, f"Failed to dequeue work - {ex}")

        return None

