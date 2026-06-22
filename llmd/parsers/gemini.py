from bs4 import BeautifulSoup, Tag

from ..base_parser import BaseParser
from ..html_to_markdown import extract_message_text
from ..message import Message
from ..post_processor import post_process


class GeminiParser(BaseParser):
    def parse(self, html: str) -> list[Message]:
        soup = BeautifulSoup(html, "html.parser")
        messages: list[Message] = []

        for el in soup.find_all(["user-query", "model-response"]):
            if el.name == "user-query":
                text = self._extract_user_text(el)
                role = "user"
            else:
                text = self._extract_model_text(el)
                role = "assistant"

            if text:
                messages.append(Message(role=role, content=post_process(text)))

        return messages

    def _extract_user_text(self, el: Tag) -> str:
        container = el.find(class_="query-content")
        if not container:
            return ""
        parts: list[str] = []
        for p in container.find_all("p", class_="query-text-line"):
            parts.append(p.get_text())
        text = " ".join(parts).strip()
        return text

    def _extract_model_text(self, el: Tag) -> str:
        panel = el.find(class_="markdown-main-panel")
        if not panel:
            return ""
        return extract_message_text(panel)
