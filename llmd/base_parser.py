from abc import ABC, abstractmethod

from .message import Message


class BaseParser(ABC):
    @abstractmethod
    def parse(self, html: str) -> list[Message]: ...
