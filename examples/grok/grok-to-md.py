"""
Parse exported conversation HTML into CONVERSATION.md.
Usage: python grok-to-md.py
"""

from bs4 import BeautifulSoup, NavigableString, Tag
from pathlib import Path
import re
import html as html_mod

HTML_FILE = Path(__file__).parent / "grok-conversation.html"
OUT_FILE = Path(__file__).parent / "CONVERSATION.md"


def decode(text: str) -> str:
    return html_mod.unescape(text)


def walk_text(node, out: list):
    """
    Walk a BeautifulSoup tree and emit text fragments + markdown markers.
    """
    if isinstance(node, NavigableString):
        t = str(node)
        # Normalize any whitespace to single space
        t = re.sub(r'\s+', ' ', t)
        if t:
            out.append(t)
        return

    if not isinstance(node, Tag):
        return

    tag = node.name

    # Skip non-content elements
    if tag in ('button', 'svg', 'path', 'g', 'defs', 'clipPath', 'rect',
               'style', 'script', 'link', 'meta', 'img', 'form', 'input',
               'label', 'select', 'option', 'figure', 'figcaption',
               'nav', 'aside'):
        return

    if tag == 'span':
        # Skip UI label spans (language indicator in code blocks)
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
        # Check if inside <pre>
        p = node.parent
        while p:
            if p.name == 'pre':
                return  # handled by pre
            p = p.parent
        # Only treat as inline code if it's a <code> tag OR has font-mono class
        if tag == 'code' or any('font-mono' in (c or '') for c in node.get('class', [])):
            code_text = decode(node.get_text().strip())
            out.append('`' + code_text + '`')
            return
        # Fall through for non-code spans

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

    # Fallback
    for child in node.children:
        walk_text(child, out)


def _walk_li_ordered(node, out: list, idx: int):
    """Handle <li> within <ol> with numbered markers."""
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
    """Convert a <pre> block to a fenced code block."""
    text = node.get_text()
    text = decode(text)
    text = text.replace('\xa0', ' ')
    # Remove leading/following blank lines
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
    """Convert a message element's content to clean markdown."""
    out: list[str] = []
    for child in el.children:
        walk_text(child, out)
    text = ''.join(out)
    text = decode(text)
    return text.strip()


def parse_conversation() -> list[tuple[str, str]]:
    html = HTML_FILE.read_text(encoding='utf-8')
    soup = BeautifulSoup(html, 'html.parser')

    response_divs = soup.find_all('div', id=re.compile(r'^response-'))
    messages: list[tuple[str, str]] = []

    for div in response_divs:
        user_msg = div.find('div', attrs={'data-testid': 'user-message'})
        if user_msg is not None:
            text = extract_message_text(user_msg)
            if text.strip():
                messages.append(('user', text))
        else:
            text = extract_message_text(div)
            if text.strip():
                messages.append(('assistant', text))

    return messages


def post_process(text: str) -> str:
    t = text

    # Remove "Thought for Xs" timing artifacts
    t = re.sub(r'^\*\*Thought for \d+s\*\*\s*\n*', '', t, flags=re.MULTILINE)
    t = re.sub(r'^Thought for \d+s\s*\n*', '', t, flags=re.MULTILINE)

    # Collapse multiple spaces (but not newlines)
    t = re.sub(r'  +', ' ', t)

    # Ensure space between text and inline markers where needed.
    # word** -> word ** (when ** follows a word char without space)
    t = re.sub(r'(?<=\w)\*\*', ' **', t)
    # **word -> ** word (when ** precedes a word char without space)
    t = re.sub(r'\*\*(?=\w)', '** ', t)
    # word` -> word `
    t = re.sub(r'(?<=\w)`', ' `', t)
    # `word -> ` word
    t = re.sub(r'`(?=\w)', '` ', t)
    # word_ -> word _
    t = re.sub(r'(?<=\w)_', ' _', t)
    # _word -> _ word
    t = re.sub(r'_(?=\w)', '_ ', t)

    # Remove space between marker and punctuation: ** , -> **,
    t = re.sub(r'\*\* ([,.;:!?\)])', r'**\1', t)
    t = re.sub(r'` ([,.;:!?\)])', r'`\1', t)
    t = re.sub(r'_ ([,.;:!?\)])', r'_\1', t)

    # Fix stray bold markers in middle of text (not wrapping anything)
    stars = re.findall(r'\*\*', t)
    if len(stars) % 2 != 0:
        idx = t.rfind('**')
        if idx >= 0:
            t = t[:idx] + t[idx + 2:]

    # Replace Grok with User-Agent
    t = re.sub(r'\bGrok\b', 'User-Agent', t)
    t = re.sub(r'(?<![a-zA-Z])grok(?![a-zA-Z])', 'user-agent', t)

    # Collapse whitespace
    t = re.sub(r'\n{4,}', '\n\n\n', t)
    t = re.sub(r'[ \t]+\n', '\n', t)
    t = re.sub(r'\n[ \t]+', '\n', t)
    t = re.sub(r' +', ' ', t)
    t = t.strip()

    return t


def main():
    messages = parse_conversation()

    lines = ["# Conversation\n", "\n---\n"]

    for role, text in messages:
        text = post_process(text)
        if not text:
            continue
        label = "## User" if role == 'user' else "## Agent"
        lines.append(f"\n{label}\n\n{text}\n")

    OUT_FILE.write_text(''.join(lines), encoding='utf-8')
    print(f"Done — {len(messages)} messages written to {OUT_FILE}")


if __name__ == '__main__':
    main()
