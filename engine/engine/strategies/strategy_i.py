"""Strategy I — Mean Reversion via Inverse Trend Factor (Portfolio-level).

박제 출처: docs/stage1-subplans/v2-strategy-i-mean-reversion.md
모델: Ridge alpha=0.01, target forward 30d cross-sectional percentile rank
진입: Bottom decile (score 낮은 5개) 매수 — 모델 예측 거꾸로
청산: SL -5% / TP +10% / time stop 7일

Portfolio-level (Strategy A/D/G와 다름): 한 cell 평가가 아니라 universe 전체 ranking.
process_strategy_i() 메서드로 daemon에서 호출.
"""
from __future__ import annotations

import json
import logging
from dataclasses import dataclass
from pathlib import Path
from typing import Mapping

import joblib
import numpy as np
import pandas as pd

from engine.strategies.base import check_sl_hit
from engine.strategies.features_v2 import build_features


log = logging.getLogger("engine.strategies.strategy_i")


@dataclass
class StrategyI:
    """Mean Reversion via Inverse Trend Factor."""

    artifact_dir: Path
    bottom_decile_n: int = 5
    sl_pct: float = 0.05
    tp_pct: float = 0.10
    time_stop_bars: int = 7

    name: str = "I"

    def __post_init__(self):
        self.model = joblib.load(self.artifact_dir / "ridge_model.pkl")
        with open(self.artifact_dir / "feature_cols.json", encoding="utf-8") as f:
            meta = json.load(f)
        self.feature_cols = meta["feature_cols"]
        log.info("strategy_i_model_loaded",
                  extra={"features": len(self.feature_cols), "alpha": meta.get("ridge_alpha"),
                          "train_end": meta.get("train_end")})

    def select_bottom_decile(
        self,
        universe_ohlcv: Mapping[str, pd.DataFrame],
        btc_global: pd.Series,
        fx: pd.Series,
    ) -> list[dict]:
        """오늘 시점 bottom decile 5개 식별 (매수 후보).

        Returns:
            list of {"market": str, "score": float, "rank": int, "snapshot": dict}
        """
        feats = build_features(universe_ohlcv, btc_global, fx)
        # 가장 최근 ts_utc 행만 사용 (daemon은 매일 어제 close까지 데이터)
        latest_ts = feats["ts_utc"].max()
        latest = feats[(feats["ts_utc"] == latest_ts) & feats["universe_member"]].copy()
        if latest.empty:
            log.warning("strategy_i_no_universe", extra={"latest_ts": str(latest_ts)})
            return []

        X = latest[self.feature_cols].fillna(0.0).values
        latest["score"] = self.model.predict(X)
        latest = latest.sort_values("score")

        bottom = latest.head(self.bottom_decile_n)
        result = []
        for rank, (_, row) in enumerate(bottom.iterrows(), start=1):
            result.append({
                "market": row["market"],
                "score": float(row["score"]),
                "rank": rank,
                "close": float(row["close"]),
                "ts_utc": str(latest_ts),
            })
        return result

    def check_exit(
        self,
        today_low: float,
        today_close: float,
        entry_price_krw: float,
        bars_held: int,
    ) -> tuple[str, dict] | None:
        """보유 포지션 exit 평가. ("sl_exit"|"exit"|None, reason)."""
        if check_sl_hit(today_low, entry_price_krw, self.sl_pct):
            return "sl_exit", {"sl_hit": True, "today_low": today_low,
                                "sl_level": entry_price_krw * (1 - self.sl_pct)}
        if today_close >= entry_price_krw * (1 + self.tp_pct):
            return "exit", {"tp_hit": True, "today_close": today_close,
                            "tp_level": entry_price_krw * (1 + self.tp_pct)}
        if bars_held >= self.time_stop_bars:
            return "exit", {"time_stop": True, "bars_held": bars_held}
        return None
