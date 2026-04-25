"""GET /api/positions — open positions + 현재가 + unrealized PnL."""
from __future__ import annotations

from fastapi import APIRouter

from app.config import STATE_DB_PATH
from app.db.state_reader import list_open_positions
from app.services.upbit_price import get_current_prices

router = APIRouter()


@router.get("/api/positions")
def positions() -> dict:
    """오픈 포지션 + 현재가 + unrealized PnL.

    박제: unrealized = volume × current_price - krw_invested (entry_fees 포함, exit_fees 미차감)
    """
    try:
        rows = list_open_positions(STATE_DB_PATH)
    except FileNotFoundError:
        return {"positions": [], "note": "state DB 미존재 (daemon 첫 cycle 전)"}

    pairs = list({r["pair"] for r in rows})
    prices = get_current_prices(pairs) if pairs else {}

    out = []
    for r in rows:
        cur = prices.get(r["pair"])
        unrealized = None
        unrealized_pct = None
        market_value = None
        if cur is not None:
            market_value = r["volume"] * cur
            unrealized = market_value - r["krw_invested"]
            unrealized_pct = unrealized / r["krw_invested"] if r["krw_invested"] > 0 else 0.0
        out.append({
            **r,
            "current_price_krw": cur,
            "market_value_krw": market_value,
            "unrealized_pnl_krw": unrealized,
            "unrealized_pnl_ratio": unrealized_pct,
        })
    return {"positions": out, "count": len(out)}
