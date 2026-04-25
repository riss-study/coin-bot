"""coin-bot 엔진 orchestration.

박제 출처:
- docs/stage1-v2-relaunch.md §2.4 main.py
- engine/config.yaml (사전 지정 파라미터)

흐름:
1. config 로드 + 런타임 디렉토리 생성
2. logger 설정
3. state 초기화 + 재시작 복원 (open positions/orders 로깅)
4. Keychain secrets (live 모드만): Upbit access/secret + Discord webhook
5. price_oracle = market_data.get_current_price 함수 참조
6. order_executor 생성 (paper or live)
7. notifier 생성 (Discord webhook 있으면)
8. 매 KST 09:05 (config schedule) 마다:
   a. 각 cell에 대해:
      - market_data fetch_ohlcv (warmup 기간 +α)
      - 현재 포지션 조회
      - strategy.compute_signal
      - signal.action 에 따라 order placement
      - position 업데이트
      - notifier 전송
   b. 일일 요약 전송 (PnL + 포지션)
"""
from __future__ import annotations

import logging
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from engine.config import (
    Config,
    ENGINE_ROOT,
    KST,
    ensure_runtime_dirs,
    get_keychain_secret,
    load_config,
    load_discord_webhook,
    load_upbit_credentials,
)
from engine.logger import setup_logger
from engine.market_data import fetch_ohlcv, get_current_price
from engine.notifier import DiscordNotifier
from engine.order import OrderExecutor, OrderRequest, make_client_oid
from engine.position import close_position_from_order, compute_unrealized_pnl, open_position_from_order
from engine.scheduler import run_daily_loop, next_trigger_at
from engine.state import StateStore
from engine.strategies import SignalAction, SignalResult, StrategyA, StrategyD


def build_strategy(name: str, cfg: Config):
    """전략 인스턴스 생성 (config 박제값 주입)."""
    if name == "A":
        return StrategyA(
            ma_period=cfg.strategy_a.ma_period,
            donchian_high=cfg.strategy_a.donchian_high,
            donchian_low=cfg.strategy_a.donchian_low,
            vol_avg_period=cfg.strategy_a.vol_avg_period,
            vol_mult=cfg.strategy_a.vol_mult,
            sl_pct=cfg.strategy_a.sl_pct,
        )
    if name == "D":
        return StrategyD(
            keltner_window=cfg.strategy_d.keltner_window,
            keltner_atr_mult=cfg.strategy_d.keltner_atr_mult,
            atr_window=cfg.strategy_d.atr_window,
            bollinger_window=cfg.strategy_d.bollinger_window,
            bollinger_sigma=cfg.strategy_d.bollinger_sigma,
            sl_hard=cfg.strategy_d.sl_hard,
        )
    raise ValueError(f"unknown strategy: {name}")


