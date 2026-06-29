from bs4 import BeautifulSoup

from ..base_parser import BaseParser
from ..html_to_markdown import extract_message_text
from ..message import Message
from ..post_processor import post_process


class ClaudeParser(BaseParser):
    def parse(self, html: str) -> list[Message]:
        soup = BeautifulSoup(html, "html.parser")
        messages: list[Message] = []

        for el in soup.find_all(True):
            if el.name != "div":
                continue

            if el.get("data-testid") == "user-message":
                text = extract_message_text(el)
                if text.strip():
                    messages.append(Message(role="user", content=post_process(text)))
                continue

            if el.get("data-is-streaming") == "false":
                md = el.find("div", class_="standard-markdown")
                if md:
                    text = extract_message_text(md)
                    if text.strip():
                        messages.append(Message(role="assistant", content=post_process(text)))
                continue

        return messages
