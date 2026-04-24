"""Upbit 시세 데이터 조회 + 로컬 캐싱.

박제 출처:
- docs/stage1-v2-relaunch.md §2.4 market_data.py
- research/CLAUDE.md 검증된 pyupbit 0.2.34 패턴
- pyupbit 실측 (2026-04-24): get_ohlcv / get_ohlcv_from / get_current_price / get_orderbook

설계:
- 일봉 OHLCV: pyupbit.get_ohlcv_from (범위 지정) + 재시도 wrapper
- 실시간 가격: pyupbit.get_current_price (초당 10회 rate limit 여유)
- 캐싱: 최근 N일 OHLCV를 pandas DataFrame으로 메모리 캐시 (persistent는 state.py 별개)
- 타임존: 응답 naive KST → UTC 변환 강제 (research/CLAUDE.md Don'ts "타임존 누락 금지")
"""
from __future__ import annotations

import time
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import TYPE_CHECKING

import pandas as pd
import pyupbit

if TYPE_CHECKING:
    pass


@dataclass
class MarketData:
    """페어별 OHLCV 캐시 + 현재가."""

    pair: str
    ohlcv: pd.DataFrame             # index=UTC datetime, columns=open/high/low/close/volume/value
    fetched_ts_utc: str             # 마지막 조회 시각 (UTC ISO)


DEFAULT_RETRY_MAX = 5
DEFAULT_RETRY_BASE_S = 0.5         # 지수 백오프 초기값


def fetch_ohlcv(
    ticker: str,
    interval: str = "day",
    count: int = 300,
    period: float = 0.2,           # pyupbit 권장 (Upbit 10 req/s 여유)
    retry_max: int = DEFAULT_RETRY_MAX,
) -> pd.DataFrame:
    """일봉 OHLCV 조회 + 재시도 + UTC 타임존.

    pyupbit.get_ohlcv 반환이 None일 수 있음 (네트워크/rate limit) → 지수 백오프 재시도.

    Returns:
        pd.DataFrame: index=UTC tz-aware, columns=['open','high','low','close','volume','value']
    """
    last_exc: Exception | None = None
    for attempt in range(retry_max):
        try:
            df = pyupbit.get_ohlcv(ticker=ticker, interval=interval, count=count, period=period)
            if df is None or df.empty:
                raise RuntimeError(f"get_ohlcv returned {'None' if df is None else 'empty'}")
            # pyupbit은 naive KST 반환 (research/CLAUDE.md 박제)
            if df.index.tz is None:
                df.index = df.index.tz_localize("Asia/Seoul").tz_convert("UTC")
            elif str(df.index.tz) != "UTC":
                df.index = df.index.tz_convert("UTC")
            return df
        except Exception as e:
            last_exc = e
            if attempt < retry_max - 1:
                wait = DEFAULT_RETRY_BASE_S * (2 ** attempt)
                time.sleep(wait)
    raise RuntimeError(f"fetch_ohlcv failed after {retry_max} retries for {ticker}") from last_exc


def fetch_ohlcv_range(
    ticker: str,
    from_datetime: datetime,
    to_datetime: datetime | None = None,
    interval: str = "day",
    period: float = 0.2,
    retry_max: int = DEFAULT_RETRY_MAX,
) -> pd.DataFrame:
    """지정 범위 OHLCV 조회 (pyupbit.get_ohlcv_from wrapper).

    Args:
        from_datetime: UTC or KST datetime. pyupbit은 내부적으로 KST로 처리
        to_datetime: None이면 현재까지
    """
    # pyupbit get_ohlcv_from의 fromDatetime은 str 또는 datetime 수용
    # 내부에서 KST 기준으로 처리하므로, 입력이 UTC aware라면 KST로 변환하여 넘김
    from_dt_kst = from_datetime.astimezone(timezone.utc).astimezone()  # 로컬 KST
    to_dt_kst = to_datetime.astimezone(timezone.utc).astimezone() if to_datetime else None

    last_exc: Exception | None = None
    for attempt in range(retry_max):
        try:
            df = pyupbit.get_ohlcv_from(
                ticker=ticker,
                interval=interval,
                fromDatetime=from_dt_kst.strftime("%Y-%m-%d %H:%M:%S"),
                to=to_dt_kst.strftime("%Y-%m-%d %H:%M:%S") if to_dt_kst else None,
                period=period,
            )
            if df is None or df.empty:
                raise RuntimeError(f"get_ohlcv_from returned {'None' if df is None else 'empty'}")
            if df.index.tz is None:
                df.index = df.index.tz_localize("Asia/Seoul").tz_convert("UTC")
            elif str(df.index.tz) != "UTC":
                df.index = df.index.tz_convert("UTC")
            return df
        except Exception as e:
            last_exc = e
            if attempt < retry_max - 1:
                wait = DEFAULT_RETRY_BASE_S * (2 ** attempt)
                time.sleep(wait)
    raise RuntimeError(
        f"fetch_ohlcv_range failed after {retry_max} retries for {ticker} "
        f"({from_datetime} ~ {to_datetime})"
    ) from last_exc


