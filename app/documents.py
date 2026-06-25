"""PDF document storage helpers with path-traversal protection."""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from app.config import DOCUMENTS_DIR


@dataclass(frozen=True)
class DocumentInfo:
    name: str
    size: int


class DocumentError(Exception):
    """Base error for document lookups."""


class InvalidDocumentName(DocumentError):
    """Raised when a requested name is unsafe or malformed."""


class DocumentNotFound(DocumentError):
    """Raised when a requested document does not exist."""


def ensure_documents_dir() -> Path:
    """Make sure the documents directory exists and return it."""
    DOCUMENTS_DIR.mkdir(parents=True, exist_ok=True)
    return DOCUMENTS_DIR


def list_documents() -> list[DocumentInfo]:
    """Return all *.pdf files in the documents directory."""
    base = ensure_documents_dir()
    docs: list[DocumentInfo] = []
    for path in sorted(base.glob("*.pdf")):
        if path.is_file():
            docs.append(DocumentInfo(name=path.name, size=path.stat().st_size))
    return docs


def resolve_document(name: str) -> Path:
    """Resolve a requested file name to a safe path inside DOCUMENTS_DIR.

    Guards against path traversal: the resolved path must stay within the
    documents directory and must be an existing .pdf file.
    """
    base = ensure_documents_dir()

    # Reject anything that is not a bare file name (no separators, no parent refs).
    if not name or name in {".", ".."}:
        raise InvalidDocumentName("Empty or invalid document name")
    if Path(name).name != name or "/" in name or "\\" in name:
        raise InvalidDocumentName("Document name must not contain path separators")
    if not name.lower().endswith(".pdf"):
        raise InvalidDocumentName("Only .pdf documents are available")

    candidate = (base / name).resolve()

    # Defense in depth: ensure the resolved path is still under the base dir.
    if base not in candidate.parents:
        raise InvalidDocumentName("Resolved path escapes the documents directory")

    if not candidate.is_file():
        raise DocumentNotFound(f"Document not found: {name}")

    return candidate
