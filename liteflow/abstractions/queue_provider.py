from interface import Interface

WORKFLOW_QUEUE = 1
EVENT_QUEUE = 2


class IQueueProvider(Interface):

    def queue_work(self, queue, data):
        pass

    def dequeue_work(self, queue):
        pass