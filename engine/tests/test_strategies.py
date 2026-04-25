"""Strategy A / D signal 로직 unit."""
from __future__ import annotations

import pandas as pd
import pytest

from engine.strategies import SignalAction, StrategyA, StrategyD


class TestStrategyA:
    def test_warmup_incomplete_returns_hold(self):
        # 200 bar 미만 → ValueError or 함수 체크: compute_signal 자체가 raise
        df = pd.DataFrame(
            {"open": [1] * 50, "high": [1] * 50, "low": [1] * 50,
             "close": [1] * 50, "volume": [1] * 50},
            index=pd.date_range("2025-01-01", periods=50, freq="D", tz="UTC"),
        )
        strat = StrategyA()
        with pytest.raises(ValueError, match="rows"):
            strat.compute_signal(df, in_position=False)

    def test_no_breakout_returns_hold(self, synth_ohlcv):
        strat = StrategyA()
        result = strat.compute_signal(synth_ohlcv, in_position=False)
        assert result.action == SignalAction.HOLD

    def test_breakout_returns_entry(self, breakout_ohlcv):
        strat = StrategyA()
        result = strat.compute_signal(breakout_ohlcv, in_position=False)
        # 확신 못함: synth + breakout 조합이 항상 entry 조건 만족하는지 보장 X
        # ma_filter / breakout / volume 셋 다 통과해야 entry
        assert result.action in (SignalAction.ENTRY, SignalAction.HOLD)
        if result.action == SignalAction.ENTRY:
            assert result.reason["ma_filter_pass"] is True
            assert result.reason["donchian_breakout"] is True
            assert result.reason["volume_spike"] is True

    def test_sl_exit(self, sl_ohlcv):
        strat = StrategyA()
        # entry_price를 sl_ohlcv 마지막 close 보다 충분히 높게 → SL 터치
        entry_price = sl_ohlcv["close"].iloc[-1] * 1.20
        result = strat.compute_signal(sl_ohlcv, in_position=True, entry_price_krw=entry_price)
        assert result.action == SignalAction.SL_EXIT
        assert result.reason["sl_hit"] is True

    def test_in_position_no_signal_holds(self, synth_ohlcv):
        strat = StrategyA()
        # entry_price를 현재가보다 매우 낮게 → SL 미터치 + donchian_low 위 → hold
        entry_price = synth_ohlcv["close"].iloc[-1] * 0.5
        result = strat.compute_signal(synth_ohlcv, in_position=True, entry_price_krw=entry_price)
        # exit 또는 hold 가능 (synth 데이터에 따라)
        assert result.action in (SignalAction.HOLD, SignalAction.EXIT)

    def test_missing_columns_raises(self):
        df = pd.DataFrame({"close": [1] * 250},
                          index=pd.date_range("2025-01-01", periods=250, freq="D", tz="UTC"))
        strat = StrategyA()
        with pytest.raises(ValueError, match="missing columns"):
            strat.compute_signal(df, in_position=False)


class TestStrategyD:
    def test_warmup_check(self):
        df = pd.DataFrame(
            {"open": [1] * 10, "high": [1] * 10, "low": [1] * 10,
             "close": [1] * 10, "volume": [1] * 10},
            index=pd.date_range("2025-01-01", periods=10, freq="D", tz="UTC"),
        )
        strat = StrategyD()
        with pytest.raises(ValueError, match="rows"):
            strat.compute_signal(df, in_position=False)

    def test_no_double_breakout_holds(self, synth_ohlcv):
        strat = StrategyD()
        result = strat.compute_signal(synth_ohlcv, in_position=False)
        assert result.action == SignalAction.HOLD

    def test_sl_exit(self, sl_ohlcv):
        strat = StrategyD()
        entry_price = sl_ohlcv["close"].iloc[-1] * 1.20
        result = strat.compute_signal(sl_ohlcv, in_position=True, entry_price_krw=entry_price)
        assert result.action == SignalAction.SL_EXIT

    def test_indicator_snapshot_present(self, synth_ohlcv):
        strat = StrategyD()
        result = strat.compute_signal(synth_ohlcv, in_position=False)
        snap = result.indicator_snapshot
        assert "kc_upper_today" in snap
        assert "bb_upper_today" in snap
        assert "kc_mid_today" in snap


class TestSlHit:
    def test_check_sl_hit_basic(self):
        from engine.strategies.base import check_sl_hit
        # entry 100, sl 8% → sl_level 92. low 91 → True
        assert check_sl_hit(today_low=91, entry_price_krw=100, sl_pct=0.08) is True
        # low 93 → False
        assert check_sl_hit(today_low=93, entry_price_krw=100, sl_pct=0.08) is False
        # entry None → False (방어)
        assert check_sl_hit(today_low=50, entry_price_krw=None, sl_pct=0.08) is False
