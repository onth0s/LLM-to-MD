import re

from bs4 import BeautifulSoup

from ..base_parser import BaseParser
from ..html_to_markdown import extract_message_text
from ..message import Message
from ..post_processor import grok_post_process


class GrokParser(BaseParser):
    def parse(self, html: str) -> list[Message]:
        soup = BeautifulSoup(html, 'html.parser')
        response_divs = soup.find_all('div', id=re.compile(r'^response-'))
        messages: list[Message] = []

        for div in response_divs:
            user_msg = div.find('div', attrs={'data-testid': 'user-message'})
            if user_msg is not None:
                text = extract_message_text(user_msg)
                if text.strip():
                    messages.append(Message(role='user', content=grok_post_process(text)))
            else:
                text = extract_message_text(div)
                if text.strip():
                    messages.append(Message(role='assistant', content=grok_post_process(text)))

        return messages