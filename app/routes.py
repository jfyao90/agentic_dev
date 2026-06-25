"""FastAPI routes for listing and downloading PDF documents."""
from __future__ import annotations

from typing import AsyncIterator
from urllib.parse import quote

from fastapi import APIRouter, HTTPException, Path as PathParam
from fastapi.responses import StreamingResponse

from app.config import STREAM_CHUNK_SIZE
from app.documents import (
    DocumentNotFound,
    InvalidDocumentName,
    list_documents,
    resolve_document,
)

router = APIRouter(prefix="/documents", tags=["documents"])


@router.get("")
def get_documents() -> dict:
    """List available PDF documents."""
    docs = list_documents()
    return {
        "count": len(docs),
        "documents": [{"name": d.name, "size": d.size} for d in docs],
    }


@router.get("/{name}/download")
def download_document(
    name: str = PathParam(..., description="PDF file name, e.g. report.pdf"),
) -> StreamingResponse:
    """Stream a PDF document back to the client as a download."""
    try:
        path = resolve_document(name)
    except InvalidDocumentName as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except DocumentNotFound as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc

    file_size = path.stat().st_size

    async def iter_file() -> AsyncIterator[bytes]:
        with path.open("rb") as fh:
            while chunk := fh.read(STREAM_CHUNK_SIZE):
                yield chunk

    # RFC 5987 encoding so non-ASCII file names survive the header.
    ascii_name = path.name.encode("ascii", "ignore").decode() or "document.pdf"
    disposition = (
        f"attachment; filename=\"{ascii_name}\"; "
        f"filename*=UTF-8''{quote(path.name)}"
    )

    return StreamingResponse(
        iter_file(),
        media_type="application/pdf",
        headers={
            "Content-Disposition": disposition,
            "Content-Length": str(file_size),
        },
    )
