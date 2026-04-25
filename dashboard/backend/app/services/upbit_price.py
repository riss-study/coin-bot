"""Upbit public ticker — 30초 캐싱.

박제 출처: docs/stage1-subplans/v2-dashboard.md §5 (positions endpoint 시세 조회)

설계:
- Upbit /v1/ticker public API (인증 X, Keychain X) — least privilege 유지
- 30초 in-memory 캐싱 (단일 프로세스, 부하 절감)
- pyupbit 미의존 (의존성 분리 — engine 영역과 격리)
"""
from __future__ import annotations

import threading
import time
from typing import Any

import requests


_TTL_SEC = 30.0
_TIMEOUT_SEC = 5.0
_BASE = "https://api.upbit.com/v1/ticker"

_cache: dict[str, tuple[float, float]] = {}  # ticker → (fetched_at, price)
_lock = threading.RLock()


def get_current_price(ticker: str) -> float | None:
    """단일 ticker 현재가 (캐싱)."""
    now = time.time()
    with _lock:
        cached = _cache.get(ticker)
        if cached and (now - cached[0]) < _TTL_SEC:
            return cached[1]
    price = _fetch([ticker]).get(ticker)
    if price is not None:
        with _lock:
            _cache[ticker] = (now, price)
    return price


def get_current_prices(tickers: list[str]) -> dict[str, float]:
    """다중 ticker — 캐시 hit/miss 분리 호출."""
    now = time.time()
    out: dict[str, float] = {}
    miss: list[str] = []
    with _lock:
        for t in tickers:
            cached = _cache.get(t)
            if cached and (now - cached[0]) < _TTL_SEC:
                out[t] = cached[1]
            else:
                miss.append(t)
    if miss:
        fresh = _fetch(miss)
        with _lock:
            for t, p in fresh.items():
                _cache[t] = (now, p)
                out[t] = p
    return out


def _fetch(tickers: list[str]) -> dict[str, float]:
    if not tickers:
        return {}
    try:
        resp = requests.get(_BASE, params={"markets": ",".join(tickers)}, timeout=_TIMEOUT_SEC)
        resp.raise_for_status()
        data = resp.json()
    except (requests.RequestException, ValueError):
        return {}
    out: dict[str, float] = {}
    for row in data:
        market = row.get("market")
        price = row.get("trade_price")
        if market and price is not None:
            try:
                out[market] = float(price)
            except (TypeError, ValueError):
                continue
    return out
