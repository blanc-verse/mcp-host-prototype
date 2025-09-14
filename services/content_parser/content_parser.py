from abc import ABC, abstractmethod


class ContentParser(ABC):
    @abstractmethod
    def from_chainlit(self):
        pass

    @abstractmethod
    def to_chainlit(self):
        pass
