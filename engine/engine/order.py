"""주문 생성 / 취소 / 조회 + 재시도 + 멱등성.

박제 출처:
- docs/stage1-v2-relaunch.md §2.4 order.py
- §2.5 숨은 복잡도 #4 (멱등성 client_oid)
- research/CLAUDE.md pyupbit 검증

pyupbit 실측 (2026-04-24):
- `Upbit.buy_market_order(ticker, price_krw, contain_req=False)` — KRW 금액 매수
- `Upbit.sell_market_order(ticker, volume, contain_req=False)` — 코인 수량 매도
- `Upbit.cancel_order(uuid, contain_req=False)` — 주문 취소
- `Upbit.get_order(ticker_or_uuid, state='wait', ...)` — 주문 조회

설계:
- run_mode="paper": 실제 API 호출 없이 현재가 기반 fake order 생성 + state 기록
- run_mode="live": pyupbit.Upbit 사용
- 멱등성: client_oid 생성 → state.get_order_uuid_by_client_oid() 체크 → 중복 방지
- 수수료: Upbit 0.05% (v1 박제). paper는 추정. live는 응답 paid_fee 사용

미확정 사항 (W-4, 2026-04-25):
- paper fee 모델 (krw_amount × 0.0005)이 Upbit 실 동작과 정확 일치 여부 미실측
- V2-05 integration test에서 실 buy_market_order 응답 paid_fee와 비교하여 모델 보정 책무
- 백테스트 ↔ 페이퍼 ±30% 일치 검증 시 fee 모델 오차도 포함됨

라이브 응답 폴링 (W-2):
- 시장가 주문 직후 응답은 status='wait'/'done' + executed_volume이 None일 수 있음 (ccxt #7235)
- _place_live는 응답 status가 'wait'면 즉시 1회 polling 시도. 그래도 미확정이면 호출자가 별도 polling 책임 (poll_status)

SL 인트라데이 차이 (W-3):
- vectorbt 백테스트는 sl_stop=0.08 인트라데이 가격 터치 시 즉시 stop 가격 체결 가정
- 본 라이브는 일봉 close 후 today_low 확인 → 다음 close 시점 시장가 매도 → 갭 다운 시 8% 초과 손실 가능
- 페이퍼 (V2-06)에서 실측 차이 관측. 백테스트 MDD가 라이브 MDD 하한.
"""
from __future__ import annotations

import time
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any

from engine.state import OrderRecord, Position, StateStore


DEFAULT_RETRY_MAX = 3
DEFAULT_RETRY_BASE_S = 0.5
UPBIT_FEE_RATE = 0.0005          # 업비트 원화마켓 수수료 (v1 박제)


@dataclass
class OrderRequest:
    """주문 요청 (paper/live 공통)."""

    cell_key: str                # 예 "KRW-BTC_A"
    pair: str                    # 예 "KRW-BTC"
    strategy: str                # 예 "A"
    side: str                    # "buy" | "sell"
    order_type: str              # "market"
    krw_amount: float | None = None     # buy 시 KRW 금액
    volume: float | None = None         # sell 시 코인 수량
    client_oid: str = ""         # 비어있으면 자동 생성
    metadata: dict[str, Any] = field(default_factory=dict)


def make_client_oid(cell_key: str, side: str, ts_utc: datetime | None = None) -> str:
    """client_oid 생성 (멱등성 키, deterministic).

    형식: `{cell_key}_{side}_{YYYYMMDDHHMM}` (분 단위 — 일봉 close 후 09:05 등)
    동일 cell + side + 동일 분에 재호출 시 **동일 oid 보장** (W-1 정정 2026-04-25,
    이전 버전 uuid8 randomness 제거).

    호출자가 동일 시그널 사이클 내에서 재시도할 때:
    - 스케줄러 tick의 분 단위 ts_utc 고정 → 동일 oid → state.get_order_uuid_by_client_oid 매칭 → 이중 주문 방지

    교차 사이클 (다른 분) 동일 cell+side 재진입은 다른 oid 자연 발생 (의도된 동작).

    Args:
        cell_key: 예 "KRW-BTC_A"
        side: "buy" | "sell"
        ts_utc: None이면 datetime.now(UTC). 멱등성 위해 호출자가 분 단위 고정 권장.
    """
    if ts_utc is None:
        ts_utc = datetime.now(timezone.utc)
    ts_str = ts_utc.strftime("%Y%m%d%H%M")  # 분 단위 (W-1 정정: 초 + uuid8 제거)
    return f"{cell_key}_{side}_{ts_str}"


