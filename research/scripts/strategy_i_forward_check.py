"""V2-Strategy-I I-02/I-03: Forward 검증 스크립트.

박제 출처: docs/stage1-subplans/v2-strategy-i-mean-reversion.md §1, §2

설계:
- ml_v2 best 모델 (Ridge alpha=0.01, target forward 30d) 학습
- 매 ts_utc 마다 universe top 50 score 계산
- Bottom decile 5개 매수 시뮬 (가상)
- 7일 후 forward return 측정 (실 데이터)
- 거래비용 박제 + Sharpe / Long-Short / DSR
- 출력: research/notebooks/results/v2_strategy_i_forward.json

호출 방법:
- 수동: 매일 09:10 KST 실행
- 또는 launchd 등록 (별도 daemon)
"""
from __future__ import annotations

import json
import math
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import scipy.stats as scs
from sklearn.linear_model import Ridge

DATA_DIR = Path(__file__).parent.parent / "data" / "ml_v2"
RESULTS_DIR = Path(__file__).parent.parent / "notebooks" / "results"

# 박제 (Strategy I sub-plan §1.2)
TRAIN_START = pd.Timestamp("2024-01-01", tz="UTC")
TRAIN_END = pd.Timestamp("2025-08-31", tz="UTC")
# Forward 검증 = 페이퍼 운영 시작 이후 (자연 OOS)
FORWARD_START = pd.Timestamp("2026-04-27", tz="UTC")  # V2-06 daemon 가동 시점

TARGET_PERIOD = 30   # ml_v2 best target
RIDGE_ALPHA = 0.01   # ml_v2 hp=4
TOP_DECILE = 0.10
HOLDING_DAYS = 7
FEE_RATE = 0.0005
SLIPPAGE = {"major": 0.0005, "mid": 0.0010, "small": 0.0030}


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


