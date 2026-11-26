from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles


def mount_spa(app: FastAPI, static_dir: Path) -> None:
    """Serve the built frontend with history-API fallback to index.html (T1.10)."""
    root = static_dir.resolve()
    index = root / "index.html"
    if not index.is_file():
        return

    # Hashed bundles under /assets are cacheable; everything else (index.html, sw.js,
    # manifest) must be revalidated so new versions are picked up.
    no_cache = {"Cache-Control": "no-cache"}
    app.mount("/assets", StaticFiles(directory=root / "assets"), name="assets")

    @app.get("/{path:path}", include_in_schema=False)
    def spa(path: str) -> FileResponse:
        if path == "api" or path.startswith("api/"):
            raise HTTPException(404)
        candidate = (root / path).resolve()
        if path and candidate.is_file() and candidate.is_relative_to(root):
            return FileResponse(candidate, headers=no_cache)
        return FileResponse(index, headers=no_cache)
