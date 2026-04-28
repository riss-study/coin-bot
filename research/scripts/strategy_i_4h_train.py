"""V2-Strategy-I 4h: Ridge 모델 학습 + artifact 저장 (4시간봉 버전).

박제 출처: ml_v3 grid best — Ridge hp=0 (alpha=0.1) t=30d (180 bars)
사용자 명시 동의 ("4시간봉 같이 굴려보자" 2026-04-28).

설계:
- features 47개 (window in 4h bars: 30d × 6 = 180 bars)
- target: forward 30d (180 bars) cross-sectional percentile rank
- Train: 2024-01-01 ~ 2025-08-31 (ml_v3 동일)
- Ridge alpha=0.1 (ml_v3 best hp=0)

artifact 저장:
- engine/data/strategy_i_4h/ridge_model.pkl
- engine/data/strategy_i_4h/feature_cols.json
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
from sklearn.linear_model import Ridge

ROOT = Path(__file__).parent.parent.parent
DATA_V3 = ROOT / "research" / "data" / "ml_v3"
DATA_V2 = ROOT / "research" / "data" / "ml_v2"
ARTIFACT_DIR = ROOT / "engine" / "data" / "strategy_i_4h"
ARTIFACT_DIR.mkdir(parents=True, exist_ok=True)

sys.path.insert(0, str(ROOT / "research" / "scripts"))
from ml_v3_features_grid import build_features, compute_macro, BARS_PER_DAY  # noqa: E402

TRAIN_START = pd.Timestamp("2024-01-01", tz="UTC")
TRAIN_END = pd.Timestamp("2025-08-31", tz="UTC")
TARGET_PERIOD_DAYS = 30
RIDGE_ALPHA = 0.1


def main() -> int:
    print("[Strategy I 4h train] Ridge alpha=0.1, target forward 30d (180 4h bars)")
    ohlcv = pd.read_parquet(DATA_V3 / "ohlcv_4h.parquet")
    ohlcv["ts_utc"] = pd.to_datetime(ohlcv["ts_utc"], utc=True)
    ohlcv = ohlcv.sort_values(["market", "ts_utc"]).reset_index(drop=True)
    ohlcv["dollar_volume"] = ohlcv["volume"] * ohlcv["close"]

    btc = pd.read_parquet(DATA_V2 / "btc_binance.parquet")
    fx = pd.read_parquet(DATA_V2 / "usdkrw.parquet")
    btc.index = pd.to_datetime(btc.index, utc=True)
    fx.index = pd.to_datetime(fx.index, utc=True)
    btc = btc[["close"]].rename(columns={"close": "btc_global_usd"})
    fx = fx[["close"]].rename(columns={"close": "usd_krw"})

    print("[step 1] macro + features build...")
    macro = compute_macro(ohlcv, btc, fx)
    df = build_features(ohlcv, macro)
    print(f"  rows: {len(df):,}, markets: {df['market'].nunique()}")

    feature_cols = [c for c in df.columns if c not in (
        "ts_utc", "market", "close", "volume", "avg_dollar_volume_30d",
        "universe_member",
        *[f"forward_return_{p}d" for p in [1, 3, 7, 14, 30]],
        *[f"target_{p}d" for p in [1, 3, 7, 14, 30]],
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
    print(f"  intercept: {model.intercept_:.6f}, coef shape: {model.coef_.shape}")

    model_path = ARTIFACT_DIR / "ridge_model.pkl"
    feat_path = ARTIFACT_DIR / "feature_cols.json"
    joblib.dump(model, model_path)
    with open(feat_path, "w", encoding="utf-8") as f:
        json.dump({
            "feature_cols": feature_cols,
            "ridge_alpha": RIDGE_ALPHA,
            "target_period_days": TARGET_PERIOD_DAYS,
            "target_period_bars": TARGET_PERIOD_DAYS * BARS_PER_DAY,
            "bars_per_day": BARS_PER_DAY,
            "train_start": TRAIN_START.isoformat(),
            "train_end": TRAIN_END.isoformat(),
            "train_rows": len(train),
            "interval": "minute240",
        }, f, ensure_ascii=False, indent=2)
    print(f"\n  saved: {model_path}")
    print(f"  saved: {feat_path}")

    coefs = pd.DataFrame({"feature": feature_cols, "coef": model.coef_,
                          "abs_coef": np.abs(model.coef_)}).sort_values("abs_coef", ascending=False)
    print("\n  top 10 |coef|:")
    for _, r in coefs.head(10).iterrows():
        print(f"    {r['feature']:<35} {r['coef']:>+8.4f}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
