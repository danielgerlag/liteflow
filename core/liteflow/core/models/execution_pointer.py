import datetime

class ExecutionPointer:
    PENDING = 0
    RUNNING = 1
    COMPLETE = 2
    SLEEPING = 3
    WAITING = 4
    FAILED = 5
    COMPENSATED = 6

    def __init__(self):
        self.id = None
        self.step_id = None
        self.active = False
        self.sleep_until: datetime.datetime = None
        self.persistence_data = None
        self.start_time = None
        self.end_time = None
        self.event_name = None
        self.event_key = None
        self.event_published = False
        self.event_data = None
        self.context_item = None
        self.predecessor_id = None
        self.outcome = None
        self.status = None
        self.retry_count = 0
        self.children = []
        self.scope = []

