"""Markdown utilities for rendering/formatting."""

import re
from typing import List

# ANSI codes
RESET = "\033[0m"
BOLD = "\033[1m"
DIM = "\033[2m"
CYAN = "\033[96m"
GREEN = "\033[92m"
RED = "\033[91m"
YELLOW = "\033[93m"


def fmt_bold(text: str) -> str:
    """Render **bold** markers as actual bold ANSI text."""
    out: List[str] = []
    bold_on = False
    i = 0
    while i < len(text):
        if text.startswith("**", i):
            out.append(RESET + (BOLD if not bold_on else ""))
            bold_on = not bold_on
            i += 2
        else:
            out.append(text[i])
            i += 1
    if bold_on:
        out.append(RESET)
    return "".join(out)


def strip_ansi(text: str) -> str:
    """Remove ANSI escape sequences."""
    return re.sub(r"\x1b\[[0-9;]*m", "", text)


def heading(text: str) -> str:
    """Format a heading with underline."""
    out = f"\n{BOLD}{text}{RESET}\n{DIM}{'─' * 50}{RESET}"
    print(out)
    return out


def ok(msg: str) -> str:
    out = f"{GREEN}✅ {msg}{RESET}"
    print(out)
    return out


def err(msg: str) -> str:
    out = f"{RED}❌ {msg}{RESET}"
    print(out)
    return out


def info(msg: str) -> str:
    out = f"{CYAN}🤖 {msg}{RESET}"
    print(out)
    return out


def warn(msg: str) -> str:
    out = f"{YELLOW}⚠️  {msg}{RESET}"
    print(out)
    return out


def dim(text: str) -> str:
    return f"{DIM}{text}{RESET}"


def bold(text: str) -> str:
    return f"{BOLD}{text}{RESET}"