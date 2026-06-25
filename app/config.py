"""Application configuration."""
from __future__ import annotations

import os
from pathlib import Path

# Directory where PDF documents live. Override with DOCUMENTS_DIR env var.
DOCUMENTS_DIR = Path(
    os.environ.get(
        "DOCUMENTS_DIR",
        str(Path(__file__).resolve().parent.parent / "documents"),
    )
).resolve()

# Chunk size (bytes) used when streaming files back to the client.
STREAM_CHUNK_SIZE = int(os.environ.get("STREAM_CHUNK_SIZE", 64 * 1024))
