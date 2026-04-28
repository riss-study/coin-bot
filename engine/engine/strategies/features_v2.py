"""V2-Strategy-I features 계산 (47 features, ml_02_features.py 이식).

박제 출처: research/scripts/ml_02_features.py + docs/stage1-subplans/v2-strategy-ml-trend-factor.md §4
모든 feature t-1 lookahead 차단 (shift(1) 강제).

엔진 daemon이 매일 cycle 시작 시 호출:
    universe_data: dict[ticker, DataFrame OHLCV (warmup + 1)]
    btc_global, fx: 일봉 시계열
    → features DataFrame (rows = market × ts_utc, cols = 47 features + universe_member)
"""
from __future__ import annotations

from typing import Mapping

import numpy as np
import pandas as pd


VOL_AVG = 20
LIQUIDITY_MIN = 1_000_000_000   # 10억 KRW (sub-plan 함정 3)


def _per_coin_features(df: pd.DataFrame, bars_per_day: int = 1) -> pd.DataFrame:
    """단일 코인 시계열 → coin-level features (rolling 후 shift(1))."""
    bpd = bars_per_day
    df = df.set_index("ts_utc").sort_index() if "ts_utc" in df.columns else df.sort_index()
    close = df["close"]
    high = df["high"]
    low = df["low"]
    volume = df["volume"]
    dollar_volume = volume * close

    out = pd.DataFrame(index=df.index)

    # Momentum / Trend (15)
    for p in [1, 3, 7, 14, 30, 60, 90]:
        out[f"return_{p}d"] = close.pct_change(p * bpd)
    for ma in [5, 20, 50, 200]:
        m = close.rolling(ma * bpd).mean()
        out[f"ma_{ma}_distance"] = (close - m) / m
    ema12 = close.ewm(span=12, adjust=False).mean()
    ema26 = close.ewm(span=26, adjust=False).mean()
    macd = ema12 - ema26
    macd_sig = macd.ewm(span=9, adjust=False).mean()
    out["macd_histogram"] = macd - macd_sig
    out["macd_signal_distance"] = (close - macd_sig) / close
    out["golden_cross_5_50"] = (close.rolling(5 * bpd).mean() > close.rolling(50 * bpd).mean()).astype(int)
    out["golden_cross_50_200"] = (close.rolling(50 * bpd).mean() > close.rolling(200 * bpd).mean()).astype(int)

    # Volatility (7)
    daily_ret = close.pct_change()
    out["realized_vol_7d"] = daily_ret.rolling(7 * bpd).std()
    out["realized_vol_30d"] = daily_ret.rolling(30 * bpd).std()
    out["realized_vol_90d"] = daily_ret.rolling(90 * bpd).std()
    tr = pd.concat([high - low, (high - close.shift(1)).abs(), (low - close.shift(1)).abs()], axis=1).max(axis=1)
    out["atr_14"] = tr.rolling(14 * bpd).mean() / close
    out["parkinson_vol_14"] = np.sqrt(
        (1.0 / (4.0 * np.log(2.0))) * (np.log(high / low) ** 2).rolling(14 * bpd).mean()
    )
    out["volatility_ratio_7d_30d"] = out["realized_vol_7d"] / out["realized_vol_30d"]
    out["volatility_change_7d"] = out["realized_vol_7d"].pct_change(7 * bpd)

    # Liquidity (7 + avg_dollar_volume_30d for filter)
    out["log_dollar_volume_avg_7d"] = np.log1p(dollar_volume.rolling(7 * bpd).mean())
    out["log_dollar_volume_avg_30d"] = np.log1p(dollar_volume.rolling(30 * bpd).mean())
    abs_ret = daily_ret.abs()
    out["amihud_illiquidity_30d"] = (abs_ret / dollar_volume.replace(0, np.nan)).rolling(30 * bpd).mean()
    out["volume_ratio_7d_30d"] = volume.rolling(7 * bpd).mean() / volume.rolling(30 * bpd).mean()
    out["volume_spike"] = volume / volume.rolling(20 * bpd).mean()
    out["liquidity_change_30d"] = dollar_volume.rolling(30 * bpd).mean().pct_change(30 * bpd)
    out["avg_dollar_volume_30d"] = dollar_volume.rolling(30 * bpd).mean()  # filter용

    # Reversal (3)
    out["return_1d_reversal"] = -daily_ret
    out["return_3d_reversal"] = -close.pct_change(3 * bpd)
    delta = close.diff()
    gain = delta.where(delta > 0, 0).rolling(14 * bpd).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(14 * bpd).mean()
    rs = gain / loss.replace(0, np.nan)
    rsi = 100 - (100 / (1 + rs))
    out["overbought_score"] = (rsi - 70).clip(lower=0) / 30

    # Asset-specific (1)
    out["days_since_listing"] = np.arange(len(df)) // bpd

    return out.shift(1)  # lookahead 차단


