"""KST 일봉 close 스케줄러 (in-process).

박제 출처:
- docs/stage1-v2-relaunch.md §2.4 scheduler.py
- engine/config.yaml schedule.signal_check_hour_kst (= 9), signal_check_minute (= 5)

설계:
- launchd / cron 대신 단순 in-process scheduler
- 매일 KST hh:mm (config 박제 시각) 에 callback 호출
- 시작 시 다음 트리거 시각 계산 → time.sleep → callback → 반복
- KeyboardInterrupt (Ctrl+C) 우아한 종료
- 다음 트리거 시각 산출 정확성 핵심 (UTC ↔ KST 변환)
"""
from __future__ import annotations

import logging
import time
from datetime import datetime, time as dtime, timedelta, timezone
from typing import Callable

from engine.config import KST


_log = logging.getLogger("engine.scheduler")


def next_trigger_4h(minute_offset: int = 5, *, now_utc: datetime | None = None) -> datetime:
    """다음 4시간 단위 트리거 (KST 기준 매 4h: 00:05, 04:05, 08:05, 12:05, 16:05, 20:05).

    Upbit 4시간봉 close 시점 (UTC 00:00, 04:00, ..., 20:00) + 5분 buffer.
    KST = UTC+9 → KST 00:05 = UTC 15:05 (전날) — 단순화 위해 UTC hour 기준.
    """
    if now_utc is None:
        now_utc = datetime.now(timezone.utc)
    if now_utc.tzinfo is None:
        raise ValueError("now_utc must be tz-aware")
    # 다음 UTC 00/04/08/12/16/20 hour + minute_offset
    candidates = [now_utc.replace(hour=h, minute=minute_offset, second=0, microsecond=0)
                  for h in [0, 4, 8, 12, 16, 20]]
    future = [c for c in candidates if c > now_utc]
    if future:
        return min(future)
    # 모두 과거 → 다음 날 00:05
    return (candidates[0] + timedelta(days=1))


def run_4h_loop(
    *,
    callback: Callable[[datetime], None],
    minute_offset: int = 5,
    on_error: Callable[[Exception], None] | None = None,
    max_iterations: int | None = None,
) -> None:
    """매 4시간 (UTC 00/04/08/12/16/20 + offset min) callback 호출."""
    iteration = 0
    _log.info("scheduler_4h_started", extra={"minute_offset": minute_offset})
    while True:
        target = next_trigger_4h(minute_offset)
        _log.info("scheduler_next_trigger", extra={
            "trigger_utc": target.isoformat(),
            "trigger_kst": target.astimezone(KST).isoformat(),
        })
        sleep_until(target)
        try:
            callback(target)
        except KeyboardInterrupt:
            _log.info("scheduler_interrupted")
            raise
        except Exception:
            if on_error is not None:
                try:
                    on_error(Exception)
                except Exception:
                    _log.exception("on_error_handler_failed")
            else:
                _log.exception("scheduler_callback_failed")
        iteration += 1
        if max_iterations is not None and iteration >= max_iterations:
            return


def next_trigger_at(hour_kst: int, minute_kst: int, *, now_utc: datetime | None = None) -> datetime:
    """다음 KST hh:mm 시각을 UTC datetime으로 반환.

    - now_utc 가 오늘 KST hh:mm 이전이면 → 오늘 hh:mm KST
    - 이후면 → 내일 hh:mm KST
    """
    if now_utc is None:
        now_utc = datetime.now(timezone.utc)
    if now_utc.tzinfo is None:
        raise ValueError("now_utc must be tz-aware")

    now_kst = now_utc.astimezone(KST)
    today_target_kst = now_kst.replace(
        hour=hour_kst, minute=minute_kst, second=0, microsecond=0
    )
    if now_kst < today_target_kst:
        target_kst = today_target_kst
    else:
        target_kst = today_target_kst + timedelta(days=1)
    return target_kst.astimezone(timezone.utc)


