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
from engine.market_data import (
    fetch_binance_btc_usd, fetch_ohlcv, fetch_top_krw_markets,
    fetch_usdkrw, get_current_price,
)
from engine.notifier import DiscordNotifier
from engine.order import OrderExecutor, OrderRequest, make_client_oid
from engine.position import close_position_from_order, compute_unrealized_pnl, open_position_from_order
from engine.scheduler import run_daily_loop, next_trigger_at
from engine.state import StateStore
from engine.strategies import SignalAction, SignalResult, StrategyA, StrategyD, StrategyG, StrategyI


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
    if name == "G":
        return StrategyG(
            entry_bar_pct=cfg.strategy_g.entry_bar_pct,
            vol_avg=cfg.strategy_g.vol_avg,
            vol_mult=cfg.strategy_g.vol_mult,
            short_break=cfg.strategy_g.short_break,
            sl_pct=cfg.strategy_g.sl_pct,
            tp_pct=cfg.strategy_g.tp_pct,
            time_stop_bars=cfg.strategy_g.time_stop_bars,
        )
    raise ValueError(f"unknown strategy: {name}")


class Engine:
    """orchestration 엔진."""

    def __init__(self, cfg: Config):
        self.cfg = cfg
        self.logger = logging.getLogger("engine.main")
        self.state = StateStore(ENGINE_ROOT / cfg.state["db_path"])

        # 정적 cells (BT-A/D 등 strategy != "G")
        self._static_pairs: list = [c for c in cfg.pairs if c.strategy != "G"]
        # config.yaml의 G cells = fallback (네트워크 fail 시)
        self._g_fallback_pairs: list = [c for c in cfg.pairs if c.strategy == "G"]
        # 매 cycle 시작 시 갱신되는 동적 G pairs
        self._dynamic_g_pairs: list = []

        # Strategy 인스턴스 (cell_key별 cache, 매 cycle init/갱신)
        self.strategies: dict = {
            f"{c.ticker}_{c.strategy}": build_strategy(c.strategy, cfg)
            for c in self._static_pairs
        }

        # Notifier (Discord webhook 없으면 None)
        # 4h worktree 식별용 prefix — engine root 경로에 "coin-bot-4h" 포함 여부로 자동 감지
        msg_prefix = "[4h] " if "coin-bot-4h" in str(ENGINE_ROOT) else ""
        self.notifier: DiscordNotifier | None = None
        try:
            url = load_discord_webhook(cfg)
            self.notifier = DiscordNotifier(url, msg_prefix=msg_prefix)
            self.logger.info("notifier_initialized", extra={"msg_prefix": msg_prefix})
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

        # Strategy I (Mean Reversion) — Portfolio-level, optional (artifact 있을 때만)
        # 4h artifact 우선 (coin-bot-4h worktree), 없으면 기본 strategy_i (일봉)
        self.strategy_i: StrategyI | None = None
        for sub in ("strategy_i_4h", "strategy_i"):
            i_artifact = ENGINE_ROOT / "data" / sub
            if (i_artifact / "ridge_model.pkl").exists():
                try:
                    self.strategy_i = StrategyI(artifact_dir=i_artifact)
                    self.logger.info("strategy_i_initialized", extra={
                        "features": len(self.strategy_i.feature_cols),
                        "artifact": sub,
                    })
                    break
                except Exception as e:
                    self.logger.warning("strategy_i_init_failed", extra={"err": str(e)[:100]})

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

        # warmup 충분히: MA200 + 여유 100 bar = 300 bars (Strategy G는 적게 필요하나 통일)
        df = fetch_ohlcv(cell.ticker, interval="day", count=300)

        pos = self.state.get_position(cell_key)
        in_position = pos is not None
        entry_price = pos.entry_price_krw if pos else None

        # bars_held 계산 (Strategy G time stop용)
        bars_held: int | None = None
        if pos and pos.entry_ts_utc:
            try:
                entry_ts = datetime.fromisoformat(pos.entry_ts_utc)
                if entry_ts.tzinfo is None:
                    entry_ts = entry_ts.replace(tzinfo=timezone.utc)
                bars_held = (trigger_utc - entry_ts).days
            except (ValueError, TypeError):
                bars_held = None

        signal: SignalResult = strat.compute_signal(
            df, in_position=in_position, entry_price_krw=entry_price, bars_held=bars_held,
        )
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
            # max_open_positions 한도 체크 (Strategy G 등 다중 cell 운영 시)
            current_open = len(self.state.list_open_positions())
            if current_open >= self.cfg.portfolio.max_open_positions:
                self.logger.info("skip_buy_max_open", extra={
                    "cell_key": cell_key, "current_open": current_open,
                    "max_open": self.cfg.portfolio.max_open_positions,
                })
                result["actions"].append({"type": "skip_buy_max_open"})
                return result
            if self.has_pending_order(cell_key, "buy"):
                self.logger.info("skip_buy_pending", extra={"cell_key": cell_key})
                result["actions"].append({"type": "skip_buy_pending"})
                return result
            # cell별 stake_amount_override (Strategy G 50k vs default)
            stake = float(cell.stake_amount_override or self.cfg.portfolio.stake_amount)
            client_oid = make_client_oid(cell_key, "buy", trigger_utc)
            order = self.order_executor.place_order(OrderRequest(
                cell_key=cell_key, pair=cell.ticker, strategy=cell.strategy,
                side="buy", order_type="market",
                krw_amount=stake,
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

    def refresh_dynamic_g_pairs(self) -> list:
        """매 cycle 시작 시 KRW 거래대금 top 30 자동 fetch + G cells 동적 갱신.

        박제: docs/stage1-subplans/v2-strategy-g-active.md §2.4 (동적 후보 풀)
        cycle 1 #5 회피: 자동 fetch 결과 그대로 채택, cherry-pick X
        """
        from engine.config import CellConfig
        top_markets = fetch_top_krw_markets(n=30)
        if not top_markets:
            # 네트워크 fail → fallback (config.yaml 정적 G cells)
            self.logger.warning("dynamic_g_fetch_failed_fallback",
                                 extra={"fallback_count": len(self._g_fallback_pairs)})
            return self._g_fallback_pairs

        # 보유 중인 G position의 ticker는 강제 포함 (exit 평가 위해)
        open_g_tickers = {
            p.cell_key.replace("_G", "") for p in self.state.list_open_positions()
            if p.cell_key.endswith("_G")
        }
        for t in open_g_tickers:
            if t not in top_markets:
                top_markets.append(t)

        stake = 50_000  # sub-plan §2.3 박제
        dynamic = [
            CellConfig(ticker=m, strategy="G", stake_amount_override=stake)
            for m in top_markets
        ]
        # strategies dict 갱신 (신규 cells 추가)
        for cell in dynamic:
            key = f"{cell.ticker}_G"
            if key not in self.strategies:
                self.strategies[key] = build_strategy("G", self.cfg)
        self._dynamic_g_pairs = dynamic
        self.logger.info("dynamic_g_pairs_refreshed",
                          extra={"count": len(dynamic), "open_g_forced": list(open_g_tickers)})
        return dynamic

    def process_strategy_i(self, trigger_utc: datetime) -> dict:
        """Strategy I (Portfolio-level Mean Reversion via inverse).

        매 cycle 시작 시:
        1. 보유 중 Strategy I positions exit 평가 (SL/TP/time stop)
        2. 새 진입: bottom decile 5 — 보유 < 5 일 때만 추가
        3. stake: 1만원 × cell (사용자 박제 5만원 한도)
        """
        if self.strategy_i is None:
            return {"skipped": True, "reason": "no_strategy_i_artifact"}

        result: dict = {"exits": [], "entries": [], "skipped_full": False}

        interval = getattr(self.strategy_i, "interval", "day")
        bars_per_day = getattr(self.strategy_i, "bars_per_day", 1)
        # 1. 보유 포지션 exit 평가
        open_positions = self.state.list_open_positions()
        i_positions = [p for p in open_positions if p.cell_key.endswith("_I")]
        for pos in i_positions:
            try:
                df = fetch_ohlcv(pos.pair, interval=interval, count=2)
                today_low = float(df["low"].iloc[-1])
                today_close = float(df["close"].iloc[-1])
                entry_ts = datetime.fromisoformat(pos.entry_ts_utc)
                if entry_ts.tzinfo is None:
                    entry_ts = entry_ts.replace(tzinfo=timezone.utc)
                # bars_held: time_stop_bars는 bars 단위 (일봉=일, 4h=4시간 bar)
                if bars_per_day == 1:
                    bars_held = (trigger_utc - entry_ts).days
                else:
                    bars_held = int((trigger_utc - entry_ts).total_seconds() // (24 * 3600 / bars_per_day))
                decision = self.strategy_i.check_exit(today_low, today_close, pos.entry_price_krw, bars_held)
                if decision:
                    action_str, reason = decision
                    if self.has_pending_order(pos.cell_key, "sell"):
                        continue
                    client_oid = make_client_oid(pos.cell_key, "sell", trigger_utc)
                    order = self.order_executor.place_order(OrderRequest(
                        cell_key=pos.cell_key, pair=pos.pair, strategy="I",
                        side="sell", order_type="market",
                        volume=pos.volume,
                        client_oid=client_oid,
                        metadata={"exit_reason": action_str, "reason": reason},
                    ))
                    if order.status == "filled":
                        pnl = close_position_from_order(
                            self.state, ENGINE_ROOT / "logs", order, run_mode=self.cfg.run_mode,
                        )
                        result["exits"].append({"cell_key": pos.cell_key, "reason": action_str, "pnl": pnl})
                        if self.notifier:
                            self.notifier.notify_order_filled(
                                cell_key=pos.cell_key, side="sell", pair=pos.pair,
                                price_krw=order.filled_price_krw or 0,
                                volume=order.filled_volume or 0,
                                krw_amount=(order.filled_volume or 0) * (order.filled_price_krw or 0),
                                fees_krw=order.fees_krw or 0,
                                order_uuid=order.order_uuid, run_mode=self.cfg.run_mode,
                            )
            except Exception:
                self.logger.exception("strategy_i_exit_failed", extra={"cell_key": pos.cell_key})

        # 2. 새 진입 — 보유 < 5 일 때만
        i_count_after = len([p for p in self.state.list_open_positions() if p.cell_key.endswith("_I")])
        slots = max(0, self.strategy_i.bottom_decile_n - i_count_after)
        if slots == 0:
            result["skipped_full"] = True
            return result

        # universe + macro fetch
        try:
            top_markets = fetch_top_krw_markets(n=50)
            if not top_markets:
                result["error"] = "fetch_top_failed"
                return result
            universe_ohlcv = {}
            count = 300 if bars_per_day == 1 else 200 * bars_per_day  # 4h: 1200 bars (~200d)
            for m in top_markets:
                try:
                    universe_ohlcv[m] = fetch_ohlcv(m, interval=interval, count=count).reset_index().rename(columns={"index": "ts_utc"})
                except Exception:
                    continue
            if "KRW-BTC" not in universe_ohlcv:
                result["error"] = "btc_missing"
                return result
            btc_global = fetch_binance_btc_usd("2023-01-01")
            fx = fetch_usdkrw("2023-01-01")
            if btc_global.empty or fx.empty:
                result["error"] = "macro_fetch_failed"
                return result
        except Exception as e:
            self.logger.exception("strategy_i_universe_fetch_failed")
            result["error"] = f"fetch_exception: {str(e)[:80]}"
            return result

        # bottom decile 5 — 보유 중 ticker는 제외
        held_tickers = {p.pair for p in self.state.list_open_positions() if p.cell_key.endswith("_I")}
        try:
            candidates = self.strategy_i.select_bottom_decile(universe_ohlcv, btc_global, fx)
        except Exception as e:
            self.logger.exception("strategy_i_select_failed")
            result["error"] = f"select_exception: {str(e)[:80]}"
            return result

        # max_open_positions 한도 내 추가
        new_entries = 0
        for cand in candidates:
            if new_entries >= slots:
                break
            if cand["market"] in held_tickers:
                continue
            cell_key = f"{cand['market']}_I"
            if self.has_pending_order(cell_key, "buy"):
                continue
            current_open = len(self.state.list_open_positions())
            if current_open >= self.cfg.portfolio.max_open_positions:
                break

            stake = 10_000.0  # sub-plan §1.2: 5 cells × 1만 = 5만 한도
            client_oid = make_client_oid(cell_key, "buy", trigger_utc)
            try:
                order = self.order_executor.place_order(OrderRequest(
                    cell_key=cell_key, pair=cand["market"], strategy="I",
                    side="buy", order_type="market",
                    krw_amount=stake,
                    client_oid=client_oid,
                    metadata={"score": cand["score"], "rank": cand["rank"]},
                ))
                if order.status == "filled":
                    open_position_from_order(self.state, order)
                    result["entries"].append({"cell_key": cell_key, "score": cand["score"], "rank": cand["rank"]})
                    new_entries += 1
                    if self.notifier:
                        self.notifier.notify_order_filled(
                            cell_key=cell_key, side="buy", pair=cand["market"],
                            price_krw=order.filled_price_krw or 0,
                            volume=order.filled_volume or 0,
                            krw_amount=order.requested_krw,
                            fees_krw=order.fees_krw or 0,
                            order_uuid=order.order_uuid, run_mode=self.cfg.run_mode,
                        )
            except Exception:
                self.logger.exception("strategy_i_entry_failed", extra={"cell_key": cell_key})

        self.logger.info("strategy_i_done", extra=result)
        return result

    def run_cycle(self, trigger_utc: datetime) -> None:
        """단일 트리거 사이클: open orders 동기화 → cell 순차 처리 → 일일 요약."""
        self.logger.info("cycle_start", extra={"trigger_utc": trigger_utc.isoformat()})

        # C-1/C-2 정정: cycle 시작 시 open orders 동기화 (filled buy/sell 처리)
        self.sync_open_orders()

        # 4h mode: Strategy I 단독 — BT-A/D + G 비활성
        bars_per_day_local = getattr(self.strategy_i, "bars_per_day", 1) if self.strategy_i else 1
        if bars_per_day_local == 6:
            all_pairs = []   # 4h cycle은 Strategy I만
        else:
            # 동적 G cells 갱신 (KRW 거래대금 top 30, 매 cycle 자동 fetch)
            g_pairs = self.refresh_dynamic_g_pairs()
            all_pairs = self._static_pairs + g_pairs

        cell_results = []
        for cell in all_pairs:
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

        # Strategy I (Portfolio-level Mean Reversion) — cell 처리 후
        try:
            i_result = self.process_strategy_i(trigger_utc)
            if not i_result.get("skipped"):
                self.logger.info("strategy_i_cycle_done", extra=i_result)
        except Exception:
            self.logger.exception("strategy_i_cycle_failed")

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
        """일별 또는 4시간 무한 루프 (KeyboardInterrupt 종료)."""
        self.restore_state()
        # 4h artifact 사용 시 4시간 cycle
        bars_per_day = getattr(self.strategy_i, "bars_per_day", 1) if self.strategy_i else 1
        if bars_per_day == 6:
            from engine.scheduler import run_4h_loop
            self.logger.info("scheduler_mode_4h")
            run_4h_loop(
                callback=self.run_cycle,
                minute_offset=self.cfg.schedule.signal_check_minute,
            )
        else:
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
