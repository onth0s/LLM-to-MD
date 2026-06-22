# llmd — LLM chat export to Markdown

Convert HTML exports from major LLM chatbots into clean, readable markdown.

```
llmd examples/grok/grok-conversation.html --provider grok
```

## Supported providers

| Provider     | Status       |
|-------------|-------------|
| Grok        | Done         |
| Gemini      | Done         |
| ChatGPT     | Coming soon  |
| Claude      | Coming soon  |
| DeepSeek    | Coming soon  |
| NotebookLM  | Coming soon  |

## Install

```bash
pip install -e .
```

## Default behavior

```
llmd <HTML input, if not provided, fall back to capturing the clipboard> -p [PROVIDER] -o <[PROVIDER]-conversation.md>, optional, defaults to cwd
```

- `input` is optional. When omitted, `llmd` reads the system clipboard via `pyperclip`.
- `-p/--provider` is required for now.
- `-o/--output` is optional. When omitted, `llmd` writes `<provider>-conversation.md` in the current working directory.
- If the destination file already exists, `llmd` prompts before overwriting.

### Examples

```bash
llmd grok-export.html -p grok                 # writes ./grok-conversation.md
llmd -p grok                                  # reads clipboard, writes ./grok-conversation.md
llmd gemini-export.html -p gemini -o notes.md # writes ./notes.md (overrides default name)
```

## Coming soon

- Automatic provider detection from HTML — for now `-p` must be supplied explicitly.