def sleep_until(target_utc: datetime, *, max_step_s: float = 60.0) -> None:
    """target_utc 시각까지 대기 (interruptible).

    `time.sleep`을 작은 단위로 쪼개 호출 (KeyboardInterrupt 응답성).
    """
    if target_utc.tzinfo is None:
        raise ValueError("target_utc must be tz-aware")
    while True:
        now = datetime.now(timezone.utc)
        remaining = (target_utc - now).total_seconds()
        if remaining <= 0:
            return
        time.sleep(min(remaining, max_step_s))


def run_daily_loop(
    *,
    callback: Callable[[datetime], None],
    hour_kst: int,
    minute_kst: int,
    on_error: Callable[[Exception], None] | None = None,
    max_iterations: int | None = None,
) -> None:
    """매일 KST hh:mm 에 callback 호출.

    Args:
        callback: trigger 시각(UTC datetime)을 받음. 내부 예외 발생 시 on_error로 위임.
        hour_kst, minute_kst: 트리거 시각 (예 09, 05).
        on_error: callback 실패 처리 (None이면 _log.exception). 봇 중단 X.
        max_iterations: None이면 무한 루프. 테스트용.
    """
    iteration = 0
    _log.info("scheduler_started", extra={"hour_kst": hour_kst, "minute_kst": minute_kst})

    while True:
        target = next_trigger_at(hour_kst, minute_kst)
        _log.info("scheduler_next_trigger", extra={
            "trigger_utc": target.isoformat(),
            "trigger_kst": target.astimezone(KST).isoformat(),
        })
        sleep_until(target)

        try:
            callback(target)
        except KeyboardInterrupt:
            _log.info("scheduler_interrupted")
            raise
        except Exception as e:
            if on_error is not None:
                try:
                    on_error(e)
                except Exception:
                    _log.exception("on_error_handler_failed")
            else:
                _log.exception("scheduler_callback_failed")

        iteration += 1
        if max_iterations is not None and iteration >= max_iterations:
            _log.info("scheduler_max_iterations_reached", extra={"iterations": iteration})
            return


if __name__ == "__main__":
    # Sanity
    from engine.config import ENGINE_ROOT, ensure_runtime_dirs, load_config
    from engine.logger import setup_logger

    ensure_runtime_dirs()
    cfg = load_config()
    setup_logger(ENGINE_ROOT / "logs", "INFO")

    # 1. next_trigger_at 정확성 (오늘 09:05 vs 내일 09:05)
    fixed_now = datetime(2026, 4, 25, 0, 0, 0, tzinfo=timezone.utc)  # KST 09:00
    nxt = next_trigger_at(9, 5, now_utc=fixed_now)
    print(f"now=2026-04-25 09:00 KST → next 09:05 = {nxt.astimezone(KST).isoformat()}")
    expected = datetime(2026, 4, 25, 9, 5, tzinfo=KST).astimezone(timezone.utc)
    assert nxt == expected, f"expected {expected}, got {nxt}"

    fixed_now2 = datetime(2026, 4, 25, 1, 0, 0, tzinfo=timezone.utc)  # KST 10:00 (이후)
    nxt2 = next_trigger_at(9, 5, now_utc=fixed_now2)
    print(f"now=2026-04-25 10:00 KST → next 09:05 = {nxt2.astimezone(KST).isoformat()}")
    expected2 = datetime(2026, 4, 26, 9, 5, tzinfo=KST).astimezone(timezone.utc)
    assert nxt2 == expected2, f"expected {expected2}, got {nxt2}"

    # 2. sleep_until 짧은 대기
    short_target = datetime.now(timezone.utc) + timedelta(seconds=2)
    print(f"sleep_until 2초 대기 시작...")
    t0 = time.time()
    sleep_until(short_target)
    elapsed = time.time() - t0
    print(f"sleep_until 완료 ({elapsed:.1f}s)")
    assert 1.5 <= elapsed <= 3.0, f"expected ~2s, got {elapsed}"

    # 3. run_daily_loop sanity (max_iterations=1, 즉시 트리거 시점 재계산하여 짧은 대기로 모킹은 어렵)
    # 별도 테스트는 V2-05 통합에서.
    print("scheduler.py sanity OK (next_trigger_at + sleep_until)")