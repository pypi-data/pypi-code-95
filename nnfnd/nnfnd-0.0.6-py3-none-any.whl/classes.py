from abc import ABC, abstractmethod


class InferenceModelABC(ABC):
    @abstractmethod
    def infer(self, config):
        pass
