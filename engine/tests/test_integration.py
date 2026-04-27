"""Integration tests — main.py Engine + sync_open_orders + has_pending_order."""
from __future__ import annotations

from datetime import datetime, timezone
from unittest.mock import patch

import pytest

from engine.config import load_config
from engine.main import Engine
from engine.state import OrderRecord


@pytest.fixture
def engine_paper(tmp_path, monkeypatch):
    """격리된 paper-mode Engine 인스턴스. notifier는 mock으로 비활성화 (테스트 환경 격리)."""
    cfg = load_config()
    cfg.run_mode = "paper"
    cfg.state["db_path"] = str(tmp_path / "test_state.sqlite")
    # 테스트에서 실제 사용자 Keychain에 webhook이 있어도 비활성화 (테스트 격리)
    cfg.keychain.discord_webhook_service = "nonexistent-webhook-for-tests"

    monkeypatch.setattr("engine.main.ENGINE_ROOT", tmp_path)
    monkeypatch.setattr("engine.config.ENGINE_ROOT", tmp_path)
    (tmp_path / "logs").mkdir(exist_ok=True)
    (tmp_path / "data").mkdir(exist_ok=True)

    return Engine(cfg)


class TestEngineInit:
    def test_engine_init_paper_mode(self, engine_paper):
        assert engine_paper.cfg.run_mode == "paper"
        # V2-06 (BT-A/D 3) + V2-Strategy-G (G 30) = 33 cells
        assert len(engine_paper.strategies) >= 3
        assert "KRW-BTC_A" in engine_paper.strategies
        assert "KRW-ETH_A" in engine_paper.strategies
        assert "KRW-BTC_D" in engine_paper.strategies

    def test_engine_init_no_webhook_disables_notifier(self, engine_paper):
        assert engine_paper.notifier is None  # Keychain webhook 미발급 시


class TestPendingGuard:
    """C-2 정정: 동일 cell pending order 시 신규 발행 차단."""

    def test_no_pending_initially(self, engine_paper):
        assert engine_paper.has_pending_order("KRW-BTC_A", "buy") is False

    def test_pending_after_open_inject(self, engine_paper):
        now = datetime.now(timezone.utc).isoformat()
        engine_paper.state.record_order(OrderRecord(
            order_uuid="open-buy-1", client_oid="oid-1",
            cell_key="KRW-BTC_A", pair="KRW-BTC", strategy="A",
            side="buy", order_type="market", status="open",
            requested_krw=100_000,
            requested_ts_utc=now, updated_ts_utc=now,
        ))
        assert engine_paper.has_pending_order("KRW-BTC_A", "buy") is True
        assert engine_paper.has_pending_order("KRW-BTC_A", "sell") is False
        assert engine_paper.has_pending_order("KRW-ETH_A", "buy") is False  # 다른 cell


