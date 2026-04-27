"""V2-Strategy-ML ML-06: 추가 학습 분석.

박제 출처: 사용자 명시 "B" (2026-04-27) — Strategy ML No-Go 후 학습 깊이 분석.

분석 목록:
- (1) Sub-period Sharpe (월별 OOS Sharpe → regime change 가설 검증)
- (2) Top vs Bottom decile long-short (market-neutral alpha 측정)
- (3) Gross vs Net 비교 (거래비용 영향)
- (4) Bottom decile만 매수 시 (모델이 거꾸로 예측?)
- (5) SHAP feature contribution (top 10 features)
- (6) Universe size에 따른 성능 분리
"""
from __future__ import annotations

import json
import math
import sys
from pathlib import Path

import lightgbm as lgb
import numpy as np
import pandas as pd
import scipy.stats as scs
import shap

DATA_DIR = Path(__file__).parent.parent / "data" / "ml_v2"
RESULTS_DIR = Path(__file__).parent.parent / "notebooks" / "results"

TRAIN_START = pd.Timestamp("2024-01-01", tz="UTC")
TRAIN_END = pd.Timestamp("2025-08-31", tz="UTC")
OOS_START = pd.Timestamp("2025-09-01", tz="UTC")
OOS_END = pd.Timestamp("2026-04-25", tz="UTC")

FORWARD_DAYS = 7
TOP_DECILE = 0.10
HOLDING_DAYS = 7
FEE_RATE = 0.0005
SLIPPAGE_MAJOR = 0.0005
SLIPPAGE_MID = 0.0010
SLIPPAGE_SMALL = 0.0030


def get_slippage(avg_dollar_volume_30d: float) -> float:
    if avg_dollar_volume_30d >= 50_000_000_000:
        return SLIPPAGE_MAJOR
    if avg_dollar_volume_30d >= 5_000_000_000:
        return SLIPPAGE_MID
    return SLIPPAGE_SMALL


def load_and_train():
    df = pd.read_parquet(DATA_DIR / "features.parquet")
    df["ts_utc"] = pd.to_datetime(df["ts_utc"], utc=True)
    df = df.sort_values(["market", "ts_utc"]).copy()
    df["forward_return_7d"] = df.groupby("market")["close"].pct_change(FORWARD_DAYS).shift(-FORWARD_DAYS)
    df["target_rank"] = np.nan
    mask = df["universe_member"]
    df.loc[mask, "target_rank"] = df.loc[mask].groupby("ts_utc")["forward_return_7d"].rank(pct=True)

    feature_cols = [c for c in df.columns if c not in (
        "ts_utc", "market", "close", "volume", "avg_dollar_volume_30d",
        "universe_member", "forward_return_7d", "target_rank",
    )]

    train = df[
        (df["ts_utc"] >= TRAIN_START) & (df["ts_utc"] <= TRAIN_END)
        & df["universe_member"] & df["target_rank"].notna()
    ].sort_values(["ts_utc", "market"])
    group_sizes = train.groupby("ts_utc").size().to_list()
    X_train = train[feature_cols].fillna(0.0).values
    y_train = (train["target_rank"].values * 30).astype(int)

    model = lgb.LGBMRanker(
        objective="lambdarank", boosting_type="gbdt",
        num_leaves=31, learning_rate=0.05, n_estimators=300,
        min_child_samples=50, reg_alpha=0.1, reg_lambda=0.1,
        random_state=42, verbose=-1,
    )
    model.fit(X_train, y_train, group=group_sizes)
    return df, feature_cols, model


def compute_returns(group: pd.DataFrame, n_select: int, top: bool = True) -> pd.Series:
    """top/bottom decile 선택 후 forward return."""
    if top:
        selected = group.nlargest(n_select, "score")
    else:
        selected = group.nsmallest(n_select, "score")
    rets = selected["forward_return_7d"].dropna()
    if rets.empty:
        return pd.Series(dtype=float)
    cost = selected.apply(
        lambda r: 2 * FEE_RATE + 2 * get_slippage(r.get("avg_dollar_volume_30d", 0) or 0),
        axis=1,
    )
    return rets - cost.reindex(rets.index)


def sharpe(daily: pd.Series) -> float:
    if len(daily) < 2 or daily.std() == 0:
        return 0.0
    return float(daily.mean() / daily.std() * math.sqrt(365))


