from pathlib import Path

from llmd.parsers import get_parser

HERE = Path(__file__).resolve().parent
EXAMPLE_HTML = HERE.parent / "examples" / "gemini" / "gemini-conversation.html"


def test_gemini_parser_returns_messages():
    html = EXAMPLE_HTML.read_text(encoding="utf-8")
    parser = get_parser("gemini")
    messages = parser.parse(html)
    assert len(messages) > 0
    for msg in messages:
        assert msg.role in ("user", "assistant")
        assert isinstance(msg.content, str)
        assert len(msg.content) > 0


def test_gemini_message_order_alternates():
    html = EXAMPLE_HTML.read_text(encoding="utf-8")
    parser = get_parser("gemini")
    messages = parser.parse(html)
    assert messages[0].role == "user"
    assert messages[1].role == "assistant"


def test_gemini_strips_screen_reader_labels():
    html = EXAMPLE_HTML.read_text(encoding="utf-8")
    parser = get_parser("gemini")
    messages = parser.parse(html)
    for msg in messages:
        assert "You said" not in msg.content
        assert "Gemini said" not in msg.content


def test_gemini_preserves_inline_underscores():
    html = EXAMPLE_HTML.read_text(encoding="utf-8")
    parser = get_parser("gemini")
    messages = parser.parse(html)
    joined = "\n".join(m.content for m in messages)
    assert "near_misses" in joined
