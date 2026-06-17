from ..base_parser import BaseParser
from ..message import Message


class NotebookLMParser(BaseParser):
    def parse(self, html: str) -> list[Message]:
        raise NotImplementedError("NotebookLM parser not yet implemented")