class TestSyncOpenOrders:
    """C-1 정정: open buy → filled 전이 시 자동 open_position."""

    def test_sync_no_open_orders(self, engine_paper):
        counts = engine_paper.sync_open_orders()
        assert counts["polled"] == 0
        assert counts["promoted_buy"] == 0
        assert counts["promoted_sell"] == 0

    def test_sync_filled_buy_promotes_to_position(self, engine_paper):
        """live mode 시뮬: open buy 주입 → poll_status가 filled 응답 → open_position 자동 호출."""
        # paper mode이므로 poll_status는 state DB 그대로 → filled로 미리 전환 후 직접 호출 검증

        # 1. open buy 주입
        now = datetime.now(timezone.utc).isoformat()
        engine_paper.state.record_order(OrderRecord(
            order_uuid="buy-uuid-1", client_oid="oid-1",
            cell_key="KRW-BTC_A", pair="KRW-BTC", strategy="A",
            side="buy", order_type="market", status="open",
            requested_krw=100_000,
            requested_ts_utc=now, updated_ts_utc=now,
        ))
        assert engine_paper.state.get_position("KRW-BTC_A") is None

        # 2. order_executor.poll_status를 mock하여 filled 응답하도록
        def fake_poll(uuid):
            rec = engine_paper.state.get_order(uuid)
            if rec is None:
                return None
            rec.status = "filled"
            rec.filled_volume = 0.0008648
            rec.filled_price_krw = 115_573_000
            rec.fees_krw = 50
            rec.updated_ts_utc = now
            engine_paper.state.record_order(rec)
            return rec
        engine_paper.order_executor.poll_status = fake_poll

        # 3. sync_open_orders 호출
        counts = engine_paper.sync_open_orders()
        assert counts["polled"] == 1
        assert counts["promoted_buy"] == 1

        # 4. 검증: position 생성됨
        pos = engine_paper.state.get_position("KRW-BTC_A")
        assert pos is not None
        assert pos.entry_price_krw == 115_573_000

    def test_sync_filled_sell_closes_position(self, engine_paper, tmp_path):
        # 1. 먼저 position 만들기
        from engine.position import open_position_from_order
        now = datetime.now(timezone.utc).isoformat()
        buy = OrderRecord(
            order_uuid="buy-prep", client_oid="o1",
            cell_key="KRW-BTC_A", pair="KRW-BTC", strategy="A",
            side="buy", order_type="market", status="filled",
            requested_krw=100_050, filled_volume=0.001, filled_price_krw=100_000_000, fees_krw=50,
            requested_ts_utc=now, updated_ts_utc=now,
        )
        engine_paper.state.record_order(buy)
        open_position_from_order(engine_paper.state, buy)

        # 2. open sell 주입
        engine_paper.state.record_order(OrderRecord(
            order_uuid="sell-uuid-1", client_oid="oid-sell-1",
            cell_key="KRW-BTC_A", pair="KRW-BTC", strategy="A",
            side="sell", order_type="market", status="open",
            requested_krw=110_000, requested_volume=0.001,
            requested_ts_utc=now, updated_ts_utc=now,
        ))

        # 3. poll_status mock: sell이 filled로 응답
        def fake_poll(uuid):
            rec = engine_paper.state.get_order(uuid)
            if rec is None or rec.status != "open":
                return rec
            rec.status = "filled"
            rec.filled_volume = 0.001
            rec.filled_price_krw = 110_000_000
            rec.fees_krw = 55
            rec.updated_ts_utc = now
            engine_paper.state.record_order(rec)
            return rec
        engine_paper.order_executor.poll_status = fake_poll

        counts = engine_paper.sync_open_orders()
        assert counts["promoted_sell"] == 1
        assert engine_paper.state.get_position("KRW-BTC_A") is None  # 종료됨


class TestRunCycleIntegration:
    """main.py run_cycle 1회 실행 — strategy hold 시나리오 (mock fetch_ohlcv)."""

    def test_run_cycle_hold_no_orders(self, engine_paper, monkeypatch):
        # market_data.fetch_ohlcv mock
        import pandas as pd
        import numpy as np
        n = 300
        np.random.seed(0)
        df = pd.DataFrame(
            {"open": [100.0] * n, "high": [101.0] * n, "low": [99.0] * n,
             "close": [100.0] * n, "volume": [1000.0] * n, "value": [100_000.0] * n},
            index=pd.date_range("2025-01-01", periods=n, freq="D", tz="UTC"),
        )
        monkeypatch.setattr("engine.main.fetch_ohlcv", lambda *a, **k: df)
        monkeypatch.setattr("engine.main.get_current_price", lambda p: 100.0)

        trigger = datetime.now(timezone.utc)
        engine_paper.run_cycle(trigger)

        # 평탄한 데이터 → 모든 cell hold → 0 주문 / 0 포지션
        assert len(engine_paper.state.list_open_positions()) == 0
        # last_run_ts 박제
        assert engine_paper.state.get_meta("last_run_ts") is not None
