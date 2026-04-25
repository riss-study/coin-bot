"""포지션 관리 + PnL 계산 + 세금 데이터.

박제 출처:
- docs/stage1-v2-relaunch.md §2.4 position.py
- CLAUDE.md "모든 매매 데이터(거래/신호/포지션)는 DB에 영구 저장 (세금 준비)"

설계:
- state.py Position dataclass + StateStore 활용 (raw 저장 책임은 state)
- position.py 책임:
  - 신호 + 주문 결과 → 포지션 entry / exit
  - 현재가 기반 unrealized PnL 계산
  - 세금 신고용 거래 기록 (logger.log_trade 호출)

PnL 정의:
- unrealized PnL = (current_price - entry_price) × volume - 미수수료
- realized PnL = (exit_price - entry_price) × volume - entry 수수료 - exit 수수료

세금 데이터:
- 매수 시: 취득가 (filled_price_krw) + 취득 수량 + 수수료 → log_trade
- 매도 시: 양도가 (filled_price_krw) + 양도 수량 + 수수료 + 양도차익 → log_trade
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from engine.logger import log_trade
from engine.state import OrderRecord, Position, StateStore


@dataclass
class PnL:
    cell_key: str
    pair: str
    strategy: str
    entry_price_krw: float
    current_price_krw: float
    volume: float
    krw_invested: float                # 진입 시 투자 KRW (수수료 포함)
    unrealized_pnl_krw: float          # 현재가 기준 평가 손익 (수수료 차감 전)
    unrealized_pnl_pct: float          # invested 대비 비율


def open_position_from_order(
    state: StateStore,
    order: OrderRecord,
    *,
    metadata: dict[str, Any] | None = None,
) -> Position:
    """매수 체결 후 Position 생성 + state 저장.

    호출 조건: order.side == 'buy' AND order.status == 'filled' AND filled_volume / filled_price 확정.
    """
    if order.side != "buy":
        raise ValueError(f"open_position requires buy order, got side={order.side}")
    if order.status != "filled":
        raise ValueError(f"open_position requires filled order, got status={order.status}")
    if not order.filled_volume or not order.filled_price_krw:
        raise ValueError("open_position requires filled_volume + filled_price_krw")

    krw_invested = float((order.filled_volume * order.filled_price_krw) + (order.fees_krw or 0))
    pos = Position(
        cell_key=order.cell_key,
        pair=order.pair,
        strategy=order.strategy,
        entry_ts_utc=order.updated_ts_utc or datetime.now(timezone.utc).isoformat(),
        entry_price_krw=float(order.filled_price_krw),
        volume=float(order.filled_volume),
        krw_invested=krw_invested,
        order_uuid=order.order_uuid,
        metadata={**(metadata or {}), "entry_fees_krw": order.fees_krw or 0},
    )
    state.upsert_position(pos)
    return pos


def close_position_from_order(
    state: StateStore,
    logs_dir: Path,
    sell_order: OrderRecord,
    *,
    run_mode: str = "paper",
    metadata: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """매도 체결 후 Position 종료 + 세금 데이터 기록 + realized PnL 반환.

    호출 조건: sell_order.side == 'sell' AND status == 'filled' AND 해당 cell_key의 Position 존재.

    Returns:
        {
            "realized_pnl_krw": float,
            "realized_pnl_pct": float,
            "entry_price_krw": float,
            "exit_price_krw": float,
            "volume": float,
            "entry_fees_krw": float,
            "exit_fees_krw": float,
        }
    """
    if sell_order.side != "sell":
        raise ValueError(f"close_position requires sell order, got side={sell_order.side}")
    if sell_order.status != "filled":
        raise ValueError(f"close_position requires filled, got status={sell_order.status}")
    if not sell_order.filled_volume or not sell_order.filled_price_krw:
        raise ValueError("close_position requires filled_volume + filled_price_krw")

    pos = state.get_position(sell_order.cell_key)
    if pos is None:
        raise RuntimeError(f"close_position: no open position for {sell_order.cell_key}")

    entry_fees = float(pos.metadata.get("entry_fees_krw", 0))
    exit_fees = float(sell_order.fees_krw or 0)
    exit_price = float(sell_order.filled_price_krw)
    exit_volume = float(sell_order.filled_volume)

    gross_proceeds = exit_volume * exit_price
    realized_pnl_krw = gross_proceeds - exit_fees - pos.krw_invested
    realized_pnl_pct = realized_pnl_krw / pos.krw_invested if pos.krw_invested > 0 else 0.0

    # 세금 데이터: entry + exit 두 거래 기록 (양도차익 명시)
    now_utc = datetime.now(timezone.utc).isoformat()
    log_trade(logs_dir, {
        "ts_utc": pos.entry_ts_utc,
        "pair": pos.pair, "strategy": pos.strategy,
        "side": "buy", "order_type": "market",
        "price_krw": pos.entry_price_krw, "volume": pos.volume,
        "krw_amount": pos.entry_price_krw * pos.volume,
        "fees_krw": entry_fees,
        "order_uuid": pos.order_uuid, "client_oid": "",
        "run_mode": run_mode,
        "linked_to": sell_order.order_uuid,
    })
    log_trade(logs_dir, {
        "ts_utc": sell_order.updated_ts_utc or now_utc,
        "pair": sell_order.pair, "strategy": sell_order.strategy,
        "side": "sell", "order_type": "market",
        "price_krw": exit_price, "volume": exit_volume,
        "krw_amount": gross_proceeds,
        "fees_krw": exit_fees,
        "order_uuid": sell_order.order_uuid, "client_oid": sell_order.client_oid,
        "run_mode": run_mode,
        "realized_pnl_krw": realized_pnl_krw,
        "realized_pnl_pct": realized_pnl_pct,
        "entry_price_krw": pos.entry_price_krw,
        "entry_fees_krw": entry_fees,
        "exit_fees_krw": exit_fees,
    })

    state.close_position(sell_order.cell_key)
    return {
        "realized_pnl_krw": realized_pnl_krw,
        "realized_pnl_pct": realized_pnl_pct,
        "entry_price_krw": pos.entry_price_krw,
        "exit_price_krw": exit_price,
        "volume": exit_volume,
        "entry_fees_krw": entry_fees,
        "exit_fees_krw": exit_fees,
    }


def compute_unrealized_pnl(pos: Position, current_price_krw: float) -> PnL:
    """현재가 기준 unrealized PnL.

    공식 (W-3 정정 docstring 명시 2026-04-25):
        market_value = volume × current_price_krw
        unrealized_pnl_krw = market_value - krw_invested
        unrealized_pnl_pct = unrealized_pnl_krw / krw_invested

    주의:
    - krw_invested 는 진입 시 (volume × entry_price) + entry_fees 를 포함 (entry fees 차감 후 PnL).
    - **exit fees는 미차감** (실현되기 전이므로). 실제 매도 시 realized_pnl 은 추가로
      exit_fees ≈ market_value × 0.0005 만큼 더 작아짐.
    - 즉 unrealized 가 0 이라도 매도하면 realized 음수 가능 (왕복 수수료 0.1%).
    - 사용자 보고 시 이 차이 유의.
    """
    market_value = pos.volume * current_price_krw
    unrealized = market_value - pos.krw_invested
    pct = unrealized / pos.krw_invested if pos.krw_invested > 0 else 0.0
    return PnL(
        cell_key=pos.cell_key, pair=pos.pair, strategy=pos.strategy,
        entry_price_krw=pos.entry_price_krw,
        current_price_krw=current_price_krw,
        volume=pos.volume, krw_invested=pos.krw_invested,
        unrealized_pnl_krw=unrealized, unrealized_pnl_pct=pct,
    )


if __name__ == "__main__":
    # Sanity
    from engine.config import ENGINE_ROOT, ensure_runtime_dirs, load_config
    from engine.logger import setup_logger
    from engine.market_data import get_current_price
    from engine.state import OrderRecord, StateStore

    ensure_runtime_dirs()
    cfg = load_config()
    setup_logger(ENGINE_ROOT / "logs", "INFO")

    tmp_db = ENGINE_ROOT / "data" / "sanity_position.sqlite"
    if tmp_db.exists():
        tmp_db.unlink()
    state = StateStore(tmp_db)

    # 1. 매수 체결 → 포지션 오픈
    buy_order = OrderRecord(
        order_uuid="paper-buy-uuid", client_oid="KRW-BTC_A_buy_202604250905",
        cell_key="KRW-BTC_A", pair="KRW-BTC", strategy="A",
        side="buy", order_type="market", status="filled",
        requested_krw=100_000, filled_volume=0.0008648,
        filled_price_krw=115_573_000, fees_krw=50,
        requested_ts_utc=datetime.now(timezone.utc).isoformat(),
        updated_ts_utc=datetime.now(timezone.utc).isoformat(),
    )
    state.record_order(buy_order)
    pos = open_position_from_order(state, buy_order)
    print(f"[open] cell={pos.cell_key} entry={pos.entry_price_krw:,.0f} volume={pos.volume:.8f} invested={pos.krw_invested:,.0f}")

    # 2. unrealized PnL (현재가 = 116,000,000 가정)
    pnl = compute_unrealized_pnl(pos, current_price_krw=116_000_000)
    print(f"[unrealized] PnL={pnl.unrealized_pnl_krw:+,.0f} KRW ({pnl.unrealized_pnl_pct*100:+.2f}%)")

    # 3. 매도 체결 → realized PnL
    sell_order = OrderRecord(
        order_uuid="paper-sell-uuid", client_oid="KRW-BTC_A_sell_202604300905",
        cell_key="KRW-BTC_A", pair="KRW-BTC", strategy="A",
        side="sell", order_type="market", status="filled",
        requested_krw=100_368, filled_volume=0.0008648,
        filled_price_krw=116_000_000, fees_krw=50,
        requested_ts_utc=datetime.now(timezone.utc).isoformat(),
        updated_ts_utc=datetime.now(timezone.utc).isoformat(),
    )
    state.record_order(sell_order)
    result = close_position_from_order(state, ENGINE_ROOT / "logs", sell_order, run_mode="paper")
    print(f"[close] realized_pnl={result['realized_pnl_krw']:+,.0f} KRW ({result['realized_pnl_pct']*100:+.2f}%)")
    print(f"  entry={result['entry_price_krw']:,.0f} exit={result['exit_price_krw']:,.0f} vol={result['volume']:.8f}")
    print(f"  fees: entry={result['entry_fees_krw']:,.0f} exit={result['exit_fees_krw']:,.0f}")

    # 4. 검증: 종료된 포지션 조회 시 None
    assert state.get_position("KRW-BTC_A") is None, "포지션 종료 후 None 이어야"
    print("[verify] close 후 포지션 None 확인 OK")

    # 5. 잘못된 입력
    try:
        open_position_from_order(state, sell_order)  # sell order 입력
    except ValueError as e:
        print(f"[validation] sell→open 거부 OK: {e}")

    tmp_db.unlink()
    print("position.py sanity OK")