class OrderExecutor:
    """주문 실행기 (paper/live 분기 + 멱등성 + 재시도).

    Live 모드: pyupbit.Upbit 인스턴스 필요.
    """

    def __init__(
        self,
        state: StateStore,
        run_mode: str,                          # "paper" | "live"
        upbit_client: Any | None = None,        # pyupbit.Upbit 인스턴스 (live만)
        price_oracle: Any | None = None,        # 현재가 조회 함수 (paper fill 계산용)
        fee_rate: float = UPBIT_FEE_RATE,
    ):
        if run_mode not in ("paper", "live"):
            raise ValueError(f"run_mode must be 'paper' or 'live', got {run_mode}")
        if run_mode == "live" and upbit_client is None:
            raise ValueError("live mode requires upbit_client (pyupbit.Upbit instance)")
        self.state = state
        self.run_mode = run_mode
        self.upbit = upbit_client
        self.price_oracle = price_oracle
        self.fee_rate = fee_rate

    def place_order(self, req: OrderRequest) -> OrderRecord:
        """주문 생성 + 멱등성 체크 + 재시도.

        Returns: OrderRecord (status 반영). 호출자는 필요 시 `get_order_status` 재폴링.
        """
        if not req.client_oid:
            req.client_oid = make_client_oid(req.cell_key, req.side)

        # 멱등성 체크
        existing_uuid = self.state.get_order_uuid_by_client_oid(req.client_oid)
        if existing_uuid:
            existing_order = self.state.get_order(existing_uuid)
            if existing_order:
                return existing_order

        if self.run_mode == "paper":
            return self._place_paper(req)
        return self._place_live(req)

    def _place_paper(self, req: OrderRequest) -> OrderRecord:
        """페이퍼 주문: 현재가 기반 즉시 체결 + state 기록."""
        if self.price_oracle is None:
            raise RuntimeError("paper mode requires price_oracle callable (current price fetcher)")

        now = datetime.now(timezone.utc).isoformat()
        current_price = float(self.price_oracle(req.pair))

        if req.side == "buy":
            if req.krw_amount is None or req.krw_amount <= 0:
                raise ValueError("buy requires krw_amount > 0")
            fees = req.krw_amount * self.fee_rate
            filled_volume = (req.krw_amount - fees) / current_price
            requested_krw = req.krw_amount
            filled_price = current_price
        else:  # sell
            if req.volume is None or req.volume <= 0:
                raise ValueError("sell requires volume > 0")
            gross = req.volume * current_price
            fees = gross * self.fee_rate
            filled_volume = req.volume
            filled_price = current_price
            requested_krw = gross

        fake_uuid = f"paper-{uuid.uuid4().hex}"
        record = OrderRecord(
            order_uuid=fake_uuid,
            client_oid=req.client_oid,
            cell_key=req.cell_key,
            pair=req.pair,
            strategy=req.strategy,
            side=req.side,
            order_type=req.order_type,
            status="filled",         # paper = 즉시 체결
            requested_krw=requested_krw,
            requested_volume=req.volume,
            filled_volume=filled_volume,
            filled_price_krw=filled_price,
            fees_krw=fees,
            requested_ts_utc=now,
            updated_ts_utc=now,
            metadata={**req.metadata, "run_mode": "paper"},
        )
        self.state.record_order(record)
        self.state.register_idempotency(req.client_oid, fake_uuid)
        return record

    def _place_live(self, req: OrderRequest) -> OrderRecord:
        """라이브 주문: pyupbit + 재시도 + 응답 파싱."""
        now = datetime.now(timezone.utc).isoformat()
        last_exc: Exception | None = None

        for attempt in range(DEFAULT_RETRY_MAX):
            try:
                if req.side == "buy":
                    if req.krw_amount is None or req.krw_amount <= 0:
                        raise ValueError("buy requires krw_amount > 0")
                    resp = self.upbit.buy_market_order(req.pair, req.krw_amount)
                elif req.side == "sell":
                    if req.volume is None or req.volume <= 0:
                        raise ValueError("sell requires volume > 0")
                    resp = self.upbit.sell_market_order(req.pair, req.volume)
                else:
                    raise ValueError(f"unsupported side: {req.side}")

                if resp is None:
                    raise RuntimeError(f"pyupbit {req.side}_market_order returned None")
                if isinstance(resp, dict) and resp.get("error"):
                    raise RuntimeError(f"Upbit error: {resp['error']}")

                order_uuid = resp.get("uuid")
                if not order_uuid:
                    raise RuntimeError(f"response missing 'uuid': {resp}")

                # Upbit 시장가 응답 파싱 (ccxt #7235: amount가 None일 수 있음, defensive)
                filled_volume = _safe_float(resp.get("executed_volume")) or _safe_float(resp.get("volume"))
                avg_price = _safe_float(resp.get("avg_price")) or _safe_float(resp.get("price"))
                fees = _safe_float(resp.get("paid_fee"))
                status = resp.get("state", "open")  # "wait" | "watch" | "done" | "cancel"
                status_map = {"wait": "open", "watch": "open", "done": "filled", "cancel": "canceled"}
                mapped_status = status_map.get(status, status)

                record = OrderRecord(
                    order_uuid=order_uuid,
                    client_oid=req.client_oid,
                    cell_key=req.cell_key,
                    pair=req.pair,
                    strategy=req.strategy,
                    side=req.side,
                    order_type=req.order_type,
                    status=mapped_status,
                    requested_krw=req.krw_amount if req.side == "buy" else (req.volume or 0) * (avg_price or 0),
                    requested_volume=req.volume,
                    filled_volume=filled_volume,
                    filled_price_krw=avg_price,
                    fees_krw=fees,
                    requested_ts_utc=now,
                    updated_ts_utc=now,
                    metadata={**req.metadata, "run_mode": "live", "upbit_raw": resp},
                )
                self.state.record_order(record)
                self.state.register_idempotency(req.client_oid, order_uuid)

                # W-2 정정 (2026-04-25): status='open' or 핵심 필드 미확정 시 즉시 폴링
                # 시장가 주문 응답은 종종 executed_volume/avg_price/paid_fee가 None (ccxt #7235)
                if mapped_status == "open" or filled_volume is None or avg_price is None:
                    polled = self._immediate_poll(order_uuid, attempts=2, delay_s=0.5)
                    if polled is not None:
                        return polled
                return record
            except Exception as e:
                last_exc = e
                if attempt < DEFAULT_RETRY_MAX - 1:
                    time.sleep(DEFAULT_RETRY_BASE_S * (2 ** attempt))
        raise RuntimeError(f"place_live failed after {DEFAULT_RETRY_MAX} retries: {last_exc}") from last_exc

    def _immediate_poll(self, order_uuid: str, attempts: int = 2, delay_s: float = 0.5) -> OrderRecord | None:
        """주문 직후 즉시 폴링 (W-2 정정 2026-04-25).

        시장가 주문 응답이 미확정 (executed_volume=None / status='wait') 일 때
        짧은 시간 (총 ~1초) 내 폴링으로 체결 확정 시도. 끝까지 미확정이면 None 반환
        (호출자는 record_order에 기록된 부분 데이터 사용 + 후속 poll_status 별도 호출).
        """
        for _ in range(attempts):
            time.sleep(delay_s)
            try:
                rec = self.poll_status(order_uuid)
            except Exception:
                continue
            if rec and rec.status in ("filled", "canceled") and rec.filled_volume is not None:
                return rec
        return None

    def cancel(self, order_uuid: str) -> bool:
        """주문 취소 (live only). paper는 이미 filled이므로 취소 불필요."""
        if self.run_mode == "paper":
            return False
        resp = self.upbit.cancel_order(order_uuid)
        if resp is None or (isinstance(resp, dict) and resp.get("error")):
            return False
        # state 업데이트
        existing = self.state.get_order(order_uuid)
        if existing:
            existing.status = "canceled"
            existing.updated_ts_utc = datetime.now(timezone.utc).isoformat()
            self.state.record_order(existing)
        return True

    def poll_status(self, order_uuid: str) -> OrderRecord | None:
        """라이브 주문 상태 재조회 (open → filled/canceled)."""
        if self.run_mode == "paper":
            return self.state.get_order(order_uuid)
        resp = self.upbit.get_order(order_uuid)
        if resp is None or (isinstance(resp, dict) and resp.get("error")):
            return None
        status_map = {"wait": "open", "watch": "open", "done": "filled", "cancel": "canceled"}
        mapped_status = status_map.get(resp.get("state", "open"), "open")
        existing = self.state.get_order(order_uuid)
        if existing:
            existing.status = mapped_status
            existing.filled_volume = _safe_float(resp.get("executed_volume")) or existing.filled_volume
            existing.filled_price_krw = _safe_float(resp.get("avg_price")) or existing.filled_price_krw
            existing.fees_krw = _safe_float(resp.get("paid_fee")) or existing.fees_krw
            existing.updated_ts_utc = datetime.now(timezone.utc).isoformat()
            self.state.record_order(existing)
            return existing
        return None


