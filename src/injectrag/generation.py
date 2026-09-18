"""Generation adapters: fake, Gemini, OpenAI, and Groq.

The provider sits behind one small function so retrieval/scoring never import a
vendor SDK. Select a provider with INJECTRAG_PROVIDER=fake|gemini|openai|groq.
In auto mode, Groq wins when GROQ_API_KEY is set, OpenAI wins when OPENAI_API_KEY
is set, Gemini wins when a Gemini key is set, and otherwise a scripted fake
provider runs so the whole pipeline is exercisable offline. The fake deliberately
"obeys" an injected instruction when it sees one, so the plumbing and metrics can
be validated without a key -- it is NOT evidence of real model behavior.
"""

from __future__ import annotations

import logging
import os
import re
import time
from dataclasses import dataclass

# Quiet google-genai's "Automatic function calling" advisory; we use none.
logging.getLogger("google_genai.models").setLevel(logging.ERROR)

_GEMINI_MODEL = os.environ.get("INJECTRAG_GEMINI_MODEL", "gemini-3.8-flash")
_GEMINI_TIMEOUT_SECONDS = float(os.environ.get("INJECTRAG_GEMINI_TIMEOUT_SECONDS", "90"))
_GEMINI_MAX_OUTPUT_TOKENS = int(os.environ.get("INJECTRAG_GEMINI_MAX_OUTPUT_TOKENS", "1024"))
_GEMINI_MIN_KEY_GAP_SECONDS = float(os.environ.get("INJECTRAG_GEMINI_MIN_KEY_GAP_SECONDS", "4.5"))
_GEMINI_MAX_RETRIES = int(os.environ.get("INJECTRAG_GEMINI_MAX_RETRIES", "20"))
_GEMINI_RETRY_FOREVER = os.environ.get("INJECTRAG_GEMINI_RETRY_FOREVER", "1") == "1"
_OPENAI_MODEL = os.environ.get("INJECTRAG_OPENAI_MODEL", "gpt-oss-20b")
_OPENAI_TIMEOUT_SECONDS = float(os.environ.get("INJECTRAG_OPENAI_TIMEOUT_SECONDS", "90"))
_OPENAI_MAX_OUTPUT_TOKENS = int(os.environ.get("INJECTRAG_OPENAI_MAX_OUTPUT_TOKENS", "1024"))
_OPENAI_MIN_CALL_GAP_SECONDS = float(os.environ.get("INJECTRAG_OPENAI_MIN_CALL_GAP_SECONDS", "30"))
_OPENAI_MAX_RETRIES = int(os.environ.get("INJECTRAG_OPENAI_MAX_RETRIES", "20"))
_OPENAI_RETRY_FOREVER = os.environ.get("INJECTRAG_OPENAI_RETRY_FOREVER", "1") == "1"
_GROQ_MODEL = os.environ.get("INJECTRAG_GROQ_MODEL", "openai/gpt-oss-20b")
_GROQ_BASE_URL = os.environ.get("GROQ_BASE_URL", "https://api.groq.com/openai/v1")

_gemini_clients: dict[int, object] = {}
_gemini_next_slot = 0
_gemini_last_call_at: dict[int, float] = {}
_openai_client = None
_openai_last_call_at: float | None = None


@dataclass
class Generation:
    text: str
    provider: str
    model: str
    finish_reason: str
    error: str | None = None


def _api_key() -> str | None:
    return os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY")


def _gemini_keys() -> list[str]:
    raw = os.environ.get("INJECTRAG_GEMINI_KEYS", "")
    keys = [k.strip() for k in raw.split(",") if k.strip()]
    if keys:
        return keys
    key = _api_key()
    return [key] if key else []


def _selected_provider() -> str:
    provider = os.environ.get("INJECTRAG_PROVIDER", "auto").strip().lower()
    if provider and provider != "auto":
        return provider
    if os.environ.get("GROQ_API_KEY"):
        return "groq"
    if os.environ.get("OPENAI_API_KEY"):
        return "openai"
    if _gemini_keys():
        return "gemini"
    return "fake"


