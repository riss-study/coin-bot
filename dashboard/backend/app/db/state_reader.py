"""Engine state.sqlite read-only reader.

박제 출처:
- docs/stage1-subplans/v2-dashboard.md §3 (sqlite mode=ro 강제)
- CLAUDE.md "dashboard-backend는 거래소 API 키에 접근 권한 없음" + state DB read-only

설계:
- sqlite3.connect URI mode=ro 사용 → write 시도 시 OperationalError
- engine.state 모듈 import 금지 (의존성 분리)
- 결과는 dict 형태 반환 (dashboard 별도 dataclass 정의 시 추후)
"""
from __future__ import annotations

import json
import sqlite3
from contextlib import contextmanager
from pathlib import Path
from typing import Any, Iterator


def _connect_readonly(db_path: Path) -> sqlite3.Connection:
    """SQLite read-only 연결 (URI mode=ro 강제)."""
    if not db_path.exists():
        raise FileNotFoundError(f"state DB not found: {db_path}")
    uri = f"file:{db_path}?mode=ro"
    conn = sqlite3.connect(uri, uri=True, timeout=10)
    conn.row_factory = sqlite3.Row
    return conn


@contextmanager
def open_state(db_path: Path) -> Iterator[sqlite3.Connection]:
    conn = _connect_readonly(db_path)
    try:
        yield conn
    finally:
        conn.close()


def get_meta(db_path: Path, key: str) -> str | None:
    with open_state(db_path) as c:
        row = c.execute("SELECT value FROM meta WHERE key=?", (key,)).fetchone()
    return row["value"] if row else None


def list_open_positions(db_path: Path) -> list[dict[str, Any]]:
    with open_state(db_path) as c:
        rows = c.execute("SELECT * FROM positions").fetchall()
    return [_row_to_position(r) for r in rows]


def list_recent_orders(db_path: Path, limit: int = 50) -> list[dict[str, Any]]:
    with open_state(db_path) as c:
        rows = c.execute(
            "SELECT * FROM orders ORDER BY updated_ts_utc DESC LIMIT ?",
            (limit,),
        ).fetchall()
    return [_row_to_order(r) for r in rows]


def list_open_orders(db_path: Path) -> list[dict[str, Any]]:
    with open_state(db_path) as c:
        rows = c.execute("SELECT * FROM orders WHERE status='open'").fetchall()
    return [_row_to_order(r) for r in rows]


def _row_to_position(row: sqlite3.Row) -> dict[str, Any]:
    return {
        "cell_key": row["cell_key"],
        "pair": row["pair"],
        "strategy": row["strategy"],
        "entry_ts_utc": row["entry_ts_utc"],
        "entry_price_krw": row["entry_price_krw"],
        "volume": row["volume"],
        "krw_invested": row["krw_invested"],
        "order_uuid": row["order_uuid"],
        "metadata": json.loads(row["metadata_json"] or "{}"),
    }


def _row_to_order(row: sqlite3.Row) -> dict[str, Any]:
    return {
        "order_uuid": row["order_uuid"],
        "client_oid": row["client_oid"],
        "cell_key": row["cell_key"],
        "pair": row["pair"],
        "strategy": row["strategy"],
        "side": row["side"],
        "order_type": row["order_type"],
        "status": row["status"],
        "requested_krw": row["requested_krw"],
        "filled_volume": row["filled_volume"],
        "filled_price_krw": row["filled_price_krw"],
        "fees_krw": row["fees_krw"],
        "requested_ts_utc": row["requested_ts_utc"],
        "updated_ts_utc": row["updated_ts_utc"],
    }
