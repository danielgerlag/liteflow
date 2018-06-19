from abc import ABCMeta, abstractmethod
from liteflow.core.builders import WorkflowBuilder


class Workflow(metaclass=ABCMeta):

    @property
    @abstractmethod
    def id(self):
        return None

    @property
    @abstractmethod
    def version(self):
        return 1

    @abstractmethod
    def build(self, builder: WorkflowBuilder):
        raise NotImplementedError
