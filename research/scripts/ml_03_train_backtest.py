"""V2-Strategy-ML ML-03 + ML-04 + ML-05: target + LightGBM lambdarank + walk-forward 백테스트.

박제 출처: docs/stage1-subplans/v2-strategy-ml-trend-factor.md §3.3, §4, §5

설계:
- Target: forward 7d return → 매 ts_utc 시점 cross-sectional percentile rank (0~1)
- Model: LightGBM LGBMRanker (objective='lambdarank')
- Train: 2024-01-01 ~ 2025-08-31 (20m)
- OOS: 2025-09-01 ~ 2026-04-25 (8m)
- Backtest: top 10% 매일 동일가중 매수 (7일 holding, rebalance)
- Cost: fee 0.05% × 왕복 + slippage 차등 (메이저/중형/소형)

Go 기준 (사전 박제):
- OOS Sharpe (거래비용 후) > 1.0
- DSR_z > 0
- OOS trades >= 50
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


DATA_DIR = Path(__file__).parent.parent / "data" / "ml_v2"
RESULTS_DIR = Path(__file__).parent.parent / "notebooks" / "results"
RESULTS_DIR.mkdir(parents=True, exist_ok=True)

# 박제 (sub-plan §3.3 정정 후)
TRAIN_START = pd.Timestamp("2024-01-01", tz="UTC")
TRAIN_END = pd.Timestamp("2025-08-31", tz="UTC")
OOS_START = pd.Timestamp("2025-09-01", tz="UTC")
OOS_END = pd.Timestamp("2026-04-25", tz="UTC")

FORWARD_DAYS = 7
TOP_DECILE = 0.10
HOLDING_DAYS = 7

# 거래비용 박제
FEE_RATE = 0.0005  # 왕복 0.10%
SLIPPAGE_MAJOR = 0.0005    # 메이저 (거래대금 ≥ 500억)
SLIPPAGE_MID = 0.0010      # 중형 (50~500억)
SLIPPAGE_SMALL = 0.0030    # 소형 (10~50억)

# Go 기준
GO_SHARPE = 1.0
GO_DSR_Z = 0.0
GO_TRADES = 50

# DSR 상수
EULER_MASCHERONI = 0.5772156649015329
N_TRIALS = 1  # 단일 hyperparameter set (보수적)


def load_features() -> pd.DataFrame:
    df = pd.read_parquet(DATA_DIR / "features.parquet")
    df["ts_utc"] = pd.to_datetime(df["ts_utc"], utc=True)
    return df


def compute_target(df: pd.DataFrame) -> pd.DataFrame:
    """Target: 다음 7일 forward return cross-sectional percentile rank."""
    df = df.sort_values(["market", "ts_utc"]).copy()
    df["forward_return_7d"] = df.groupby("market")["close"].pct_change(FORWARD_DAYS).shift(-FORWARD_DAYS)
    # universe_member에 해당하는 행만 ranking 계산
    df["target_rank"] = np.nan
    mask = df["universe_member"]
    df.loc[mask, "target_rank"] = (
        df.loc[mask].groupby("ts_utc")["forward_return_7d"].rank(pct=True)
    )
    return df


def get_slippage(avg_dollar_volume_30d: float) -> float:
    if avg_dollar_volume_30d >= 50_000_000_000:
        return SLIPPAGE_MAJOR
    if avg_dollar_volume_30d >= 5_000_000_000:
        return SLIPPAGE_MID
    return SLIPPAGE_SMALL


def train_model(df: pd.DataFrame, feature_cols: list[str]) -> lgb.LGBMRanker:
    train = df[
        (df["ts_utc"] >= TRAIN_START) & (df["ts_utc"] <= TRAIN_END)
        & df["universe_member"]
        & df["target_rank"].notna()
    ].copy()
    # fillna(0)로 처리 (47 features 중 warmup NaN은 0 → LightGBM이 자체 학습)
    # dropna(subset=feature_cols)는 너무 strict (모든 feature 유효 행만 → 0 rows)
    train = train.sort_values(["ts_utc", "market"])

    print(f"  train rows: {len(train):,}")
    print(f"  train ts range: {train['ts_utc'].min().date()} ~ {train['ts_utc'].max().date()}")

    # LambdaRank: group by ts_utc (각 시점 = 한 query)
    group_sizes = train.groupby("ts_utc").size().to_list()
    X_train = train[feature_cols].fillna(0.0).values
    # LambdaRank target: discretize percentile rank to integer levels (0~30, higher=better)
    y_train = (train["target_rank"].values * 30).astype(int)

    model = lgb.LGBMRanker(
        objective="lambdarank",
        boosting_type="gbdt",
        num_leaves=31,
        learning_rate=0.05,
        n_estimators=300,
        min_child_samples=50,
        reg_alpha=0.1,
        reg_lambda=0.1,
        random_state=42,
        verbose=-1,
    )
    model.fit(X_train, y_train, group=group_sizes)
    return model


def backtest_oos(df: pd.DataFrame, model: lgb.LGBMRanker, feature_cols: list[str]) -> dict:
    oos = df[
        (df["ts_utc"] >= OOS_START) & (df["ts_utc"] <= OOS_END)
        & df["universe_member"]
    ].copy()
    # fillna(0) 일관 (training과 동일 처리)

    print(f"  oos rows: {len(oos):,}")
    print(f"  oos ts range: {oos['ts_utc'].min().date()} ~ {oos['ts_utc'].max().date()}")

    X_oos = oos[feature_cols].fillna(0.0).values
    oos["score"] = model.predict(X_oos)

    # 매 ts_utc마다 score top decile 선정 → 7일 보유 → realized return 계산
    daily_returns: list[dict] = []
    trade_count = 0
    for ts, group in oos.groupby("ts_utc"):
        n = len(group)
        if n < 5:
            continue
        n_select = max(1, int(round(n * TOP_DECILE)))
        top = group.nlargest(n_select, "score")
        # 실제 forward return (target_rank 계산 시 사용한 동일 forward_return_7d)
        rets = top["forward_return_7d"].dropna()
        if rets.empty:
            continue
        # 거래비용: fee 왕복 0.10% + slippage (cell 거래대금 따라 차등)
        cost = top.apply(
            lambda r: 2 * FEE_RATE + 2 * get_slippage(r.get("avg_dollar_volume_30d", 0) or 0),
            axis=1,
        )
        net_rets = rets - cost.reindex(rets.index)
        daily_return = net_rets.mean()  # equal-weight top decile
        daily_returns.append({
            "ts_utc": ts, "n_universe": n, "n_select": n_select,
            "gross_return": rets.mean(), "net_return": daily_return,
        })
        trade_count += n_select

    if not daily_returns:
        return {"error": "no trades"}

    ret_df = pd.DataFrame(daily_returns).set_index("ts_utc")
    # 7일 holding이라 매일 진입은 7일 평균 → 연환산은 daily 기준 √365 사용 (overlap 단순화)
    daily_net = ret_df["net_return"] / HOLDING_DAYS  # 7d return → daily 평균
    sharpe_net = float(daily_net.mean() / daily_net.std() * math.sqrt(365)) if daily_net.std() > 0 else 0.0
    daily_gross = ret_df["gross_return"] / HOLDING_DAYS
    sharpe_gross = float(daily_gross.mean() / daily_gross.std() * math.sqrt(365)) if daily_gross.std() > 0 else 0.0

    # MDD (overlap holding 단순 cumulative)
    cum_net = (1 + daily_net).cumprod()
    mdd_net = float(((cum_net.cummax() - cum_net) / cum_net.cummax()).max())

    # DSR (Bailey 2014, N_trials=1 → 단일 시도)
    skew = float(scs.skew(daily_net.values))
    kurt_raw = float(scs.kurtosis(daily_net.values, fisher=False))
    T = len(daily_net)
    sr_0 = math.sqrt(np.var([sharpe_net], ddof=0)) if N_TRIALS > 1 else 0.0  # N_trials=1 → SR_0=0
    denom = 1.0 - skew * sharpe_net + ((kurt_raw - 1.0) / 4.0) * sharpe_net ** 2
    dsr_z = (sharpe_net - sr_0) * math.sqrt((T - 1) / denom) if denom > 0 and T > 1 else 0.0

    # Go 판정
    go = (sharpe_net > GO_SHARPE) and (dsr_z > GO_DSR_Z) and (trade_count >= GO_TRADES)

    return {
        "sharpe_gross": sharpe_gross,
        "sharpe_net": sharpe_net,
        "mdd_net": mdd_net,
        "trade_count": trade_count,
        "T_daily_obs": T,
        "skew": skew,
        "kurtosis_raw": kurt_raw,
        "dsr_z": dsr_z,
        "n_trials": N_TRIALS,
        "go": go,
        "go_criteria": {
            "sharpe_threshold": GO_SHARPE, "dsr_z_threshold": GO_DSR_Z, "trades_min": GO_TRADES,
        },
        "cum_return_oos": float(cum_net.iloc[-1] - 1),
        "win_rate": float((daily_net > 0).mean()),
    }


def main() -> int:
    print("[ML-03/04/05] target + LightGBM lambdarank + OOS 백테스트")
    print("[step 1] features 로드 + target 계산...")
    df = load_features()
    df = compute_target(df)
    print(f"  rows: {len(df):,}")
    target_count = df["target_rank"].notna().sum()
    print(f"  target valid rows: {target_count:,}")

    feature_cols = [c for c in df.columns if c not in (
        "ts_utc", "market", "close", "volume", "avg_dollar_volume_30d",
        "universe_member", "forward_return_7d", "target_rank",
    )]
    print(f"  features: {len(feature_cols)}")

    print("\n[step 2] LightGBM 학습 (lambdarank)...")
    model = train_model(df, feature_cols)

    importance = pd.DataFrame({
        "feature": feature_cols,
        "importance": model.feature_importances_,
    }).sort_values("importance", ascending=False)
    print("  top 10 importance:")
    for _, row in importance.head(10).iterrows():
        print(f"    {row['feature']:<35} {int(row['importance']):>6}")

    print("\n[step 3] OOS 백테스트 (top 10% 동일가중 매수, 거래비용 박제)...")
    result = backtest_oos(df, model, feature_cols)

    if "error" in result:
        print(f"  ERROR: {result['error']}")
        return 1

    print(f"\n[result]")
    print(f"  Sharpe (gross):       {result['sharpe_gross']:>8.3f}")
    print(f"  Sharpe (net, 비용 후): {result['sharpe_net']:>8.3f}  (Go 기준 > {GO_SHARPE})")
    print(f"  MDD:                  {result['mdd_net']*100:>7.2f}%")
    print(f"  cum return OOS:       {result['cum_return_oos']*100:>+7.2f}%")
    print(f"  trade count:          {result['trade_count']:>8}     (Go 기준 ≥ {GO_TRADES})")
    print(f"  win rate (daily):     {result['win_rate']*100:>7.2f}%")
    print(f"  DSR_z:                {result['dsr_z']:>8.3f}     (Go 기준 > {GO_DSR_Z})")
    print(f"\n  Go/No-Go: {'GO' if result['go'] else 'NO-GO'}")

    output = {
        **result,
        "feature_importance_top10": importance.head(10).to_dict("records"),
        "train_period": [str(TRAIN_START.date()), str(TRAIN_END.date())],
        "oos_period": [str(OOS_START.date()), str(OOS_END.date())],
    }
    out_path = RESULTS_DIR / "v2_strategy_ml_oos.json"
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2, default=str)
    print(f"\nsaved: {out_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
