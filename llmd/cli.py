import argparse
import io
import os
import sys
from pathlib import Path

import pyperclip
from rich.console import Console
from rich_argparse import RichHelpFormatter

from .message import Message
from .parsers import get_parser


def render(messages: list[Message]) -> str:
    lines = ["# Conversation\n", "\n---\n"]
    for msg in messages:
        label = "## User" if msg.role == "user" else "## Agent"
        lines.append(f"\n{label}\n\n{msg.content}\n")
    return "".join(lines)


def _default_output_path(provider: str, cwd: Path | None = None) -> Path:
    base = cwd if cwd is not None else Path.cwd()
    return base / f"{provider}-conversation.md"


def _ensure_md_suffix(path: Path) -> Path:
    return path if path.suffix.lower() == ".md" else Path(str(path) + ".md")


def _read_input_html(input_path: Path | None, console: Console) -> str:
    if input_path is not None:
        if not input_path.exists():
            console.print(f"[red]Error:[/] input file not found: {input_path}")
            sys.exit(1)
        return input_path.read_text(encoding="utf-8")

    try:
        html = pyperclip.paste()
    except pyperclip.PyperclipException as exc:
        console.print(
            "[red]Error:[/] could not access the clipboard "
            f"({exc.__class__.__name__}: {exc}). "
            "Install a clipboard backend or pass an input HTML file."
        )
        sys.exit(1)

    if not html or not html.strip():
        console.print(
            "[red]Error:[/] clipboard is empty. Copy an HTML export first, "
            "or pass an input HTML file as an argument."
        )
        sys.exit(1)

    return html


def _confirm_overwrite(path: Path, prompt_fn=input, console: Console = None) -> bool:
    if console is None:
        console = Console()
    answer = prompt_fn(f"'{path}' already exists. Overwrite? [y/N]: ").strip().lower()
    return answer in ("y", "yes")


def run(args, prompt_fn=input, console: Console = None):
    if console is None:
        console = Console()

    html = _read_input_html(args.input, console)

    try:
        provider = get_parser(args.provider)
    except ValueError as exc:
        console.print(f"[red]Error:[/] {exc}")
        sys.exit(1)

    messages = provider.parse(html)
    output_text = render(messages)

    output_path = args.output if args.output is not None else _default_output_path(args.provider)
    output_path = _ensure_md_suffix(output_path)

    if output_path.exists():
        if not _confirm_overwrite(output_path, prompt_fn=prompt_fn, console=console):
            console.print("[yellow]Aborted.[/] No files written.")
            sys.exit(0)

    output_path.write_text(output_text, encoding="utf-8")
    console.print(f"[green]Done[/] \u2014 {len(messages)} messages written to {output_path}")


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="llmd",
        description=(
            "Convert LLM chat exports to markdown. "
            "Reads an HTML file (or the clipboard if no file is given) "
            "and writes <provider>-conversation.md in the current directory."
        ),
        formatter_class=RichHelpFormatter,
    )
    parser.add_argument(
        "input",
        type=Path,
        nargs="?",
        default=None,
        help="Path to the input HTML file. If omitted, the clipboard is read.",
    )
    parser.add_argument(
        "--provider",
        "-p",
        required=True,
        help="Provider name (e.g. grok, chatgpt, gemini, claude, deepseek, notebooklm)",
    )
    parser.add_argument(
        "--output",
        "-o",
        type=Path,
        default=None,
        help="Output markdown file; .md is appended if missing (default: <provider>-conversation.md in the current directory)",
    )
    return parser


def main(argv=None, prompt_fn=input, console: Console = None):
    if console is None:
        console = Console()

    parser = _build_parser()
    args = parser.parse_args(argv)
    run(args, prompt_fn=prompt_fn, console=console)


if __name__ == "__main__":
    if sys.platform == "win32":
        os.system("")

    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

    main()
