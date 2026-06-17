from ..base_parser import BaseParser
from ..message import Message


class GeminiParser(BaseParser):
    def parse(self, html: str) -> list[Message]:
        raise NotImplementedError("Gemini parser not yet implemented")
