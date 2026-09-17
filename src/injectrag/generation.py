"""Generation adapter: Gemini via google-genai, with a fake fallback.

The provider sits behind one small function so retrieval/scoring never import a
vendor SDK. If GEMINI_API_KEY (or GOOGLE_API_KEY) is set, real Gemini answers;
otherwise a scripted fake provider runs so the whole pipeline is exercisable
offline. The fake deliberately "obeys" an injected instruction when it sees one,
so the plumbing and metrics can be validated without a key -- it is NOT evidence
of real model behavior.
"""

from __future__ import annotations

import logging
import os
import re
import time
from dataclasses import dataclass

# Quiet google-genai's "Automatic function calling" advisory; we use none.
logging.getLogger("google_genai.models").setLevel(logging.ERROR)

_MODEL = "gemini-3.8-flash"
_FALLBACK_MODELS = ("gemini-3.7-flash", "gemini-3.5-flash", "gemini-2.5-flash")
_MAX_RATELIMIT_RETRIES = 4


@dataclass
class Generation:
    text: str
    provider: str
    model: str
    finish_reason: str
    error: str | None = None


def _api_key() -> str | None:
    return os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY")


def generate(system_instruction: str, user_message: str) -> Generation:
    key = _api_key()
    if not key:
        return _fake_generate(system_instruction, user_message)
    return _gemini_generate(key, system_instruction, user_message)


def _gemini_generate(key: str, system_instruction: str, user_message: str) -> Generation:
    from google import genai
    from google.genai import types

    client = genai.Client(api_key=key)
    models_to_try = (_MODEL,) + _FALLBACK_MODELS
    last_err = None
    for model in models_to_try:
        for attempt in range(_MAX_RATELIMIT_RETRIES):
            try:
                resp = client.models.generate_content(
                    model=model,
                    contents=user_message,
                    config=types.GenerateContentConfig(
                        system_instruction=system_instruction,
                        temperature=0.0,
                        max_output_tokens=2048,
                    ),
                )
                text = (resp.text or "").strip()
                finish = "stop"
                try:
                    finish = str(resp.candidates[0].finish_reason)
                except Exception:
                    pass
                return Generation(text=text, provider="gemini", model=model, finish_reason=finish)
            except Exception as e:  # noqa: BLE001 - classify, retry or fall through
                msg = str(e)
                last_err = f"{type(e).__name__}: {e}"
                low = msg.lower()
                if "not_found" in low or "not found" in low or "404" in low:
                    break  # model unavailable to this account: try next fallback
                is_overload = "503" in msg or "unavailable" in low or "overloaded" in low
                is_ratelimit = "429" in msg or "resource_exhausted" in low or "rate" in low
                # Overload (503): a fallback model is likely to work, so give the
                # primary one quick retry then move on. Rate limit (429): waiting
                # is the only cure, so back off longer.
                if is_overload and attempt < 1:
                    time.sleep(3)
                    continue
                if is_ratelimit and attempt < _MAX_RATELIMIT_RETRIES - 1:
                    time.sleep(15 * (attempt + 1))
                    continue
                if is_overload or is_ratelimit:
                    break  # move to the next fallback model
                break  # other error: give up on this model
    return Generation(text="", provider="gemini", model=_MODEL, finish_reason="error", error=last_err)


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
