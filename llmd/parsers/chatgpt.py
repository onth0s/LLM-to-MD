from bs4 import BeautifulSoup, NavigableString, Tag

from ..base_parser import BaseParser
from ..html_to_markdown import extract_message_text
from ..message import Message
from ..post_processor import post_process


class ChatGPTParser(BaseParser):
    def parse(self, html: str) -> list[Message]:
        soup = BeautifulSoup(html, "html.parser")
        messages: list[Message] = []

        for section in soup.find_all("section", attrs={"data-turn-id": True}):
            user_div = section.find(attrs={"data-message-author-role": "user"})
            if user_div is not None:
                text = self._extract_user_text(user_div)
                if text:
                    messages.append(Message(role="user", content=post_process(text)))
                continue

            assistant_div = section.find(attrs={"data-message-author-role": "assistant"})
            if assistant_div is not None:
                text = self._extract_assistant_text(assistant_div)
                if text:
                    messages.append(Message(role="assistant", content=post_process(text)))

        return messages

    @staticmethod
    def _extract_user_text(container: Tag) -> str:
        bubble = container.select_one("div.whitespace-pre-wrap")
        if bubble is None:
            return ""
        for code in bubble.find_all("code", class_="user-message-inline-code"):
            if not code.get_text().strip():
                code.decompose()
        return extract_message_text(bubble)

    @staticmethod
    def _extract_assistant_text(container: Tag) -> str:
        markdown = container.find("div", class_="markdown")
        if markdown is None:
            return ""
        _collapse_code_blocks(markdown)
        return extract_message_text(markdown)


def _collapse_code_blocks(container: Tag) -> None:
    for outer in container.select('pre[class*="overflow-visible"]'):
        inner = outer.find("pre", class_="cm-content")
        if inner is None:
            continue
        for br in inner.find_all("br"):
            br.replace_with(NavigableString("\n"))
        for span in inner.find_all("span"):
            span.unwrap()
        outer.clear()
        outer.append(inner)
        outer.unwrap()
