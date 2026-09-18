"""FastAPI surface for the demonstration application.

Thin by design: every route validates its input, calls one DemoService method and
returns the result. Handlers are sync `def` so FastAPI runs them in a threadpool --
embedding and generation block, and must not sit on the event loop.
"""

from __future__ import annotations

import pathlib

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

from .service import DemoService

WEB_DIR = pathlib.Path(__file__).resolve().parents[2] / "web"


class TicketIn(BaseModel):
    subject: str = Field(default="", max_length=200)
    description: str = Field(min_length=1, max_length=20000)
    submitted_by: str = Field(default="employee", max_length=40)
    membership: str = Field(default="clean")


class ResolutionIn(BaseModel):
    resolution: str = Field(min_length=1, max_length=20000)


class ChatIn(BaseModel):
    question: str = Field(min_length=1, max_length=2000)
    defense: str = Field(default="off")


def create_app(service: DemoService) -> FastAPI:
    app = FastAPI(title="InjectRAG helpdesk demo", docs_url="/api/docs")
    app.mount("/static", StaticFiles(directory=str(WEB_DIR)), name="static")

    @app.get("/")
    def index() -> FileResponse:
        return FileResponse(WEB_DIR / "index.html")

    @app.get("/api/status")
    def status() -> dict:
        return service.status()

    @app.get("/api/corpus")
    def corpus() -> dict:
        return service.corpus()

    @app.get("/api/attack-payloads")
    def attack_payloads() -> dict:
        return {"payloads": service.attack_payloads()}

    @app.get("/api/tickets")
    def list_tickets() -> dict:
        return {"tickets": service.tickets()}

    @app.post("/api/tickets")
    def create_ticket(payload: TicketIn) -> dict:
        try:
            ticket = service.submit_ticket(
                payload.subject, payload.description,
                payload.submitted_by, payload.membership,
            )
        except ValueError as e:
            raise HTTPException(status_code=422, detail=str(e))
        return {"ticket": ticket.__dict__, "corpus": service.status()}

    @app.post("/api/tickets/{ticket_id}/resolve")
    def resolve_ticket(ticket_id: str, payload: ResolutionIn) -> dict:
        try:
            return service.resolve_ticket(ticket_id, payload.resolution)
        except KeyError:
            raise HTTPException(status_code=404, detail=f"no ticket {ticket_id}")
        except ValueError as e:
            raise HTTPException(status_code=422, detail=str(e))

    @app.post("/api/chat")
    def chat(payload: ChatIn) -> dict:
        try:
            return service.ask(payload.question, payload.defense)
        except ValueError as e:
            raise HTTPException(status_code=422, detail=str(e))

    @app.post("/api/reset")
    def reset() -> dict:
        return service.reset()

    return app