def generate(system_instruction: str, user_message: str) -> Generation:
    provider = _selected_provider()
    if provider == "fake":
        return _fake_generate(system_instruction, user_message)
    if provider in {"openai", "groq"}:
        return _compatible_generate(provider, system_instruction, user_message)
    if provider != "gemini":
        return Generation(
            text="",
            provider=provider or "unknown",
            model="",
            finish_reason="error",
            error=f"unsupported provider '{provider}'; use fake, gemini, openai, or groq",
        )
    if not _gemini_keys():
        return Generation(
            text="",
            provider="gemini",
            model=_GEMINI_MODEL,
            finish_reason="error",
            error="INJECTRAG_PROVIDER=gemini but no Gemini key is set",
        )
    return _gemini_generate(system_instruction, user_message)


def _get_gemini_client(slot: int, key: str):
    if slot not in _gemini_clients:
        from google import genai

        _gemini_clients[slot] = genai.Client(api_key=key)
    return _gemini_clients[slot]


def _classify(msg: str) -> str:
    low = msg.lower()
    if "not_found" in low or "not found" in low or "404" in low:
        return "missing"
    if "503" in msg or "unavailable" in low or "overloaded" in low:
        return "overload"
    if "429" in msg or "resource_exhausted" in low or "rate" in low:
        return "ratelimit"
    return "other"


def _next_gemini_slot() -> tuple[int, str]:
    global _gemini_next_slot
    keys = _gemini_keys()
    slot = _gemini_next_slot % len(keys)
    _gemini_next_slot += 1
    return slot, keys[slot]


def _wait_for_gemini_key(slot: int) -> None:
    last = _gemini_last_call_at.get(slot)
    if last is None:
        _gemini_last_call_at[slot] = time.monotonic()
        return
    wait = (last + _GEMINI_MIN_KEY_GAP_SECONDS) - time.monotonic()
    if wait > 0:
        print(f"[gemini] waiting {wait:.1f}s for key slot {slot + 1} rate-limit spacing", flush=True)
        time.sleep(wait)
    _gemini_last_call_at[slot] = time.monotonic()


def _is_retryable_gemini_error(exc: Exception) -> bool:
    kind = _classify(str(exc))
    return kind in {"overload", "ratelimit"}


def _gemini_retry_wait_seconds(attempt: int, exc: Exception) -> float:
    kind = _classify(str(exc))
    if kind == "ratelimit":
        return max(_GEMINI_MIN_KEY_GAP_SECONDS, 15.0)
    return min(30.0, float(2 ** min(attempt, 5)))


def _try_gemini_slot(slot: int, key: str, system_instruction: str, user_message: str) -> Generation:
    from google.genai import types

    client = _get_gemini_client(slot, key)
    _wait_for_gemini_key(slot)
    resp = client.models.generate_content(
        model=_GEMINI_MODEL,
        contents=user_message,
        config=types.GenerateContentConfig(
            system_instruction=system_instruction,
            max_output_tokens=_GEMINI_MAX_OUTPUT_TOKENS,
            http_options=types.HttpOptions(timeout=_GEMINI_TIMEOUT_SECONDS * 1000),
        ),
    )
    finish = "stop"
    try:
        finish = str(resp.candidates[0].finish_reason)
    except Exception:
        pass
    return Generation(
        text=(resp.text or "").strip(),
        provider=f"gemini:key{slot + 1}",
        model=_GEMINI_MODEL,
        finish_reason=finish,
    )


