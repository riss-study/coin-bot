"""Strategy D — Volatility Breakout (Keltner + Bollinger + SL 8%).

박제 출처:
- docs/candidate-pool.md v7 Strategy D
- research/_tools/make_notebook_08.py cell 8 (W2-03 strategy_d_signals)
- W2-02 v5 박제: ta `KeltnerChannel(window=20, window_atr=14, original_version=False, multiplier=1.5)`

파라미터 (W2-02 v5, 재튜닝 금지):
- KELTNER_WINDOW = 20
- KELTNER_ATR_MULT = 1.5
- ATR_WINDOW = 14 (Keltner 내부 ATR, ta default 10과 다름)
- BOLLINGER_WINDOW = 20
- BOLLINGER_SIGMA = 2.0
- SL_HARD = 0.08 (하드 스톱 8%)

신호 규칙 (W2-03 구현 동등, strict crossover):
- entry: (close > kc_upper) AND (close.shift(1) <= kc_upper.shift(1))
         AND (close > bb_upper) AND (close.shift(1) <= bb_upper.shift(1))
- exit:  (close < kc_mid) AND (close.shift(1) >= kc_mid.shift(1))
  (kc_mid = EMA(close, 20) — original_version=False에서 EMA 사용)
- sl_exit: today low <= entry × (1 - SL_HARD)
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import pandas as pd
from ta.volatility import BollingerBands, KeltnerChannel

from engine.strategies.base import SignalAction, SignalResult, check_sl_hit


@dataclass
class StrategyD:
    """Volatility Breakout (Keltner + Bollinger 동시 돌파)."""

    keltner_window: int = 20
    keltner_atr_mult: float = 1.5
    atr_window: int = 14
    bollinger_window: int = 20
    bollinger_sigma: float = 2.0
    sl_hard: float = 0.08

    name: str = "D"

    def compute_signal(
        self,
        df: pd.DataFrame,
        in_position: bool,
        entry_price_krw: float | None = None,
    ) -> SignalResult:
        required_cols = {"open", "high", "low", "close", "volume"}
        missing = required_cols - set(df.columns)
        if missing:
            raise ValueError(f"df missing columns: {missing}")
        # warmup = max(keltner_window, bollinger_window, atr_window) + 1 최소
        min_bars = max(self.keltner_window, self.bollinger_window, self.atr_window) + 2
        if len(df) < min_bars:
            raise ValueError(f"df must have >= {min_bars} rows, got {len(df)}")

        close = df["close"]
        high = df["high"]
        low = df["low"]

        # ta KeltnerChannel (W2-02 v5 박제 명시 호출, default 다름)
        kc = KeltnerChannel(
            high=high, low=low, close=close,
            window=self.keltner_window, window_atr=self.atr_window,
            original_version=False, multiplier=self.keltner_atr_mult,
        )
        kc_upper = kc.keltner_channel_hband()
        kc_mid = kc.keltner_channel_mband()  # EMA(close, 20)

        # ta BollingerBands
        bb = BollingerBands(close=close, window=self.bollinger_window, window_dev=self.bollinger_sigma)
        bb_upper = bb.bollinger_hband()

        # 오늘 (마지막) + 어제 (shift(1)) 값
        today_close = float(close.iloc[-1])
        today_low = float(low.iloc[-1])
        yesterday_close = float(close.iloc[-2])

        def _val(series, idx=-1):
            v = series.iloc[idx]
            return float(v) if not pd.isna(v) else None

        kc_u_today = _val(kc_upper, -1)
        kc_u_yest = _val(kc_upper, -2)
        kc_m_today = _val(kc_mid, -1)
        kc_m_yest = _val(kc_mid, -2)
        bb_u_today = _val(bb_upper, -1)
        bb_u_yest = _val(bb_upper, -2)

        snapshot: dict[str, Any] = {
            "close": today_close,
            "low": today_low,
            "kc_upper_today": kc_u_today,
            "kc_upper_yest": kc_u_yest,
            "kc_mid_today": kc_m_today,
            "kc_mid_yest": kc_m_yest,
            "bb_upper_today": bb_u_today,
            "bb_upper_yest": bb_u_yest,
        }

        if any(v is None for v in (kc_u_today, kc_u_yest, kc_m_today, kc_m_yest, bb_u_today, bb_u_yest)):
            return SignalResult(
                action=SignalAction.HOLD,
                reason={"warmup_incomplete": True, "required_bars": min_bars},
                indicator_snapshot=snapshot,
            )

        # In-position: SL → kc_mid 하향 crossover exit
        if in_position:
            if entry_price_krw is not None and check_sl_hit(today_low, entry_price_krw, self.sl_hard):
                return SignalResult(
                    action=SignalAction.SL_EXIT,
                    reason={"sl_hit": True, "entry": entry_price_krw, "today_low": today_low,
                            "sl_level": entry_price_krw * (1 - self.sl_hard)},
                    indicator_snapshot=snapshot,
                )
            # kc_mid 하향 strict crossover
            mid_exit = today_close < kc_m_today and yesterday_close >= kc_m_yest
            if mid_exit:
                return SignalResult(
                    action=SignalAction.EXIT,
                    reason={"kc_mid_downward_cross": True},
                    indicator_snapshot=snapshot,
                )
            return SignalResult(
                action=SignalAction.HOLD,
                reason={"in_position_no_exit_signal": True},
                indicator_snapshot=snapshot,
            )

        # Flat: strict 동시 상향 돌파
        kc_break = today_close > kc_u_today and yesterday_close <= kc_u_yest
        bb_break = today_close > bb_u_today and yesterday_close <= bb_u_yest
        if kc_break and bb_break:
            return SignalResult(
                action=SignalAction.ENTRY,
                reason={"kc_upper_crossover": True, "bb_upper_crossover": True},
                indicator_snapshot=snapshot,
            )
        return SignalResult(
            action=SignalAction.HOLD,
            reason={"kc_upper_crossover": kc_break, "bb_upper_crossover": bb_break},
            indicator_snapshot=snapshot,
        )


if __name__ == "__main__":
    from engine.config import ENGINE_ROOT, ensure_runtime_dirs, load_config
    from engine.logger import setup_logger
    from engine.market_data import fetch_ohlcv

    ensure_runtime_dirs()
    cfg = load_config()
    logger = setup_logger(ENGINE_ROOT / "logs", "INFO")

    btc = fetch_ohlcv("KRW-BTC", interval="day", count=100)
    print(f"BTC {len(btc)} bars, 오늘 close={btc['close'].iloc[-1]:,.0f}")

    strat_d = StrategyD(
        keltner_window=cfg.strategy_d.keltner_window,
        keltner_atr_mult=cfg.strategy_d.keltner_atr_mult,
        atr_window=cfg.strategy_d.atr_window,
        bollinger_window=cfg.strategy_d.bollinger_window,
        bollinger_sigma=cfg.strategy_d.bollinger_sigma,
        sl_hard=cfg.strategy_d.sl_hard,
    )

    # No position
    result_flat = strat_d.compute_signal(btc, in_position=False)
    print(f"\n[No position] action={result_flat.action.value}, reason={result_flat.reason}")
    print(f"  snapshot: close={result_flat.indicator_snapshot['close']:,.0f}, "
          f"kc_upper={result_flat.indicator_snapshot['kc_upper_today']:,.0f}, "
          f"bb_upper={result_flat.indicator_snapshot['bb_upper_today']:,.0f}")

    # In position (가짜 entry = 현재보다 10% 높음 → SL 터치 가능)
    fake_entry = btc["close"].iloc[-1] * 1.1
    result_in = strat_d.compute_signal(btc, in_position=True, entry_price_krw=fake_entry)
    print(f"\n[In position, entry={fake_entry:,.0f}] action={result_in.action.value}")

    logger.info("strategy_d_sanity_ok", extra={"today_action": result_flat.action.value})
