from ..base_parser import BaseParser
from ..message import Message


class ChatGPTParser(BaseParser):
    def parse(self, html: str) -> list[Message]:
        raise NotImplementedError("ChatGPT parser not yet implemented")
