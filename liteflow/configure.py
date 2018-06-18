from typing import List
import datetime
from concurrent.futures import ThreadPoolExecutor, Executor
from liteflow.abstractions import *
from liteflow.services import *


default_persistence_service = MemoryPersistenceProvider()
default_queue_service = LocalQueueProvider()
default_lock_service = LocalLockProvider()


def configure_workflow_host(persistence_service: IPersistenceProvider=default_persistence_service, queue_service: IQueueProvider=default_queue_service, lock_service: ILockProvider=default_lock_service) -> IWorkflowHost:
    worker_pool = ThreadPoolExecutor()
    registry = WorkflowRegistry()
    pointer_factory = ExecutionPointerFactory()
    result_processor = ExecutionResultProcessor(pointer_factory)
    executor = WorkflowExecutor(result_processor, registry)

    background_services = [RunnablePoller(persistence_service, queue_service),
                           WorkflowConsumer(executor, persistence_service, queue_service, lock_service, worker_pool, 2),
                           EventConsumer(persistence_service, queue_service, lock_service, worker_pool, 2)]

    host = WorkflowHost(persistence_service, queue_service, pointer_factory, registry, background_services)

    return host
