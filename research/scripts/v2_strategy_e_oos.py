"""V2-Strategy-E C-04: OOS 3.8m 검증.

박제 출처:
- docs/stage1-subplans/v2-strategy-e-momentum.md §3.3 OOS 2026-01-01 ~ 2026-04-25
- §4.2 OOS Sharpe > 0.4 (in-sample 50%) AND trades ≥ 3

설계:
- in-sample GO cells만 평가 (cherry-pick X)
- 동일 Strategy E params + Portfolio params 적용
"""
from __future__ import annotations

import argparse
import json
import math
import sys
from datetime import timedelta
from pathlib import Path
from typing import Any

import pandas as pd
import pyupbit
import scipy.stats as scs
import vectorbt as vbt

sys.path.insert(0, str(Path(__file__).parent))
from strategy_e import STRATEGY_E_PARAMS, strategy_e_signals  # noqa: E402

vbt.settings.returns["year_freq"] = "365 days"

OOS_START = pd.Timestamp("2026-01-01", tz="UTC")
OOS_END = pd.Timestamp("2026-04-25", tz="UTC")
WARMUP_DAYS = 60

PORTFOLIO_PARAMS = {
    "INIT_CASH": 1_000_000, "FEES": 0.0005, "SLIPPAGE": 0.0010, "FREQ": "1D",
}
OOS_SHARPE_THRESHOLD = 0.4
OOS_MIN_TRADES = 3


def fetch_oos(ticker: str) -> pd.DataFrame:
    extended_start = OOS_START - timedelta(days=WARMUP_DAYS)
    end_kst = OOS_END.tz_convert("Asia/Seoul")
    df = pyupbit.get_ohlcv_from(
        ticker=ticker, interval="day",
        fromDatetime=extended_start.tz_convert("Asia/Seoul").strftime("%Y-%m-%d %H:%M:%S"),
        to=end_kst.strftime("%Y-%m-%d %H:%M:%S"),
        period=0.2,
    )
    if df is None or df.empty:
        raise RuntimeError(f"empty OHLCV: {ticker}")
    if df.index.tz is None:
        df.index = df.index.tz_localize("Asia/Seoul").tz_convert("UTC")
    return df


def run_cell(market: str, df: pd.DataFrame) -> dict[str, Any]:
    entries, exits = strategy_e_signals(df)
    close = df["close"].loc[OOS_START:OOS_END]
    entries = entries.loc[OOS_START:OOS_END]
    exits = exits.loc[OOS_START:OOS_END]

    pf = vbt.Portfolio.from_signals(
        close, entries=entries, exits=exits,
        sl_stop=STRATEGY_E_PARAMS["SL_STOP"],
        init_cash=PORTFOLIO_PARAMS["INIT_CASH"],
        fees=PORTFOLIO_PARAMS["FEES"],
        slippage=PORTFOLIO_PARAMS["SLIPPAGE"],
        freq=PORTFOLIO_PARAMS["FREQ"],
    )
    sharpe = float(pf.sharpe_ratio(year_freq="365 days")) if pf.trades.count() > 0 else 0.0
    return {
        "market": market,
        "sharpe": sharpe,
        "total_return": float(pf.total_return()),
        "max_drawdown": float(pf.max_drawdown()),
        "trades_total": int(pf.trades.count()),
        "trades_winning": int(pf.trades.winning.count()),
        "entries_signals": int(entries.sum()),
        "exits_signals": int(exits.sum()),
        "T": int(len(close)),
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--in-sample-json", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    with open(args.in_sample_json, encoding="utf-8") as f:
        in_sample = json.load(f)
    go_cells = in_sample["go_cells"]
    in_sample_by_market = {c["market"]: c for c in in_sample["cells"]}

    print(f"[OOS window] {OOS_START.date()} ~ {OOS_END.date()}")
    print(f"[in-sample GO cells] {go_cells}\n")

    results: list[dict[str, Any]] = []
    print(f"  {'market':<14} {'IS Shp':>7} {'OOS Shp':>8} {'OOS Ret':>9} {'MDD':>7} {'trades':>7} {'OOS Pass':>9}")
    for m in go_cells:
        try:
            df = fetch_oos(m)
            stats = run_cell(m, df)
        except Exception as e:
            print(f"  [{m}] FAIL: {e}")
            continue

        is_sharpe = in_sample_by_market[m]["sharpe"]
        oos_pass = (
            stats["sharpe"] >= OOS_SHARPE_THRESHOLD
            and stats["trades_total"] >= OOS_MIN_TRADES
        )
        stats["in_sample_sharpe"] = is_sharpe
        stats["oos_pass"] = oos_pass
        results.append(stats)

        ret_pct = stats["total_return"] * 100
        mdd_pct = stats["max_drawdown"] * 100
        print(f"  {m:<14} {is_sharpe:>7.3f} {stats['sharpe']:>8.3f} "
              f"{ret_pct:>+8.1f}% {mdd_pct:>6.1f}% {stats['trades_total']:>7} "
              f"{'PASS' if oos_pass else 'FAIL':>9}")

    final_go = [r["market"] for r in results if r["oos_pass"]]
    print(f"\n[final] in-sample GO + OOS Pass cells ({len(final_go)}): {final_go}")
    print(f"[criteria] OOS Sharpe ≥ {OOS_SHARPE_THRESHOLD} AND trades ≥ {OOS_MIN_TRADES}")

    output_data = {
        "oos_start_utc": OOS_START.isoformat(),
        "oos_end_utc": OOS_END.isoformat(),
        "oos_sharpe_threshold": OOS_SHARPE_THRESHOLD,
        "oos_min_trades": OOS_MIN_TRADES,
        "in_sample_go_cells": go_cells,
        "final_go_cells": final_go,
        "cells": results,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with open(args.output, "w", encoding="utf-8") as f:
        json.dump(output_data, f, ensure_ascii=False, indent=2)
    print(f"saved: {args.output}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
