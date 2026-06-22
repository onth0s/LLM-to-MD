from pathlib import Path

from llmd.parsers import get_parser

HERE = Path(__file__).resolve().parent
EXAMPLE_HTML = HERE.parent / "examples" / "chatgpt" / "chatgpt-conversation.html"


def test_chatgpt_parser_returns_messages():
    html = EXAMPLE_HTML.read_text(encoding="utf-8")
    parser = get_parser("chatgpt")
    messages = parser.parse(html)
    assert len(messages) > 0
    for msg in messages:
        assert msg.role in ("user", "assistant")
        assert isinstance(msg.content, str)
        assert len(msg.content) > 0


def test_chatgpt_message_order_alternates():
    html = EXAMPLE_HTML.read_text(encoding="utf-8")
    parser = get_parser("chatgpt")
    messages = parser.parse(html)
    assert messages[0].role == "user"
    assert messages[1].role == "assistant"
    assert messages[2].role == "user"
    assert messages[3].role == "assistant"
    assert messages[4].role == "user"
    assert messages[5].role == "assistant"


def test_chatgpt_strips_screen_reader_labels():
    html = EXAMPLE_HTML.read_text(encoding="utf-8")
    parser = get_parser("chatgpt")
    messages = parser.parse(html)
    joined = "\n".join(m.content for m in messages)
    assert "You said" not in joined
    assert "ChatGPT said" not in joined


def test_chatgpt_preserves_user_inline_code():
    html = EXAMPLE_HTML.read_text(encoding="utf-8")
    parser = get_parser("chatgpt")
    messages = parser.parse(html)
    user2 = messages[2].content
    assert "`H5 (phonetic matching) feels questionable`" in user2


def test_chatgpt_no_duplicate_code_blocks():
    html = EXAMPLE_HTML.read_text(encoding="utf-8")
    parser = get_parser("chatgpt")
    messages = parser.parse(html)
    joined = "\n".join(m.content for m in messages)
    fence_count = joined.count("```")
    assert fence_count > 0
    assert fence_count % 2 == 0
    assert fence_count < 200


def test_chatgpt_strips_code_block_labels():
    html = EXAMPLE_HTML.read_text(encoding="utf-8")
    parser = get_parser("chatgpt")
    messages = parser.parse(html)
    joined = "\n".join(m.content for m in messages)
    assert "YAML" not in joined
