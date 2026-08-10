from pathlib import Path
from types import SimpleNamespace

import pyperclip
import pytest

from llmd import cli
from llmd.cli import _default_output_path, main

HERE = Path(__file__).resolve().parent
EXAMPLE_HTML = HERE.parent / "examples" / "grok" / "grok-conversation.html"


@pytest.fixture
def grok_html():
    return EXAMPLE_HTML.read_text(encoding="utf-8")


def test_default_output_path_uses_cwd(tmp_path):
    out = _default_output_path("grok", cwd=tmp_path)
    assert out == tmp_path / "grok-conversation.md"


def test_run_writes_default_output_in_cwd(tmp_path, monkeypatch, grok_html):
    monkeypatch.chdir(tmp_path)

    args = SimpleNamespace(input=None, provider="grok", output=None)
    monkeypatch.setattr(pyperclip, "paste", lambda: grok_html)

    cli.run(args)

    out = tmp_path / "grok-conversation.md"
    assert out.exists()
    assert "## User" in out.read_text(encoding="utf-8")


def test_run_honors_explicit_output(tmp_path, monkeypatch, grok_html):
    monkeypatch.chdir(tmp_path)
    target = tmp_path / "custom.md"

    args = SimpleNamespace(input=None, provider="grok", output=target)
    monkeypatch.setattr(pyperclip, "paste", lambda: grok_html)

    cli.run(args)

    assert target.exists()
    assert not (tmp_path / "grok-conversation.md").exists()


def test_run_adds_md_extension_to_explicit_output(tmp_path, monkeypatch, grok_html):
    monkeypatch.chdir(tmp_path)
    target = tmp_path / "custom"

    args = SimpleNamespace(input=None, provider="grok", output=target)
    monkeypatch.setattr(pyperclip, "paste", lambda: grok_html)

    cli.run(args)

    assert (tmp_path / "custom.md").exists()
    assert not target.exists()


def test_run_does_not_duplicate_md_extension(tmp_path, monkeypatch, grok_html):
    monkeypatch.chdir(tmp_path)
    target = tmp_path / "custom.md"

    args = SimpleNamespace(input=None, provider="grok", output=target)
    monkeypatch.setattr(pyperclip, "paste", lambda: grok_html)

    cli.run(args)

    assert target.exists()
    assert not (tmp_path / "custom.md.md").exists()


def test_run_handles_uppercase_md_extension(tmp_path, monkeypatch, grok_html):
    monkeypatch.chdir(tmp_path)
    target = tmp_path / "custom.MD"

    args = SimpleNamespace(input=None, provider="grok", output=target)
    monkeypatch.setattr(pyperclip, "paste", lambda: grok_html)

    cli.run(args)

    assert target.exists()
    assert not (tmp_path / "custom.MD.md").exists()


def test_run_reads_from_input_file(tmp_path, monkeypatch, grok_html):
    monkeypatch.chdir(tmp_path)
    src = tmp_path / "in.html"
    src.write_text(grok_html, encoding="utf-8")

    args = SimpleNamespace(input=src, provider="grok", output=None)

    def _fail_paste():
        raise AssertionError("clipboard should not be read when input file is provided")

    monkeypatch.setattr(pyperclip, "paste", _fail_paste)

    cli.run(args)

    assert (tmp_path / "grok-conversation.md").exists()


def test_run_prompts_on_collision_and_overwrites(tmp_path, monkeypatch, grok_html):
    monkeypatch.chdir(tmp_path)
    target = tmp_path / "grok-conversation.md"
    target.write_text("stale contents", encoding="utf-8")

    args = SimpleNamespace(input=None, provider="grok", output=None)
    monkeypatch.setattr(pyperclip, "paste", lambda: grok_html)

    cli.run(args, prompt_fn=lambda _: "y")

    assert "stale contents" not in target.read_text(encoding="utf-8")
    assert "## User" in target.read_text(encoding="utf-8")


def test_run_prompts_on_collision_and_aborts(tmp_path, monkeypatch, grok_html):
    monkeypatch.chdir(tmp_path)
    target = tmp_path / "grok-conversation.md"
    target.write_text("stale contents", encoding="utf-8")

    args = SimpleNamespace(input=None, provider="grok", output=None)
    monkeypatch.setattr(pyperclip, "paste", lambda: grok_html)

    with pytest.raises(SystemExit) as exc_info:
        cli.run(args, prompt_fn=lambda _: "n")

    assert exc_info.value.code == 0
    assert target.read_text(encoding="utf-8") == "stale contents"


def test_run_exits_when_clipboard_empty(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(pyperclip, "paste", lambda: "")

    args = SimpleNamespace(input=None, provider="grok", output=None)

    with pytest.raises(SystemExit) as exc_info:
        cli.run(args)

    assert exc_info.value.code == 1
    assert not (tmp_path / "grok-conversation.md").exists()


def test_run_exits_when_clipboard_unavailable(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)

    def _raise():
        raise pyperclip.PyperclipException("no clipboard backend")

    monkeypatch.setattr(pyperclip, "paste", _raise)

    args = SimpleNamespace(input=None, provider="grok", output=None)

    with pytest.raises(SystemExit) as exc_info:
        cli.run(args)

    assert exc_info.value.code == 1


def test_main_requires_provider(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)

    with pytest.raises(SystemExit) as exc_info:
        main([str(tmp_path / "anything.html")])

    assert exc_info.value.code == 2
