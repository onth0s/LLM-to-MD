from ..base_parser import BaseParser
from ..message import Message


class DeepSeekParser(BaseParser):
    def parse(self, html: str) -> list[Message]:
        raise NotImplementedError("DeepSeek parser not yet implemented")
