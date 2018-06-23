from typing import List
import logging
from concurrent.futures import ThreadPoolExecutor, Executor
from liteflow.core.abstractions import *
from liteflow.core.services import *


default_persistence_service = MemoryPersistenceProvider()
default_queue_service = LocalQueueProvider()
default_lock_service = LocalLockProvider()


def configure_workflow_host(persistence_service: IPersistenceProvider=default_persistence_service, queue_service: IQueueProvider=default_queue_service, lock_service: ILockProvider=default_lock_service) -> IWorkflowHost:

    logger = logging.getLogger("liteflow.core")
    worker_pool = ThreadPoolExecutor()
    registry = WorkflowRegistry()
    pointer_factory = ExecutionPointerFactory()
    result_processor = ExecutionResultProcessor(pointer_factory, logger)
    executor = WorkflowExecutor(result_processor, registry, logger)

    background_services = [RunnablePoller(persistence_service, queue_service, logger),
                           WorkflowConsumer(executor, persistence_service, queue_service, lock_service, worker_pool, logger, 2),
                           EventConsumer(persistence_service, queue_service, lock_service, worker_pool, logger, 2)]

    host = WorkflowHost(persistence_service, queue_service, lock_service, pointer_factory, registry, background_services)

    return host
