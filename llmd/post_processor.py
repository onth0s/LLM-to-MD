import re


def post_process(text: str) -> str:
    t = text

    t = re.sub(r"^\*\*Thought for \d+s\*\*\s*\n*", "", t, flags=re.MULTILINE)
    t = re.sub(r"^Thought for \d+s\s*\n*", "", t, flags=re.MULTILINE)

    t = re.sub(r"\n{4,}", "\n\n\n", t)
    t = re.sub(r"[ \t]+\n", "\n", t)
    t = re.sub(r"\n[ \t]+", "\n", t)
    t = re.sub(r" +", " ", t)
    t = t.strip()

    return t


def grok_post_process(text: str) -> str:
    t = post_process(text)

    t = re.sub(r"  +", " ", t)

    t = re.sub(r"(?<=\w)\*\*", " **", t)
    t = re.sub(r"\*\*(?=\w)", "** ", t)
    t = re.sub(r"(?<=\w)`", " `", t)
    t = re.sub(r"`(?=\w)", "` ", t)
    t = re.sub(r"(?<=\w)_", " _", t)
    t = re.sub(r"_(?=\w)", "_ ", t)

    t = re.sub(r"\*\* ([,.;:!?\)])", r"**\1", t)
    t = re.sub(r"` ([,.;:!?\)])", r"`\1", t)
    t = re.sub(r"_ ([,.;:!?\)])", r"_\1", t)

    stars = re.findall(r"\*\*", t)
    if len(stars) % 2 != 0:
        idx = t.rfind("**")
        if idx >= 0:
            t = t[:idx] + t[idx + 2 :]

    t = re.sub(r"\bGrok\b", "User-Agent", t)
    t = re.sub(r"(?<![a-zA-Z])grok(?![a-zA-Z])", "user-agent", t)

    t = re.sub(r" +", " ", t)
    t = t.strip()

    return t
