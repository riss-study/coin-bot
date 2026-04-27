"""V2-Strategy-ML v3: 분봉 (4시간봉) features + 125 trial grid.

박제: ML-v2 일봉 grid는 Top decile fail + L-S inverse alpha 발견.
ML-v3 분봉으로 일봉과 비교 → microstructure alpha 검증.

설계:
- Universe: top 50 KRW (ml_v3_intraday_collect.py 결과)
- Timeframe: 4시간봉 (1d = 6 bars)
- Features: 47개 (ml_v2 동일, window을 4시간봉 단위로)
- Train/OOS: 2024-01-01 ~ 2025-08-31 / 2025-09-01 ~ 2026-04-25
- Models × Hyperparam × Targets = 125 trials (ml_v2 동일)

핵심 차이:
- realized_vol_30d → 30일 × 6 = 180 4h bars
- forward return 1d/3d/7d/14d/30d → 6/18/42/84/180 bars
- 김치 프리미엄: 일봉 값 broadcast (4시간 동일)
"""
from __future__ import annotations

import json
import math
import sys
import warnings
from pathlib import Path

import lightgbm as lgb
import numpy as np
import pandas as pd
import scipy.stats as scs
import xgboost as xgb
from sklearn.ensemble import RandomForestRegressor
from sklearn.linear_model import Ridge

warnings.filterwarnings("ignore")

DATA_V2 = Path(__file__).parent.parent / "data" / "ml_v2"
DATA_V3 = Path(__file__).parent.parent / "data" / "ml_v3"
RESULTS_DIR = Path(__file__).parent.parent / "notebooks" / "results"

TRAIN_START = pd.Timestamp("2024-01-01", tz="UTC")
TRAIN_END = pd.Timestamp("2025-08-31", tz="UTC")
OOS_START = pd.Timestamp("2025-09-01", tz="UTC")
OOS_END = pd.Timestamp("2026-04-25", tz="UTC")

# 4시간봉 단위로 환산
BARS_PER_DAY = 6
TARGETS = [1, 3, 7, 14, 30]   # days
TARGETS_BARS = {d: d * BARS_PER_DAY for d in TARGETS}

TOP_DECILE = 0.10
FEE_RATE = 0.0005
SLIPPAGE = {"major": 0.0005, "mid": 0.0010, "small": 0.0030}
LIQUIDITY_MIN = 1_000_000_000
EULER = 0.5772156649015329


def load_data():
    ohlcv = pd.read_parquet(DATA_V3 / "ohlcv_4h.parquet")
    ohlcv["ts_utc"] = pd.to_datetime(ohlcv["ts_utc"], utc=True)
    ohlcv = ohlcv.sort_values(["market", "ts_utc"]).reset_index(drop=True)
    ohlcv["dollar_volume"] = ohlcv["volume"] * ohlcv["close"]

    # macro (일봉 broadcast)
    btc = pd.read_parquet(DATA_V2 / "btc_binance.parquet")
    fx = pd.read_parquet(DATA_V2 / "usdkrw.parquet")
    btc.index = pd.to_datetime(btc.index, utc=True)
    fx.index = pd.to_datetime(fx.index, utc=True)
    return ohlcv, btc[["close"]].rename(columns={"close": "btc_global_usd"}), fx[["close"]].rename(columns={"close": "usd_krw"})


