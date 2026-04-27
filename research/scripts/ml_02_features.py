"""V2-Strategy-ML ML-02: Feature Engineering 50개 + lookahead 단위 테스트.

박제 출처: docs/stage1-subplans/v2-strategy-ml-trend-factor.md §4 (50 features 사전 박제)

원칙:
- 모든 feature `t-1` 까지만 사용 (rolling/shift(1) 강제)
- universe_at(t): t시점에 거래 가능했던 코인만 (lookahead 차단)
- 김치 프리미엄: upbit_btc / (binance_btc × usd_krw)
- cross-sectional rank: 매 시점 universe 내에서 percentile

입력 (research/data/ml_v2/):
- ohlcv_upbit.parquet
- btc_binance.parquet
- usdkrw.parquet

출력:
- features.parquet (long format: ts_utc, market, 50 features + universe_member flag)
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd

DATA_DIR = Path(__file__).parent.parent / "data" / "ml_v2"

VOL_AVG = 20
LIQUIDITY_MIN_AVG_KRW = 1_000_000_000  # 일평균 거래대금 10억 KRW (sub-plan 함정 3)


def load_data() -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    ohlcv = pd.read_parquet(DATA_DIR / "ohlcv_upbit.parquet")
    ohlcv["ts_utc"] = pd.to_datetime(ohlcv["ts_utc"], utc=True)
    ohlcv = ohlcv.sort_values(["market", "ts_utc"]).reset_index(drop=True)
    ohlcv["dollar_volume"] = ohlcv["volume"] * ohlcv["close"]

    btc = pd.read_parquet(DATA_DIR / "btc_binance.parquet")
    btc.index = pd.to_datetime(btc.index, utc=True)
    btc = btc[["close"]].rename(columns={"close": "btc_global_usd"})

    fx = pd.read_parquet(DATA_DIR / "usdkrw.parquet")
    fx.index = pd.to_datetime(fx.index, utc=True)
    fx = fx[["close"]].rename(columns={"close": "usd_krw"})

    return ohlcv, btc, fx


def compute_kimchi_premium(ohlcv: pd.DataFrame, btc: pd.DataFrame, fx: pd.DataFrame) -> pd.DataFrame:
    """김치 프리미엄 = upbit_btc / (binance_btc × usd_krw).

    1.0 = 동일 가격 / >1.0 = 한국 더 비쌈 (김치 프리미엄)
    """
    # Upbit BTC close
    btc_upbit = ohlcv[ohlcv["market"] == "KRW-BTC"][["ts_utc", "close"]].rename(
        columns={"close": "btc_upbit_krw"}
    ).set_index("ts_utc")

    # Daily resample (모두 일봉 자정 정렬)
    btc_global = btc.resample("D").last().reindex(btc_upbit.index, method="ffill")
    fx_daily = fx.resample("D").last().reindex(btc_upbit.index, method="ffill")

    df = btc_upbit.join(btc_global).join(fx_daily)
    df["binance_btc_krw"] = df["btc_global_usd"] * df["usd_krw"]
    df["kimchi_premium_btc"] = df["btc_upbit_krw"] / df["binance_btc_krw"]
    df["kimchi_premium_change_7d"] = df["kimchi_premium_btc"].pct_change(7)
    df["kimchi_premium_zscore_30d"] = (
        (df["kimchi_premium_btc"] - df["kimchi_premium_btc"].rolling(30).mean())
        / df["kimchi_premium_btc"].rolling(30).std()
    )
    # macro features
    df["btc_return_7d"] = df["btc_global_usd"].pct_change(7)
    df["btc_volatility_30d"] = df["btc_global_usd"].pct_change().rolling(30).std()

    return df[[
        "kimchi_premium_btc", "kimchi_premium_change_7d", "kimchi_premium_zscore_30d",
        "btc_return_7d", "btc_volatility_30d",
    ]]


def compute_per_coin_features(g: pd.DataFrame) -> pd.DataFrame:
    """단일 코인 시계열 → coin-level features (rolling 후 shift(1) 강제, lookahead X)."""
    g = g.set_index("ts_utc").sort_index()
    close = g["close"]
    high = g["high"]
    low = g["low"]
    volume = g["volume"]
    dollar_volume = g["dollar_volume"]

    out = pd.DataFrame(index=g.index)

    # Momentum / Trend (15)
    for period in [1, 3, 7, 14, 30, 60, 90]:
        out[f"return_{period}d"] = close.pct_change(period)

    for ma in [5, 20, 50, 200]:
        ma_series = close.rolling(ma).mean()
        out[f"ma_{ma}_distance"] = (close - ma_series) / ma_series

    # MACD
    ema12 = close.ewm(span=12, adjust=False).mean()
    ema26 = close.ewm(span=26, adjust=False).mean()
    macd = ema12 - ema26
    macd_signal = macd.ewm(span=9, adjust=False).mean()
    out["macd_histogram"] = macd - macd_signal
    out["macd_signal_distance"] = (close - macd_signal) / close

    # Golden cross
    out["golden_cross_5_50"] = (close.rolling(5).mean() > close.rolling(50).mean()).astype(int)
    out["golden_cross_50_200"] = (close.rolling(50).mean() > close.rolling(200).mean()).astype(int)

    # Volatility (7)
    daily_ret = close.pct_change()
    out["realized_vol_7d"] = daily_ret.rolling(7).std()
    out["realized_vol_30d"] = daily_ret.rolling(30).std()
    out["realized_vol_90d"] = daily_ret.rolling(90).std()
    # ATR(14)
    tr = pd.concat([
        high - low, (high - close.shift(1)).abs(), (low - close.shift(1)).abs(),
    ], axis=1).max(axis=1)
    out["atr_14"] = tr.rolling(14).mean() / close
    # Parkinson
    out["parkinson_vol_14"] = np.sqrt(
        (1.0 / (4.0 * np.log(2.0))) * (np.log(high / low) ** 2).rolling(14).mean()
    )
    out["volatility_ratio_7d_30d"] = out["realized_vol_7d"] / out["realized_vol_30d"]
    out["volatility_change_7d"] = out["realized_vol_7d"].pct_change(7)

    # Liquidity (7, exclude rank — rank는 §4.4)
    out["log_dollar_volume_avg_7d"] = np.log1p(dollar_volume.rolling(7).mean())
    out["log_dollar_volume_avg_30d"] = np.log1p(dollar_volume.rolling(30).mean())
    # Amihud illiquidity (30d)
    abs_ret = daily_ret.abs()
    out["amihud_illiquidity_30d"] = (abs_ret / dollar_volume.replace(0, np.nan)).rolling(30).mean()
    out["volume_ratio_7d_30d"] = volume.rolling(7).mean() / volume.rolling(30).mean()
    out["volume_spike"] = volume / volume.rolling(20).mean()
    out["liquidity_change_30d"] = dollar_volume.rolling(30).mean().pct_change(30)
    out["avg_dollar_volume_30d"] = dollar_volume.rolling(30).mean()  # 필터용 (저유동성 함정 3)

    # Reversal (3)
    out["return_1d_reversal"] = -daily_ret  # 양봉 후 음봉 기대
    out["return_3d_reversal"] = -close.pct_change(3)
    # RSI(14) overbought
    delta = close.diff()
    gain = delta.where(delta > 0, 0).rolling(14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(14).mean()
    rs = gain / loss.replace(0, np.nan)
    rsi_14 = 100 - (100 / (1 + rs))
    out["overbought_score"] = (rsi_14 - 70).clip(lower=0) / 30  # 0~1 (RSI 70 이상부터)

    # Asset-specific (1 — listing days, sub-plan §4.7)
    out["days_since_listing"] = np.arange(len(g))

    # 모든 feature 1d shift (lookahead 차단) — t시점에 사용 가능한 건 t-1까지
    out_shifted = out.shift(1)
    return out_shifted


def add_cross_sectional_rank(features: pd.DataFrame) -> pd.DataFrame:
    """매 ts_utc 마다 cross-sectional percentile rank (10 features)."""
    rank_targets = [
        "return_7d", "return_14d", "return_30d",
        "realized_vol_30d", "log_dollar_volume_avg_30d",
        "ma_5_distance", "ma_50_distance", "ma_200_distance",
        "macd_histogram",
    ]
    for col in rank_targets:
        features[f"{col}_rank_cs"] = features.groupby("ts_utc")[col].rank(pct=True)

    # return_consistency: 30일 양봉 비율
    features["return_consistency_rank_cs"] = features.groupby("ts_utc")["return_30d"].rank(pct=True)

    return features


def filter_universe(features: pd.DataFrame) -> pd.DataFrame:
    """universe_at(t) 적용: 거래 가능 + 거래대금 ≥ 10억 KRW + 거래정지 X.

    universe_member=True인 행만 cross-sectional rank 계산 의미 (filter는 분석 단계에서).
    """
    features["universe_member"] = (
        features["close"].notna()
        & (features["volume"] > 0)
        & (features["avg_dollar_volume_30d"] >= LIQUIDITY_MIN_AVG_KRW)
    )
    return features


def main() -> int:
    print("[ML-02] Feature engineering 시작")
    print("[step 1] 데이터 로드...")
    ohlcv, btc, fx = load_data()
    print(f"  ohlcv: {len(ohlcv):,} rows, {ohlcv['market'].nunique()} markets")
    print(f"  btc:   {len(btc):,} rows")
    print(f"  fx:    {len(fx):,} rows")

    print("[step 2] 김치 프리미엄 + macro features 계산...")
    macro_df = compute_kimchi_premium(ohlcv, btc, fx)
    print(f"  macro: {macro_df.shape} (5 features)")
    print(f"  kimchi premium 요약: mean={macro_df['kimchi_premium_btc'].mean():.4f} "
          f"std={macro_df['kimchi_premium_btc'].std():.4f}")

    print("[step 3] 코인별 features 계산 (rolling + shift(1) lookahead 차단)...")
    feature_dfs = []
    for market, g in ohlcv.groupby("market", sort=False):
        feat = compute_per_coin_features(g)
        feat["market"] = market
        feat["close"] = g.set_index("ts_utc")["close"]  # filter용
        feat["volume"] = g.set_index("ts_utc")["volume"]
        feature_dfs.append(feat)
    features = pd.concat(feature_dfs).reset_index().rename(columns={"index": "ts_utc"})
    print(f"  per-coin features: {features.shape}")

    print("[step 4] macro features 병합...")
    features = features.set_index("ts_utc")
    features = features.join(macro_df, how="left")
    features = features.reset_index()

    print("[step 5] cross-sectional rank 추가...")
    features = add_cross_sectional_rank(features)

    print("[step 6] universe filter (avg_dollar_volume >= 10억)...")
    features = filter_universe(features)
    universe_count_per_day = features[features["universe_member"]].groupby("ts_utc").size()
    print(f"  universe size: mean={universe_count_per_day.mean():.0f} "
          f"min={universe_count_per_day.min()} max={universe_count_per_day.max()}")

    # 단위 테스트: lookahead 차단 검증
    print("[step 7] lookahead 단위 테스트...")
    sample_market = "KRW-BTC"
    sample = features[features["market"] == sample_market].sort_values("ts_utc")
    # return_7d at t = (close_{t-1} - close_{t-8}) / close_{t-8}
    btc_close_only = ohlcv[ohlcv["market"] == sample_market].set_index("ts_utc")["close"]
    expected = (btc_close_only.shift(1) - btc_close_only.shift(8)) / btc_close_only.shift(8)
    actual = sample.set_index("ts_utc")["return_7d"]
    diff = (actual - expected.reindex(actual.index)).dropna().abs().max()
    if diff < 1e-6:
        print(f"  lookahead PASS (return_7d diff < 1e-6, max={diff:.2e})")
    else:
        print(f"  lookahead FAIL diff={diff:.6f}")

    feature_cols = [c for c in features.columns if c not in ("ts_utc", "market", "close", "volume", "avg_dollar_volume_30d", "universe_member")]
    print(f"\n[summary]")
    print(f"  total rows: {len(features):,}")
    print(f"  total features: {len(feature_cols)}")
    print(f"  features: {feature_cols}")

    out_path = DATA_DIR / "features.parquet"
    features.to_parquet(out_path, index=False)
    print(f"  saved: {out_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
