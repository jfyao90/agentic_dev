"""Application entry point."""
from __future__ import annotations

from fastapi import FastAPI

from app.documents import ensure_documents_dir
from app.routes import router as documents_router

app = FastAPI(title="agentic_dev document API", version="0.1.0")
app.include_router(documents_router)


@app.on_event("startup")
def _startup() -> None:
    ensure_documents_dir()


@app.get("/health")
def health() -> dict:
    return {"status": "ok"}
