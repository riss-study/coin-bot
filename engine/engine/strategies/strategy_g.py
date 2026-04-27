"""Strategy G — Active Multi-pair (활동 빈도 우선, 통계 검증 X).

박제 출처:
- docs/stage1-subplans/v2-strategy-g-active.md §2 사전 박제
- 사용자 명시 동의 (2026-04-26 "그렇게 해봐"): alpha 검증 X + 빈번 활동 + 위험 감수

진입 (3 AND):
    (1) close >= open × 1.02
    (2) volume > vol_avg(20).shift(1) × 1.2
    (3) close > high.rolling(3).max().shift(1)

청산 (어느 하나라도):
    (a) SL_EXIT: today_low <= entry × 0.97        (-3%)
    (b) EXIT (TP):  today_close >= entry × 1.05   (+5%)
    (c) EXIT (time): bars_held >= 3                (3일)

위험: 통계 alpha 검증 X. 회당 -0.20% expected value (수수료+slippage).
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import pandas as pd

from engine.strategies.base import SignalAction, SignalResult, check_sl_hit


@dataclass
class StrategyG:
    """Active Multi-pair (활동 빈도 우선)."""

    entry_bar_pct: float = 0.02
    vol_avg: int = 20
    vol_mult: float = 1.2
    short_break: int = 3
    sl_pct: float = 0.03
    tp_pct: float = 0.05
    time_stop_bars: int = 3

    name: str = "G"

    def compute_signal(
        self,
        df: pd.DataFrame,
        in_position: bool,
        entry_price_krw: float | None = None,
        bars_held: int | None = None,
    ) -> SignalResult:
        required = {"open", "high", "low", "close", "volume"}
        missing = required - set(df.columns)
        if missing:
            raise ValueError(f"df missing columns: {missing}")
        if len(df) < self.vol_avg + 1:
            # 신규 상장 코인 등 — graceful hold (process_cell 차단 X, 다른 cells 진행)
            return SignalResult(
                SignalAction.HOLD,
                reason={"insufficient_data": True, "rows": len(df), "required": self.vol_avg + 1},
            )

        today_close = float(df["close"].iloc[-1])
        today_low = float(df["low"].iloc[-1])
        today_open = float(df["open"].iloc[-1])

        # 보유 중: SL/TP/time stop 평가
        if in_position:
            if entry_price_krw is None or entry_price_krw <= 0:
                return SignalResult(SignalAction.HOLD, reason={"error": "no_entry_price"})

            if check_sl_hit(today_low, entry_price_krw, self.sl_pct):
                return SignalResult(
                    SignalAction.SL_EXIT,
                    reason={"sl_hit": True, "today_low": today_low,
                            "sl_level": entry_price_krw * (1 - self.sl_pct)},
                )
            if today_close >= entry_price_krw * (1 + self.tp_pct):
                return SignalResult(
                    SignalAction.EXIT,
                    reason={"tp_hit": True, "today_close": today_close,
                            "tp_level": entry_price_krw * (1 + self.tp_pct)},
                )
            if bars_held is not None and bars_held >= self.time_stop_bars:
                return SignalResult(
                    SignalAction.EXIT,
                    reason={"time_stop": True, "bars_held": bars_held},
                )
            return SignalResult(SignalAction.HOLD, reason={"in_position": True, "bars_held": bars_held})

        # 미보유: entry 평가
        close = df["close"]
        volume = df["volume"]
        high = df["high"]

        vol_avg = volume.rolling(window=self.vol_avg).mean().shift(1)
        short_high = high.rolling(window=self.short_break).max().shift(1)

        today_volume = float(volume.iloc[-1])
        today_va = float(vol_avg.iloc[-1]) if not pd.isna(vol_avg.iloc[-1]) else None
        today_sh = float(short_high.iloc[-1]) if not pd.isna(short_high.iloc[-1]) else None

        snapshot: dict[str, Any] = {
            "close": today_close, "open": today_open, "low": today_low,
            "volume": today_volume, "vol_avg": today_va, "short_high": today_sh,
        }

        bull_pass = today_close >= today_open * (1 + self.entry_bar_pct)
        vol_pass = today_va is not None and today_volume > today_va * self.vol_mult
        break_pass = today_sh is not None and today_close > today_sh

        reason = {
            "bull_pass": bull_pass, "vol_pass": vol_pass, "break_pass": break_pass,
            "bull_ratio": today_close / today_open if today_open else None,
        }

        if bull_pass and vol_pass and break_pass:
            return SignalResult(SignalAction.ENTRY, reason=reason, indicator_snapshot=snapshot)
        return SignalResult(SignalAction.HOLD, reason=reason, indicator_snapshot=snapshot)
