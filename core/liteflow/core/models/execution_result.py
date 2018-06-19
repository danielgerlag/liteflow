from typing import List


class ExecutionResult:
    def __init__(self):
        self.proceed: bool = False
        self.outcome_value = None
        self.sleep_for = None
        self.persistence_data = None
        self.event_name = None
        self.event_key = None
        self.event_as_of = None
        self.branch_values = []

    @staticmethod
    def next():
        result = ExecutionResult()
        result.proceed = True
        return result

    @staticmethod
    def persist(data):
        result = ExecutionResult()
        result.proceed = False
        result.persistence_data = data
        return result

    @staticmethod
    def wait_for_event(event_name, event_key, effective_date):
        result = ExecutionResult()
        result.proceed = False
        result.event_name = event_name
        result.event_key = event_key
        result.event_as_of = effective_date
        return result

    @staticmethod
    def sleep(duration, data):
        result = ExecutionResult()
        result.proceed = False
        result.sleep_for = duration
        result.persistence_data = data
        return result

    @staticmethod
    def branch(branches: List, data):
        result = ExecutionResult()
        result.proceed = False
        result.persistence_data = data
        result.branch_values = branches
        return result
