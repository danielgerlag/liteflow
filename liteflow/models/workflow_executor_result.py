from typing import List
from liteflow.models.event_subscription import EventSubscription
from liteflow.models.execution_error import ExecutionError


class WorkflowExecutorResult:

    def __init__(self):
        self.subscriptions: List[EventSubscription] = []
        self.errors: List[ExecutionError] = []