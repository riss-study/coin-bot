"""V2-Strategy-I I-02: 모델 학습 + artifact 저장.

박제 출처: docs/stage1-subplans/v2-strategy-i-mean-reversion.md §1.2

설계:
- ml_v2/v3 grid 발견 best 모델 그대로:
  * Algorithm: Ridge alpha=0.01
  * Target: forward 30d cross-sectional percentile rank
  * Features: 47 (ml_v2 동일)
  * Train: 2024-01-01 ~ 2025-08-31 (cycle 1 #5 회피, 박제 변경 X)
- artifact 저장 (engine daemon이 매일 load 가능):
  * model.pkl — Ridge 모델 weights
  * feature_cols.json — feature 컬럼 순서

엔진은 매일 cycle에서 본 모델 load + features 재계산 + bottom decile 5 매수.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.linear_model import Ridge

import joblib

DATA_DIR = Path(__file__).parent.parent / "data" / "ml_v2"
ARTIFACT_DIR = Path(__file__).parent.parent.parent / "engine" / "data" / "strategy_i"
ARTIFACT_DIR.mkdir(parents=True, exist_ok=True)

TRAIN_START = pd.Timestamp("2024-01-01", tz="UTC")
TRAIN_END = pd.Timestamp("2025-08-31", tz="UTC")
TARGET_PERIOD = 30
RIDGE_ALPHA = 0.01


def main() -> int:
    print("[Strategy I train] Ridge alpha=0.01, target forward 30d")
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

    train = df[
        (df["ts_utc"] >= TRAIN_START) & (df["ts_utc"] <= TRAIN_END)
        & df["universe_member"] & df["target_30d"].notna()
    ]
    X_train = train[feature_cols].fillna(0.0).values
    y_train = train["target_30d"].values
    print(f"  train rows: {len(train):,}")

    model = Ridge(alpha=RIDGE_ALPHA, random_state=42)
    model.fit(X_train, y_train)
    print(f"  model coef shape: {model.coef_.shape}, intercept: {model.intercept_:.6f}")

    # 저장 (joblib for sklearn)
    model_path = ARTIFACT_DIR / "ridge_model.pkl"
    feature_path = ARTIFACT_DIR / "feature_cols.json"
    joblib.dump(model, model_path)
    with open(feature_path, "w", encoding="utf-8") as f:
        json.dump({
            "feature_cols": feature_cols,
            "ridge_alpha": RIDGE_ALPHA,
            "target_period": TARGET_PERIOD,
            "train_start": TRAIN_START.isoformat(),
            "train_end": TRAIN_END.isoformat(),
            "train_rows": len(train),
        }, f, ensure_ascii=False, indent=2)

    print(f"\n  saved: {model_path}")
    print(f"  saved: {feature_path}")

    # Top 10 abs coef
    coefs = pd.DataFrame({"feature": feature_cols, "coef": model.coef_,
                          "abs_coef": np.abs(model.coef_)}).sort_values("abs_coef", ascending=False)
    print("\n  top 10 |coef|:")
    for _, r in coefs.head(10).iterrows():
        print(f"    {r['feature']:<35} {r['coef']:>+8.4f}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
