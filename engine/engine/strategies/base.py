"""Strategy 공통 인터페이스.

페이퍼/라이브 공통:
- 매일 일봉 close 시점 (KST 09:00) 에 compute_signal() 호출
- 최근 N+1 일 OHLCV를 입력으로 받아 "오늘 close 기준" 신호 반환
- 포지션 유무는 외부 (state.py)에서 관리하고 Strategy는 **순수 신호만** 계산
"""
from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Protocol, runtime_checkable

import pandas as pd


class SignalAction(str, Enum):
    """신호 유형."""

    ENTRY = "entry"          # 포지션 없을 때만 유효
    EXIT = "exit"            # 포지션 있을 때만 유효 (indicator 기반 exit)
    SL_EXIT = "sl_exit"      # 하드 스톱 터치 (오늘 low <= entry × (1 - sl_pct))
    HOLD = "hold"            # 아무 동작 없음


@dataclass
class SignalResult:
    """신호 평가 결과.

    - action: 권장 행동
    - reason: 신호 근거 (dict — 로깅/디버깅용)
    - indicator_snapshot: 오늘 시점 지표 값 (감사 trace)
    """

    action: SignalAction
    reason: dict = field(default_factory=dict)
    indicator_snapshot: dict = field(default_factory=dict)


@runtime_checkable
class Strategy(Protocol):
    """전략 Protocol — `compute_signal`만 구현하면 됨.

    주의: Protocol이므로 상속 강제 X. structural typing.
    """

    name: str                # "A" | "D" 등

    def compute_signal(
        self,
        df: pd.DataFrame,
        in_position: bool,
        entry_price_krw: float | None = None,
    ) -> SignalResult:
        """오늘 close 기준 신호 평가.

        Args:
            df: 최소 warmup+1 일 OHLCV. index=UTC tz-aware. columns=open/high/low/close/volume.
                **마지막 row = 오늘 close (방금 마감)**.
            in_position: 현재 포지션 보유 여부
            entry_price_krw: 보유 중일 때 진입 단가 (SL 계산용). None이면 in_position=False.

        Returns:
            SignalResult
        """
        ...


def check_sl_hit(
    today_low: float,
    entry_price_krw: float,
    sl_pct: float,
) -> bool:
    """하드 스톱 터치 확인.

    기준: 오늘 일봉 저가가 entry × (1 - sl_pct) 이하면 SL 터치 = True.

    W-3 정정 (2026-04-25): 백테스트 ↔ 라이브 SL 차이 명시.

    백테스트 (vectorbt sl_stop=0.08):
        인트라데이 가격이 stop 터치 → 즉시 stop level 가격 체결 가정.
        손실 ≈ 8% (미끄러짐 무시).

    라이브 (본 로직):
        오늘 일봉 close 시점 (KST 09:00 일봉 종가 확정 후) 에 today_low 확인.
        SL 터치 확인 시 다음 일봉 close 시점에 시장가 매도 (engine main loop).
        → 갭 다운 시 8% 초과 손실 가능 (예: 15% 갭 다운 후 close).
        → 백테스트 MDD가 실제 라이브 MDD의 하한일 수 있음.

    페이퍼 (V2-06)에서 실측 차이 관측 책무.
    Sub-minute 모니터링은 V2-07 이후 확장 가능 (현재 범위 외).
    """
    if entry_price_krw is None or entry_price_krw <= 0:
        return False
    sl_level = entry_price_krw * (1.0 - sl_pct)
    return today_low <= sl_level
