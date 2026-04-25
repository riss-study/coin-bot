"""GET /api/health — daemon 상태 + state DB 접근 확인."""
from __future__ import annotations

from datetime import datetime, timezone
from zoneinfo import ZoneInfo

from fastapi import APIRouter, HTTPException

from app.config import STATE_DB_PATH
from app.db.state_reader import get_meta

router = APIRouter()
KST = ZoneInfo("Asia/Seoul")


@router.get("/api/health")
def health() -> dict:
    """daemon 살아있는지 간접 판정 — state.meta.last_run_ts 기준.

    last_run_ts가 마지막 cycle 시각. 24시간 이내면 daemon alive 추정.
    (cycle은 매일 KST 09:05, 정상이면 차이 < 24h + 5min)
    """
    now_utc = datetime.now(timezone.utc)
    payload = {
        "status": "ok",
        "ts_utc": now_utc.isoformat(),
        "ts_kst": now_utc.astimezone(KST).isoformat(),
    }
    try:
        last_run = get_meta(STATE_DB_PATH, "last_run_ts")
    except FileNotFoundError:
        payload["state_db"] = "not_found"
        payload["daemon_alive"] = None
        return payload

    payload["state_db"] = "ok"
    payload["last_run_ts_utc"] = last_run

    if last_run is None:
        payload["daemon_alive"] = None
        payload["note"] = "last_run_ts 미기록 (daemon 첫 cycle 전)"
        return payload

    try:
        last = datetime.fromisoformat(last_run)
        if last.tzinfo is None:
            last = last.replace(tzinfo=timezone.utc)
        gap_sec = (now_utc - last).total_seconds()
        payload["last_run_kst"] = last.astimezone(KST).isoformat()
        payload["seconds_since_last_run"] = int(gap_sec)
        # 26시간 이내 (24h cycle + 2h 여유) → alive 추정
        payload["daemon_alive"] = gap_sec < 26 * 3600
    except ValueError:
        payload["daemon_alive"] = None
        payload["note"] = "last_run_ts parse 실패"
    return payload