def main() -> int:
    print("[ML-06] 추가 학습 분석")
    print("[step 1] 학습 + OOS prediction...")
    df, feature_cols, model = load_and_train()

    oos = df[
        (df["ts_utc"] >= OOS_START) & (df["ts_utc"] <= OOS_END)
        & df["universe_member"]
    ].copy()
    X_oos = oos[feature_cols].fillna(0.0).values
    oos["score"] = model.predict(X_oos)
    print(f"  oos rows: {len(oos):,}")

    # ---- (1) Sub-period (월별) Sharpe ----
    print("\n[1] 월별 Sub-period Sharpe (top decile)...")
    monthly = []
    oos["month"] = oos["ts_utc"].dt.to_period("M")
    for month, group in oos.groupby("month"):
        rows = []
        for ts, day_group in group.groupby("ts_utc"):
            n_sel = max(1, int(round(len(day_group) * TOP_DECILE)))
            rets = compute_returns(day_group, n_sel, top=True)
            if not rets.empty:
                rows.append(rets.mean() / HOLDING_DAYS)
        if rows:
            s = pd.Series(rows)
            sh = sharpe(s)
            monthly.append({"month": str(month), "n_obs": len(rows),
                             "mean_daily": float(s.mean()), "sharpe_annual": sh,
                             "cum_return_pct": float(((1 + s).prod() - 1) * 100)})
    monthly_df = pd.DataFrame(monthly)
    print(monthly_df.to_string(index=False))

    # ---- (2) Top vs Bottom decile (long-short) ----
    print("\n[2] Top vs Bottom decile long-short (market-neutral)...")
    top_rows, bot_rows, ls_rows = [], [], []
    for ts, day_group in oos.groupby("ts_utc"):
        n_sel = max(1, int(round(len(day_group) * TOP_DECILE)))
        top_ret = compute_returns(day_group, n_sel, top=True).mean()
        bot_ret = compute_returns(day_group, n_sel, top=False).mean()
        if not (np.isnan(top_ret) or np.isnan(bot_ret)):
            top_rows.append(top_ret / HOLDING_DAYS)
            bot_rows.append(bot_ret / HOLDING_DAYS)
            ls_rows.append((top_ret - bot_ret) / HOLDING_DAYS)
    s_top = pd.Series(top_rows)
    s_bot = pd.Series(bot_rows)
    s_ls = pd.Series(ls_rows)
    print(f"  Top decile:        mean_daily={s_top.mean()*100:>+.4f}%, Sharpe={sharpe(s_top):>+.3f}")
    print(f"  Bottom decile:     mean_daily={s_bot.mean()*100:>+.4f}%, Sharpe={sharpe(s_bot):>+.3f}")
    print(f"  Long-Short (T-B):  mean_daily={s_ls.mean()*100:>+.4f}%, Sharpe={sharpe(s_ls):>+.3f}")

    # ---- (3) Gross vs Net (cost 0 시 Sharpe) ----
    print("\n[3] Gross (cost=0) Sharpe (top decile)...")
    gross_rows = []
    for ts, day_group in oos.groupby("ts_utc"):
        n_sel = max(1, int(round(len(day_group) * TOP_DECILE)))
        top = day_group.nlargest(n_sel, "score")
        rets = top["forward_return_7d"].dropna()
        if not rets.empty:
            gross_rows.append(rets.mean() / HOLDING_DAYS)
    s_gross = pd.Series(gross_rows)
    print(f"  Gross (cost=0):    mean_daily={s_gross.mean()*100:>+.4f}%, Sharpe={sharpe(s_gross):>+.3f}")
    print(f"  Net (cost 박제):    Sharpe={sharpe(s_top):>+.3f}  (gross - net = {sharpe(s_gross) - sharpe(s_top):>+.3f})")

    # ---- (4) Bottom decile only (모델이 거꾸로?) ----
    print("\n[4] Bottom decile only 매수 (모델 inverse 가설 검증)...")
    print(f"  Bottom decile Sharpe: {sharpe(s_bot):>+.3f}  (양수면 모델이 거꾸로 예측)")

    # ---- (5) SHAP top 10 (sample 1000) ----
    print("\n[5] SHAP feature contribution (sample 2000)...")
    sample = oos.sample(min(2000, len(oos)), random_state=42)
    X_sample = sample[feature_cols].fillna(0.0).values
    explainer = shap.TreeExplainer(model)
    shap_values = explainer.shap_values(X_sample)
    mean_abs_shap = np.abs(shap_values).mean(axis=0)
    shap_top = pd.DataFrame({
        "feature": feature_cols,
        "mean_abs_shap": mean_abs_shap,
    }).sort_values("mean_abs_shap", ascending=False).head(15)
    print(shap_top.to_string(index=False))

    # ---- (6) Universe size별 성능 ----
    print("\n[6] Universe size 분포...")
    universe_size = oos.groupby("ts_utc").size()
    print(f"  ts_utc count: {len(universe_size)}")
    print(f"  size mean: {universe_size.mean():.0f}, min: {universe_size.min()}, max: {universe_size.max()}")

    # 결과 저장
    output = {
        "monthly_sharpe": monthly,
        "long_short": {
            "top_sharpe": sharpe(s_top), "bottom_sharpe": sharpe(s_bot),
            "long_short_sharpe": sharpe(s_ls),
            "top_mean_daily": float(s_top.mean()), "bottom_mean_daily": float(s_bot.mean()),
        },
        "gross_vs_net": {
            "gross_sharpe": sharpe(s_gross), "net_sharpe": sharpe(s_top),
            "cost_impact": sharpe(s_gross) - sharpe(s_top),
        },
        "shap_top_15": shap_top.to_dict("records"),
        "universe_size_stats": {
            "mean": float(universe_size.mean()),
            "min": int(universe_size.min()), "max": int(universe_size.max()),
        },
    }
    out_path = RESULTS_DIR / "v2_strategy_ml_analysis.json"
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2, default=str)
    print(f"\nsaved: {out_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
