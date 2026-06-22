# llmd — LLM chat export to Markdown

Convert HTML exports from major LLM chatbots into clean, readable markdown.

```
llmd examples/grok/grok-conversation.html --provider grok -o output.md
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

## Usage

```bash
llmd input.html --provider <provider> [-o output.md]
```

If `--output` is omitted, output is written to stdout.