def _safe_float(v: Any) -> float | None:
    """None / 빈 문자열 / 숫자를 float로 안전 변환 (ccxt #7235 defensive)."""
    if v is None or v == "":
        return None
    try:
        return float(v)
    except (TypeError, ValueError):
        return None


if __name__ == "__main__":
    # Sanity: paper mode 매수/매도
    from pathlib import Path
    from engine.config import ENGINE_ROOT, ensure_runtime_dirs, load_config
    from engine.logger import setup_logger
    from engine.market_data import get_current_price
    from engine.state import StateStore

    ensure_runtime_dirs()
    cfg = load_config()
    logger = setup_logger(ENGINE_ROOT / "logs", "INFO")

    # 임시 state DB (sanity 격리)
    tmp_db = ENGINE_ROOT / "data" / "sanity_order.sqlite"
    if tmp_db.exists():
        tmp_db.unlink()
    state = StateStore(tmp_db)

    executor = OrderExecutor(
        state=state,
        run_mode="paper",
        price_oracle=get_current_price,
    )

    # 1. Paper buy
    req_buy = OrderRequest(
        cell_key="KRW-BTC_A", pair="KRW-BTC", strategy="A",
        side="buy", order_type="market", krw_amount=100_000,
    )
    rec_buy = executor.place_order(req_buy)
    print(f"[paper buy] uuid={rec_buy.order_uuid}, status={rec_buy.status}, "
          f"filled_price={rec_buy.filled_price_krw:,.0f}, filled_volume={rec_buy.filled_volume:.8f}, "
          f"fees={rec_buy.fees_krw:,.2f}")

    # 2. 재시도 멱등성: 동일 client_oid로 재호출 → 기존 record 반환
    rec_buy2 = executor.place_order(OrderRequest(
        cell_key="KRW-BTC_A", pair="KRW-BTC", strategy="A",
        side="buy", order_type="market", krw_amount=100_000,
        client_oid=req_buy.client_oid,  # 동일 oid
    ))
    assert rec_buy.order_uuid == rec_buy2.order_uuid, "멱등성 실패"
    print(f"[idempotency] 동일 client_oid 재호출 시 기존 uuid 반환 OK")

    # 3. Paper sell
    req_sell = OrderRequest(
        cell_key="KRW-BTC_A", pair="KRW-BTC", strategy="A",
        side="sell", order_type="market", volume=rec_buy.filled_volume,
    )
    rec_sell = executor.place_order(req_sell)
    print(f"[paper sell] uuid={rec_sell.order_uuid}, filled_volume={rec_sell.filled_volume:.8f}, "
          f"fees={rec_sell.fees_krw:,.2f}")

    # 4. 입력 검증
    try:
        executor.place_order(OrderRequest(
            cell_key="KRW-BTC_A", pair="KRW-BTC", strategy="A",
            side="buy", order_type="market", krw_amount=0,
        ))
    except ValueError as e:
        print(f"[validation] krw_amount<=0 거부 OK: {e}")

    # 5. Live mode requires upbit_client
    try:
        OrderExecutor(state=state, run_mode="live")
    except ValueError as e:
        print(f"[validation] live mode client 필수 OK: {e}")

    logger.info("order_sanity_ok")
    tmp_db.unlink()  # 정리
