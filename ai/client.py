"""AI client for OpenRouter."""

import json
import time
from typing import Any, Optional

import requests

from ..config import get_config


class AIClient:
    """Wrapper around the OpenRouter chat-completion endpoint."""

    URL = "https://openrouter.ai/api/v1/chat/completions"

    def __init__(self, api_key: str, model: str = "openrouter/free") -> None:
        self.api_key = api_key
        self.model = model or "openrouter/free"

    def ask(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        stream: bool = False,
        temperature: float = 0.7,
        timeout: int = 600,
        max_retries: int = 3,
    ) -> Optional[str]:
        """Send a prompt via OpenRouter and return the response text."""
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "Accept": "text/event-stream" if stream else "application/json",
        }
        messages: list[dict[str, str]] = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        payload: dict[str, Any] = {
            "messages": messages,
            "model": self.model,
            "max_tokens": 16384,
            "stream": stream,
            "temperature": temperature,
        }

        attempt = 0
        while True:
            try:
                response = requests.post(
                    self.URL,
                    headers=headers,
                    json=payload,
                    stream=stream,
                    timeout=timeout,
                )
            except Exception as exc:
                attempt += 1
                if attempt < max_retries:
                    from ..utils import warn
                    warn(f"Network error: {exc}. Retrying ({attempt}/{max_retries})...")
                    time.sleep(2 * attempt)
                    continue
                from ..utils import err
                err(f"API Error: {exc}. Check your internet and API key.")
                return None

            status = getattr(response, "status_code", 0)

            if status == 429:
                attempt += 1
                if attempt < max_retries:
                    wait = self._retry_after_seconds(response, 10 * attempt)
                    from ..utils import warn
                    warn(f"Rate limited (429). Waiting {wait}s... (attempt {attempt}/{max_retries})")
                    time.sleep(wait)
                    continue
                from ..utils import err
                err("Rate limited (429) after retries. Wait a few minutes and try again.")
                return None
            if status == 401:
                from ..utils import err
                err("Invalid API key (401). Check the api_key in ~/tracker/config.json")
                return None
            if status != 200:
                from ..utils import err
                err(f"HTTP {status}: {self._body_preview(response)}")
                return None

            if stream:
                return self._read_stream(response)
            return self._read_json(response)

    @staticmethod
    def _retry_after_seconds(response: Any, default: int) -> int:
        try:
            raw = (getattr(response, "headers", {}) or {}).get("Retry-After")
            if raw is not None and str(raw).strip().isdigit():
                return int(str(raw).strip())
        except Exception:
            pass
        return default

    @staticmethod
    def _body_preview(response: Any, limit: int = 300) -> str:
        try:
            return (response.text or "")[:limit]
        except Exception:
            return "<unreadable response body>"

    def _read_stream(self, response: Any) -> Optional[str]:
        """Parse SSE chunks, print content live, return full text."""
        from ..utils import DIM, RESET, fmt_bold

        parts: list[str] = []
        pending = ""
        try:
            for line in response.iter_lines():
                if not line:
                    continue
                decoded = line.decode("utf-8", errors="replace")
                if not decoded.startswith("data:"):
                    continue
                data = decoded[len("data:") :].strip()
                if data == "[DONE]":
                    break
                try:
                    chunk = json.loads(data)
                except json.JSONDecodeError:
                    continue
                choices = chunk.get("choices") if isinstance(chunk, dict) else None
                if not choices:
                    continue
                first = choices[0] or {}
                delta = first.get("delta") or {}
                reasoning = delta.get("reasoning_content") or delta.get("reasoning")
                if reasoning:
                    print(f"{DIM}{reasoning}{RESET}", end="", flush=True)
                    continue
                piece = delta.get("content")
                if piece:
                    parts.append(piece)
                    buf = pending + piece
                    if buf.endswith("*") and not buf.endswith("**"):
                        emit, pending = buf[:-1], "*"
                    else:
                        emit, pending = buf, ""
                    if emit:
                        print(fmt_bold(emit), end="", flush=True)
        except Exception as exc:
            from ..utils import err
            err(f"API Error while streaming: {exc}")
            return "".join(parts) or None
        if pending:
            print(fmt_bold(pending), end="", flush=True)
        print()
        return "".join(parts) or None

    def _read_json(self, response: Any) -> Optional[str]:
        """Extract answer text from non-streaming JSON response."""
        try:
            data = response.json()
        except Exception as exc:
            from ..utils import err
            err(f"API Error: could not parse JSON response ({exc}).")
            return None
        if not isinstance(data, dict):
            from ..utils import err
            err(f"Unexpected response shape: {str(data)[:300]}")
            return None
        choices = data.get("choices")
        if not choices:
            from ..utils import err
            err(f"Unexpected response (no choices): {json.dumps(data)[:500]}")
            return None
        choice = choices[0] or {}
        message = choice.get("message") or {}
        if isinstance(message, dict) and message.get("content"):
            return message["content"]
        delta = choice.get("delta") or {}
        if isinstance(delta, dict) and delta.get("content"):
            return delta["content"]
        for key in ("text", "content", "output"):
            if choice.get(key):
                return choice[key]
        from ..utils import err
        err(f"Unknown response structure: {json.dumps(data)[:500]}")
        return None


def create_client() -> AIClient | None:
    """Create AIClient from config, or None if no API key."""
    cfg = get_config()
    if not cfg.get("api_key"):
        return None
    return AIClient(cfg["api_key"], model=cfg.get("model", "openrouter/free"))