class Engine:
    """orchestration 엔진."""

    def __init__(self, cfg: Config):
        self.cfg = cfg
        self.logger = logging.getLogger("engine.main")
        self.state = StateStore(ENGINE_ROOT / cfg.state["db_path"])

        # Strategy 인스턴스 (cell마다)
        self.strategies = {
            f"{c.ticker}_{c.strategy}": build_strategy(c.strategy, cfg)
            for c in cfg.pairs
        }

        # Notifier (Discord webhook 없으면 None)
        self.notifier: DiscordNotifier | None = None
        try:
            url = load_discord_webhook(cfg)
            self.notifier = DiscordNotifier(url)
            self.logger.info("notifier_initialized")
        except RuntimeError as e:
            self.logger.warning("notifier_disabled_no_webhook", extra={"reason": str(e)[:100]})

        # OrderExecutor
        self.upbit_client = None
        if cfg.run_mode == "live":
            access, secret = load_upbit_credentials(cfg)
            import pyupbit
            self.upbit_client = pyupbit.Upbit(access, secret)
            self.logger.info("upbit_client_initialized")
        self.order_executor = OrderExecutor(
            state=self.state,
            run_mode=cfg.run_mode,
            upbit_client=self.upbit_client,
            price_oracle=get_current_price,
        )

    def restore_state(self) -> None:
        """재시작 시 open positions/orders 로깅 + 동기화."""
        positions = self.state.list_open_positions()
        open_orders = self.state.list_open_orders()
        self.logger.info("state_restored", extra={
            "open_positions": len(positions),
            "open_orders": len(open_orders),
            "position_cells": [p.cell_key for p in positions],
        })
        # 시작 시 open orders 동기화 (C-1/C-2 정정)
        if open_orders:
            self.sync_open_orders()

    def sync_open_orders(self) -> dict[str, int]:
        """open orders 폴링 + filled 전이 시 position open/close 자동 호출 (C-1/C-2 정정 2026-04-25).

        문제 시나리오:
            - 라이브 buy → 응답 status='open' → filled 후 다음 cycle에서도 position 미생성
            - sell → status='open' 잔존 → 다음 cycle exit 신호 시 이중 매도 위험

        해결:
            cycle 시작 시 모든 open orders 폴링 → filled로 전이된 buy → open_position
            filled로 전이된 sell → close_position. canceled/rejected는 idempotency 그대로 두고 정리만.

        Returns: {"polled": int, "promoted_buy": int, "promoted_sell": int}
        """
        counts = {"polled": 0, "promoted_buy": 0, "promoted_sell": 0, "canceled": 0}
        for o in self.state.list_open_orders():
            counts["polled"] += 1
            try:
                # paper는 record가 이미 filled여서 list_open_orders에 없을 것. live만 polling.
                rec = self.order_executor.poll_status(o.order_uuid)
            except Exception:
                self.logger.exception("sync_poll_failed", extra={"order_uuid": o.order_uuid})
                continue
            if rec is None:
                continue
            if rec.status == "filled":
                if rec.side == "buy":
                    if self.state.get_position(rec.cell_key) is None:
                        try:
                            open_position_from_order(self.state, rec)
                            counts["promoted_buy"] += 1
                        except Exception:
                            self.logger.exception("sync_open_position_failed",
                                                   extra={"order_uuid": rec.order_uuid})
                elif rec.side == "sell":
                    if self.state.get_position(rec.cell_key) is not None:
                        try:
                            close_position_from_order(
                                self.state, ENGINE_ROOT / "logs", rec, run_mode=self.cfg.run_mode,
                            )
                            counts["promoted_sell"] += 1
                        except Exception:
                            self.logger.exception("sync_close_position_failed",
                                                   extra={"order_uuid": rec.order_uuid})
            elif rec.status in ("canceled", "rejected", "failed"):
                counts["canceled"] += 1
        if counts["polled"] > 0:
            self.logger.info("sync_open_orders_done", extra=counts)
        return counts

    def has_pending_order(self, cell_key: str, side: str) -> bool:
        """동일 cell + side의 status='open' 주문 존재 확인 (C-2 정정 — 이중 발행 방지)."""
        for o in self.state.list_open_orders():
            if o.cell_key == cell_key and o.side == side:
                return True
        return False

    def process_cell(self, cell: dict, trigger_utc: datetime) -> dict[str, Any]:
        """단일 cell 처리: 시세 → 신호 → 주문 → 포지션 → 알림. 결과 dict 반환."""
        cell_key = f"{cell.ticker}_{cell.strategy}"
        strat = self.strategies[cell_key]
        result: dict[str, Any] = {"cell_key": cell_key, "actions": []}

        # warmup 충분히: MA200 + 여유 100 bar = 300 bars
        df = fetch_ohlcv(cell.ticker, interval="day", count=300)

        pos = self.state.get_position(cell_key)
        in_position = pos is not None
        entry_price = pos.entry_price_krw if pos else None

        signal: SignalResult = strat.compute_signal(df, in_position=in_position, entry_price_krw=entry_price)
        result["signal"] = {"action": signal.action.value, "reason": signal.reason}
        self.logger.info("signal_evaluated", extra={
            "cell_key": cell_key, "action": signal.action.value,
            "in_position": in_position, "reason": signal.reason,
        })

        # 시그널 알림 (entry/exit/sl_exit 만)
        today_close = float(df["close"].iloc[-1])
        if signal.action != SignalAction.HOLD and self.notifier:
            self.notifier.notify_signal(
                cell_key=cell_key, action=signal.action.value,
                pair=cell.ticker, strategy=cell.strategy,
                price_krw=today_close, reason=signal.reason,
            )

        # 주문 처리 (C-2 정정: 동일 cell pending order 있으면 발행 X — 이중 주문 방지)
        if signal.action == SignalAction.ENTRY and not in_position:
            if self.has_pending_order(cell_key, "buy"):
                self.logger.info("skip_buy_pending", extra={"cell_key": cell_key})
                result["actions"].append({"type": "skip_buy_pending"})
                return result
            client_oid = make_client_oid(cell_key, "buy", trigger_utc)
            order = self.order_executor.place_order(OrderRequest(
                cell_key=cell_key, pair=cell.ticker, strategy=cell.strategy,
                side="buy", order_type="market",
                krw_amount=float(self.cfg.portfolio.stake_amount),
                client_oid=client_oid,
            ))
            result["actions"].append({"type": "buy", "order_uuid": order.order_uuid, "status": order.status})
            if order.status == "filled":
                pos = open_position_from_order(self.state, order)
                if self.notifier:
                    self.notifier.notify_order_filled(
                        cell_key=cell_key, side="buy", pair=cell.ticker,
                        price_krw=order.filled_price_krw or 0,
                        volume=order.filled_volume or 0,
                        krw_amount=order.requested_krw,
                        fees_krw=order.fees_krw or 0,
                        order_uuid=order.order_uuid, run_mode=self.cfg.run_mode,
                    )

        elif signal.action in (SignalAction.EXIT, SignalAction.SL_EXIT) and in_position:
            if self.has_pending_order(cell_key, "sell"):
                self.logger.info("skip_sell_pending", extra={"cell_key": cell_key})
                result["actions"].append({"type": "skip_sell_pending"})
                return result
            client_oid = make_client_oid(cell_key, "sell", trigger_utc)
            order = self.order_executor.place_order(OrderRequest(
                cell_key=cell_key, pair=cell.ticker, strategy=cell.strategy,
                side="sell", order_type="market",
                volume=pos.volume,
                client_oid=client_oid,
                metadata={"exit_reason": signal.action.value},
            ))
            result["actions"].append({"type": "sell", "order_uuid": order.order_uuid, "status": order.status})
            if order.status == "filled":
                pnl = close_position_from_order(
                    self.state, ENGINE_ROOT / "logs", order, run_mode=self.cfg.run_mode,
                )
                result["realized_pnl"] = pnl
                if self.notifier:
                    self.notifier.notify_order_filled(
                        cell_key=cell_key, side="sell", pair=cell.ticker,
                        price_krw=order.filled_price_krw or 0,
                        volume=order.filled_volume or 0,
                        krw_amount=order.filled_volume * order.filled_price_krw,
                        fees_krw=order.fees_krw or 0,
                        order_uuid=order.order_uuid, run_mode=self.cfg.run_mode,
                    )
        else:
            result["actions"].append({"type": "hold"})

        return result

    def run_cycle(self, trigger_utc: datetime) -> None:
        """단일 트리거 사이클: open orders 동기화 → cell 순차 처리 → 일일 요약."""
        self.logger.info("cycle_start", extra={"trigger_utc": trigger_utc.isoformat()})

        # C-1/C-2 정정: cycle 시작 시 open orders 동기화 (filled buy/sell 처리)
        self.sync_open_orders()

        cell_results = []
        for cell in self.cfg.pairs:
            try:
                r = self.process_cell(cell, trigger_utc)
                cell_results.append(r)
            except Exception:
                self.logger.exception("cell_processing_failed", extra={"cell": f"{cell.ticker}_{cell.strategy}"})
                if self.notifier:
                    self.notifier.notify_error(
                        key=f"cell_fail_{cell.ticker}_{cell.strategy}",
                        message=f"cell {cell.ticker}_{cell.strategy} 처리 실패. 로그 확인 필요.",
                    )

        # 일일 요약: open positions PnL
        positions = self.state.list_open_positions()
        cell_pnls: dict[str, float] = {}
        total_pnl = 0.0
        for p in positions:
            try:
                cur = get_current_price(p.pair)
                pnl = compute_unrealized_pnl(p, cur)
                cell_pnls[p.cell_key] = pnl.unrealized_pnl_krw
                total_pnl += pnl.unrealized_pnl_krw
            except Exception:
                self.logger.exception("pnl_calc_failed", extra={"cell": p.cell_key})

        if self.notifier:
            ts_kst = trigger_utc.astimezone(KST).strftime("%Y-%m-%d %H:%M")
            self.notifier.notify_summary(
                ts_kst=ts_kst, open_positions=len(positions), total_pnl_krw=total_pnl,
                cell_pnls=cell_pnls, run_mode=self.cfg.run_mode,
            )

        self.state.set_meta("last_run_ts", trigger_utc.isoformat())
        self.logger.info("cycle_done", extra={
            "open_positions": len(positions), "total_pnl_krw": total_pnl,
        })

    def run_forever(self) -> None:
        """일별 무한 루프 (KeyboardInterrupt 종료)."""
        self.restore_state()
        run_daily_loop(
            callback=self.run_cycle,
            hour_kst=self.cfg.schedule.signal_check_hour_kst,
            minute_kst=self.cfg.schedule.signal_check_minute,
        )


