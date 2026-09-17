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

# Primary is the D11-selected model; the study should use it when it answers.
# Fallbacks are other models confirmed available on the free tier, newest first.
# (gemini-2.5-flash was dropped: it now 404s for new users.)
_MODEL = os.environ.get("INJECTRAG_MODEL", "gemini-3.8-flash")
_FALLBACK_MODELS = ("gemini-3.7-flash", "gemini-3.6-flash", "gemini-3.5-flash")
_MAX_RATELIMIT_RETRIES = 4

# Once a model answers, remember it and try it first on later calls. This avoids
# hammering an overloaded primary 54 times and spreading rate-limit churn across
# models -- the whole run settles on one working model.
_resolved_model: str | None = None
_client = None


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


def _get_client(key: str):
    global _client
    if _client is None:
        from google import genai

        _client = genai.Client(api_key=key)
    return _client


def _classify(msg: str) -> str:
    low = msg.lower()
    if "not_found" in low or "not found" in low or "404" in low:
        return "missing"
    if "503" in msg or "unavailable" in low or "overloaded" in low:
        return "overload"
    if "429" in msg or "resource_exhausted" in low or "rate" in low:
        return "ratelimit"
    return "other"


def _try_model(client, model: str, system_instruction: str, user_message: str):
    """One model, with bounded retries for transient errors. Returns a Generation
    on success, or raises the last exception so the caller can fall back."""
    from google.genai import types

    last_exc = None
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
            finish = "stop"
            try:
                finish = str(resp.candidates[0].finish_reason)
            except Exception:
                pass
            return Generation(text=(resp.text or "").strip(), provider="gemini",
                              model=model, finish_reason=finish)
        except Exception as e:  # noqa: BLE001 - classify to retry or give up
            last_exc = e
            kind = _classify(str(e))
            if kind == "missing" or kind == "other":
                raise
            if kind == "overload" and attempt < 1:
                time.sleep(3)
                continue
            if kind == "ratelimit" and attempt < _MAX_RATELIMIT_RETRIES - 1:
                time.sleep(15 * (attempt + 1))
                continue
            raise
    raise last_exc  # pragma: no cover


def _gemini_generate(key: str, system_instruction: str, user_message: str) -> Generation:
    global _resolved_model
    client = _get_client(key)

    # Try the already-working model first, then primary, then fallbacks -- deduped.
    order = []
    for m in ((_resolved_model,) if _resolved_model else ()) + (_MODEL,) + _FALLBACK_MODELS:
        if m and m not in order:
            order.append(m)

    last_err = None
    for model in order:
        try:
            gen = _try_model(client, model, system_instruction, user_message)
            _resolved_model = model  # stick to whatever answered
            return gen
        except Exception as e:  # noqa: BLE001 - remember and try next model
            last_err = f"{model}: {type(e).__name__}: {e}"
            continue
    return Generation(text="", provider="gemini", model=order[-1] if order else _MODEL,
                      finish_reason="error", error=last_err)


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
