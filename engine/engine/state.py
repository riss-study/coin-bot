"""SQLite 상태 DB + 재시작 복원 + 멱등성 지원.

박제 출처:
- docs/stage1-v2-relaunch.md §2.4 state.py
- §2.5 숨은 복잡도 #1 (재시작 복원), #4 (멱등성)

설계:
- SQLite 단일 파일 (data/state.sqlite)
- 테이블:
  - `positions`: 열려 있는 포지션 (cell별, FK to orders)
  - `orders`: 모든 주문 기록 (open / filled / canceled / rejected)
  - `idempotency`: client_oid → order_uuid 매핑 (재시도 시 이중 주문 방지)
  - `meta`: 단일 key-value (last_run_ts 등)
- ACID: SQLite WAL 모드 (concurrent read 허용)
- 재시작 시 open orders + 포지션 복원
"""
from __future__ import annotations

import json
import sqlite3
import threading
from contextlib import contextmanager
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterator


@dataclass
class Position:
    cell_key: str              # 예 "KRW-BTC_A"
    pair: str
    strategy: str
    entry_ts_utc: str
    entry_price_krw: float
    volume: float              # 코인 보유량
    krw_invested: float        # 매수 시점 투자 KRW
    order_uuid: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class OrderRecord:
    order_uuid: str
    client_oid: str
    cell_key: str
    pair: str
    strategy: str
    side: str                  # "buy" | "sell"
    order_type: str            # "market" | "limit"
    status: str                # "open" | "filled" | "canceled" | "rejected" | "failed"
    requested_krw: float       # 요청 KRW (buy) or 요청 volume×price (sell)
    requested_volume: float | None = None
    filled_volume: float | None = None
    filled_price_krw: float | None = None
    fees_krw: float | None = None
    requested_ts_utc: str = ""
    updated_ts_utc: str = ""
    metadata: dict[str, Any] = field(default_factory=dict)


_SCHEMA = """
CREATE TABLE IF NOT EXISTS meta (
    key TEXT PRIMARY KEY,
    value TEXT NOT NULL,
    updated_ts_utc TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS positions (
    cell_key TEXT PRIMARY KEY,
    pair TEXT NOT NULL,
    strategy TEXT NOT NULL,
    entry_ts_utc TEXT NOT NULL,
    entry_price_krw REAL NOT NULL,
    volume REAL NOT NULL,
    krw_invested REAL NOT NULL,
    order_uuid TEXT,
    metadata_json TEXT NOT NULL DEFAULT '{}'
);

CREATE TABLE IF NOT EXISTS orders (
    order_uuid TEXT PRIMARY KEY,
    client_oid TEXT NOT NULL,
    cell_key TEXT NOT NULL,
    pair TEXT NOT NULL,
    strategy TEXT NOT NULL,
    side TEXT NOT NULL,
    order_type TEXT NOT NULL,
    status TEXT NOT NULL,
    requested_krw REAL NOT NULL,
    requested_volume REAL,
    filled_volume REAL,
    filled_price_krw REAL,
    fees_krw REAL,
    requested_ts_utc TEXT NOT NULL,
    updated_ts_utc TEXT NOT NULL,
    metadata_json TEXT NOT NULL DEFAULT '{}'
);

CREATE INDEX IF NOT EXISTS idx_orders_cell_status ON orders(cell_key, status);
CREATE INDEX IF NOT EXISTS idx_orders_client_oid ON orders(client_oid);

CREATE TABLE IF NOT EXISTS idempotency (
    client_oid TEXT PRIMARY KEY,
    order_uuid TEXT NOT NULL,
    created_ts_utc TEXT NOT NULL,
    FOREIGN KEY(order_uuid) REFERENCES orders(order_uuid)
);
"""


