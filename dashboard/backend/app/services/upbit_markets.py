"""Upbit KRW 마켓 전체 조회 + ticker 통합 (top N 정렬).

박제 출처: docs/stage1-subplans/v2-dashboard.md (D 옵션 — 알트 시세 표시)
실측 (2026-04-26):
- GET /v1/market/all → [{market, korean_name, ...}, ...] (정적, 1시간 캐싱)
- GET /v1/ticker?markets=...  → 다중 ticker (signed_change_rate, acc_trade_price_24h 등)
- 인증 X (public API, Keychain 미접근)
"""
from __future__ import annotations

import threading
import time
from typing import Any

import requests

_TICKER_TTL = 30.0
_MARKET_LIST_TTL = 3600.0
_TIMEOUT_SEC = 5.0
_BATCH_SIZE = 100  # /v1/ticker?markets=... URL 길이 제약

_market_cache: tuple[float, list[dict]] | None = None
_ticker_cache: tuple[float, list[dict]] | None = None
_lock = threading.RLock()


def _list_krw_markets() -> list[dict[str, Any]]:
    global _market_cache
    now = time.time()
    with _lock:
        if _market_cache and (now - _market_cache[0]) < _MARKET_LIST_TTL:
            return _market_cache[1]
    try:
        resp = requests.get(
            "https://api.upbit.com/v1/market/all",
            params={"isDetails": "false"}, timeout=_TIMEOUT_SEC,
        )
        resp.raise_for_status()
        all_markets = resp.json()
    except (requests.RequestException, ValueError):
        return _market_cache[1] if _market_cache else []
    krw = [m for m in all_markets if m.get("market", "").startswith("KRW-")]
    with _lock:
        _market_cache = (now, krw)
    return krw


def _list_all_tickers() -> list[dict[str, Any]]:
    global _ticker_cache
    now = time.time()
    with _lock:
        if _ticker_cache and (now - _ticker_cache[0]) < _TICKER_TTL:
            return _ticker_cache[1]

    krw_markets = _list_krw_markets()
    if not krw_markets:
        return []
    market_codes = [m["market"] for m in krw_markets]

    tickers: list[dict[str, Any]] = []
    for i in range(0, len(market_codes), _BATCH_SIZE):
        chunk = market_codes[i:i + _BATCH_SIZE]
        try:
            resp = requests.get(
                "https://api.upbit.com/v1/ticker",
                params={"markets": ",".join(chunk)}, timeout=_TIMEOUT_SEC,
            )
            resp.raise_for_status()
            tickers.extend(resp.json())
        except (requests.RequestException, ValueError):
            continue

    name_map = {m["market"]: m.get("korean_name", "") for m in krw_markets}
    for t in tickers:
        t["korean_name"] = name_map.get(t["market"], "")

    with _lock:
        _ticker_cache = (now, tickers)
    return tickers


def top_markets(n: int = 20, sort: str = "change_rate") -> list[dict[str, Any]]:
    """KRW 마켓 top N (정렬 기준: change_rate | volume).

    응답 필드 (실측 박제):
        market / korean_name / trade_price (현재가) / signed_change_rate (24h 변동률 ratio)
        acc_trade_price_24h (24h 거래대금 KRW) / opening_price / high_price / low_price
    """
    tickers = _list_all_tickers()
    if not tickers:
        return []
    if sort == "change_rate":
        tickers.sort(key=lambda t: t.get("signed_change_rate", 0) or 0, reverse=True)
    elif sort == "volume":
        tickers.sort(key=lambda t: t.get("acc_trade_price_24h", 0) or 0, reverse=True)
    elif sort == "loser":
        tickers.sort(key=lambda t: t.get("signed_change_rate", 0) or 0)
    else:
        raise ValueError(f"sort must be change_rate | volume | loser, got {sort}")
    return [
        {
            "market": t.get("market"),
            "korean_name": t.get("korean_name"),
            "trade_price": t.get("trade_price"),
            "signed_change_rate": t.get("signed_change_rate"),
            "acc_trade_price_24h": t.get("acc_trade_price_24h"),
            "opening_price": t.get("opening_price"),
            "high_price": t.get("high_price"),
            "low_price": t.get("low_price"),
        }
        for t in tickers[:n]
    ]