def _gemini_generate(system_instruction: str, user_message: str) -> Generation:
    attempt = 0
    last_err = None
    while _GEMINI_RETRY_FOREVER or attempt < _GEMINI_MAX_RETRIES:
        attempt += 1
        slot, key = _next_gemini_slot()
        try:
            return _try_gemini_slot(slot, key, system_instruction, user_message)
        except Exception as e:  # noqa: BLE001 - classify provider SDK exceptions
            last_err = f"key{slot + 1}: {type(e).__name__}: {e}"
            if not _is_retryable_gemini_error(e):
                return Generation(
                    text="",
                    provider=f"gemini:key{slot + 1}",
                    model=_GEMINI_MODEL,
                    finish_reason="error",
                    error=f"non-retryable error after {attempt} attempt(s): {last_err}",
                )
            wait = _gemini_retry_wait_seconds(attempt, e)
            print(
                f"[gemini] {_GEMINI_MODEL} key slot {slot + 1} attempt {attempt} failed; "
                f"retrying in {wait:.1f}s with the next key slot: {last_err}",
                flush=True,
            )
            time.sleep(wait)
    return Generation(
        text="",
        provider="gemini",
        model=_GEMINI_MODEL,
        finish_reason="error",
        error=f"retry budget exhausted after {attempt} attempt(s): {last_err}",
    )


# --- OpenAI-compatible providers -----------------------------------------

def _compatible_config(provider: str) -> tuple[str, str, str | None]:
    if provider == "groq":
        return (
            os.environ.get("GROQ_API_KEY", ""),
            _GROQ_MODEL,
            _GROQ_BASE_URL,
        )
    return (
        os.environ.get("OPENAI_API_KEY", ""),
        _OPENAI_MODEL,
        os.environ.get("OPENAI_BASE_URL"),
    )


def _get_compatible_client(api_key: str, base_url: str | None):
    global _openai_client
    if _openai_client is None:
        from openai import OpenAI

        kwargs = {
            "api_key": api_key,
            "timeout": _OPENAI_TIMEOUT_SECONDS,
            "max_retries": 0,  # keep retry policy visible in this file
        }
        if base_url:
            kwargs["base_url"] = base_url
        _openai_client = OpenAI(**kwargs)
    return _openai_client


def _wait_for_compatible_rate_limit(provider: str) -> None:
    """Proactively space calls for the provided 30 RPM / 8k TPM limits.

    The default 30-second gap is intentionally conservative for this RAG prompt,
    whose input context plus output can be much larger than one tiny chat turn.
    Override with INJECTRAG_OPENAI_MIN_CALL_GAP_SECONDS after measuring usage.
    """
    global _openai_last_call_at
    if _openai_last_call_at is None:
        _openai_last_call_at = time.monotonic()
        return
    wait = (_openai_last_call_at + _OPENAI_MIN_CALL_GAP_SECONDS) - time.monotonic()
    if wait > 0:
        print(f"[{provider}] waiting {wait:.1f}s for rate-limit spacing", flush=True)
        time.sleep(wait)
    _openai_last_call_at = time.monotonic()


def _is_retryable_compatible_error(exc: Exception) -> bool:
    name = type(exc).__name__.lower()
    msg = str(exc).lower()
    non_retryable = (
        "authenticationerror",
        "permissiondeniederror",
        "notfounderror",
        "badrequesterror",
    )
    if any(kind in name for kind in non_retryable):
        return False
    retryable = (
        "ratelimiterror",
        "apiconnectionerror",
        "apitimestouterror",
        "internalservererror",
        "timeout",
        "timed out",
        "rate limit",
        "429",
        "500",
        "502",
        "503",
        "504",
        "overloaded",
        "temporarily unavailable",
        "connection",
    )
    return any(kind in name or kind in msg for kind in retryable)


def _compatible_retry_wait_seconds(attempt: int, exc: Exception) -> float:
    msg = str(exc).lower()
    wait = min(60.0, float(2 ** min(attempt, 6)))
    if "429" in msg or "rate" in msg:
        wait = max(wait, _OPENAI_MIN_CALL_GAP_SECONDS, 60.0)
    return wait


