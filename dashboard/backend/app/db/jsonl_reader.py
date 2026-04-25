"""JSONL 파일 read-only 파서 (trades / signals / engine logs).

박제 출처: docs/stage1-subplans/v2-dashboard.md §5

설계:
- 파일 미존재 시 빈 리스트 반환 (404 X, 정상 동작)
- 마지막 N줄 효율 읽기 (`tail` 패턴)
- ts_utc 필터링 지원 (since_utc 이후만)
"""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    """전체 JSONL 파싱 (소형 파일용)."""
    if not path.exists():
        return []
    rows: list[dict[str, Any]] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            rows.append(json.loads(line))
        except json.JSONDecodeError:
            continue
    return rows


def tail_jsonl(path: Path, n: int) -> list[dict[str, Any]]:
    """마지막 N줄만 파싱 (대형 로그 파일용 — 큰 파일도 메모리 절약).

    Note: 단순 read 후 [-n:] (Mac mini 24/7 운영 규모면 충분).
    """
    if not path.exists():
        return []
    lines = path.read_text(encoding="utf-8").splitlines()[-n:]
    rows: list[dict[str, Any]] = []
    for line in lines:
        line = line.strip()
        if not line:
            continue
        try:
            rows.append(json.loads(line))
        except json.JSONDecodeError:
            continue
    return rows


def filter_since(
    rows: list[dict[str, Any]],
    since_utc: datetime | None,
    ts_field: str = "ts_utc",
) -> list[dict[str, Any]]:
    """since_utc 이후 행만."""
    if since_utc is None:
        return rows
    out: list[dict[str, Any]] = []
    for r in rows:
        ts_str = r.get(ts_field)
        if not ts_str:
            continue
        try:
            ts = datetime.fromisoformat(ts_str)
            if ts.tzinfo is None:
                ts = ts.replace(tzinfo=timezone.utc)
        except (ValueError, TypeError):
            continue
        if ts >= since_utc:
            out.append(r)
    return out


def trades_path(logs_dir: Path, year: int | None = None) -> Path:
    if year is None:
        year = datetime.now(timezone.utc).year
    return logs_dir / f"trades-{year}.jsonl"


def engine_log_path(logs_dir: Path, date_yyyymmdd: str | None = None) -> Path:
    if date_yyyymmdd is None:
        date_yyyymmdd = datetime.now(timezone.utc).strftime("%Y%m%d")
    return logs_dir / f"engine-{date_yyyymmdd}.log"
