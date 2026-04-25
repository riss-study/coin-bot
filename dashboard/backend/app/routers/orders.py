"""GET /api/orders/recent — 최근 N개 주문 (state DB orders 테이블)."""
from __future__ import annotations

from fastapi import APIRouter, Query

from app.config import STATE_DB_PATH
from app.db.state_reader import list_open_orders, list_recent_orders

router = APIRouter()


@router.get("/api/orders/recent")
def orders_recent(n: int = Query(default=20, ge=1, le=500)) -> dict:
    try:
        rows = list_recent_orders(STATE_DB_PATH, limit=n)
    except FileNotFoundError:
        return {"orders": [], "count": 0, "note": "state DB 미존재"}
    return {"orders": rows, "count": len(rows)}


@router.get("/api/orders/open")
def orders_open() -> dict:
    try:
        rows = list_open_orders(STATE_DB_PATH)
    except FileNotFoundError:
        return {"orders": [], "count": 0, "note": "state DB 미존재"}
    return {"orders": rows, "count": len(rows)}
