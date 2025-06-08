from abc import ABC, abstractmethod

class NLPStrategy(ABC):
    @abstractmethod
    def analyze(self, **kwargs):
        pass