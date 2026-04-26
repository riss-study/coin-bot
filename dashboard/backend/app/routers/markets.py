"""GET /api/markets/top — KRW 마켓 top N (참고용, 매매 X)."""
from __future__ import annotations

from fastapi import APIRouter, HTTPException, Query

from app.services.upbit_markets import top_markets

router = APIRouter()


@router.get("/api/markets/top")
def markets_top(
    n: int = Query(default=20, ge=1, le=100),
    sort: str = Query(default="change_rate", pattern="^(change_rate|volume|loser)$"),
) -> dict:
    try:
        rows = top_markets(n=n, sort=sort)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    return {"markets": rows, "count": len(rows), "sort": sort}
