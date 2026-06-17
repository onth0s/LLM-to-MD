from ..base_parser import BaseParser
from ..message import Message


class ClaudeParser(BaseParser):
    def parse(self, html: str) -> list[Message]:
        raise NotImplementedError("Claude parser not yet implemented")
