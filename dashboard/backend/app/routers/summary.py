"""GET /api/summary — 페이퍼 누적 통계 (compare 도구 PaperStats 포맷)."""
from __future__ import annotations

from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Query

from app.config import ENGINE_LOGS
from app.db.jsonl_reader import filter_since, read_jsonl, trades_path

router = APIRouter()


@router.get("/api/summary")
def summary(days: int | None = Query(default=None, ge=1, le=3650)) -> dict:
    rows = read_jsonl(trades_path(ENGINE_LOGS))
    if days is not None:
        since = datetime.now(timezone.utc) - timedelta(days=days)
        rows = filter_since(rows, since, ts_field="ts_utc")

    sells = [t for t in rows if t.get("side") == "sell" and "realized_pnl_krw" in t]
    total_realized = sum(t["realized_pnl_krw"] for t in sells)
    total_invested = sum(t["entry_price_krw"] * t["volume"] for t in sells)
    cum_ret = (total_realized / total_invested) if total_invested > 0 else 0.0
    win = sum(1 for t in sells if t["realized_pnl_krw"] > 0)
    loss = sum(1 for t in sells if t["realized_pnl_krw"] <= 0)
    return {
        "trade_count": len(sells),
        "total_realized_krw": total_realized,
        "total_invested_krw": total_invested,
        "cumulative_return_ratio": cum_ret,
        "win_count": win,
        "loss_count": loss,
        "filter_days": days,
    }
