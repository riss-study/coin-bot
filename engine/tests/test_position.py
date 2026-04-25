"""position.py — Position open/close + PnL + 세금 데이터."""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

import pytest

from engine.position import (
    PnL,
    close_position_from_order,
    compute_unrealized_pnl,
    open_position_from_order,
)
from engine.state import OrderRecord


def _filled_buy(price: float = 100_000_000, volume: float = 0.001, fees: float = 50) -> OrderRecord:
    now = datetime.now(timezone.utc).isoformat()
    return OrderRecord(
        order_uuid="buy-u1", client_oid="buy-o1",
        cell_key="KRW-BTC_A", pair="KRW-BTC", strategy="A",
        side="buy", order_type="market", status="filled",
        requested_krw=price * volume + fees, requested_volume=None,
        filled_volume=volume, filled_price_krw=price, fees_krw=fees,
        requested_ts_utc=now, updated_ts_utc=now,
    )


def _filled_sell(price: float = 110_000_000, volume: float = 0.001, fees: float = 55) -> OrderRecord:
    now = datetime.now(timezone.utc).isoformat()
    return OrderRecord(
        order_uuid="sell-u1", client_oid="sell-o1",
        cell_key="KRW-BTC_A", pair="KRW-BTC", strategy="A",
        side="sell", order_type="market", status="filled",
        requested_krw=price * volume, requested_volume=volume,
        filled_volume=volume, filled_price_krw=price, fees_krw=fees,
        requested_ts_utc=now, updated_ts_utc=now,
    )


class TestOpenPosition:
    def test_open_from_filled_buy(self, tmp_state):
        order = _filled_buy()
        tmp_state.record_order(order)
        pos = open_position_from_order(tmp_state, order)
        assert pos.cell_key == "KRW-BTC_A"
        assert pos.entry_price_krw == 100_000_000
        assert pos.volume == 0.001
        # krw_invested = volume × price + fees = 100,000 + 50 = 100,050
        assert pos.krw_invested == pytest.approx(100_050.0)

    def test_open_rejects_sell(self, tmp_state):
        sell = _filled_sell()
        with pytest.raises(ValueError, match="buy order"):
            open_position_from_order(tmp_state, sell)

    def test_open_rejects_unfilled(self, tmp_state):
        order = _filled_buy()
        order.status = "open"
        with pytest.raises(ValueError, match="filled"):
            open_position_from_order(tmp_state, order)


class TestComputeUnrealized:
    def test_profit(self, tmp_state):
        buy = _filled_buy(price=100_000_000, volume=0.001, fees=50)
        tmp_state.record_order(buy)
        pos = open_position_from_order(tmp_state, buy)
        # 현재가 110_000_000 (10% 상승)
        pnl: PnL = compute_unrealized_pnl(pos, current_price_krw=110_000_000)
        # market_value = 0.001 × 110,000,000 = 110,000
        # unrealized = 110,000 - 100,050 = 9,950
        assert pnl.unrealized_pnl_krw == pytest.approx(9_950.0)
        assert pnl.unrealized_pnl_pct == pytest.approx(9_950 / 100_050)

    def test_loss(self, tmp_state):
        buy = _filled_buy(price=100_000_000, volume=0.001, fees=50)
        tmp_state.record_order(buy)
        pos = open_position_from_order(tmp_state, buy)
        pnl = compute_unrealized_pnl(pos, current_price_krw=90_000_000)
        # market = 90,000, unrealized = 90,000 - 100,050 = -10,050
        assert pnl.unrealized_pnl_krw == pytest.approx(-10_050.0)


class TestClosePosition:
    def test_close_realized_pnl(self, tmp_state, tmp_path):
        buy = _filled_buy(price=100_000_000, volume=0.001, fees=50)
        tmp_state.record_order(buy)
        open_position_from_order(tmp_state, buy)

        sell = _filled_sell(price=110_000_000, volume=0.001, fees=55)
        tmp_state.record_order(sell)

        result = close_position_from_order(tmp_state, tmp_path, sell, run_mode="paper")
        # gross = 110,000, exit_fees=55, krw_invested=100,050
        # realized = 110,000 - 55 - 100,050 = 9,895
        assert result["realized_pnl_krw"] == pytest.approx(9_895.0)
        assert result["entry_fees_krw"] == 50.0
        assert result["exit_fees_krw"] == 55.0

    def test_close_writes_tax_records(self, tmp_state, tmp_path):
        """trades-YYYY.jsonl 에 entry + exit 두 행 기록되는지 검증 (CLAUDE.md 박제: 세금 데이터)."""
        buy = _filled_buy()
        tmp_state.record_order(buy)
        open_position_from_order(tmp_state, buy)
        sell = _filled_sell()
        tmp_state.record_order(sell)
        close_position_from_order(tmp_state, tmp_path, sell, run_mode="paper")

        year = datetime.now(timezone.utc).strftime("%Y")
        trades_file = tmp_path / f"trades-{year}.jsonl"
        assert trades_file.exists()
        lines = trades_file.read_text().strip().split("\n")
        assert len(lines) == 2  # buy + sell

        entry = json.loads(lines[0])
        exit_ = json.loads(lines[1])
        assert entry["side"] == "buy"
        assert exit_["side"] == "sell"
        assert "realized_pnl_krw" in exit_
        assert exit_["entry_price_krw"] == 100_000_000

    def test_close_position_removes_state(self, tmp_state, tmp_path):
        buy = _filled_buy()
        tmp_state.record_order(buy)
        open_position_from_order(tmp_state, buy)
        sell = _filled_sell()
        tmp_state.record_order(sell)
        close_position_from_order(tmp_state, tmp_path, sell, run_mode="paper")
        assert tmp_state.get_position("KRW-BTC_A") is None

    def test_close_without_open_raises(self, tmp_state, tmp_path):
        sell = _filled_sell()
        tmp_state.record_order(sell)
        with pytest.raises(RuntimeError, match="no open position"):
            close_position_from_order(tmp_state, tmp_path, sell)

    def test_close_rejects_buy_order(self, tmp_state, tmp_path):
        buy = _filled_buy()
        with pytest.raises(ValueError, match="sell order"):
            close_position_from_order(tmp_state, tmp_path, buy)