def compute_macro(ohlcv: pd.DataFrame, btc: pd.DataFrame, fx: pd.DataFrame) -> pd.DataFrame:
    btc_upbit = ohlcv[ohlcv["market"] == "KRW-BTC"][["ts_utc", "close"]].rename(
        columns={"close": "btc_upbit_krw"}
    ).set_index("ts_utc")
    btc_g = btc.resample("D").last().reindex(btc_upbit.index, method="ffill")
    fx_d = fx.resample("D").last().reindex(btc_upbit.index, method="ffill")
    df = btc_upbit.join(btc_g).join(fx_d)
    df["binance_btc_krw"] = df["btc_global_usd"] * df["usd_krw"]
    df["kimchi_premium_btc"] = df["btc_upbit_krw"] / df["binance_btc_krw"]
    df["kimchi_premium_change_7d"] = df["kimchi_premium_btc"].pct_change(7 * BARS_PER_DAY)
    df["kimchi_premium_zscore_30d"] = (
        (df["kimchi_premium_btc"] - df["kimchi_premium_btc"].rolling(30 * BARS_PER_DAY).mean())
        / df["kimchi_premium_btc"].rolling(30 * BARS_PER_DAY).std()
    )
    df["btc_return_7d"] = df["btc_global_usd"].pct_change(7 * BARS_PER_DAY)
    df["btc_volatility_30d"] = df["btc_global_usd"].pct_change().rolling(30 * BARS_PER_DAY).std()
    return df[[
        "kimchi_premium_btc", "kimchi_premium_change_7d", "kimchi_premium_zscore_30d",
        "btc_return_7d", "btc_volatility_30d",
    ]]


def compute_per_coin(g: pd.DataFrame) -> pd.DataFrame:
    g = g.set_index("ts_utc").sort_index()
    close, high, low, volume, dv = g["close"], g["high"], g["low"], g["volume"], g["dollar_volume"]
    out = pd.DataFrame(index=g.index)

    # Momentum (window in 4h bars)
    for d in [1, 3, 7, 14, 30, 60, 90]:
        out[f"return_{d}d"] = close.pct_change(d * BARS_PER_DAY)
    for ma in [5, 20, 50, 200]:
        m = close.rolling(ma * BARS_PER_DAY).mean()
        out[f"ma_{ma}_distance"] = (close - m) / m

    # MACD (4시간봉 standard 12/26/9 그대로)
    ema12 = close.ewm(span=12, adjust=False).mean()
    ema26 = close.ewm(span=26, adjust=False).mean()
    macd = ema12 - ema26
    macd_sig = macd.ewm(span=9, adjust=False).mean()
    out["macd_histogram"] = macd - macd_sig
    out["macd_signal_distance"] = (close - macd_sig) / close

    out["golden_cross_5_50"] = (close.rolling(5 * BARS_PER_DAY).mean() > close.rolling(50 * BARS_PER_DAY).mean()).astype(int)
    out["golden_cross_50_200"] = (close.rolling(50 * BARS_PER_DAY).mean() > close.rolling(200 * BARS_PER_DAY).mean()).astype(int)

    # Volatility
    ret = close.pct_change()
    out["realized_vol_7d"] = ret.rolling(7 * BARS_PER_DAY).std()
    out["realized_vol_30d"] = ret.rolling(30 * BARS_PER_DAY).std()
    out["realized_vol_90d"] = ret.rolling(90 * BARS_PER_DAY).std()
    tr = pd.concat([high - low, (high - close.shift(1)).abs(), (low - close.shift(1)).abs()], axis=1).max(axis=1)
    out["atr_14"] = tr.rolling(14 * BARS_PER_DAY).mean() / close
    out["parkinson_vol_14"] = np.sqrt((1.0 / (4.0 * np.log(2.0))) * (np.log(high / low) ** 2).rolling(14 * BARS_PER_DAY).mean())
    out["volatility_ratio_7d_30d"] = out["realized_vol_7d"] / out["realized_vol_30d"]
    out["volatility_change_7d"] = out["realized_vol_7d"].pct_change(7 * BARS_PER_DAY)

    # Liquidity
    out["log_dollar_volume_avg_7d"] = np.log1p(dv.rolling(7 * BARS_PER_DAY).mean())
    out["log_dollar_volume_avg_30d"] = np.log1p(dv.rolling(30 * BARS_PER_DAY).mean())
    abs_ret = ret.abs()
    out["amihud_illiquidity_30d"] = (abs_ret / dv.replace(0, np.nan)).rolling(30 * BARS_PER_DAY).mean()
    out["volume_ratio_7d_30d"] = volume.rolling(7 * BARS_PER_DAY).mean() / volume.rolling(30 * BARS_PER_DAY).mean()
    out["volume_spike"] = volume / volume.rolling(20 * BARS_PER_DAY).mean()
    out["liquidity_change_30d"] = dv.rolling(30 * BARS_PER_DAY).mean().pct_change(30 * BARS_PER_DAY)
    out["avg_dollar_volume_30d"] = dv.rolling(30 * BARS_PER_DAY).mean()

    # Reversal
    out["return_1d_reversal"] = -ret
    out["return_3d_reversal"] = -close.pct_change(3 * BARS_PER_DAY)
    delta = close.diff()
    gain = delta.where(delta > 0, 0).rolling(14 * BARS_PER_DAY).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(14 * BARS_PER_DAY).mean()
    rs = gain / loss.replace(0, np.nan)
    rsi = 100 - (100 / (1 + rs))
    out["overbought_score"] = (rsi - 70).clip(lower=0) / 30

    out["days_since_listing"] = np.arange(len(g)) // BARS_PER_DAY  # 일 단위 환산
    return out.shift(1)  # lookahead 차단


