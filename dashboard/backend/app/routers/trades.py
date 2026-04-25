"""GET /api/trades — trades-YYYY.jsonl 파싱."""
from __future__ import annotations

from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Query

from app.config import ENGINE_LOGS
from app.db.jsonl_reader import filter_since, read_jsonl, trades_path

router = APIRouter()


@router.get("/api/trades")
def trades(
    days: int | None = Query(default=None, ge=1, le=3650, description="최근 N일 (None=전체)"),
    year: int | None = Query(default=None, description="특정 연도 (default=올해)"),
) -> dict:
    rows = read_jsonl(trades_path(ENGINE_LOGS, year))
    if days is not None:
        since = datetime.now(timezone.utc) - timedelta(days=days)
        rows = filter_since(rows, since, ts_field="ts_utc")
    return {"trades": rows, "count": len(rows)}
