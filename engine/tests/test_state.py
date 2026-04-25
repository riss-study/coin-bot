"""state.py — Position / Order / idempotency / restart 시나리오."""
from __future__ import annotations

from datetime import datetime, timezone

from engine.state import OrderRecord, Position, StateStore


def _make_buy_order(uuid: str = "uuid-1", oid: str = "oid-1", status: str = "filled") -> OrderRecord:
    now = datetime.now(timezone.utc).isoformat()
    return OrderRecord(
        order_uuid=uuid, client_oid=oid,
        cell_key="KRW-BTC_A", pair="KRW-BTC", strategy="A",
        side="buy", order_type="market", status=status,
        requested_krw=100_000, requested_volume=None,
        filled_volume=0.0008648 if status == "filled" else None,
        filled_price_krw=115_573_000 if status == "filled" else None,
        fees_krw=50 if status == "filled" else None,
        requested_ts_utc=now, updated_ts_utc=now,
    )


class TestMeta:
    def test_set_and_get_meta(self, tmp_state: StateStore):
        tmp_state.set_meta("k1", "v1")
        assert tmp_state.get_meta("k1") == "v1"

    def test_get_meta_default(self, tmp_state: StateStore):
        assert tmp_state.get_meta("missing", "default") == "default"

    def test_meta_overwrite(self, tmp_state: StateStore):
        tmp_state.set_meta("k1", "v1")
        tmp_state.set_meta("k1", "v2")
        assert tmp_state.get_meta("k1") == "v2"


class TestPosition:
    def test_upsert_and_get(self, tmp_state: StateStore):
        pos = Position(
            cell_key="KRW-BTC_A", pair="KRW-BTC", strategy="A",
            entry_ts_utc=datetime.now(timezone.utc).isoformat(),
            entry_price_krw=115_000_000, volume=0.001, krw_invested=115_050,
            order_uuid="u1",
        )
        tmp_state.upsert_position(pos)
        loaded = tmp_state.get_position("KRW-BTC_A")
        assert loaded is not None
        assert loaded.entry_price_krw == 115_000_000

    def test_close(self, tmp_state: StateStore):
        pos = Position(cell_key="X", pair="KRW-BTC", strategy="A",
                       entry_ts_utc="2026-01-01", entry_price_krw=1, volume=1, krw_invested=1)
        tmp_state.upsert_position(pos)
        tmp_state.close_position("X")
        assert tmp_state.get_position("X") is None

    def test_list(self, tmp_state: StateStore):
        for i in range(3):
            tmp_state.upsert_position(Position(
                cell_key=f"X{i}", pair="P", strategy="A",
                entry_ts_utc="t", entry_price_krw=1, volume=1, krw_invested=1,
            ))
        assert len(tmp_state.list_open_positions()) == 3


class TestOrders:
    def test_record_and_get(self, tmp_state: StateStore):
        order = _make_buy_order()
        tmp_state.record_order(order)
        loaded = tmp_state.get_order("uuid-1")
        assert loaded is not None
        assert loaded.status == "filled"
        assert loaded.filled_price_krw == 115_573_000

    def test_record_upsert_status_update(self, tmp_state: StateStore):
        # open → filled 전이 (라이브 시나리오)
        open_ord = _make_buy_order(status="open")
        tmp_state.record_order(open_ord)
        assert tmp_state.get_order("uuid-1").status == "open"

        filled = _make_buy_order(status="filled")
        tmp_state.record_order(filled)
        assert tmp_state.get_order("uuid-1").status == "filled"

    def test_list_open_orders_filters(self, tmp_state: StateStore):
        tmp_state.record_order(_make_buy_order(uuid="u1", oid="o1", status="open"))
        tmp_state.record_order(_make_buy_order(uuid="u2", oid="o2", status="filled"))
        tmp_state.record_order(_make_buy_order(uuid="u3", oid="o3", status="canceled"))
        opens = tmp_state.list_open_orders()
        assert {o.order_uuid for o in opens} == {"u1"}


class TestIdempotency:
    def test_register_and_lookup(self, tmp_state: StateStore):
        tmp_state.record_order(_make_buy_order())
        tmp_state.register_idempotency("oid-1", "uuid-1")
        assert tmp_state.get_order_uuid_by_client_oid("oid-1") == "uuid-1"

    def test_lookup_missing(self, tmp_state: StateStore):
        assert tmp_state.get_order_uuid_by_client_oid("nope") is None


class TestRestart:
    def test_persist_across_instances(self, tmp_path):
        """프로세스 재시작 시 SQLite 파일 그대로 → state 복원 가능."""
        db = tmp_path / "restart.sqlite"
        s1 = StateStore(db)
        pos = Position(cell_key="C1", pair="KRW-BTC", strategy="A",
                       entry_ts_utc="t", entry_price_krw=1, volume=1, krw_invested=1)
        s1.upsert_position(pos)
        s1.record_order(_make_buy_order(status="open"))

        # 새 인스턴스 (재시작)
        s2 = StateStore(db)
        assert s2.get_position("C1") is not None
        assert len(s2.list_open_orders()) == 1