def compute_macro(btc_global: pd.Series, fx: pd.Series, btc_upbit: pd.Series,
                   idx: pd.Index, bars_per_day: int = 1) -> pd.DataFrame:
    """김치 프리미엄 + macro features (5)."""
    bpd = bars_per_day
    btc_g = btc_global.reindex(idx, method="ffill")
    fx_d = fx.reindex(idx, method="ffill")
    df = pd.DataFrame(index=idx)
    df["binance_btc_krw"] = btc_g * fx_d
    df["kimchi_premium_btc"] = btc_upbit.reindex(idx) / df["binance_btc_krw"]
    df["kimchi_premium_change_7d"] = df["kimchi_premium_btc"].pct_change(7 * bpd)
    df["kimchi_premium_zscore_30d"] = (
        (df["kimchi_premium_btc"] - df["kimchi_premium_btc"].rolling(30 * bpd).mean())
        / df["kimchi_premium_btc"].rolling(30 * bpd).std()
    )
    df["btc_return_7d"] = btc_g.pct_change(7 * bpd)
    df["btc_volatility_30d"] = btc_g.pct_change().rolling(30 * bpd).std()
    return df[[
        "kimchi_premium_btc", "kimchi_premium_change_7d", "kimchi_premium_zscore_30d",
        "btc_return_7d", "btc_volatility_30d",
    ]]


def build_features(
    universe_data: Mapping[str, pd.DataFrame],
    btc_global: pd.Series,
    fx: pd.Series,
    bars_per_day: int = 1,
) -> pd.DataFrame:
    """전체 universe features 계산 + cross-sectional rank + universe_member.

    Args:
        universe_data: {market: DataFrame[ts_utc index, OHLCV cols]}
        btc_global: Binance BTC USD close (ts_utc index)
        fx: USD/KRW close (ts_utc index)

    Returns:
        DataFrame columns:
            ts_utc, market, close,
            (47 features),
            avg_dollar_volume_30d, universe_member
    """
    btc_upbit = universe_data.get("KRW-BTC")
    if btc_upbit is None:
        raise ValueError("KRW-BTC required for kimchi premium computation")
    btc_upbit_close = btc_upbit.set_index("ts_utc")["close"] if "ts_utc" in btc_upbit.columns else btc_upbit["close"]

    # per-coin
    feat_dfs = []
    for market, raw in universe_data.items():
        f = _per_coin_features(raw, bars_per_day=bars_per_day)
        f["market"] = market
        f["close"] = (raw.set_index("ts_utc")["close"] if "ts_utc" in raw.columns else raw["close"])
        feat_dfs.append(f)
    feats = pd.concat(feat_dfs).reset_index().rename(columns={"index": "ts_utc"})

    # macro (per ts_utc, broadcast all markets)
    all_idx = feats["ts_utc"].drop_duplicates().sort_values()
    macro = compute_macro(btc_global, fx, btc_upbit_close, pd.Index(all_idx), bars_per_day=bars_per_day)
    feats = feats.set_index("ts_utc").join(macro, how="left").reset_index()

    # cross-sectional rank (10)
    rank_targets = [
        "return_7d", "return_14d", "return_30d",
        "realized_vol_30d", "log_dollar_volume_avg_30d",
        "ma_5_distance", "ma_50_distance", "ma_200_distance",
        "macd_histogram",
    ]
    for col in rank_targets:
        feats[f"{col}_rank_cs"] = feats.groupby("ts_utc")[col].rank(pct=True)
    feats["return_consistency_rank_cs"] = feats.groupby("ts_utc")["return_30d"].rank(pct=True)

    # universe filter
    feats["universe_member"] = (
        feats["close"].notna()
        & (feats["avg_dollar_volume_30d"] >= LIQUIDITY_MIN)
    )
    return feats
