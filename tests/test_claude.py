from pathlib import Path

from llmd.parsers import get_parser

HERE = Path(__file__).resolve().parent
EXAMPLE_HTML = HERE.parent / "examples" / "claude" / "claude-conversation.html"


def test_claude_parser_returns_messages():
    html = EXAMPLE_HTML.read_text(encoding="utf-8")
    parser = get_parser("claude")
    messages = parser.parse(html)
    assert len(messages) > 0
    for msg in messages:
        assert msg.role in ("user", "assistant")
        assert isinstance(msg.content, str)
        assert len(msg.content) > 0


def test_claude_parser_extracts_user_and_assistant():
    html = EXAMPLE_HTML.read_text(encoding="utf-8")
    parser = get_parser("claude")
    messages = parser.parse(html)

    roles = [m.role for m in messages]
    assert "user" in roles
    assert "assistant" in roles


def test_claude_parser_preserves_order():
    html = EXAMPLE_HTML.read_text(encoding="utf-8")
    parser = get_parser("claude")
    messages = parser.parse(html)

    # First message should be user, second should be assistant
    assert messages[0].role == "user"
    assert "Fun project" in messages[0].content
    assert messages[1].role == "assistant"
    assert "yey" in messages[1].content