class StateStore:
    """SQLite 기반 봇 상태 저장소. Thread-safe."""

    def __init__(self, db_path: Path):
        self.db_path = db_path
        db_path.parent.mkdir(parents=True, exist_ok=True)
        self._lock = threading.RLock()
        self._init_schema()

    def _init_schema(self) -> None:
        # executescript는 자체 transaction을 관리하므로 BEGIN IMMEDIATE 없이 독립 연결 사용
        conn = sqlite3.connect(self.db_path, isolation_level=None, timeout=30)
        try:
            conn.execute("PRAGMA journal_mode=WAL")
            conn.execute("PRAGMA synchronous=NORMAL")
            conn.executescript(_SCHEMA)
        finally:
            conn.close()

    @contextmanager
    def _conn(self, *, write: bool = True) -> Iterator[sqlite3.Connection]:
        """컨텍스트 매니저. write=True → BEGIN IMMEDIATE (writer lock 즉시 획득).

        W-1 정정 (2026-04-24): read-only 쿼리는 write=False → DEFERRED (read lock만).
        WAL 모드에서 concurrent read 허용 = 3 cell 병렬 처리 시 lock contention 감소.
        """
        with self._lock:
            conn = sqlite3.connect(self.db_path, isolation_level=None, timeout=30)
            conn.row_factory = sqlite3.Row
            try:
                conn.execute("BEGIN IMMEDIATE" if write else "BEGIN DEFERRED")
                yield conn
                conn.execute("COMMIT")
            except Exception:
                conn.execute("ROLLBACK")
                raise
            finally:
                conn.close()

    # ---------- Meta ----------

    def set_meta(self, key: str, value: str) -> None:
        ts = datetime.now(timezone.utc).isoformat()
        with self._conn() as c:
            c.execute(
                "INSERT INTO meta (key, value, updated_ts_utc) VALUES (?, ?, ?) "
                "ON CONFLICT(key) DO UPDATE SET value=excluded.value, updated_ts_utc=excluded.updated_ts_utc",
                (key, value, ts),
            )

    def get_meta(self, key: str, default: str | None = None) -> str | None:
        with self._conn(write=False) as c:
            row = c.execute("SELECT value FROM meta WHERE key=?", (key,)).fetchone()
        return row["value"] if row else default

    # ---------- Positions ----------

    def upsert_position(self, pos: Position) -> None:
        with self._conn() as c:
            c.execute(
                "INSERT INTO positions (cell_key, pair, strategy, entry_ts_utc, entry_price_krw, "
                "volume, krw_invested, order_uuid, metadata_json) "
                "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?) "
                "ON CONFLICT(cell_key) DO UPDATE SET "
                "pair=excluded.pair, strategy=excluded.strategy, entry_ts_utc=excluded.entry_ts_utc, "
                "entry_price_krw=excluded.entry_price_krw, volume=excluded.volume, "
                "krw_invested=excluded.krw_invested, order_uuid=excluded.order_uuid, "
                "metadata_json=excluded.metadata_json",
                (
                    pos.cell_key, pos.pair, pos.strategy, pos.entry_ts_utc,
                    pos.entry_price_krw, pos.volume, pos.krw_invested, pos.order_uuid,
                    json.dumps(pos.metadata, ensure_ascii=False),
                ),
            )

    def close_position(self, cell_key: str) -> None:
        """포지션 DELETE (positions 테이블만).

        W-5 고지 (2026-04-24): 연관 exit 주문의 status='filled' 업데이트는
        **호출자 책임**. 일반적 순서:
            1. order.py에서 exit 체결 확인
            2. store.record_order(...) status='filled' 업데이트 (멱등)
            3. store.close_position(cell_key)
        이 순서를 어기면 position 사라졌는데 order 상태 stale할 수 있음.
        """
        with self._conn() as c:
            c.execute("DELETE FROM positions WHERE cell_key=?", (cell_key,))

    def get_position(self, cell_key: str) -> Position | None:
        with self._conn(write=False) as c:
            row = c.execute("SELECT * FROM positions WHERE cell_key=?", (cell_key,)).fetchone()
        if row is None:
            return None
        return Position(
            cell_key=row["cell_key"], pair=row["pair"], strategy=row["strategy"],
            entry_ts_utc=row["entry_ts_utc"], entry_price_krw=row["entry_price_krw"],
            volume=row["volume"], krw_invested=row["krw_invested"],
            order_uuid=row["order_uuid"],
            metadata=json.loads(row["metadata_json"]),
        )

    def list_open_positions(self) -> list[Position]:
        with self._conn(write=False) as c:
            rows = c.execute("SELECT * FROM positions").fetchall()
        return [
            Position(
                cell_key=r["cell_key"], pair=r["pair"], strategy=r["strategy"],
                entry_ts_utc=r["entry_ts_utc"], entry_price_krw=r["entry_price_krw"],
                volume=r["volume"], krw_invested=r["krw_invested"],
                order_uuid=r["order_uuid"], metadata=json.loads(r["metadata_json"]),
            )
            for r in rows
        ]

    # ---------- Orders ----------

    def record_order(self, order: OrderRecord) -> None:
        now = datetime.now(timezone.utc).isoformat()
        if not order.requested_ts_utc:
            order.requested_ts_utc = now
        order.updated_ts_utc = now
        with self._conn() as c:
            c.execute(
                "INSERT INTO orders (order_uuid, client_oid, cell_key, pair, strategy, side, "
                "order_type, status, requested_krw, requested_volume, filled_volume, "
                "filled_price_krw, fees_krw, requested_ts_utc, updated_ts_utc, metadata_json) "
                "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?) "
                "ON CONFLICT(order_uuid) DO UPDATE SET "
                "status=excluded.status, filled_volume=excluded.filled_volume, "
                "filled_price_krw=excluded.filled_price_krw, fees_krw=excluded.fees_krw, "
                "updated_ts_utc=excluded.updated_ts_utc, metadata_json=excluded.metadata_json",
                (
                    order.order_uuid, order.client_oid, order.cell_key, order.pair, order.strategy,
                    order.side, order.order_type, order.status,
                    order.requested_krw, order.requested_volume,
                    order.filled_volume, order.filled_price_krw, order.fees_krw,
                    order.requested_ts_utc, order.updated_ts_utc,
                    json.dumps(order.metadata, ensure_ascii=False),
                ),
            )

    def get_order(self, order_uuid: str) -> OrderRecord | None:
        with self._conn(write=False) as c:
            row = c.execute("SELECT * FROM orders WHERE order_uuid=?", (order_uuid,)).fetchone()
        if row is None:
            return None
        return OrderRecord(
            order_uuid=row["order_uuid"], client_oid=row["client_oid"],
            cell_key=row["cell_key"], pair=row["pair"], strategy=row["strategy"],
            side=row["side"], order_type=row["order_type"], status=row["status"],
            requested_krw=row["requested_krw"], requested_volume=row["requested_volume"],
            filled_volume=row["filled_volume"], filled_price_krw=row["filled_price_krw"],
            fees_krw=row["fees_krw"],
            requested_ts_utc=row["requested_ts_utc"], updated_ts_utc=row["updated_ts_utc"],
            metadata=json.loads(row["metadata_json"]),
        )

    def list_open_orders(self) -> list[OrderRecord]:
        """status='open' 주문 — 재시작 시 Upbit API와 대조해 상태 동기화."""
        with self._conn(write=False) as c:
            rows = c.execute("SELECT * FROM orders WHERE status='open'").fetchall()
        return [
            OrderRecord(
                order_uuid=r["order_uuid"], client_oid=r["client_oid"],
                cell_key=r["cell_key"], pair=r["pair"], strategy=r["strategy"],
                side=r["side"], order_type=r["order_type"], status=r["status"],
                requested_krw=r["requested_krw"], requested_volume=r["requested_volume"],
                filled_volume=r["filled_volume"], filled_price_krw=r["filled_price_krw"],
                fees_krw=r["fees_krw"],
                requested_ts_utc=r["requested_ts_utc"], updated_ts_utc=r["updated_ts_utc"],
                metadata=json.loads(r["metadata_json"]),
            )
            for r in rows
        ]

    # ---------- Idempotency ----------

    def get_order_uuid_by_client_oid(self, client_oid: str) -> str | None:
        """client_oid → order_uuid 매핑 조회 (재시도 시 이중 주문 방지)."""
        with self._conn(write=False) as c:
            row = c.execute(
                "SELECT order_uuid FROM idempotency WHERE client_oid=?", (client_oid,)
            ).fetchone()
        return row["order_uuid"] if row else None

    def register_idempotency(self, client_oid: str, order_uuid: str) -> None:
        ts = datetime.now(timezone.utc).isoformat()
        with self._conn() as c:
            c.execute(
                "INSERT INTO idempotency (client_oid, order_uuid, created_ts_utc) VALUES (?, ?, ?)",
                (client_oid, order_uuid, ts),
            )


