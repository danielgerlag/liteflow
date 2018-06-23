from abc import ABCMeta, ABC, abstractmethod
from threading import Thread, Event
from concurrent.futures import Executor
from interface import implements
from liteflow.core.abstractions import IBackgroundService, IQueueProvider


class QueueConsumer(ABC):

    def __init__(self, queue_service: IQueueProvider, thread_pool: Executor, logger, idle_time: float):
        self._logger = logger
        self._thread = Thread(target=self.execute)
        self._active = False
        self._exit = Event()
        self._queue_service = queue_service
        self.idle_time = idle_time
        self._thread_pool = thread_pool

    def start(self):
        self._active = True
        self._exit.clear()
        self._thread.start()

    def stop(self):
        self._active = False
        self._exit.set()
        self._thread.join()

    def execute(self):

        while self._active:
            try:
                item = self._queue_service.dequeue_work(self.get_queue())

                if item is None:
                    self._exit.wait(self.idle_time)
                    continue

                self._thread_pool.submit(self.process_item, item)
            except Exception as ex:
                self._logger.log(logging.ERROR, f"Error consuming queue - {ex}")

    @abstractmethod
    def get_queue(self):
        raise NotImplementedError

    @abstractmethod
    def process_item(self, item):
        raise NotImplementedError
