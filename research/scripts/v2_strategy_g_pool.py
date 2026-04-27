"""V2-Strategy-G G-03 + G-04: KRW top 30 자동 fetch + 빈도 sanity.

박제 출처: docs/stage1-subplans/v2-strategy-g-active.md §2.4 후보 풀 + §5 G-04

설계:
- Upbit /v1/ticker 거래대금 24h 정렬 top 30 (market_warning="NONE")
- 각 market 90일 OHLCV (warmup 30 + 측정 60일) Strategy G signals
- vectorbt Portfolio.from_signals (sl_stop=0.03, tp_stop=0.05) — time stop은 daemon에서 별도
- 활동 빈도 측정: 일평균 entries / 측정 60일 기준 trades count
"""
from __future__ import annotations

import argparse
import json
import sys
import time
from datetime import timedelta
from pathlib import Path

import pandas as pd
import pyupbit
import requests
import vectorbt as vbt

sys.path.insert(0, str(Path(__file__).parent))
from strategy_g import STRATEGY_G_PARAMS, strategy_g_signals  # noqa: E402

vbt.settings.returns["year_freq"] = "365 days"

WINDOW_DAYS = 60
WARMUP_DAYS = 30


def fetch_top_markets(n: int = 30) -> list[dict]:
    """Upbit KRW 마켓 거래대금 24h top N (market_warning="NONE")."""
    all_markets = requests.get(
        "https://api.upbit.com/v1/market/all",
        params={"isDetails": "true"}, timeout=10,
    ).json()
    krw_meta = {
        m["market"]: {
            "korean_name": m.get("korean_name", ""),
            "market_warning": m.get("market_warning", "NONE"),
        }
        for m in all_markets if m.get("market", "").startswith("KRW-")
    }
    markets = list(krw_meta.keys())

    tickers = []
    BATCH = 100
    for i in range(0, len(markets), BATCH):
        chunk = markets[i:i + BATCH]
        r = requests.get(
            "https://api.upbit.com/v1/ticker",
            params={"markets": ",".join(chunk)}, timeout=10,
        )
        tickers.extend(r.json())

    rows = []
    for t in tickers:
        m = t.get("market")
        meta = krw_meta.get(m, {})
        if meta.get("market_warning", "NONE") != "NONE":
            continue
        rows.append({
            "market": m,
            "korean_name": meta.get("korean_name", ""),
            "trade_price": t.get("trade_price"),
            "acc_trade_price_24h": t.get("acc_trade_price_24h", 0) or 0,
        })
    rows.sort(key=lambda r: r["acc_trade_price_24h"] or 0, reverse=True)
    return rows[:n]


def fetch_window(market: str, end_utc: pd.Timestamp) -> pd.DataFrame:
    extended_start = end_utc - timedelta(days=WINDOW_DAYS + WARMUP_DAYS)
    end_kst = end_utc.tz_convert("Asia/Seoul")
    df = pyupbit.get_ohlcv_from(
        ticker=market, interval="day",
        fromDatetime=extended_start.tz_convert("Asia/Seoul").strftime("%Y-%m-%d %H:%M:%S"),
        to=end_kst.strftime("%Y-%m-%d %H:%M:%S"),
        period=0.2,
    )
    if df is None or df.empty:
        raise RuntimeError("empty OHLCV")
    if df.index.tz is None:
        df.index = df.index.tz_localize("Asia/Seoul").tz_convert("UTC")
    return df


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--top-n", type=int, default=30)
    parser.add_argument("--end-date", default="2026-04-25", help="측정 창 끝 (YYYY-MM-DD UTC)")
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()

    end_utc = pd.Timestamp(args.end_date, tz="UTC")
    window_start = end_utc - timedelta(days=WINDOW_DAYS)
    print(f"[window] {window_start.date()} ~ {end_utc.date()} ({WINDOW_DAYS}d)")

    print(f"[step 1] Upbit 거래대금 top {args.top_n} fetch...")
    pool = fetch_top_markets(args.top_n)
    for r in pool[:10]:
        print(f"  {r['market']:<14} ({r['korean_name'][:8]:<10}) "
              f"trade_price={r['trade_price']:>12,.0f}  vol_24h={r['acc_trade_price_24h']/1e8:>8.0f}억")
    print(f"  ... (total {len(pool)})")

    print(f"\n[step 2] Strategy G signals + 빈도 측정 (sl_stop=3%, tp_stop=5%)")
    print(f"  {'market':<14} {'entries':>8} {'trades':>7} {'win':>5} {'TotRet':>9} {'/day':>6}")

    cells = []
    total_trades = 0
    total_wins = 0
    fail_count = 0
    for r in pool:
        m = r["market"]
        time.sleep(0.25)
        try:
            df = fetch_window(m, end_utc)
        except Exception as e:
            print(f"  [{m:<12}] OHLCV fail: {str(e)[:40]}")
            fail_count += 1
            continue

        # Strategy G signals
        try:
            entries, exits = strategy_g_signals(df)
        except ValueError:
            fail_count += 1
            continue

        close = df["close"].loc[window_start:end_utc]
        entries_w = entries.loc[window_start:end_utc]
        exits_w = exits.loc[window_start:end_utc]

        if entries_w.sum() == 0:
            cells.append({
                "market": m, "entries": 0, "trades_total": 0, "trades_winning": 0,
                "total_return": 0.0, "trades_per_day": 0.0,
            })
            print(f"  {m:<14} {0:>8} {0:>7} {0:>5} {0:>+8.1f}% {0:>5.2f}")
            continue

        try:
            pf = vbt.Portfolio.from_signals(
                close, entries=entries_w, exits=exits_w,
                sl_stop=STRATEGY_G_PARAMS["SL_STOP"],
                tp_stop=STRATEGY_G_PARAMS["TP_STOP"],
                init_cash=1_000_000, fees=0.0005, slippage=0.0010, freq="1D",
            )
            t_count = int(pf.trades.count())
            t_win = int(pf.trades.winning.count())
            t_ret = float(pf.total_return())
        except Exception as e:
            print(f"  [{m:<12}] backtest fail: {str(e)[:40]}")
            fail_count += 1
            continue

        per_day = t_count / WINDOW_DAYS
        cells.append({
            "market": m, "entries": int(entries_w.sum()),
            "trades_total": t_count, "trades_winning": t_win,
            "total_return": t_ret, "trades_per_day": per_day,
        })
        total_trades += t_count
        total_wins += t_win
        print(f"  {m:<14} {int(entries_w.sum()):>8} {t_count:>7} {t_win:>5} {t_ret*100:>+8.1f}% {per_day:>5.2f}")

    print(f"\n[summary] cells={len(cells)} (failed={fail_count})")
    print(f"  total trades (60d, 30 cells): {total_trades}")
    print(f"  total wins:                   {total_wins}  ({total_wins/total_trades*100 if total_trades else 0:.0f}%)")
    print(f"  trades/day (전체):             {total_trades/WINDOW_DAYS:.2f}  (목표 ≥ 1.0)")

    output = {
        "window_start_utc": window_start.isoformat(),
        "window_end_utc": end_utc.isoformat(),
        "window_days": WINDOW_DAYS,
        "pool_top_n": args.top_n,
        "pool": pool,
        "cells": cells,
        "total_trades": total_trades,
        "total_wins": total_wins,
        "trades_per_day_overall": total_trades / WINDOW_DAYS,
        "strategy_g_params": STRATEGY_G_PARAMS,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with open(args.output, "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)
    print(f"\nsaved: {args.output}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
