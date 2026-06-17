import re
import html as html_mod
from pathlib import Path

from bs4 import BeautifulSoup, NavigableString, Tag

from ..base_parser import BaseParser
from ..message import Message
from ..post_processor import post_process


def decode(text: str) -> str:
    return html_mod.unescape(text)


def walk_text(node, out: list):
    if isinstance(node, NavigableString):
        t = str(node)
        t = re.sub(r'\s+', ' ', t)
        if t:
            out.append(t)
        return

    if not isinstance(node, Tag):
        return

    tag = node.name

    if tag in ('button', 'svg', 'path', 'g', 'defs', 'clipPath', 'rect',
               'style', 'script', 'link', 'meta', 'img', 'form', 'input',
               'label', 'select', 'option', 'figure', 'figcaption',
               'nav', 'aside'):
        return

    if tag == 'span':
        cls = node.get('class', [])
        if any('select-none' in (c or '') for c in cls):
            return
        for child in node.children:
            walk_text(child, out)
        return

    if tag in ('section', 'div'):
        for child in node.children:
            walk_text(child, out)
        return

    if tag == 'p':
        for child in node.children:
            walk_text(child, out)
        out.append('\n\n')
        return

    if tag in ('h1', 'h2', 'h3', 'h4', 'h5', 'h6'):
        prefix = '#' * int(tag[1])
        out.append('\n\n' + prefix + ' ')
        for child in node.children:
            walk_text(child, out)
        out.append('\n\n')
        return

    if tag == 'br':
        out.append('\n')
        return

    if tag == 'hr':
        out.append('\n\n---\n\n')
        return

    if tag == 'ul':
        out.append('\n')
        for child in node.children:
            walk_text(child, out)
        out.append('\n')
        return

    if tag == 'ol':
        out.append('\n')
        li_children = [c for c in node.children if isinstance(c, Tag) and c.name == 'li']
        for idx, child in enumerate(li_children, 1):
            _walk_li_ordered(child, out, idx)
        out.append('\n')
        return

    if tag == 'li':
        depth = 0
        p = node.parent
        while p:
            if p.name in ('ul', 'ol'):
                depth += 1
            p = p.parent
        indent = '  ' * (depth - 1)
        out.append('\n' + indent + '- ')
        for child in node.children:
            walk_text(child, out)
        return

    if tag == 'pre':
        _emit_code_block(node, out)
        return

    if tag == 'figure':
        return

    if tag == 'code' or (tag == 'span' and node.get('class') and 'font-mono' in ' '.join(node.get('class', []))):
        p = node.parent
        while p:
            if p.name == 'pre':
                return
            p = p.parent
        if tag == 'code' or any('font-mono' in (c or '') for c in node.get('class', [])):
            code_text = decode(node.get_text().strip())
            out.append('`' + code_text + '`')
            return

    if tag == 'strong':
        out.append('**')
        for child in node.children:
            walk_text(child, out)
        out.append('**')
        return

    if tag in ('em', 'i'):
        out.append('_')
        for child in node.children:
            walk_text(child, out)
        out.append('_')
        return

    if tag == 'a':
        href = node.get('href', '')
        text_content = decode(node.get_text(strip=True))
        if href:
            out.append('[' + text_content + '](' + href + ')')
        else:
            out.append(text_content)
        return

    for child in node.children:
        walk_text(child, out)


def _walk_li_ordered(node, out: list, idx: int):
    if not isinstance(node, Tag):
        return
    if node.name != 'li':
        for child in node.children:
            _walk_li_ordered(child, out, idx)
        return

    depth = 0
    p = node.parent
    while p:
        if p.name in ('ul', 'ol'):
            depth += 1
        p = p.parent
    indent = '  ' * (depth - 1)
    out.append(f'\n{indent}{idx}. ')
    for child in node.children:
        walk_text(child, out)


def _emit_code_block(node, out: list):
    text = node.get_text()
    text = decode(text)
    text = text.replace('\xa0', ' ')
    lines = text.split('\n')
    while lines and not lines[0].strip():
        lines.pop(0)
    while lines and not lines[-1].strip():
        lines.pop()
    if lines:
        min_indent = min((len(l) - len(l.lstrip()) for l in lines if l.strip()), default=0)
        lines = [l[min_indent:] if l.strip() else l for l in lines]
    code = '\n'.join(lines)
    out.append(f'\n```\n{code}\n```\n')


def extract_message_text(el) -> str:
    out: list[str] = []
    for child in el.children:
        walk_text(child, out)
    text = ''.join(out)
    text = decode(text)
    return text.strip()


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
                    messages.append(Message(role='user', content=post_process(text)))
            else:
                text = extract_message_text(div)
                if text.strip():
                    messages.append(Message(role='assistant', content=post_process(text)))

        return messages
