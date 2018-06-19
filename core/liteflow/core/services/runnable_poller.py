import logging
from threading import Thread, Event
from interface import implements
from datetime import datetime
from liteflow.core.abstractions import *


class RunnablePoller(implements(IBackgroundService)):

    def __init__(self, persistence_service: IPersistenceProvider, queue_service: IQueueProvider):
        self._queue_service = queue_service
        self._persistence_service = persistence_service
        self._thread = Thread(target=self.execute)
        self._active = False
        self._exit = Event()
        self._logger = logging.getLogger(str(self.__class__))

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
            self._logger.info("Polling for runnable workflows")
            try:
                workflows = self._persistence_service.get_runnable_instances()
                for item in workflows:
                    self._queue_service.queue_work(WORKFLOW_QUEUE, item)

                events = self._persistence_service.get_runnable_events(datetime.utcnow())
                for item in events:
                    self._queue_service.queue_work(EVENT_QUEUE, item)

            except Exception as ex:
                self._logger.error(ex.__class__.__name__)

            self._exit.wait(10)
