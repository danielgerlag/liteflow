from typing import List
from liteflow.core.models.event_subscription import EventSubscription
from liteflow.core.models.execution_error import ExecutionError


class WorkflowExecutorResult:

    def __init__(self):
        self.subscriptions: List[EventSubscription] = []
        self.errors: List[ExecutionError] = []