def build_features(ohlcv, macro):
    print("[features] per-coin 계산 (window in 4h bars)...")
    dfs = []
    for market, g in ohlcv.groupby("market", sort=False):
        feat = compute_per_coin(g)
        feat["market"] = market
        feat["close"] = g.set_index("ts_utc")["close"]
        dfs.append(feat)
    features = pd.concat(dfs).reset_index().rename(columns={"index": "ts_utc"})
    features = features.set_index("ts_utc").join(macro, how="left").reset_index()

    # cross-sectional rank
    rank_cols = ["return_7d", "return_14d", "return_30d", "realized_vol_30d",
                 "log_dollar_volume_avg_30d", "ma_5_distance", "ma_50_distance",
                 "ma_200_distance", "macd_histogram"]
    for col in rank_cols:
        features[f"{col}_rank_cs"] = features.groupby("ts_utc")[col].rank(pct=True)
    features["return_consistency_rank_cs"] = features.groupby("ts_utc")["return_30d"].rank(pct=True)

    features["universe_member"] = (
        features["close"].notna()
        & (features["avg_dollar_volume_30d"] >= LIQUIDITY_MIN)
    )

    for d in TARGETS:
        bars = TARGETS_BARS[d]
        features[f"forward_return_{d}d"] = features.groupby("market")["close"].pct_change(bars).shift(-bars)
        col = f"target_{d}d"
        features[col] = np.nan
        mask = features["universe_member"]
        features.loc[mask, col] = features.loc[mask].groupby("ts_utc")[f"forward_return_{d}d"].rank(pct=True)
    return features


def get_slippage(volume: float) -> float:
    if volume >= 50_000_000_000:
        return SLIPPAGE["major"]
    if volume >= 5_000_000_000:
        return SLIPPAGE["mid"]
    return SLIPPAGE["small"]


def sharpe(daily: pd.Series, periods_per_year: int = 365 * BARS_PER_DAY) -> float:
    if len(daily) < 2 or daily.std() == 0:
        return 0.0
    return float(daily.mean() / daily.std() * math.sqrt(periods_per_year))


