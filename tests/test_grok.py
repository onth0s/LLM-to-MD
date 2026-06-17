from pathlib import Path

from llmd.parsers import get_parser

HERE = Path(__file__).resolve().parent
EXAMPLE_HTML = HERE.parent / "examples" / "grok" / "grok-conversation.html"


def test_grok_parser_returns_messages():
    html = EXAMPLE_HTML.read_text(encoding="utf-8")
    parser = get_parser("grok")
    messages = parser.parse(html)
    assert len(messages) > 0
    for msg in messages:
        assert msg.role in ("user", "assistant")
        assert isinstance(msg.content, str)
        assert len(msg.content) > 0
