"""coin-bot dashboard backend (V2-Dashboard Phase 1).

박제 출처:
- docs/stage1-subplans/v2-dashboard.md
- dashboard/CLAUDE.md

실행:
    cd dashboard/backend
    source .venv/bin/activate
    uvicorn app.main:app --host 127.0.0.1 --port 8001 --reload
또는:
    python -m app.main
"""
from __future__ import annotations

import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import CORS_ORIGINS, HOST, PORT
from app.routers import health


logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")
log = logging.getLogger("dashboard.backend")


def create_app() -> FastAPI:
    app = FastAPI(
        title="coin-bot dashboard",
        version="0.1.0",
        description="V2-Dashboard Phase 1 read-only API. Upbit secrets 미접근, state DB read-only.",
    )
    app.add_middleware(
        CORSMiddleware,
        allow_origins=CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["GET", "OPTIONS"],
        allow_headers=["*"],
    )
    app.include_router(health.router)

    @app.get("/")
    def root() -> dict:
        return {"service": "coin-bot dashboard", "version": "0.1.0", "docs": "/docs"}

    return app


app = create_app()


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host=HOST, port=PORT, reload=False)
