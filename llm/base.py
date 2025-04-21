from abc import ABC, abstractmethod

class BaseLLM(ABC):
    @abstractmethod
    def query(self, context: str, question: str) -> str:
        pass
