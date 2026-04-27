"""V2-Strategy-ML ML-01b: 데이터 수집 (Upbit 250 코인 + Binance global BTC + USD/KRW 환율).

박제 출처: docs/stage1-subplans/v2-strategy-ml-trend-factor.md §3.3 (정정 후 24m)

데이터:
- Upbit pyupbit OHLCV: 2023-04-01 ~ 2026-04-25 (warmup 9m + 24m + OOS 8m)
- Binance public API BTCUSDT 일봉: 동기간
- yfinance USD/KRW: 동기간
- 결과: research/data/ml_v2/ 디렉토리
"""
from __future__ import annotations

import json
import time
from datetime import datetime, timedelta, timezone
from pathlib import Path

import pandas as pd
import pyupbit
import requests


OUT_DIR = Path(__file__).parent.parent / "data" / "ml_v2"
OUT_DIR.mkdir(parents=True, exist_ok=True)

# 학습 시작 + warmup 200d + OOS 8m (총 ~36m)
WINDOW_START = pd.Timestamp("2023-04-01", tz="UTC")
WINDOW_END = pd.Timestamp("2026-04-25", tz="UTC")


def fetch_upbit_universe() -> list[dict]:
    resp = requests.get(
        "https://api.upbit.com/v1/market/all",
        params={"isDetails": "true"}, timeout=10,
    )
    resp.raise_for_status()
    krw = [m for m in resp.json() if m.get("market", "").startswith("KRW-")]
    return krw


def fetch_upbit_ohlcv(market: str, start_utc: pd.Timestamp, end_utc: pd.Timestamp) -> pd.DataFrame:
    """pyupbit get_ohlcv_from — 200 bars limit per call, 자동 paging."""
    end_kst = end_utc.tz_convert("Asia/Seoul")
    start_kst = start_utc.tz_convert("Asia/Seoul")
    df = pyupbit.get_ohlcv_from(
        ticker=market, interval="day",
        fromDatetime=start_kst.strftime("%Y-%m-%d %H:%M:%S"),
        to=end_kst.strftime("%Y-%m-%d %H:%M:%S"),
        period=0.15,
    )
    if df is None or df.empty:
        return pd.DataFrame()
    if df.index.tz is None:
        df.index = df.index.tz_localize("Asia/Seoul").tz_convert("UTC")
    df = df.loc[start_utc:end_utc]
    df["market"] = market
    return df


def fetch_binance_btc() -> pd.DataFrame:
    """Binance BTCUSDT 일봉 (페이징 1000 bar 한번)."""
    start_ms = int(WINDOW_START.timestamp() * 1000)
    end_ms = int(WINDOW_END.timestamp() * 1000)
    rows = []
    cur = start_ms
    while cur < end_ms:
        resp = requests.get(
            "https://api.binance.com/api/v3/klines",
            params={"symbol": "BTCUSDT", "interval": "1d",
                    "startTime": cur, "endTime": end_ms, "limit": 1000},
            timeout=10,
        )
        resp.raise_for_status()
        batch = resp.json()
        if not batch:
            break
        rows.extend(batch)
        last_ts = batch[-1][0]
        if last_ts == cur:
            break
        cur = last_ts + 86_400_000
        time.sleep(0.1)
    if not rows:
        return pd.DataFrame()
    df = pd.DataFrame(rows, columns=[
        "open_time", "open", "high", "low", "close", "volume",
        "close_time", "quote_volume", "trades", "taker_buy", "taker_quote", "ignore",
    ])
    df["ts_utc"] = pd.to_datetime(df["open_time"], unit="ms", utc=True)
    df = df.set_index("ts_utc")
    for c in ["open", "high", "low", "close", "volume"]:
        df[c] = df[c].astype(float)
    df = df[["open", "high", "low", "close", "volume"]]
    df = df.loc[WINDOW_START:WINDOW_END]
    return df


def fetch_usd_krw() -> pd.DataFrame:
    """yfinance USDKRW=X 일봉. 미설치 시 None 반환."""
    try:
        import yfinance as yf
    except ImportError:
        print("[warn] yfinance 미설치 → USD/KRW skip. pip install yfinance")
        return pd.DataFrame()
    df = yf.download("KRW=X", start=WINDOW_START.strftime("%Y-%m-%d"),
                     end=WINDOW_END.strftime("%Y-%m-%d"), progress=False, auto_adjust=False)
    if df is None or df.empty:
        return pd.DataFrame()
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = [c[0] for c in df.columns]
    df.index = pd.to_datetime(df.index, utc=True)
    df = df[["Open", "High", "Low", "Close", "Volume"]]
    df.columns = ["open", "high", "low", "close", "volume"]
    return df


def main() -> int:
    print(f"[window] {WINDOW_START.date()} ~ {WINDOW_END.date()}")

    # 1. Upbit universe
    print("[step 1] Upbit KRW universe fetch...")
    universe = fetch_upbit_universe()
    market_codes = [m["market"] for m in universe]
    print(f"  {len(market_codes)} KRW markets")
    with open(OUT_DIR / "market_meta.json", "w", encoding="utf-8") as f:
        json.dump(universe, f, ensure_ascii=False, indent=2)

    # 2. Upbit OHLCV (250 코인)
    print(f"[step 2] Upbit OHLCV fetch ({len(market_codes)} coins, {WINDOW_START.date()} ~ {WINDOW_END.date()})...")
    all_dfs = []
    fail_count = 0
    for i, market in enumerate(market_codes):
        try:
            df = fetch_upbit_ohlcv(market, WINDOW_START, WINDOW_END)
            if df.empty:
                fail_count += 1
                continue
            all_dfs.append(df)
            if (i + 1) % 50 == 0:
                print(f"  [{i+1}/{len(market_codes)}] OK (last={market}, rows={len(df)})")
        except Exception as e:
            print(f"  [{market}] FAIL: {str(e)[:60]}")
            fail_count += 1

    print(f"  total fetched: {len(all_dfs)} / fail: {fail_count}")
    if all_dfs:
        ohlcv = pd.concat(all_dfs)
        ohlcv = ohlcv.reset_index().rename(columns={"index": "ts_utc"})
        ohlcv.to_parquet(OUT_DIR / "ohlcv_upbit.parquet", index=False)
        print(f"  saved: {OUT_DIR / 'ohlcv_upbit.parquet'} ({len(ohlcv)} rows)")

    # 3. Binance global BTC
    print("[step 3] Binance BTCUSDT 일봉 fetch...")
    btc = fetch_binance_btc()
    if not btc.empty:
        btc.to_parquet(OUT_DIR / "btc_binance.parquet")
        print(f"  saved: btc_binance.parquet ({len(btc)} rows, {btc.index[0].date()} ~ {btc.index[-1].date()})")

    # 4. USD/KRW
    print("[step 4] USD/KRW (yfinance) fetch...")
    fx = fetch_usd_krw()
    if not fx.empty:
        fx.to_parquet(OUT_DIR / "usdkrw.parquet")
        print(f"  saved: usdkrw.parquet ({len(fx)} rows)")
    else:
        print("  [skip] yfinance unavailable. ML-02에서 환율 fallback 검토")

    # 요약
    print("\n[summary]")
    print(f"  Upbit OHLCV: {len(all_dfs)} markets, {sum(len(d) for d in all_dfs)} rows")
    print(f"  Binance BTC: {len(btc) if not btc.empty else 0} rows")
    print(f"  USD/KRW:     {len(fx) if not fx.empty else 0} rows")
    print(f"  saved → {OUT_DIR}")
    return 0


if __name__ == "__main__":
    import sys
    sys.exit(main())