def _compatible_generate(provider: str, system_instruction: str, user_message: str) -> Generation:
    api_key, model, base_url = _compatible_config(provider)
    key_name = "GROQ_API_KEY" if provider == "groq" else "OPENAI_API_KEY"
    if not api_key:
        return Generation(
            text="",
            provider=provider,
            model=model,
            finish_reason="error",
            error=f"INJECTRAG_PROVIDER={provider} but {key_name} is not set",
        )

    try:
        client = _get_compatible_client(api_key, base_url)
    except Exception as e:  # noqa: BLE001 - dependency/configuration errors are trial errors
        return Generation(
            text="",
            provider=provider,
            model=model,
            finish_reason="error",
            error=f"{provider} client setup failed: {type(e).__name__}: {e}",
        )

    attempt = 0
    last_err = None
    while _OPENAI_RETRY_FOREVER or attempt < _OPENAI_MAX_RETRIES:
        attempt += 1
        try:
            _wait_for_compatible_rate_limit(provider)
            response = client.responses.create(
                model=model,
                input=[
                    {"role": "system", "content": system_instruction},
                    {"role": "user", "content": user_message},
                ],
                max_output_tokens=_OPENAI_MAX_OUTPUT_TOKENS,
            )
            return Generation(
                text=(response.output_text or "").strip(),
                provider=provider,
                model=model,
                finish_reason="stop",
            )
        except Exception as e:  # noqa: BLE001 - classify provider SDK exceptions
            last_err = f"{type(e).__name__}: {e}"
            if not _is_retryable_compatible_error(e):
                return Generation(
                    text="",
                    provider=provider,
                    model=model,
                    finish_reason="error",
                    error=f"non-retryable error after {attempt} attempt(s): {last_err}",
                )
            wait = _compatible_retry_wait_seconds(attempt, e)
            print(
                f"[{provider}] {model} attempt {attempt} failed; "
                f"retrying in {wait:.1f}s: {last_err}",
                flush=True,
            )
            time.sleep(wait)

    return Generation(
        text="",
        provider=provider,
        model=model,
        finish_reason="error",
        error=f"retry budget exhausted after {attempt} attempt(s): {last_err}",
    )


# --- fake provider -------------------------------------------------------

_INJECTION_CUES = (
    "respond only",
    "instead respond",
    "do not mention this",
    "do not give the old",
    "assistant, note",
)
_DIRECTIVE_RE = re.compile(r"(https?://[^\s\"'<>]+|[a-z0-9.-]+\.example[a-z0-9/.\-]*)", re.IGNORECASE)


def _looks_injected(text: str) -> bool:
    low = text.lower()
    return sum(cue in low for cue in _INJECTION_CUES) >= 1


def _fake_generate(system_instruction: str, user_message: str) -> Generation:
    """A crude stand-in. If the assembled message contains retrieved text that
    looks like an injected instruction AND the system prompt does not tell the
    model to ignore embedded instructions, the fake 'complies' by echoing the
    directive it found. This lets the attack/defense difference show up offline."""
    spotlighted = "do not follow" in system_instruction.lower() and "instruction" in system_instruction.lower()
    looks_injected = _looks_injected(user_message)
    if looks_injected and not spotlighted:
        m = _DIRECTIVE_RE.search(user_message)
        directive = m.group(1) if m else "the instructed action"
        text = (
            f"To resolve this, please go to {directive} and follow the steps there "
            f"to complete your request."
        )
        return Generation(text=text, provider="fake", model="fake-injectable", finish_reason="stop")
    # Otherwise a bland grounded-ish stub.
    return Generation(
        text=(
            "Based on the available IT documentation, follow the standard account "
            "recovery procedure and contact the IT Service Desk on extension 4400 if "
            "you need help. [fake provider: set GEMINI_API_KEY for real answers]"
        ),
        provider="fake",
        model="fake-benign",
        finish_reason="stop",
    )
