"""GET /api/logs — engine-YYYYMMDD.log JSONL tail."""
from __future__ import annotations

from datetime import datetime, timezone

from fastapi import APIRouter, Query

from app.config import ENGINE_LOGS
from app.db.jsonl_reader import engine_log_path, tail_jsonl

router = APIRouter()


@router.get("/api/logs")
def logs(
    n: int = Query(default=50, ge=1, le=2000),
    level: str | None = Query(default=None, description="ERROR | WARNING | INFO | DEBUG (None=전체)"),
    date: str | None = Query(default=None, description="YYYYMMDD (default=UTC 오늘)"),
) -> dict:
    path = engine_log_path(ENGINE_LOGS, date)
    rows = tail_jsonl(path, n=n * 5 if level else n)  # level 필터 시 더 가져와서 필터
    if level:
        upper = level.upper()
        rows = [r for r in rows if str(r.get("level", "")).upper() == upper]
    rows = rows[-n:]
    return {"logs": rows, "count": len(rows), "log_file": path.name, "level_filter": level}
