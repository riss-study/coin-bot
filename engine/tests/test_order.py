"""order.py — paper + live mock + 멱등성."""
from __future__ import annotations

from datetime import datetime, timezone
from unittest.mock import MagicMock

import pytest

from engine.order import OrderExecutor, OrderRequest, make_client_oid, _safe_float


class TestMakeClientOid:
    def test_deterministic_same_minute(self):
        ts = datetime(2026, 4, 26, 0, 5, 0, tzinfo=timezone.utc)
        a = make_client_oid("KRW-BTC_A", "buy", ts)
        b = make_client_oid("KRW-BTC_A", "buy", ts)
        assert a == b
        assert "KRW-BTC_A_buy_202604260005" == a

    def test_different_minute_different_oid(self):
        a = make_client_oid("KRW-BTC_A", "buy", datetime(2026, 4, 26, 0, 5, tzinfo=timezone.utc))
        b = make_client_oid("KRW-BTC_A", "buy", datetime(2026, 4, 26, 0, 6, tzinfo=timezone.utc))
        assert a != b

    def test_different_side_different_oid(self):
        ts = datetime(2026, 4, 26, 0, 5, tzinfo=timezone.utc)
        assert make_client_oid("X", "buy", ts) != make_client_oid("X", "sell", ts)


class TestSafeFloat:
    def test_none(self):
        assert _safe_float(None) is None
        assert _safe_float("") is None
        assert _safe_float("not_a_number") is None

    def test_numeric(self):
        assert _safe_float("1.5") == 1.5
        assert _safe_float(2) == 2.0
        assert _safe_float(0.0008) == 0.0008


class TestPaperBuy:
    def test_paper_buy_filled(self, tmp_state):
        executor = OrderExecutor(
            state=tmp_state, run_mode="paper",
            price_oracle=lambda pair: 100_000_000.0,
        )
        req = OrderRequest(
            cell_key="KRW-BTC_A", pair="KRW-BTC", strategy="A",
            side="buy", order_type="market", krw_amount=100_000,
        )
        rec = executor.place_order(req)
        assert rec.status == "filled"
        assert rec.filled_price_krw == 100_000_000
        assert rec.fees_krw == pytest.approx(50.0)  # 100,000 × 0.0005
        assert rec.filled_volume == pytest.approx((100_000 - 50) / 100_000_000)

    def test_paper_idempotency(self, tmp_state):
        executor = OrderExecutor(
            state=tmp_state, run_mode="paper",
            price_oracle=lambda pair: 100_000_000.0,
        )
        oid = make_client_oid("KRW-BTC_A", "buy", datetime(2026, 4, 26, 0, 5, tzinfo=timezone.utc))
        req = OrderRequest(
            cell_key="KRW-BTC_A", pair="KRW-BTC", strategy="A",
            side="buy", order_type="market", krw_amount=100_000, client_oid=oid,
        )
        rec1 = executor.place_order(req)
        rec2 = executor.place_order(req)
        assert rec1.order_uuid == rec2.order_uuid  # 동일 oid → 동일 record

    def test_paper_buy_zero_amount_rejected(self, tmp_state):
        executor = OrderExecutor(
            state=tmp_state, run_mode="paper",
            price_oracle=lambda pair: 100_000_000.0,
        )
        with pytest.raises(ValueError, match="krw_amount"):
            executor.place_order(OrderRequest(
                cell_key="X", pair="P", strategy="A",
                side="buy", order_type="market", krw_amount=0,
            ))


class TestPaperSell:
    def test_paper_sell_filled(self, tmp_state):
        executor = OrderExecutor(
            state=tmp_state, run_mode="paper",
            price_oracle=lambda pair: 110_000_000.0,
        )
        req = OrderRequest(
            cell_key="KRW-BTC_A", pair="KRW-BTC", strategy="A",
            side="sell", order_type="market", volume=0.001,
        )
        rec = executor.place_order(req)
        assert rec.status == "filled"
        assert rec.filled_volume == 0.001
        # gross = 0.001 × 110,000,000 = 110,000. fees = 55. net 109,945
        assert rec.fees_krw == pytest.approx(55.0)


