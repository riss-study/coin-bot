"""V2-Strategy-ML v3: 분봉 데이터 수집 (4시간봉 top 50 KRW × 24m).

박제: 일봉 ML alpha 부재 → 분봉 microstructure 학술 지원 강함 (조사 결과).

Universe: Upbit KRW 거래대금 top 50 (ml_v2 30 + 추가 20)
Timeframe: 4시간봉 (24m × 6 = 4380 bars/coin)
Period: 2024-01-01 ~ 2026-04-25 (28m + warmup 4m)

이론적 데이터 양:
- 50 coins × ~4380 bars = 219,000 rows
- pyupbit 4시간봉 fetch: 200 bar/call × 22 calls/coin = 1,100 calls
- 50 coins × 22 calls × 0.2s = ~3.7분

출력: research/data/ml_v3/ohlcv_4h.parquet
"""
from __future__ import annotations

import json
import sys
import time
from datetime import timedelta
from pathlib import Path

import pandas as pd
import pyupbit
import requests


OUT_DIR = Path(__file__).parent.parent / "data" / "ml_v3"
OUT_DIR.mkdir(parents=True, exist_ok=True)

WINDOW_START = pd.Timestamp("2023-09-01", tz="UTC")  # warmup 4m + train 24m + OOS
WINDOW_END = pd.Timestamp("2026-04-25", tz="UTC")
INTERVAL = "minute240"  # 4시간봉
TOP_N = 50


def fetch_top_krw(n: int = 50) -> list[str]:
    all_markets = requests.get(
        "https://api.upbit.com/v1/market/all", params={"isDetails": "true"}, timeout=10,
    ).json()
    krw_meta = {
        m["market"]: m.get("market_warning", "NONE")
        for m in all_markets if m.get("market", "").startswith("KRW-")
    }
    markets = list(krw_meta.keys())

    tickers = []
    BATCH = 100
    for i in range(0, len(markets), BATCH):
        chunk = markets[i:i + BATCH]
        r = requests.get(
            "https://api.upbit.com/v1/ticker", params={"markets": ",".join(chunk)}, timeout=10,
        )
        tickers.extend(r.json())

    rows = [
        t for t in tickers
        if krw_meta.get(t.get("market", ""), "NONE") == "NONE"
    ]
    rows.sort(key=lambda t: t.get("acc_trade_price_24h", 0) or 0, reverse=True)
    return [t["market"] for t in rows[:n]]


def fetch_4h(market: str) -> pd.DataFrame:
    end_kst = WINDOW_END.tz_convert("Asia/Seoul")
    start_kst = WINDOW_START.tz_convert("Asia/Seoul")
    df = pyupbit.get_ohlcv_from(
        ticker=market, interval=INTERVAL,
        fromDatetime=start_kst.strftime("%Y-%m-%d %H:%M:%S"),
        to=end_kst.strftime("%Y-%m-%d %H:%M:%S"),
        period=0.15,
    )
    if df is None or df.empty:
        return pd.DataFrame()
    if df.index.tz is None:
        df.index = df.index.tz_localize("Asia/Seoul").tz_convert("UTC")
    df = df.loc[WINDOW_START:WINDOW_END]
    df["market"] = market
    return df


def main() -> int:
    print(f"[ML-v3 분봉 수집] {WINDOW_START.date()} ~ {WINDOW_END.date()}, {INTERVAL}, top {TOP_N}")

    print("[step 1] Upbit 거래대금 top fetch...")
    markets = fetch_top_krw(TOP_N)
    print(f"  {len(markets)} markets: {markets[:5]} ... {markets[-3:]}")
    with open(OUT_DIR / "universe.json", "w", encoding="utf-8") as f:
        json.dump(markets, f, ensure_ascii=False, indent=2)

    print(f"[step 2] {INTERVAL} OHLCV fetch ({len(markets)} coins)...")
    all_dfs = []
    fail = 0
    for i, m in enumerate(markets):
        try:
            df = fetch_4h(m)
            if df.empty:
                fail += 1
                continue
            all_dfs.append(df)
            if (i + 1) % 10 == 0:
                print(f"  [{i+1}/{len(markets)}] {m} rows={len(df)}")
        except Exception as e:
            print(f"  [{m}] FAIL {str(e)[:60]}")
            fail += 1

    print(f"  total: {len(all_dfs)} / fail: {fail}")
    if all_dfs:
        ohlcv = pd.concat(all_dfs)
        ohlcv = ohlcv.reset_index().rename(columns={"index": "ts_utc"})
        out_path = OUT_DIR / "ohlcv_4h.parquet"
        ohlcv.to_parquet(out_path, index=False)
        print(f"  saved: {out_path} ({len(ohlcv):,} rows)")
        # 통계
        bar_counts = ohlcv.groupby("market").size()
        print(f"  bars/market: mean={bar_counts.mean():.0f}, min={bar_counts.min()}, max={bar_counts.max()}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
