from interface import implements
from queue import Queue, Empty
from typing import Dict
from liteflow.core.abstractions import IQueueProvider, EVENT_QUEUE, WORKFLOW_QUEUE


class LocalQueueProvider(implements(IQueueProvider)):

    def __init__(self):
        self._queues: Dict[Queue] = {WORKFLOW_QUEUE: Queue(), EVENT_QUEUE: Queue()}

    def queue_work(self, queue, data):
        self._queues[queue].put(data)

    def dequeue_work(self, queue):
        try:
            return self._queues[queue].get(True, 1)
        except Empty:
            return None