class TestLiveModeValidation:
    def test_live_requires_client(self, tmp_state):
        with pytest.raises(ValueError, match="upbit_client"):
            OrderExecutor(state=tmp_state, run_mode="live")

    def test_invalid_run_mode(self, tmp_state):
        with pytest.raises(ValueError, match="run_mode"):
            OrderExecutor(state=tmp_state, run_mode="invalid")


class TestLiveMockBuy:
    def test_live_buy_filled(self, tmp_state):
        mock_upbit = MagicMock()
        mock_upbit.buy_market_order.return_value = {
            "uuid": "live-uuid-1",
            "side": "bid", "ord_type": "price",
            "state": "done",
            "executed_volume": "0.0008648",
            "avg_price": "115573000",
            "paid_fee": "50.0",
        }
        executor = OrderExecutor(
            state=tmp_state, run_mode="live", upbit_client=mock_upbit,
        )
        rec = executor.place_order(OrderRequest(
            cell_key="KRW-BTC_A", pair="KRW-BTC", strategy="A",
            side="buy", order_type="market", krw_amount=100_000,
        ))
        assert rec.status == "filled"
        assert rec.order_uuid == "live-uuid-1"
        assert rec.filled_volume == pytest.approx(0.0008648)
        assert rec.filled_price_krw == 115_573_000
        assert rec.fees_krw == 50.0
        mock_upbit.buy_market_order.assert_called_once_with("KRW-BTC", 100_000)

    def test_live_buy_response_open_then_polled_filled(self, tmp_state, monkeypatch):
        """주문 직후 응답 status='wait', 폴링 시 'done'으로 전이 — _immediate_poll 작동 검증."""
        mock_upbit = MagicMock()
        mock_upbit.buy_market_order.return_value = {
            "uuid": "live-uuid-2",
            "state": "wait",
            "executed_volume": None,
            "avg_price": None,
            "paid_fee": None,
        }
        mock_upbit.get_order.return_value = {
            "uuid": "live-uuid-2",
            "state": "done",
            "executed_volume": "0.001",
            "avg_price": "115000000",
            "paid_fee": "57.5",
        }
        executor = OrderExecutor(
            state=tmp_state, run_mode="live", upbit_client=mock_upbit,
        )
        # _immediate_poll 의 sleep을 0초로 패치 (테스트 속도)
        monkeypatch.setattr("engine.order.time.sleep", lambda s: None)
        rec = executor.place_order(OrderRequest(
            cell_key="KRW-BTC_A", pair="KRW-BTC", strategy="A",
            side="buy", order_type="market", krw_amount=100_000,
        ))
        assert rec.status == "filled"
        assert rec.filled_volume == 0.001
        assert mock_upbit.get_order.called

    def test_live_buy_error_response(self, tmp_state, monkeypatch):
        mock_upbit = MagicMock()
        mock_upbit.buy_market_order.return_value = {"error": {"message": "insufficient balance"}}
        executor = OrderExecutor(
            state=tmp_state, run_mode="live", upbit_client=mock_upbit,
        )
        monkeypatch.setattr("engine.order.time.sleep", lambda s: None)
        with pytest.raises(RuntimeError, match="place_live failed"):
            executor.place_order(OrderRequest(
                cell_key="X", pair="P", strategy="A",
                side="buy", order_type="market", krw_amount=100_000,
            ))


class TestCancel:
    def test_paper_cancel_returns_false(self, tmp_state):
        executor = OrderExecutor(
            state=tmp_state, run_mode="paper",
            price_oracle=lambda pair: 1.0,
        )
        # paper는 즉시 filled이므로 cancel 의미 없음 → False 반환
        assert executor.cancel("any-uuid") is False

    def test_live_cancel(self, tmp_state):
        mock_upbit = MagicMock()
        mock_upbit.cancel_order.return_value = {"uuid": "u1", "state": "cancel"}
        executor = OrderExecutor(state=tmp_state, run_mode="live", upbit_client=mock_upbit)
        assert executor.cancel("u1") is True
        mock_upbit.cancel_order.assert_called_once_with("u1")
