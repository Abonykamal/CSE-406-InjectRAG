"""Seeded accounts for the demonstration application.

Plaintext, in memory, no hashing and no sessions. This is a deliberate and
documented deviation from D12, which specified hashed passwords in SQLite behind
signed-cookie sessions with the role re-checked on every protected request. The
demo scopes authentication out entirely: the role comes from this table and the
browser carries the resolved identity in its request bodies, unverified. DEMO.md
records the deviation; nothing here should be read as an auth design.

Routing is by role: `employee` reaches the chat screen, `technician` reaches the
case-entry screen.
"""

from __future__ import annotations

ACCOUNTS: dict[str, dict[str, str]] = {
    "arif":   {"user_id": "E-1001", "password": "emp123",  "role": "employee",   "display": "Arif Hasan"},
    "nusrat": {"user_id": "E-1002", "password": "emp123",  "role": "employee",   "display": "Nusrat Jahan"},
    "rakib":  {"user_id": "T-2001", "password": "tech123", "role": "technician", "display": "Rakib Islam"},
}


def authenticate(username: str, password: str) -> dict | None:
    """Return the account without its password, or None.

    The password is never part of the returned dict, so a handler cannot leak it
    by serialising whatever authenticate() hands back.
    """
    account = ACCOUNTS.get((username or "").strip().lower())
    if account is None or password != account["password"]:
        return None
    return {
        "user_id": account["user_id"],
        "username": (username or "").strip().lower(),
        "display": account["display"],
        "role": account["role"],
    }
