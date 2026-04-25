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

from engine.config import KST


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
                df.index = df.index.tz_localize(KST).tz_convert("UTC")
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

    pyupbit 소스 실측 (2026-04-24):
    - fromDatetime은 str 또는 naive datetime 수용 (내부 `candle_date_time_kst` 사용)
    - 따라서 **명시적 KST 변환** 후 strftime 전달 (로컬 timezone 의존 제거, C-1 정정)

    Args:
        from_datetime: UTC-aware or KST-aware datetime (naive 금지)
        to_datetime: None이면 현재까지
    """
    # 명시적 Asia/Seoul 변환 (로컬 timezone 의존 제거)
    if from_datetime.tzinfo is None:
        raise ValueError("from_datetime은 tzinfo-aware 필수 (naive datetime 금지)")
    if to_datetime is not None and to_datetime.tzinfo is None:
        raise ValueError("to_datetime은 tzinfo-aware 필수 (naive datetime 금지)")

    from_dt_kst = from_datetime.astimezone(KST)
    to_dt_kst = to_datetime.astimezone(KST) if to_datetime else None

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
                df.index = df.index.tz_localize(KST).tz_convert("UTC")
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


def get_current_price(ticker: str, retry_max: int = DEFAULT_RETRY_MAX) -> float:
    """단일 페어 현재가 조회 + 재시도.

    W-4 정정 (2026-04-24): 이전 버전의 float | dict 반환 타입 분리.
    list 입력이 필요하면 get_current_prices() 사용.
    """
    if not isinstance(ticker, str):
        raise TypeError(f"ticker must be str, got {type(ticker).__name__}. Use get_current_prices for list.")

    last_exc: Exception | None = None
    for attempt in range(retry_max):
        try:
            price = pyupbit.get_current_price(ticker=ticker)
            if price is None:
                raise RuntimeError("get_current_price returned None")
            return float(price)
        except Exception as e:
            last_exc = e
            if attempt < retry_max - 1:
                time.sleep(DEFAULT_RETRY_BASE_S * (2 ** attempt))
    raise RuntimeError(f"get_current_price failed after {retry_max} retries for {ticker}") from last_exc


def get_current_prices(tickers: list[str], retry_max: int = DEFAULT_RETRY_MAX) -> dict[str, float]:
    """다중 페어 현재가 조회 + 재시도 (W-4 신설, 2026-04-24)."""
    if not isinstance(tickers, list) or not all(isinstance(t, str) for t in tickers):
        raise TypeError("tickers must be list[str]")

    last_exc: Exception | None = None
    for attempt in range(retry_max):
        try:
            prices = pyupbit.get_current_price(ticker=tickers)
            if prices is None:
                raise RuntimeError("get_current_price returned None")
            if isinstance(prices, (int, float)):
                # pyupbit이 단일 반환하는 경우 (예: len(tickers)==1)
                return {tickers[0]: float(prices)}
            return {k: float(v) for k, v in prices.items()}
        except Exception as e:
            last_exc = e
            if attempt < retry_max - 1:
                time.sleep(DEFAULT_RETRY_BASE_S * (2 ** attempt))
    raise RuntimeError(f"get_current_prices failed after {retry_max} retries for {tickers}") from last_exc


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
    # V2-02 sanity check (C-2 정정 2026-04-24: fetch_ohlcv_range + get_current_prices 포함)
    from datetime import timedelta
    from engine.config import ENGINE_ROOT, ensure_runtime_dirs, load_config
    from engine.logger import setup_logger

    ensure_runtime_dirs()
    cfg = load_config()
    logger = setup_logger(ENGINE_ROOT / "logs", "INFO")

    # 1: BTC 최근 5일 OHLCV (get_ohlcv)
    logger.info("fetch_ohlcv_start", extra={"pair": "KRW-BTC", "count": 5})
    btc = fetch_ohlcv("KRW-BTC", interval="day", count=5)
    print(f"KRW-BTC 최근 5일 OHLCV:")
    print(btc[["open", "high", "low", "close", "volume"]].to_string())
    print(f"  index tz: {btc.index.tz}")
    assert str(btc.index.tz) == "UTC", f"index tz should be UTC, got {btc.index.tz}"

    # 2: BTC 지난 30일 OHLCV (fetch_ohlcv_range) — C-2 신규 sanity
    now_utc = datetime.now(timezone.utc)
    from_utc = now_utc - timedelta(days=30)
    btc_range = fetch_ohlcv_range("KRW-BTC", from_datetime=from_utc, to_datetime=now_utc, interval="day")
    print(f"\nKRW-BTC 지난 30일 OHLCV: {len(btc_range)} bars, index tz={btc_range.index.tz}")
    assert str(btc_range.index.tz) == "UTC", "range index tz must be UTC"
    assert len(btc_range) >= 25, f"expected ~30 bars, got {len(btc_range)}"

    # 3: ETH 단일 현재가 (W-4 정정)
    eth_price = get_current_price("KRW-ETH")
    print(f"\nKRW-ETH 현재가: {eth_price:,.0f} KRW  (type={type(eth_price).__name__})")
    assert isinstance(eth_price, float)

    # 4: BTC + ETH 현재가 (W-4 신규 get_current_prices)
    prices = get_current_prices(["KRW-BTC", "KRW-ETH"])
    print(f"다중 현재가: {prices}")
    assert isinstance(prices, dict) and set(prices.keys()) == {"KRW-BTC", "KRW-ETH"}

    # 5: BTC 호가
    ob = get_orderbook("KRW-BTC")
    units = ob.get("orderbook_units", [])
    if units:
        top_bid = units[0].get("bid_price")
        top_ask = units[0].get("ask_price")
        spread = (top_ask - top_bid) if (top_bid and top_ask) else None
        print(f"\nKRW-BTC 최우선 호가: bid={top_bid:,.0f} / ask={top_ask:,.0f} / spread={spread}")

    # 6: 잘못된 입력 타입 검증
    try:
        get_current_price(["KRW-BTC"])  # list로 잘못 호출
    except TypeError as e:
        print(f"\nget_current_price list 거부 OK: {e}")

    try:
        fetch_ohlcv_range("KRW-BTC", from_datetime=datetime(2026, 1, 1))  # naive
    except ValueError as e:
        print(f"fetch_ohlcv_range naive 거부 OK: {e}")

    logger.info("market_data_sanity_ok", extra={
        "btc_rows": len(btc), "btc_range_rows": len(btc_range),
        "eth_price": eth_price, "prices_keys": list(prices.keys()),
    })
