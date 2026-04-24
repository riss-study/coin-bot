"""구조화 로깅 + 거래 JSON 영구 저장.

박제 출처:
- CLAUDE.md "모든 매매 데이터(거래/신호/포지션)는 DB에 영구 저장 (세금 준비)"
- docs/stage1-v2-relaunch.md §2.4 `logger.py`

설계:
- 일반 로그: `logs/engine-YYYYMMDD.log` (JSONL, 일별 로테이션)
- 거래 영구 기록: `logs/trades-YYYY.jsonl` (연도별 분할, 세금 신고용)
- 신호 기록: `logs/signals-YYYYMMDD.jsonl` (daily 검증용)
"""
from __future__ import annotations

import json
import logging
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


# Module-level logger (초기화 후 setup_logger로 구성)
_logger: logging.Logger | None = None


class JsonFormatter(logging.Formatter):
    """JSONL 포맷터 — 각 log record를 한 줄 JSON으로."""

    def format(self, record: logging.LogRecord) -> str:
        payload: dict[str, Any] = {
            "ts_utc": datetime.fromtimestamp(record.created, tz=timezone.utc).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }
        # extra 필드 (log() extra= 또는 LoggerAdapter로 전달)
        standard_attrs = {
            "name", "msg", "args", "levelname", "levelno", "pathname", "filename",
            "module", "exc_info", "exc_text", "stack_info", "lineno", "funcName",
            "created", "msecs", "relativeCreated", "thread", "threadName",
            "processName", "process", "message", "taskName", "getMessage",
        }
        for key, value in record.__dict__.items():
            if key not in standard_attrs and not key.startswith("_"):
                payload[key] = value
        if record.exc_info:
            payload["exc_info"] = self.formatException(record.exc_info)
        return json.dumps(payload, ensure_ascii=False, default=str)


def setup_logger(logs_dir: Path, level: str = "INFO", force: bool = False) -> logging.Logger:
    """엔진 공용 로거 설정.

    - stdout: 사람이 읽기 용이한 포맷
    - 파일 (logs/engine-YYYYMMDD.log): JSONL (프로그램적 분석 용이)

    W-2 정정 (2026-04-24): `force=True`로 재설정 허용 (테스트/logs_dir 변경 시).
    """
    global _logger
    if _logger is not None and not force:
        return _logger

    logs_dir.mkdir(parents=True, exist_ok=True)

    logger = logging.getLogger("engine")
    logger.setLevel(level.upper())
    logger.handlers.clear()  # 재호출 시 중복 방지

    # Console handler (사람 친화)
    console = logging.StreamHandler(sys.stdout)
    console.setFormatter(logging.Formatter(
        fmt="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    ))
    console.setLevel(level.upper())
    logger.addHandler(console)

    # File handler (JSONL)
    today = datetime.now(timezone.utc).strftime("%Y%m%d")
    log_file = logs_dir / f"engine-{today}.log"
    file_handler = logging.FileHandler(log_file, encoding="utf-8")
    file_handler.setFormatter(JsonFormatter())
    file_handler.setLevel(level.upper())
    logger.addHandler(file_handler)

    _logger = logger
    logger.info("logger_initialized", extra={"log_file": str(log_file)})
    return logger


def log_trade(logs_dir: Path, trade: dict[str, Any]) -> None:
    """거래 영구 기록 (세금 준비 + 감사).

    파일: logs/trades-YYYY.jsonl (연도별 분할)
    세금 신고 시 직접 참조 가능한 표준 필드 보존.

    권장 필드 (호출자가 채움):
    - ts_utc, ts_kst: 거래 체결 시각
    - pair: 예 "KRW-BTC"
    - strategy: 예 "A" | "D"
    - side: "buy" | "sell"
    - order_type: "market" | "limit"
    - price_krw: 체결 단가 (KRW)
    - volume: 체결 수량 (코인)
    - krw_amount: KRW 기준 체결 금액
    - fees_krw: 수수료 (KRW)
    - slippage_bps: 예상 대비 슬리피지 (basis points)
    - order_uuid: Upbit 주문 UUID
    - client_oid: 봇 내부 멱등성 ID
    - run_mode: "paper" | "live"
    """
    logs_dir.mkdir(parents=True, exist_ok=True)
    year = datetime.now(timezone.utc).strftime("%Y")
    path = logs_dir / f"trades-{year}.jsonl"

    record = dict(trade)
    record.setdefault("logged_at_utc", datetime.now(timezone.utc).isoformat())

    with open(path, "a", encoding="utf-8") as f:
        f.write(json.dumps(record, ensure_ascii=False, default=str) + "\n")


def log_signal(logs_dir: Path, signal: dict[str, Any]) -> None:
    """신호 기록 (일봉 close 후 각 cell 신호 평가 결과).

    파일: logs/signals-YYYYMMDD.jsonl

    권장 필드:
    - ts_utc, pair, strategy
    - action: "entry" | "exit" | "hold"
    - reason: 신호 근거 (지표 값 등)
    """
    logs_dir.mkdir(parents=True, exist_ok=True)
    today = datetime.now(timezone.utc).strftime("%Y%m%d")
    path = logs_dir / f"signals-{today}.jsonl"

    record = dict(signal)
    record.setdefault("logged_at_utc", datetime.now(timezone.utc).isoformat())

    with open(path, "a", encoding="utf-8") as f:
        f.write(json.dumps(record, ensure_ascii=False, default=str) + "\n")


if __name__ == "__main__":
    # V2-02 sanity check
    from engine.config import load_config, ENGINE_ROOT

    cfg = load_config()
    logs_dir = ENGINE_ROOT / "logs"
    logger = setup_logger(logs_dir, cfg.logging.get("level", "INFO"))

    logger.info("sanity_check_start", extra={"run_mode": cfg.run_mode})
    logger.warning("test_warning", extra={"key1": "value1", "number": 42})

    # 거래 기록 sanity
    log_trade(logs_dir, {
        "ts_utc": datetime.now(timezone.utc).isoformat(),
        "pair": "KRW-BTC",
        "strategy": "A",
        "side": "buy",
        "order_type": "market",
        "price_krw": 85_000_000,
        "volume": 0.001176,
        "krw_amount": 100_000,
        "fees_krw": 50,
        "slippage_bps": 2.3,
        "order_uuid": "sanity-check-uuid",
        "client_oid": "sanity-check-coid",
        "run_mode": "paper",
    })

    # 신호 기록 sanity
    log_signal(logs_dir, {
        "ts_utc": datetime.now(timezone.utc).isoformat(),
        "pair": "KRW-BTC",
        "strategy": "A",
        "action": "hold",
        "reason": "close<ma200",
    })

    logger.info("sanity_check_done", extra={"files_in_logs": sorted(p.name for p in logs_dir.iterdir())})
