"""V2-Strategy-I 1h: 1시간봉 데이터 수집 + Ridge 모델 학습 + artifact 저장.

박제: ml_v3 4시간봉 best (Ridge alpha=0.1, target 30d) 패턴 그대로 1시간봉 적용
- BARS_PER_DAY = 24
- target forward 30d = 720 bars
- Universe top 50 KRW

출력:
- research/data/ml_1h/ohlcv_1h.parquet
- engine/data/strategy_i_1h/{ridge_model.pkl, feature_cols.json}
"""
from __future__ import annotations

import json
import sys
import time
from datetime import timedelta
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
import pyupbit
import requests
from sklearn.linear_model import Ridge

ROOT = Path(__file__).parent.parent.parent
DATA_OUT = ROOT / "research" / "data" / "ml_1h"
DATA_V2 = ROOT / "research" / "data" / "ml_v2"
ARTIFACT_DIR = ROOT / "engine" / "data" / "strategy_i_1h"
DATA_OUT.mkdir(parents=True, exist_ok=True)
ARTIFACT_DIR.mkdir(parents=True, exist_ok=True)

sys.path.insert(0, str(ROOT / "research" / "scripts"))

# 학습 + warmup 데이터 1.5년 (1h × 24 × 365 = 8760 bars/년 × 1.5 = 13,140 bars/coin)
WINDOW_START = pd.Timestamp("2024-10-01", tz="UTC")
WINDOW_END = pd.Timestamp("2026-04-25", tz="UTC")
TRAIN_START = pd.Timestamp("2025-01-01", tz="UTC")  # warmup 3m 후
TRAIN_END = pd.Timestamp("2025-08-31", tz="UTC")
INTERVAL = "minute60"
TOP_N = 50
BARS_PER_DAY = 24
TARGET_PERIOD_DAYS = 30
RIDGE_ALPHA = 0.1
LIQUIDITY_MIN = 1_000_000_000


def fetch_top_krw(n: int = 50) -> list[str]:
    all_markets = requests.get(
        "https://api.upbit.com/v1/market/all", params={"isDetails": "true"}, timeout=10,
    ).json()
    krw_meta = {m["market"]: m.get("market_warning", "NONE")
                for m in all_markets if m.get("market", "").startswith("KRW-")}
    markets = list(krw_meta.keys())
    tickers = []
    BATCH = 100
    for i in range(0, len(markets), BATCH):
        chunk = markets[i:i + BATCH]
        r = requests.get("https://api.upbit.com/v1/ticker",
                         params={"markets": ",".join(chunk)}, timeout=10)
        tickers.extend(r.json())
    rows = [t for t in tickers if krw_meta.get(t.get("market", ""), "NONE") == "NONE"]
    rows.sort(key=lambda t: t.get("acc_trade_price_24h", 0) or 0, reverse=True)
    return [t["market"] for t in rows[:n]]


def fetch_1h(market: str) -> pd.DataFrame:
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
    print(f"[1h collect+train] {WINDOW_START.date()}~{WINDOW_END.date()}, {INTERVAL}, top {TOP_N}")

    # 1. universe + OHLCV
    if not (DATA_OUT / "ohlcv_1h.parquet").exists():
        print("[step 1] universe + OHLCV fetch...")
        markets = fetch_top_krw(TOP_N)
        print(f"  {len(markets)} markets")
        all_dfs = []
        for i, m in enumerate(markets):
            try:
                df = fetch_1h(m)
                if df.empty:
                    continue
                all_dfs.append(df)
                if (i + 1) % 10 == 0:
                    print(f"  [{i+1}/{len(markets)}] {m} rows={len(df)}")
            except Exception as e:
                print(f"  [{m}] FAIL {str(e)[:60]}")
        ohlcv = pd.concat(all_dfs).reset_index().rename(columns={"index": "ts_utc"})
        ohlcv.to_parquet(DATA_OUT / "ohlcv_1h.parquet", index=False)
        print(f"  saved: ohlcv_1h.parquet ({len(ohlcv):,} rows)")
    else:
        print("[step 1] ohlcv_1h.parquet 이미 존재 — skip")

    # 2. features + train
    print("[step 2] features build + train...")
    ohlcv = pd.read_parquet(DATA_OUT / "ohlcv_1h.parquet")
    ohlcv["ts_utc"] = pd.to_datetime(ohlcv["ts_utc"], utc=True)
    ohlcv = ohlcv.sort_values(["market", "ts_utc"]).reset_index(drop=True)
    ohlcv["dollar_volume"] = ohlcv["volume"] * ohlcv["close"]

    btc = pd.read_parquet(DATA_V2 / "btc_binance.parquet")
    fx = pd.read_parquet(DATA_V2 / "usdkrw.parquet")
    btc.index = pd.to_datetime(btc.index, utc=True)
    fx.index = pd.to_datetime(fx.index, utc=True)
    btc = btc[["close"]].rename(columns={"close": "btc_global_usd"})
    fx = fx[["close"]].rename(columns={"close": "usd_krw"})

    # ml_v3 기반 features (BARS_PER_DAY 변환만 다름)
    from ml_v3_features_grid import compute_macro
    import ml_v3_features_grid as v3
    v3.BARS_PER_DAY = BARS_PER_DAY  # 1h 단위로 override
    v3.TARGETS_BARS = {d: d * BARS_PER_DAY for d in [1, 3, 7, 14, 30]}

    macro = compute_macro(ohlcv, btc, fx)
    df = v3.build_features(ohlcv, macro)
    print(f"  rows: {len(df):,}, markets: {df['market'].nunique()}")

    feature_cols = [c for c in df.columns if c not in (
        "ts_utc", "market", "close", "volume", "avg_dollar_volume_30d",
        "universe_member",
        *[f"forward_return_{p}d" for p in [1, 3, 7, 14, 30]],
        *[f"target_{p}d" for p in [1, 3, 7, 14, 30]],
    )]

    train = df[
        (df["ts_utc"] >= TRAIN_START) & (df["ts_utc"] <= TRAIN_END)
        & df["universe_member"] & df["target_30d"].notna()
    ]
    if len(train) < 100:
        print(f"  ERROR: train rows {len(train)} 부족")
        return 1

    X_train = train[feature_cols].fillna(0.0).values
    y_train = train["target_30d"].values
    print(f"  train rows: {len(train):,}, features: {len(feature_cols)}")

    model = Ridge(alpha=RIDGE_ALPHA, random_state=42)
    model.fit(X_train, y_train)

    joblib.dump(model, ARTIFACT_DIR / "ridge_model.pkl")
    with open(ARTIFACT_DIR / "feature_cols.json", "w", encoding="utf-8") as f:
        json.dump({
            "feature_cols": feature_cols,
            "ridge_alpha": RIDGE_ALPHA,
            "target_period_days": TARGET_PERIOD_DAYS,
            "target_period_bars": TARGET_PERIOD_DAYS * BARS_PER_DAY,
            "bars_per_day": BARS_PER_DAY,
            "interval": INTERVAL,
            "train_start": TRAIN_START.isoformat(),
            "train_end": TRAIN_END.isoformat(),
            "train_rows": len(train),
        }, f, ensure_ascii=False, indent=2)
    print(f"  saved: {ARTIFACT_DIR}/{{ridge_model.pkl, feature_cols.json}}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
