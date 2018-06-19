class StepOutcome:
    def __init__(self):
        self.value: function = None
        self.next_step = None
        self.label = None

    def get_value(self, data):
        if self.value is None:
            return None

        return self.value(data)
