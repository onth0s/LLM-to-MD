from .chatgpt import ChatGPTParser
from .claude import ClaudeParser
from .deepseek import DeepSeekParser
from .gemini import GeminiParser
from .grok import GrokParser
from .notebooklm import NotebookLMParser

_PARSERS = {
    "chatgpt": ChatGPTParser,
    "claude": ClaudeParser,
    "deepseek": DeepSeekParser,
    "gemini": GeminiParser,
    "grok": GrokParser,
    "notebooklm": NotebookLMParser,
}

def get_parser(name: str):
    cls = _PARSERS.get(name)
    if cls is None:
        known = ", ".join(sorted(_PARSERS))
        raise ValueError(f"Unknown provider '{name}'. Known: {known}")
    return cls()
