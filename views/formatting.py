import re

RESET = "\033[0m"

_COLORS = {
    "RESERVED": "\033[33m",  # 노랑
    "CONFIRMED": "\033[32m",  # 초록
    "PRODUCING": "\033[36m",  # 청록
    "RELEASE": "\033[35m",  # 보라
    "REJECTED": "\033[31m",  # 빨강
    "여유": "\033[32m",
    "부족": "\033[33m",
    "고갈": "\033[31m",
}

_ANSI_RE = re.compile(r"\033\[[0-9;]*m")


def colorize(text: str, key: str) -> str:
    color = _COLORS.get(key)
    if color is None:
        return text
    return f"{color}{text}{RESET}"


def _visible_len(text: str) -> int:
    return len(_ANSI_RE.sub("", str(text)))


def _pad(text: str, width: int) -> str:
    text = str(text)
    return text + " " * max(0, width - _visible_len(text))


def print_table(headers: list[str], rows: list[list[str]], widths: list[int]) -> None:
    header_line = "".join(_pad(h, w) for h, w in zip(headers, widths))
    print(header_line)
    print("-" * sum(widths))
    for row in rows:
        print("".join(_pad(cell, w) for cell, w in zip(row, widths)))