def make_model(name: str, hp_idx: int):
    if name == "lgbm_ranker":
        sets = [dict(num_leaves=31, learning_rate=0.05, n_estimators=300),
                dict(num_leaves=63, learning_rate=0.03, n_estimators=500),
                dict(num_leaves=15, learning_rate=0.10, n_estimators=200),
                dict(num_leaves=127, learning_rate=0.05, n_estimators=300),
                dict(num_leaves=31, learning_rate=0.05, n_estimators=1000)]
        return lgb.LGBMRanker(objective="lambdarank", min_child_samples=50,
                               reg_alpha=0.1, reg_lambda=0.1, random_state=42, verbose=-1, **sets[hp_idx])
    if name == "lgbm_reg":
        sets = [dict(num_leaves=31, learning_rate=0.05, n_estimators=300),
                dict(num_leaves=63, learning_rate=0.03, n_estimators=500),
                dict(num_leaves=15, learning_rate=0.10, n_estimators=200),
                dict(num_leaves=127, learning_rate=0.05, n_estimators=300),
                dict(num_leaves=31, learning_rate=0.05, n_estimators=1000)]
        return lgb.LGBMRegressor(objective="regression", min_child_samples=50,
                                  reg_alpha=0.1, reg_lambda=0.1, random_state=42, verbose=-1, **sets[hp_idx])
    if name == "xgb_reg":
        sets = [dict(max_depth=5, learning_rate=0.05, n_estimators=300),
                dict(max_depth=6, learning_rate=0.03, n_estimators=500),
                dict(max_depth=4, learning_rate=0.10, n_estimators=200),
                dict(max_depth=7, learning_rate=0.05, n_estimators=300),
                dict(max_depth=5, learning_rate=0.05, n_estimators=1000)]
        return xgb.XGBRegressor(objective="reg:squarederror", reg_alpha=0.1, reg_lambda=0.1,
                                 random_state=42, verbosity=0, n_jobs=-1, **sets[hp_idx])
    if name == "rf":
        sets = [dict(n_estimators=100, max_depth=10), dict(n_estimators=200, max_depth=15),
                dict(n_estimators=100, max_depth=5), dict(n_estimators=300, max_depth=20),
                dict(n_estimators=200, max_depth=None)]
        return RandomForestRegressor(random_state=42, n_jobs=-1, **sets[hp_idx])
    if name == "ridge":
        sets = [dict(alpha=0.1), dict(alpha=1.0), dict(alpha=10.0), dict(alpha=100.0), dict(alpha=0.01)]
        return Ridge(random_state=42, **sets[hp_idx])
    raise ValueError(name)


MODELS = ["lgbm_ranker", "lgbm_reg", "xgb_reg", "rf", "ridge"]


def run_trial(df, feature_cols, target_p, model_name, hp_idx) -> dict:
    target_col = f"target_{target_p}d"
    fwd_col = f"forward_return_{target_p}d"
    train = df[(df["ts_utc"] >= TRAIN_START) & (df["ts_utc"] <= TRAIN_END)
               & df["universe_member"] & df[target_col].notna()].sort_values(["ts_utc", "market"])
    if len(train) < 100:
        return {"error": f"train_too_small_{len(train)}"}

    X_train = train[feature_cols].fillna(0.0).values
    y_train = train[target_col].values
    if model_name == "lgbm_ranker":
        model = make_model(model_name, hp_idx)
        groups = train.groupby("ts_utc").size().to_list()
        y_train = (y_train * 30).astype(int)
        model.fit(X_train, y_train, group=groups)
    else:
        model = make_model(model_name, hp_idx)
        model.fit(X_train, y_train)

    oos = df[(df["ts_utc"] >= OOS_START) & (df["ts_utc"] <= OOS_END) & df["universe_member"]].copy()
    X_oos = oos[feature_cols].fillna(0.0).values
    oos["score"] = model.predict(X_oos)

    top_rows, bot_rows = [], []
    trade_count = 0
    for ts, g in oos.groupby("ts_utc"):
        n_sel = max(1, int(round(len(g) * TOP_DECILE)))
        top = g.nlargest(n_sel, "score")
        bot = g.nsmallest(n_sel, "score")
        top_r = top[fwd_col].dropna()
        bot_r = bot[fwd_col].dropna()
        if top_r.empty or bot_r.empty:
            continue
        top_cost = top.apply(lambda r: 2 * FEE_RATE + 2 * get_slippage(r.get("avg_dollar_volume_30d", 0) or 0), axis=1).reindex(top_r.index)
        bot_cost = bot.apply(lambda r: 2 * FEE_RATE + 2 * get_slippage(r.get("avg_dollar_volume_30d", 0) or 0), axis=1).reindex(bot_r.index)
        top_rows.append((top_r - top_cost).mean() / target_p)
        bot_rows.append((bot_r - bot_cost).mean() / target_p)
        trade_count += n_sel

    if not top_rows:
        return {"error": "no_trades"}

    s_t = pd.Series(top_rows)
    s_b = pd.Series(bot_rows)
    s_ls = s_t - s_b
    return {
        "model": model_name, "hp_idx": hp_idx, "target_period": target_p,
        "sharpe_top": sharpe(s_t), "sharpe_bottom": sharpe(s_b),
        "sharpe_long_short": sharpe(s_ls),
        "cum_return_top": float(((1 + s_t).prod() - 1) * 100),
        "trade_count": trade_count, "T_obs": len(s_t),
    }


