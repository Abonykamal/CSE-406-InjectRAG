"""FastAPI surface for the helpdesk application.

Five routes, thin by design. Handlers are sync `def` so FastAPI runs them in a
threadpool -- embedding and generation block, and must not sit on the event loop.

Response bodies carry the minimum: an answer, or a document id. No sources, no
scores, no exposure flags, no condition label. tools/test_integration.py asserts
the exact key sets, so re-adding a diagnostic field here fails the test rather
than quietly leaking the experiment into the product.

The one deliberate exception is GET /api/demo-config, which tells the browser
the model name to display and -- when INJECTRAG_DEMO_CONTROLS is on -- lets it
choose the corpus and the defense per conversation. With the flag off, any
corpus/defense a request carries is IGNORED rather than rejected: the product
surface cannot be driven from the browser, and a stale tab cannot silently
change the condition an answer was produced under.

Identity arrives in the request body and is NOT verified -- authentication was
explicitly scoped out of this build (see accounts.py and DEMO.md). The username
in the body is only resolved against the account table so the logs carry a real
user_id and display name.
"""

from __future__ import annotations

import pathlib

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

from .accounts import ACCOUNTS, authenticate
from .service import (
    HelpdeskService,
    demo_controls_enabled,
    resolved_model_name,
)

WEB_DIR = pathlib.Path(__file__).resolve().parents[2] / "web"


class LoginIn(BaseModel):
    username: str = Field(min_length=1, max_length=64)
    password: str = Field(min_length=1, max_length=128)


class ChatIn(BaseModel):
    question: str = Field(min_length=1, max_length=2000)
    user_id: str = Field(default="", max_length=64)
    username: str = Field(default="", max_length=64)
    conversation_id: str = Field(default="", max_length=64)
    # Honoured only when the demo controls are enabled; see the module docstring.
    corpus: str | None = Field(default=None, max_length=16)
    defense: str | None = Field(default=None, max_length=16)


class CaseIn(BaseModel):
    case_date: str = Field(min_length=1, max_length=32)
    title: str = Field(min_length=1, max_length=200)
    description: str = Field(min_length=1, max_length=20000)
    resolution: str = Field(min_length=1, max_length=20000)
    user_id: str = Field(default="", max_length=64)
    username: str = Field(default="", max_length=64)


def _caller(username: str, user_id: str) -> dict:
    """Resolve the claimed identity for the log line. Unverified by design."""
    account = ACCOUNTS.get((username or "").strip().lower())
    if account is None:
        return {"user_id": user_id or None, "username": username or None, "display": None}
    return {
        "user_id": account["user_id"],
        "username": (username or "").strip().lower(),
        "display": account["display"],
    }


def create_app(service: HelpdeskService) -> FastAPI:
    app = FastAPI(title="Northwind IT Helpdesk", docs_url=None, redoc_url=None)
    app.mount("/static", StaticFiles(directory=str(WEB_DIR)), name="static")

    @app.get("/")
    def index() -> FileResponse:
        return FileResponse(WEB_DIR / "index.html")

    @app.post("/api/login")
    def login(payload: LoginIn) -> dict:
        account = authenticate(payload.username, payload.password)
        if account is None:
            raise HTTPException(status_code=401, detail="Incorrect username or password")
        return account

    @app.get("/api/demo-config")
    def demo_config() -> dict:
        """What the browser needs to render itself.

        `model` is display-only and always present -- the employee is told which
        assistant answered them. The rest describes the demo controls: whether
        they are shown at all, and what they start on.
        """
        return {
            "controls": demo_controls_enabled(),
            "corpus": service.corpus,
            "defense": service.defense,
            "model": resolved_model_name(),
        }

    @app.post("/api/chat")
    def chat(payload: ChatIn) -> dict:
        controls = demo_controls_enabled()
        try:
            answer = service.ask(
                payload.question,
                _caller(payload.username, payload.user_id),
                defense=payload.defense if controls else None,
                corpus=payload.corpus if controls else None,
                conversation_id=payload.conversation_id or None,
            )
        except ValueError as e:
            raise HTTPException(status_code=422, detail=str(e))
        return {"answer": answer}

    @app.post("/api/cases")
    def create_case(payload: CaseIn) -> dict:
        try:
            document_id = service.submit_case(
                {
                    "case_date": payload.case_date,
                    "title": payload.title,
                    "description": payload.description,
                    "resolution": payload.resolution,
                },
                _caller(payload.username, payload.user_id),
            )
        except ValueError as e:
            raise HTTPException(status_code=422, detail=str(e))
        return {"document_id": document_id}

    return app
