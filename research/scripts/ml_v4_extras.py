"""V2-Strategy-ML v4 추가 분석 (Auto mode 다 해 사용자 명시):

1. Ensemble: 5 모델 평균 score
2. Regime classifier: BTC 30d return 기반 강세/약세 → 강세만 매수
3. CPCV walk-forward (manual purged k-fold)
4. Universe 확대 (top 100)

박제 출처: ml_v2 grid 결과 (Long-Short Sharpe +7.43 mean, Best +26.74 Ridge t=30d)
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

DATA_DIR = Path(__file__).parent.parent / "data" / "ml_v2"
RESULTS_DIR = Path(__file__).parent.parent / "notebooks" / "results"

TRAIN_START = pd.Timestamp("2024-01-01", tz="UTC")
TRAIN_END = pd.Timestamp("2025-08-31", tz="UTC")
OOS_START = pd.Timestamp("2025-09-01", tz="UTC")
OOS_END = pd.Timestamp("2026-04-25", tz="UTC")

TARGET_PERIOD = 30  # ml_v2 best
TOP_DECILE = 0.10
FEE_RATE = 0.0005
SLIPPAGE = {"major": 0.0005, "mid": 0.0010, "small": 0.0030}


def get_slippage(v):
    if v >= 50_000_000_000:
        return SLIPPAGE["major"]
    if v >= 5_000_000_000:
        return SLIPPAGE["mid"]
    return SLIPPAGE["small"]


def sharpe(daily):
    if len(daily) < 2 or daily.std() == 0:
        return 0.0
    return float(daily.mean() / daily.std() * math.sqrt(365))


def load_data(universe_size: int | None = None):
    df = pd.read_parquet(DATA_DIR / "features.parquet")
    df["ts_utc"] = pd.to_datetime(df["ts_utc"], utc=True)
    df = df.sort_values(["market", "ts_utc"]).copy()
    df["forward_return_30d"] = df.groupby("market")["close"].pct_change(TARGET_PERIOD).shift(-TARGET_PERIOD)
    df["target_30d"] = np.nan
    mask = df["universe_member"]
    df.loc[mask, "target_30d"] = df.loc[mask].groupby("ts_utc")["forward_return_30d"].rank(pct=True)

    # universe 확대 (top N by avg_dollar_volume_30d)
    if universe_size is not None:
        # 매 ts_utc 시점에 top N 코인만 universe_member True
        df["volume_rank"] = df.groupby("ts_utc")["avg_dollar_volume_30d"].rank(ascending=False)
        df["universe_member"] = df["universe_member"] & (df["volume_rank"] <= universe_size)
        # target 재계산 (universe 변경 반영)
        df["target_30d"] = np.nan
        mask = df["universe_member"]
        df.loc[mask, "target_30d"] = df.loc[mask].groupby("ts_utc")["forward_return_30d"].rank(pct=True)
    return df


def make_models(hp_idx: int = 4):
    """Best hp set per model (ml_v2 default)."""
    return {
        "ridge": Ridge(alpha=0.01, random_state=42),
        "lgbm_reg": lgb.LGBMRegressor(num_leaves=31, learning_rate=0.05, n_estimators=300,
                                        min_child_samples=50, reg_alpha=0.1, reg_lambda=0.1,
                                        random_state=42, verbose=-1),
        "xgb_reg": xgb.XGBRegressor(max_depth=5, learning_rate=0.05, n_estimators=300,
                                      reg_alpha=0.1, reg_lambda=0.1, random_state=42,
                                      verbosity=0, n_jobs=-1),
        "rf": RandomForestRegressor(n_estimators=200, max_depth=15, random_state=42, n_jobs=-1),
    }


def get_features(df):
    return [c for c in df.columns if c not in (
        "ts_utc", "market", "close", "volume", "avg_dollar_volume_30d",
        "universe_member", "forward_return_30d", "target_30d", "volume_rank",
    )]


def backtest_scores(df_oos, top_decile: float = TOP_DECILE):
    """매 ts_utc 마다 score top/bottom decile → backtest."""
    top_rows, bot_rows = [], []
    trade_count = 0
    for ts, g in df_oos.groupby("ts_utc"):
        n_sel = max(1, int(round(len(g) * top_decile)))
        top = g.nlargest(n_sel, "score")
        bot = g.nsmallest(n_sel, "score")
        top_r = top["forward_return_30d"].dropna()
        bot_r = bot["forward_return_30d"].dropna()
        if top_r.empty or bot_r.empty:
            continue
        top_cost = top.apply(lambda r: 2 * FEE_RATE + 2 * get_slippage(r.get("avg_dollar_volume_30d", 0) or 0), axis=1).reindex(top_r.index)
        bot_cost = bot.apply(lambda r: 2 * FEE_RATE + 2 * get_slippage(r.get("avg_dollar_volume_30d", 0) or 0), axis=1).reindex(bot_r.index)
        top_rows.append((top_r - top_cost).mean() / TARGET_PERIOD)
        bot_rows.append((bot_r - bot_cost).mean() / TARGET_PERIOD)
        trade_count += n_sel
    return pd.Series(top_rows), pd.Series(bot_rows), trade_count


# ======================
# 1. Ensemble (5 모델 평균)
# ======================

def run_ensemble(df, feature_cols):
    print("\n[1] Ensemble (4 모델 평균 score)")
    models = make_models()
    train = df[(df["ts_utc"] >= TRAIN_START) & (df["ts_utc"] <= TRAIN_END)
               & df["universe_member"] & df["target_30d"].notna()].sort_values(["ts_utc", "market"])
    X_train = train[feature_cols].fillna(0.0).values
    y_train = train["target_30d"].values

    for name, m in models.items():
        m.fit(X_train, y_train)

    oos = df[(df["ts_utc"] >= OOS_START) & (df["ts_utc"] <= OOS_END) & df["universe_member"]].copy()
    X_oos = oos[feature_cols].fillna(0.0).values
    scores = np.zeros(len(oos))
    for name, m in models.items():
        s = m.predict(X_oos)
        # rank percentile per ts_utc로 normalize (cross-sectional 평균)
        oos_tmp = oos.copy()
        oos_tmp["_s"] = s
        scores += oos_tmp.groupby("ts_utc")["_s"].rank(pct=True).values
    oos["score"] = scores / len(models)

    s_t, s_b, tc = backtest_scores(oos)
    print(f"  Top Sharpe: {sharpe(s_t):>+.3f}, Bot Sharpe: {sharpe(s_b):>+.3f}, L-S Sharpe: {sharpe(s_t - s_b):>+.3f}")
    print(f"  trades: {tc}")
    return {
        "method": "ensemble_4models",
        "sharpe_top": sharpe(s_t), "sharpe_bottom": sharpe(s_b),
        "sharpe_long_short": sharpe(s_t - s_b), "trade_count": tc,
    }


# ======================
# 2. Regime classifier
# ======================

def run_regime(df, feature_cols):
    print("\n[2] Regime classifier (BTC 30d return > 0 시기만 매수)")
    btc = df[df["market"] == "KRW-BTC"][["ts_utc", "close"]].set_index("ts_utc")
    btc["btc_return_30d"] = btc["close"].pct_change(30).shift(1)  # lookahead 차단
    btc["regime_bull"] = (btc["btc_return_30d"] > 0).astype(int)

    # Ridge model 학습 (best ml_v2)
    train = df[(df["ts_utc"] >= TRAIN_START) & (df["ts_utc"] <= TRAIN_END)
               & df["universe_member"] & df["target_30d"].notna()].sort_values(["ts_utc", "market"])
    X_train = train[feature_cols].fillna(0.0).values
    y_train = train["target_30d"].values
    model = Ridge(alpha=0.01, random_state=42)
    model.fit(X_train, y_train)

    oos = df[(df["ts_utc"] >= OOS_START) & (df["ts_utc"] <= OOS_END) & df["universe_member"]].copy()
    X_oos = oos[feature_cols].fillna(0.0).values
    oos["score"] = model.predict(X_oos)

    # regime filter
    oos = oos.merge(btc[["regime_bull"]].reset_index(), on="ts_utc", how="left")
    oos_bull = oos[oos["regime_bull"] == 1].copy()
    oos_bear = oos[oos["regime_bull"] == 0].copy()

    # bull 시기만 — top decile 매수 (mean reversion 가설: bull 시기엔 trend 우위)
    s_t_bull, s_b_bull, tc_bull = backtest_scores(oos_bull) if len(oos_bull) > 0 else (pd.Series(dtype=float), pd.Series(dtype=float), 0)
    s_t_bear, s_b_bear, tc_bear = backtest_scores(oos_bear) if len(oos_bear) > 0 else (pd.Series(dtype=float), pd.Series(dtype=float), 0)
    print(f"  Bull regime ({len(oos_bull):,} rows): Top Sharpe {sharpe(s_t_bull):>+.3f}, L-S Sharpe {sharpe(s_t_bull - s_b_bull):>+.3f}")
    print(f"  Bear regime ({len(oos_bear):,} rows): Top Sharpe {sharpe(s_t_bear):>+.3f}, L-S Sharpe {sharpe(s_t_bear - s_b_bear):>+.3f}")

    return {
        "method": "regime_classifier",
        "bull": {"top_sharpe": sharpe(s_t_bull), "ls_sharpe": sharpe(s_t_bull - s_b_bull) if len(s_t_bull) > 0 else 0, "trades": tc_bull},
        "bear": {"top_sharpe": sharpe(s_t_bear), "ls_sharpe": sharpe(s_t_bear - s_b_bear) if len(s_t_bear) > 0 else 0, "trades": tc_bear},
    }


# ======================
# 3. CPCV walk-forward (manual purged k-fold)
# ======================

def run_cpcv(df, feature_cols, n_splits: int = 4, embargo_days: int = 7):
    print(f"\n[3] CPCV walk-forward (n_splits={n_splits}, embargo={embargo_days}d)")
    full = df[df["universe_member"] & df["target_30d"].notna()
              & (df["ts_utc"] >= TRAIN_START)].sort_values("ts_utc")
    ts_unique = full["ts_utc"].drop_duplicates().sort_values().to_list()
    n = len(ts_unique)
    fold_size = n // n_splits

    fold_results = []
    for fold_i in range(n_splits):
        test_start = fold_i * fold_size
        test_end = (fold_i + 1) * fold_size if fold_i < n_splits - 1 else n
        test_ts = ts_unique[test_start:test_end]
        # purge embargo
        test_first = test_ts[0]
        test_last = test_ts[-1]
        train_ts = [t for t in ts_unique if t < test_first - pd.Timedelta(days=embargo_days)
                    or t > test_last + pd.Timedelta(days=embargo_days)]

        train = full[full["ts_utc"].isin(train_ts)]
        test = full[full["ts_utc"].isin(test_ts)]
        if len(train) < 100 or len(test) < 100:
            continue

        model = Ridge(alpha=0.01, random_state=42)
        X_train = train[feature_cols].fillna(0.0).values
        model.fit(X_train, train["target_30d"].values)
        X_test = test[feature_cols].fillna(0.0).values
        test = test.copy()
        test["score"] = model.predict(X_test)

        s_t, s_b, tc = backtest_scores(test)
        fold_result = {
            "fold": fold_i + 1, "train_n": len(train), "test_n": len(test),
            "test_period": f"{test_first.date()} ~ {test_last.date()}",
            "sharpe_top": sharpe(s_t), "sharpe_bottom": sharpe(s_b),
            "sharpe_long_short": sharpe(s_t - s_b), "trades": tc,
        }
        fold_results.append(fold_result)
        print(f"  fold {fold_i+1}: {test_first.date()}~{test_last.date()} "
              f"Top {sharpe(s_t):>+.3f} / L-S {sharpe(s_t - s_b):>+.3f} / trades {tc}")

    if fold_results:
        ls_sharpes = [f["sharpe_long_short"] for f in fold_results]
        print(f"  CPCV L-S Sharpe: mean={np.mean(ls_sharpes):.3f}, std={np.std(ls_sharpes):.3f}")
        print(f"  positive folds: {sum(1 for s in ls_sharpes if s > 0)}/{len(ls_sharpes)}")
    return {"method": "cpcv_4fold", "folds": fold_results}


# ======================
# 4. Universe top 100
# ======================

def run_universe100(feature_cols_template):
    print("\n[4] Universe 확대 top 100 (vs 기존 universe_member ~129 mean)")
    df = load_data(universe_size=100)
    feature_cols = [c for c in feature_cols_template if c in df.columns]

    train = df[(df["ts_utc"] >= TRAIN_START) & (df["ts_utc"] <= TRAIN_END)
               & df["universe_member"] & df["target_30d"].notna()].sort_values(["ts_utc", "market"])
    X_train = train[feature_cols].fillna(0.0).values
    model = Ridge(alpha=0.01, random_state=42)
    model.fit(X_train, train["target_30d"].values)

    oos = df[(df["ts_utc"] >= OOS_START) & (df["ts_utc"] <= OOS_END) & df["universe_member"]].copy()
    X_oos = oos[feature_cols].fillna(0.0).values
    oos["score"] = model.predict(X_oos)

    s_t, s_b, tc = backtest_scores(oos)
    print(f"  Top Sharpe: {sharpe(s_t):>+.3f}, L-S Sharpe: {sharpe(s_t - s_b):>+.3f}, trades: {tc}")
    return {
        "method": "universe_top100", "n_train": len(train), "n_oos": len(oos),
        "sharpe_top": sharpe(s_t), "sharpe_bottom": sharpe(s_b),
        "sharpe_long_short": sharpe(s_t - s_b), "trade_count": tc,
    }


def main() -> int:
    print("[ML-v4 extras] Ensemble + Regime + CPCV + Universe 확대")
    df = load_data()
    feature_cols = get_features(df)
    print(f"  features: {len(feature_cols)}, total rows: {len(df):,}")

    results = {}
    results["ensemble"] = run_ensemble(df, feature_cols)
    results["regime"] = run_regime(df, feature_cols)
    results["cpcv"] = run_cpcv(df, feature_cols)
    results["universe100"] = run_universe100(feature_cols)

    out_path = RESULTS_DIR / "v2_strategy_ml_v4_extras.json"
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2, default=str)
    print(f"\nsaved: {out_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