def main() -> int:
    """Engine 진입점.

    Usage:
        python -m engine.main          # daemon mode (KST 09:05 매일 무한 루프)
        python -m engine.main --once   # 즉시 1회 cycle 실행 후 종료 (W-5 정정 2026-04-25)
    """
    import argparse
    parser = argparse.ArgumentParser(description="coin-bot Custom engine (Stage 1 v2)")
    parser.add_argument("--once", action="store_true",
                        help="다음 트리거를 기다리지 않고 즉시 1회 cycle 실행")
    args = parser.parse_args()

    ensure_runtime_dirs()
    cfg = load_config()
    setup_logger(ENGINE_ROOT / "logs", cfg.logging.get("level", "INFO"))
    log = logging.getLogger("engine.main")

    log.info("engine_starting", extra={
        "run_mode": cfg.run_mode,
        "pairs": [(c.ticker, c.strategy) for c in cfg.pairs],
        "trigger_kst": f"{cfg.schedule.signal_check_hour_kst:02d}:{cfg.schedule.signal_check_minute:02d}",
        "once": args.once,
    })

    try:
        engine = Engine(cfg)
        if args.once:
            engine.restore_state()
            engine.run_cycle(datetime.now(timezone.utc))
        else:
            engine.run_forever()
    except KeyboardInterrupt:
        log.info("engine_interrupted")
        return 0
    except Exception:
        log.exception("engine_fatal")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
