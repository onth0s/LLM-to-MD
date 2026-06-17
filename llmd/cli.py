import argparse
import io
import sys
from pathlib import Path

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

from .message import Message
from .parsers import get_parser


def render(messages: list[Message]) -> str:
    lines = ["# Conversation\n", "\n---\n"]
    for msg in messages:
        label = "## User" if msg.role == "user" else "## Agent"
        lines.append(f"\n{label}\n\n{msg.content}\n")
    return "".join(lines)


def main():
    parser = argparse.ArgumentParser(prog="llmd", description="Convert LLM chat exports to markdown")
    parser.add_argument("input", type=Path, help="Path to the input HTML file")
    parser.add_argument("--provider", "-p", required=True,
                        help="Provider name (e.g. grok, chatgpt, gemini, claude, deepseek, notebooklm)")
    parser.add_argument("--output", "-o", type=Path, default=None,
                        help="Output markdown file (default: stdout)")

    args = parser.parse_args()

    if not args.input.exists():
        print(f"Error: input file not found: {args.input}", file=sys.stderr)
        sys.exit(1)

    html = args.input.read_text(encoding="utf-8")
    provider = get_parser(args.provider)
    messages = provider.parse(html)

    output = render(messages)

    if args.output:
        args.output.write_text(output, encoding="utf-8")
        print(f"Done — {len(messages)} messages written to {args.output}")
    else:
        print(output)


if __name__ == "__main__":
    main()