def main() -> int:
    print("[ML-v3 Grid] 분봉 4시간봉 50 코인 × 125 trials")
    print("[step 1] 데이터 로드 + macro...")
    ohlcv, btc, fx = load_data()
    print(f"  ohlcv: {len(ohlcv):,} rows, {ohlcv['market'].nunique()} markets")
    macro = compute_macro(ohlcv, btc, fx)

    print("[step 2] features + targets 계산...")
    df = build_features(ohlcv, macro)
    feature_cols = [c for c in df.columns if c not in (
        "ts_utc", "market", "close", "volume", "avg_dollar_volume_30d", "universe_member",
        *[f"forward_return_{p}d" for p in TARGETS],
        *[f"target_{p}d" for p in TARGETS],
    )]
    print(f"  rows: {len(df):,}, features: {len(feature_cols)}")

    universe_count = df[df["universe_member"]].groupby("ts_utc").size()
    print(f"  universe: mean={universe_count.mean():.0f}, min={universe_count.min()}, max={universe_count.max()}")

    print("\n[step 3] 125 trial grid...")
    trials = []
    total = len(MODELS) * 5 * len(TARGETS)
    idx = 0
    for m in MODELS:
        for hp in range(5):
            for t in TARGETS:
                idx += 1
                try:
                    r = run_trial(df, feature_cols, t, m, hp)
                    trials.append(r)
                    print(f"  [{idx}/{total}] {m:<12} hp={hp} t={t:>2}d "
                          f"top={r.get('sharpe_top', 0):>+6.2f} L-S={r.get('sharpe_long_short', 0):>+6.2f} "
                          f"trades={r.get('trade_count', 0):>5}")
                except Exception as e:
                    print(f"  [{idx}/{total}] {m} hp={hp} t={t} FAIL {str(e)[:60]}")
                    trials.append({"model": m, "hp_idx": hp, "target_period": t, "error": str(e)[:200]})

    valid = [t for t in trials if "error" not in t]
    if valid:
        df_t = pd.DataFrame(valid)
        print("\n[종합]")
        print(f"  Top decile Sharpe:     mean={df_t['sharpe_top'].mean():.3f}, positive={(df_t['sharpe_top']>0).sum()}/{len(df_t)}, Go(>1)={(df_t['sharpe_top']>1).sum()}")
        print(f"  Bottom decile Sharpe:  mean={df_t['sharpe_bottom'].mean():.3f}, positive={(df_t['sharpe_bottom']>0).sum()}/{len(df_t)}")
        print(f"  Long-Short Sharpe:     mean={df_t['sharpe_long_short'].mean():.3f}, positive={(df_t['sharpe_long_short']>0).sum()}/{len(df_t)}, Go(>0.5)={(df_t['sharpe_long_short']>0.5).sum()}")
        n_trials = len(valid)
        v_emp = float(df_t["sharpe_long_short"].var())
        sr_0 = math.sqrt(v_emp) * ((1 - EULER) * scs.norm.ppf(1 - 1.0 / n_trials)
                                    + EULER * scs.norm.ppf(1 - 1.0 / (n_trials * math.e)))
        print(f"  DSR: N={n_trials}, V={v_emp:.3f}, SR_0={sr_0:.3f}")
        best_idx = df_t["sharpe_long_short"].idxmax()
        best = df_t.loc[best_idx]
        print(f"  best L-S: {best['sharpe_long_short']:.3f} ({best['model']}, hp={best['hp_idx']}, t={best['target_period']}d)")
        print(f"  best > SR_0: {best['sharpe_long_short'] > sr_0}")

    out = {"trials": trials, "n_trials": len(trials), "n_valid": len(valid),
           "timeframe": "4h", "universe_size": int(ohlcv["market"].nunique())}
    out_path = RESULTS_DIR / "v2_strategy_ml_v3_grid.json"
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=2, default=str)
    print(f"\nsaved: {out_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