def get_current_price(ticker: str | list[str], retry_max: int = DEFAULT_RETRY_MAX) -> float | dict[str, float]:
    """현재가 조회 + 재시도."""
    last_exc: Exception | None = None
    for attempt in range(retry_max):
        try:
            price = pyupbit.get_current_price(ticker=ticker)
            if price is None:
                raise RuntimeError(f"get_current_price returned None")
            return price
        except Exception as e:
            last_exc = e
            if attempt < retry_max - 1:
                time.sleep(DEFAULT_RETRY_BASE_S * (2 ** attempt))
    raise RuntimeError(f"get_current_price failed after {retry_max} retries") from last_exc


def get_orderbook(ticker: str, retry_max: int = DEFAULT_RETRY_MAX) -> dict:
    """호가창 조회 (슬리피지 사전 확인용)."""
    last_exc: Exception | None = None
    for attempt in range(retry_max):
        try:
            ob = pyupbit.get_orderbook(ticker=ticker)
            if ob is None:
                raise RuntimeError("get_orderbook returned None")
            # pyupbit 최신 버전은 dict 반환 (과거 버전 list 호환성 고려)
            if isinstance(ob, list) and len(ob) == 1:
                ob = ob[0]
            return ob
        except Exception as e:
            last_exc = e
            if attempt < retry_max - 1:
                time.sleep(DEFAULT_RETRY_BASE_S * (2 ** attempt))
    raise RuntimeError(f"get_orderbook failed after {retry_max} retries for {ticker}") from last_exc


if __name__ == "__main__":
    # V2-02 sanity check
    from engine.config import ENGINE_ROOT, ensure_runtime_dirs, load_config
    from engine.logger import setup_logger

    ensure_runtime_dirs()
    cfg = load_config()
    logger = setup_logger(ENGINE_ROOT / "logs", "INFO")

    # Pair 1: BTC 최근 5일 OHLCV
    logger.info("fetch_ohlcv_start", extra={"pair": "KRW-BTC", "count": 5})
    btc = fetch_ohlcv("KRW-BTC", interval="day", count=5)
    print(f"KRW-BTC 최근 5일 OHLCV:")
    print(btc[["open", "high", "low", "close", "volume"]].to_string())
    print(f"  index tz: {btc.index.tz}")

    # Pair 2: ETH 현재가
    eth_price = get_current_price("KRW-ETH")
    print(f"\nKRW-ETH 현재가: {eth_price:,.0f} KRW")

    # Pair 3: BTC 호가 (slice only)
    ob = get_orderbook("KRW-BTC")
    units = ob.get("orderbook_units", [])
    if units:
        top_bid = units[0].get("bid_price")
        top_ask = units[0].get("ask_price")
        spread = (top_ask - top_bid) if (top_bid and top_ask) else None
        print(f"\nKRW-BTC 최우선 호가: bid={top_bid:,.0f} / ask={top_ask:,.0f} / spread={spread}")

    logger.info("market_data_sanity_ok", extra={"btc_rows": len(btc), "eth_price": eth_price})
