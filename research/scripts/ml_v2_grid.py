"""V2-Strategy-ML v2 확장 그리드: 5 hyperparam × 5 targets × 5 models = 125 trials.

박제 출처: 사용자 명시 "다 해" (2026-04-27 Auto mode)
cycle 1 #5 회피: 사전 박제 grid 125 + DSR N_trials=125 보정 + 결과 그대로 박제

설계:
- Target: forward 1d/3d/7d/14d/30d cross-sectional percentile rank
- Model: LGBMRanker / LGBMRegressor / XGBRegressor / RandomForestRegressor / Ridge
- Hyperparam: 5 set per model (default + 4 variations, simple)
- Train/OOS: 동일 (2024-01~2025-08 / 2025-09~2026-04-25)
- Backtest: top 10% 동일가중 + 거래비용 박제

출력: research/notebooks/results/v2_strategy_ml_v2_grid.json
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

TOP_DECILE = 0.10
HOLDING_DAYS = 7
FEE_RATE = 0.0005
SLIPPAGE = {"major": 0.0005, "mid": 0.0010, "small": 0.0030}

GO_SHARPE = 1.0
GO_DSR_Z = 0.0

# DSR 상수
EULER = 0.5772156649015329


def get_slippage(volume: float) -> float:
    if volume >= 50_000_000_000:
        return SLIPPAGE["major"]
    if volume >= 5_000_000_000:
        return SLIPPAGE["mid"]
    return SLIPPAGE["small"]


def sharpe(daily: pd.Series) -> float:
    if len(daily) < 2 or daily.std() == 0:
        return 0.0
    return float(daily.mean() / daily.std() * math.sqrt(365))


def compute_targets(df: pd.DataFrame, periods: list[int]) -> pd.DataFrame:
    """다중 forward period target 추가."""
    df = df.sort_values(["market", "ts_utc"]).copy()
    for p in periods:
        df[f"forward_return_{p}d"] = df.groupby("market")["close"].pct_change(p).shift(-p)
        col = f"target_{p}d"
        df[col] = np.nan
        mask = df["universe_member"]
        df.loc[mask, col] = df.loc[mask].groupby("ts_utc")[f"forward_return_{p}d"].rank(pct=True)
    return df


# ---- Models ----

def model_lgbm_ranker(hp_idx: int) -> lgb.LGBMRanker:
    sets = [
        dict(num_leaves=31, learning_rate=0.05, n_estimators=300),
        dict(num_leaves=63, learning_rate=0.03, n_estimators=500),
        dict(num_leaves=15, learning_rate=0.10, n_estimators=200),
        dict(num_leaves=127, learning_rate=0.05, n_estimators=300),
        dict(num_leaves=31, learning_rate=0.05, n_estimators=1000),
    ]
    return lgb.LGBMRanker(objective="lambdarank", boosting_type="gbdt",
                          min_child_samples=50, reg_alpha=0.1, reg_lambda=0.1,
                          random_state=42, verbose=-1, **sets[hp_idx])


def model_lgbm_regressor(hp_idx: int) -> lgb.LGBMRegressor:
    sets = [
        dict(num_leaves=31, learning_rate=0.05, n_estimators=300),
        dict(num_leaves=63, learning_rate=0.03, n_estimators=500),
        dict(num_leaves=15, learning_rate=0.10, n_estimators=200),
        dict(num_leaves=127, learning_rate=0.05, n_estimators=300),
        dict(num_leaves=31, learning_rate=0.05, n_estimators=1000),
    ]
    return lgb.LGBMRegressor(objective="regression", boosting_type="gbdt",
                             min_child_samples=50, reg_alpha=0.1, reg_lambda=0.1,
                             random_state=42, verbose=-1, **sets[hp_idx])


def model_xgb_regressor(hp_idx: int) -> xgb.XGBRegressor:
    sets = [
        dict(max_depth=5, learning_rate=0.05, n_estimators=300),
        dict(max_depth=6, learning_rate=0.03, n_estimators=500),
        dict(max_depth=4, learning_rate=0.10, n_estimators=200),
        dict(max_depth=7, learning_rate=0.05, n_estimators=300),
        dict(max_depth=5, learning_rate=0.05, n_estimators=1000),
    ]
    return xgb.XGBRegressor(objective="reg:squarederror",
                             reg_alpha=0.1, reg_lambda=0.1,
                             random_state=42, verbosity=0, n_jobs=-1, **sets[hp_idx])


def model_rf(hp_idx: int) -> RandomForestRegressor:
    sets = [
        dict(n_estimators=100, max_depth=10),
        dict(n_estimators=200, max_depth=15),
        dict(n_estimators=100, max_depth=5),
        dict(n_estimators=300, max_depth=20),
        dict(n_estimators=200, max_depth=None),
    ]
    return RandomForestRegressor(random_state=42, n_jobs=-1, **sets[hp_idx])


def model_ridge(hp_idx: int) -> Ridge:
    sets = [
        dict(alpha=0.1),
        dict(alpha=1.0),
        dict(alpha=10.0),
        dict(alpha=100.0),
        dict(alpha=0.01),
    ]
    return Ridge(random_state=42, **sets[hp_idx])


MODELS = {
    "lgbm_ranker": model_lgbm_ranker,
    "lgbm_reg": model_lgbm_regressor,
    "xgb_reg": model_xgb_regressor,
    "rf": model_rf,
    "ridge": model_ridge,
}


def run_trial(df: pd.DataFrame, feature_cols: list[str],
              target_period: int, model_name: str, hp_idx: int) -> dict:
    target_col = f"target_{target_period}d"
    fwd_col = f"forward_return_{target_period}d"

    train = df[
        (df["ts_utc"] >= TRAIN_START) & (df["ts_utc"] <= TRAIN_END)
        & df["universe_member"] & df[target_col].notna()
    ].sort_values(["ts_utc", "market"])

    X_train = train[feature_cols].fillna(0.0).values
    y_train = train[target_col].values

    if model_name == "lgbm_ranker":
        model = model_lgbm_ranker(hp_idx)
        group_sizes = train.groupby("ts_utc").size().to_list()
        y_train = (y_train * 30).astype(int)
        model.fit(X_train, y_train, group=group_sizes)
    else:
        model = MODELS[model_name](hp_idx)
        model.fit(X_train, y_train)

    oos = df[
        (df["ts_utc"] >= OOS_START) & (df["ts_utc"] <= OOS_END)
        & df["universe_member"]
    ].copy()
    X_oos = oos[feature_cols].fillna(0.0).values
    oos["score"] = model.predict(X_oos)

    # Top decile backtest
    top_rows = []
    bot_rows = []
    trade_count = 0
    for ts, g in oos.groupby("ts_utc"):
        n_sel = max(1, int(round(len(g) * TOP_DECILE)))
        top = g.nlargest(n_sel, "score")
        bot = g.nsmallest(n_sel, "score")
        top_rets = top[fwd_col].dropna()
        bot_rets = bot[fwd_col].dropna()
        if top_rets.empty or bot_rets.empty:
            continue
        top_cost = top.apply(
            lambda r: 2 * FEE_RATE + 2 * get_slippage(r.get("avg_dollar_volume_30d", 0) or 0), axis=1,
        ).reindex(top_rets.index)
        bot_cost = bot.apply(
            lambda r: 2 * FEE_RATE + 2 * get_slippage(r.get("avg_dollar_volume_30d", 0) or 0), axis=1,
        ).reindex(bot_rets.index)
        top_rows.append((top_rets - top_cost).mean() / target_period)
        bot_rows.append((bot_rets - bot_cost).mean() / target_period)
        trade_count += n_sel

    if not top_rows:
        return {"error": "no_trades"}

    s_top = pd.Series(top_rows)
    s_bot = pd.Series(bot_rows)
    s_ls = s_top - s_bot
    return {
        "model": model_name, "hp_idx": hp_idx, "target_period": target_period,
        "sharpe_top": sharpe(s_top),
        "sharpe_bottom": sharpe(s_bot),
        "sharpe_long_short": sharpe(s_ls),
        "cum_return_top": float(((1 + s_top).prod() - 1) * 100),
        "trade_count": trade_count,
        "T_obs": len(s_top),
    }


def main() -> int:
    print("[ML-v2 Grid] 5 models × 5 hyperparams × 5 targets = 125 trials")
    df = pd.read_parquet(DATA_DIR / "features.parquet")
    df["ts_utc"] = pd.to_datetime(df["ts_utc"], utc=True)
    targets = [1, 3, 7, 14, 30]
    df = compute_targets(df, targets)

    feature_cols = [c for c in df.columns if c not in (
        "ts_utc", "market", "close", "volume", "avg_dollar_volume_30d",
        "universe_member",
        *[f"forward_return_{p}d" for p in targets],
        *[f"target_{p}d" for p in targets],
    )]
    print(f"  features: {len(feature_cols)}")
    print(f"  targets: {targets}")
    print(f"  models: {list(MODELS.keys())}")

    trials = []
    trial_idx = 0
    total = len(MODELS) * 5 * len(targets)
    for model_name in MODELS:
        for hp_idx in range(5):
            for target_p in targets:
                trial_idx += 1
                try:
                    r = run_trial(df, feature_cols, target_p, model_name, hp_idx)
                    trials.append(r)
                    print(f"  [{trial_idx}/{total}] {model_name:<12} hp={hp_idx} t={target_p:>2}d "
                          f"Sharpe(top)={r.get('sharpe_top', 0):>+6.2f} "
                          f"L-S={r.get('sharpe_long_short', 0):>+6.2f}")
                except Exception as e:
                    print(f"  [{trial_idx}/{total}] {model_name} hp={hp_idx} t={target_p}d FAIL: {str(e)[:80]}")
                    trials.append({"model": model_name, "hp_idx": hp_idx, "target_period": target_p,
                                    "error": str(e)[:200]})

    # 종합
    valid = [t for t in trials if "error" not in t]
    if valid:
        df_t = pd.DataFrame(valid)
        print("\n[종합] Sharpe top decile 분포:")
        print(f"  mean={df_t['sharpe_top'].mean():.3f}, std={df_t['sharpe_top'].std():.3f}")
        print(f"  min={df_t['sharpe_top'].min():.3f}, max={df_t['sharpe_top'].max():.3f}")
        print(f"  positive (>0): {(df_t['sharpe_top'] > 0).sum()} / {len(df_t)}")
        print(f"  Go (Sharpe>1.0): {(df_t['sharpe_top'] > 1.0).sum()} / {len(df_t)}")
        print(f"\n[종합] Long-Short Sharpe 분포:")
        print(f"  mean={df_t['sharpe_long_short'].mean():.3f}, std={df_t['sharpe_long_short'].std():.3f}")
        print(f"  positive (>0): {(df_t['sharpe_long_short'] > 0).sum()} / {len(df_t)}")
        print(f"  Go (L-S Sharpe>0.5): {(df_t['sharpe_long_short'] > 0.5).sum()} / {len(df_t)}")

        # DSR 보정 (N_trials=125)
        n_trials = len(valid)
        v_emp = float(df_t["sharpe_long_short"].var())
        sr_0 = math.sqrt(v_emp) * (
            (1 - EULER) * scs.norm.ppf(1 - 1.0 / n_trials)
            + EULER * scs.norm.ppf(1 - 1.0 / (n_trials * math.e))
        )
        print(f"\n[DSR] N_trials={n_trials}, V_empirical={v_emp:.4f}, SR_0={sr_0:.3f}")
        best_idx = df_t["sharpe_long_short"].idxmax()
        best = df_t.loc[best_idx]
        print(f"  best L-S Sharpe: {best['sharpe_long_short']:.3f} ({best['model']}, hp={best['hp_idx']}, t={best['target_period']}d)")
        print(f"  best > SR_0? {best['sharpe_long_short'] > sr_0}")

    out = {
        "trials": trials,
        "n_trials": len(trials),
        "n_valid": len(valid),
    }
    out_path = RESULTS_DIR / "v2_strategy_ml_v2_grid.json"
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=2, default=str)
    print(f"\nsaved: {out_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