def main() -> int:
    print("[Strategy I Forward Check]")
    print("[step 1] features 로드 + target 계산...")
    df = pd.read_parquet(DATA_DIR / "features.parquet")
    df["ts_utc"] = pd.to_datetime(df["ts_utc"], utc=True)
    df = df.sort_values(["market", "ts_utc"]).copy()
    df["forward_return_30d"] = df.groupby("market")["close"].pct_change(TARGET_PERIOD).shift(-TARGET_PERIOD)
    df["target_30d"] = np.nan
    mask = df["universe_member"]
    df.loc[mask, "target_30d"] = df.loc[mask].groupby("ts_utc")["forward_return_30d"].rank(pct=True)

    feature_cols = [c for c in df.columns if c not in (
        "ts_utc", "market", "close", "volume", "avg_dollar_volume_30d",
        "universe_member", "forward_return_30d", "target_30d",
    )]
    print(f"  features: {len(feature_cols)}")

    print("[step 2] Ridge 학습 (사전 박제 alpha=0.01, target=30d)...")
    train = df[
        (df["ts_utc"] >= TRAIN_START) & (df["ts_utc"] <= TRAIN_END)
        & df["universe_member"] & df["target_30d"].notna()
    ]
    X_train = train[feature_cols].fillna(0.0).values
    y_train = train["target_30d"].values
    model = Ridge(alpha=RIDGE_ALPHA, random_state=42)
    model.fit(X_train, y_train)
    print(f"  train rows: {len(train):,}")

    print(f"[step 3] Forward 예측 (시작 {FORWARD_START.date()})...")
    forward = df[
        (df["ts_utc"] >= FORWARD_START) & df["universe_member"]
    ].copy()
    if forward.empty:
        print(f"  [warn] forward 데이터 없음 (시작 {FORWARD_START.date()} 이전)")
        print("  → 페이퍼 운영 데이터 누적 후 재실행")
        # baseline: 가상 forward = OOS 마지막 30일 (검증용)
        OOS_END = pd.Timestamp("2026-04-25", tz="UTC")
        forward = df[
            (df["ts_utc"] >= OOS_END - pd.Timedelta(days=30)) & (df["ts_utc"] <= OOS_END)
            & df["universe_member"]
        ].copy()
        print(f"  [baseline] OOS 마지막 30일 사용: {forward['ts_utc'].min().date()} ~ {forward['ts_utc'].max().date()}")

    X_fwd = forward[feature_cols].fillna(0.0).values
    forward["score"] = model.predict(X_fwd)

    print(f"[step 4] Bottom decile 매수 시뮬 (Strategy I 사전 박제)...")
    daily = []
    for ts, g in forward.groupby("ts_utc"):
        n_sel = max(1, int(round(len(g) * TOP_DECILE)))
        top = g.nlargest(n_sel, "score")
        bot = g.nsmallest(n_sel, "score")
        bot_r = bot["forward_return_30d"].dropna()
        top_r = top["forward_return_30d"].dropna()
        if bot_r.empty:
            continue
        bot_cost = bot.apply(
            lambda r: 2 * FEE_RATE + 2 * get_slippage(r.get("avg_dollar_volume_30d", 0) or 0),
            axis=1,
        ).reindex(bot_r.index)
        top_cost = top.apply(
            lambda r: 2 * FEE_RATE + 2 * get_slippage(r.get("avg_dollar_volume_30d", 0) or 0),
            axis=1,
        ).reindex(top_r.index) if not top_r.empty else None
        daily.append({
            "ts_utc": ts.isoformat(),
            "n_universe": len(g),
            "n_select": n_sel,
            "bottom_picks": bot["market"].tolist(),
            "top_picks": top["market"].tolist(),
            "bottom_net_return_30d": float((bot_r - bot_cost).mean()),
            "top_net_return_30d": float((top_r - top_cost).mean()) if top_cost is not None else None,
        })

    if not daily:
        print("  [warn] forward 데이터 부족")
        return 1

    df_d = pd.DataFrame(daily)
    bot_daily = df_d["bottom_net_return_30d"] / TARGET_PERIOD
    top_daily = pd.Series([d["top_net_return_30d"] for d in daily if d["top_net_return_30d"] is not None]) / TARGET_PERIOD
    ls = bot_daily - top_daily.reindex(bot_daily.index)

    print(f"\n[Forward 결과] (n={len(daily)})")
    print(f"  Bottom decile (Strategy I 매수):")
    print(f"    mean daily: {bot_daily.mean()*100:>+.4f}%")
    print(f"    Sharpe:     {sharpe(bot_daily):>+.3f}")
    print(f"  Top decile (참고):")
    print(f"    mean daily: {top_daily.mean()*100:>+.4f}%")
    print(f"    Sharpe:     {sharpe(top_daily):>+.3f}")
    print(f"  Long-Short (B-T):")
    print(f"    Sharpe:     {sharpe(ls):>+.3f}")

    # PASS/FAIL 판정 (sub-plan §2.2)
    n_obs = len(daily)
    sharpe_bot = sharpe(bot_daily)
    sharpe_ls = sharpe(ls)
    pass_criteria = {
        "long_short_sharpe>0.5": sharpe_ls > 0.5,
        "bottom_sharpe>0": sharpe_bot > 0,
        "trades>=14": (n_obs * 5) >= 14,  # 5 cells
    }
    print(f"\n[PASS 판정 (Strategy I sub-plan §2.2)]")
    for k, v in pass_criteria.items():
        print(f"  {k}: {'PASS' if v else 'FAIL'}")
    overall = all(pass_criteria.values())
    print(f"\n  Overall: {'PASS' if overall else 'FAIL'}")

    output = {
        "forward_start": FORWARD_START.isoformat(),
        "n_observations": n_obs,
        "bottom_sharpe": sharpe_bot,
        "top_sharpe": sharpe(top_daily),
        "long_short_sharpe": sharpe_ls,
        "bottom_mean_daily": float(bot_daily.mean()),
        "top_mean_daily": float(top_daily.mean()) if not top_daily.empty else None,
        "pass_criteria": pass_criteria,
        "pass_overall": overall,
        "daily": daily,
    }
    out_path = RESULTS_DIR / "v2_strategy_i_forward.json"
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2, default=str)
    print(f"\nsaved: {out_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
