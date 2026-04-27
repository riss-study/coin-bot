"""Strategy A — Trend Following (MA200 + Donchian + Volume filter).

박제 출처:
- docs/candidate-pool.md v7 Strategy A
- research/notebooks/02_strategy_a_trend_daily.ipynb (W1-02 검증)
- research/_tools/make_notebook_08.py cell 6 (W2-03 strategy_a_signals)

파라미터 (W2-02 v5 박제, 재튜닝 금지):
- MA_PERIOD = 200 (MA200 filter)
- DONCHIAN_HIGH = 20 (breakout 판정)
- DONCHIAN_LOW = 10 (reverse exit)
- VOL_AVG_PERIOD = 20
- VOL_MULT = 1.5 (거래량 > 평균 × 1.5)
- SL_PCT = 0.08 (8% 하드 스톱)

신호 규칙 (W2-03 vectorbt 구현과 동등, look-ahead 차단):
- entry: close > MA200 AND close > donchian_high.shift(1) AND volume > vol_avg.shift(1) × VOL_MULT
- exit:  close < donchian_low.shift(1)
- sl_exit: today low <= entry × (1 - SL_PCT)
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import pandas as pd

from engine.strategies.base import SignalAction, SignalResult, check_sl_hit


@dataclass
class StrategyA:
    """Trend Following (MA200 + Donchian + Volume)."""

    ma_period: int = 200
    donchian_high: int = 20
    donchian_low: int = 10
    vol_avg_period: int = 20
    vol_mult: float = 1.5
    sl_pct: float = 0.08

    name: str = "A"

    def compute_signal(
        self,
        df: pd.DataFrame,
        in_position: bool,
        entry_price_krw: float | None = None,
        bars_held: int | None = None,  # interface compat (Strategy A는 미사용)
    ) -> SignalResult:
        required_cols = {"open", "high", "low", "close", "volume"}
        missing = required_cols - set(df.columns)
        if missing:
            raise ValueError(f"df missing columns: {missing}")
        if len(df) < self.ma_period + 1:
            raise ValueError(f"df must have >= {self.ma_period + 1} rows, got {len(df)}")

        close = df["close"]
        high = df["high"]
        low = df["low"]
        volume = df["volume"]

        # 지표 계산 (look-ahead 차단: donchian / vol_avg 는 .shift(1))
        ma = close.rolling(window=self.ma_period).mean()
        donchian_high = high.rolling(window=self.donchian_high).max().shift(1)
        donchian_low = low.rolling(window=self.donchian_low).min().shift(1)
        vol_avg = volume.rolling(window=self.vol_avg_period).mean().shift(1)

        # 오늘 (마지막 row) 시점
        today_close = float(close.iloc[-1])
        today_low = float(low.iloc[-1])
        today_volume = float(volume.iloc[-1])
        today_ma = float(ma.iloc[-1]) if not pd.isna(ma.iloc[-1]) else None
        today_dh = float(donchian_high.iloc[-1]) if not pd.isna(donchian_high.iloc[-1]) else None
        today_dl = float(donchian_low.iloc[-1]) if not pd.isna(donchian_low.iloc[-1]) else None
        today_va = float(vol_avg.iloc[-1]) if not pd.isna(vol_avg.iloc[-1]) else None

        snapshot: dict[str, Any] = {
            "close": today_close,
            "low": today_low,
            "volume": today_volume,
            "ma200": today_ma,
            "donchian_high_shifted": today_dh,
            "donchian_low_shifted": today_dl,
            "vol_avg_shifted": today_va,
        }

        # Warmup 미완료 시 hold
        if any(v is None for v in (today_ma, today_dh, today_dl, today_va)):
            return SignalResult(
                action=SignalAction.HOLD,
                reason={"warmup_incomplete": True, "required_bars": self.ma_period + 1},
                indicator_snapshot=snapshot,
            )

        # 포지션 있을 때: SL → exit 순서
        if in_position:
            if entry_price_krw is not None and check_sl_hit(today_low, entry_price_krw, self.sl_pct):
                return SignalResult(
                    action=SignalAction.SL_EXIT,
                    reason={"sl_hit": True, "entry": entry_price_krw, "today_low": today_low,
                            "sl_level": entry_price_krw * (1 - self.sl_pct)},
                    indicator_snapshot=snapshot,
                )
            if today_close < today_dl:
                return SignalResult(
                    action=SignalAction.EXIT,
                    reason={"close_below_donchian_low": True, "close": today_close, "donchian_low": today_dl},
                    indicator_snapshot=snapshot,
                )
            return SignalResult(
                action=SignalAction.HOLD,
                reason={"in_position_no_exit_signal": True},
                indicator_snapshot=snapshot,
            )

        # 포지션 없을 때: entry 조건 평가
        entry_cond_ma = today_close > today_ma
        entry_cond_breakout = today_close > today_dh
        entry_cond_volume = today_volume > today_va * self.vol_mult
        all_entry = entry_cond_ma and entry_cond_breakout and entry_cond_volume

        if all_entry:
            return SignalResult(
                action=SignalAction.ENTRY,
                reason={
                    "ma_filter_pass": entry_cond_ma,
                    "donchian_breakout": entry_cond_breakout,
                    "volume_spike": entry_cond_volume,
                },
                indicator_snapshot=snapshot,
            )
        return SignalResult(
            action=SignalAction.HOLD,
            reason={
                "ma_filter_pass": entry_cond_ma,
                "donchian_breakout": entry_cond_breakout,
                "volume_spike": entry_cond_volume,
            },
            indicator_snapshot=snapshot,
        )


if __name__ == "__main__":
    # Sanity: 최근 BTC 400일 OHLCV로 오늘 신호 평가
    from datetime import datetime, timedelta, timezone
    from engine.config import ENGINE_ROOT, ensure_runtime_dirs, load_config
    from engine.logger import setup_logger
    from engine.market_data import fetch_ohlcv

    ensure_runtime_dirs()
    cfg = load_config()
    logger = setup_logger(ENGINE_ROOT / "logs", "INFO")

    btc = fetch_ohlcv("KRW-BTC", interval="day", count=400)
    print(f"BTC 데이터 {len(btc)} bars, 최신: {btc.index[-1].date()} close={btc['close'].iloc[-1]:,.0f}")

    strat_a = StrategyA(
        ma_period=cfg.strategy_a.ma_period,
        donchian_high=cfg.strategy_a.donchian_high,
        donchian_low=cfg.strategy_a.donchian_low,
        vol_avg_period=cfg.strategy_a.vol_avg_period,
        vol_mult=cfg.strategy_a.vol_mult,
        sl_pct=cfg.strategy_a.sl_pct,
    )

    # 포지션 없음 시나리오
    result_flat = strat_a.compute_signal(btc, in_position=False)
    print(f"\n[No position] action={result_flat.action.value}, reason={result_flat.reason}")

    # 포지션 있음 시나리오 (SL 테스트, entry 가짜값)
    fake_entry = btc["close"].iloc[-1] * 1.1  # 현재보다 10% 높은 진입가 → SL 터치 가능성
    result_in = strat_a.compute_signal(btc, in_position=True, entry_price_krw=fake_entry)
    print(f"\n[In position, entry={fake_entry:,.0f}] action={result_in.action.value}, reason={result_in.reason}")

    logger.info("strategy_a_sanity_ok", extra={"today_action": result_flat.action.value})