if __name__ == "__main__":
    # V2-02 sanity check
    from engine.config import ENGINE_ROOT, ensure_runtime_dirs, load_config

    ensure_runtime_dirs()
    cfg = load_config()
    db_path = ENGINE_ROOT / cfg.state["db_path"]
    store = StateStore(db_path)

    # meta sanity
    store.set_meta("last_run_ts", datetime.now(timezone.utc).isoformat())
    print(f"last_run_ts: {store.get_meta('last_run_ts')}")

    # position sanity
    pos = Position(
        cell_key="KRW-BTC_A",
        pair="KRW-BTC", strategy="A",
        entry_ts_utc=datetime.now(timezone.utc).isoformat(),
        entry_price_krw=85_000_000, volume=0.001176, krw_invested=100_000,
        order_uuid="sanity-uuid",
    )
    store.upsert_position(pos)
    print(f"position: {store.get_position('KRW-BTC_A')}")

    # order sanity
    order = OrderRecord(
        order_uuid="sanity-uuid", client_oid="sanity-coid",
        cell_key="KRW-BTC_A", pair="KRW-BTC", strategy="A",
        side="buy", order_type="market", status="filled",
        requested_krw=100_000, filled_volume=0.001176,
        filled_price_krw=85_000_000, fees_krw=50,
    )
    store.record_order(order)
    store.register_idempotency("sanity-coid", "sanity-uuid")
    print(f"order: status={store.get_order('sanity-uuid').status}")
    print(f"idempotency lookup: {store.get_order_uuid_by_client_oid('sanity-coid')}")

    # 재시작 복원 sanity
    print(f"open positions: {len(store.list_open_positions())}")
    print(f"open orders: {len(store.list_open_orders())} (filled 제외)")

    # cleanup (sanity check 후 실제 DB에 데이터 남지 않도록)
    store.close_position("KRW-BTC_A")
    print(f"state.py sanity OK (DB: {db_path})")
