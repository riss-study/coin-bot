"""V2-Strategy-E C-03: in-sample 24m grid + Sharpe + DSR.

박제 출처:
- docs/stage1-subplans/v2-strategy-e-momentum.md §3.3 (in-sample 2024-01 ~ 2025-12)
- research/notebooks/08_insample_grid.ipynb (DSR 계산 패턴)
- Bailey & López de Prado 2014 (DSR 공식)

후보:
- Tier 3 PASSED markets (research/notebooks/results/v2_tier3_pool.json)
- Strategy E 단독 (사전 박제 §2)

Go 기준 (사전 박제):
- Sharpe (in-sample 24m) > 0.8 AND DSR_z > 0

사용:
    cd /Users/riss/project/coin-bot
    source research/.venv/bin/activate
    python research/scripts/v2_strategy_e_grid.py \\
        --pool-json research/notebooks/results/v2_tier3_pool.json \\
        --output research/notebooks/results/v2_strategy_e_grid.json
"""
from __future__ import annotations

import argparse
import json
import math
import sys
from datetime import timedelta
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
import pyupbit
import scipy.stats as scs
import vectorbt as vbt

sys.path.insert(0, str(Path(__file__).parent))
from strategy_e import STRATEGY_E_PARAMS, strategy_e_signals  # noqa: E402


# vectorbt year_freq 글로벌 (W2-03 패턴)
vbt.settings.returns["year_freq"] = "365 days"

IN_SAMPLE_START = pd.Timestamp("2024-01-01", tz="UTC")
IN_SAMPLE_END = pd.Timestamp("2025-12-31", tz="UTC")
WARMUP_DAYS = 60  # MA20/Donchian5 등 warmup

PORTFOLIO_PARAMS = {
    "INIT_CASH": 1_000_000,
    "FEES": 0.0005,
    "SLIPPAGE": 0.0010,    # 알트 박제 (sub-plan §2.3)
    "FREQ": "1D",
}

GO_SHARPE_THRESHOLD = 0.8
GO_DSR_Z_THRESHOLD = 0.0
EULER_MASCHERONI = 0.5772156649015329


def fetch_in_sample(ticker: str) -> pd.DataFrame:
    """in-sample 기간 + warmup OHLCV fetch."""
    extended_start = IN_SAMPLE_START - timedelta(days=WARMUP_DAYS)
    end_kst = IN_SAMPLE_END.tz_convert("Asia/Seoul")
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
    """단일 cell: Strategy E signals + Portfolio + stats."""
    entries, exits = strategy_e_signals(df)
    # in-sample 기간만 slice (signals는 warmup 포함, slice 후 사용)
    close = df["close"].loc[IN_SAMPLE_START:IN_SAMPLE_END]
    entries = entries.loc[IN_SAMPLE_START:IN_SAMPLE_END]
    exits = exits.loc[IN_SAMPLE_START:IN_SAMPLE_END]

    pf = vbt.Portfolio.from_signals(
        close, entries=entries, exits=exits,
        sl_stop=STRATEGY_E_PARAMS["SL_STOP"],
        init_cash=PORTFOLIO_PARAMS["INIT_CASH"],
        fees=PORTFOLIO_PARAMS["FEES"],
        slippage=PORTFOLIO_PARAMS["SLIPPAGE"],
        freq=PORTFOLIO_PARAMS["FREQ"],
    )

    sharpe = float(pf.sharpe_ratio(year_freq="365 days"))
    total_return = float(pf.total_return())
    mdd = float(pf.max_drawdown())
    trades_total = int(pf.trades.count())
    wins = int(pf.trades.winning.count())

    returns = pf.returns().dropna()
    skew = float(scs.skew(returns.values)) if len(returns) > 2 else 0.0
    # Bailey 2014: raw kurtosis = fisher + 3
    kurt = float(scs.kurtosis(returns.values, fisher=False)) if len(returns) > 2 else 3.0

    return {
        "market": market,
        "sharpe": sharpe,
        "total_return": total_return,
        "max_drawdown": mdd,
        "trades_total": trades_total,
        "trades_winning": wins,
        "entries_signals": int(entries.sum()),
        "exits_signals": int(exits.sum()),
        "returns_skew": skew,
        "returns_kurtosis_raw": kurt,
        "T": int(len(returns)),
    }


def compute_sr_0(variance_sr: float, n_trials: int) -> float:
    """Bailey 2014 expected max SR under H_0."""
    phi_inv_n = scs.norm.ppf(1 - 1.0 / n_trials)
    phi_inv_ne = scs.norm.ppf(1 - 1.0 / (n_trials * math.e))
    sr_0 = math.sqrt(variance_sr) * (
        (1 - EULER_MASCHERONI) * phi_inv_n + EULER_MASCHERONI * phi_inv_ne
    )
    return sr_0


def compute_dsr(sr_hat: float, sr_0: float, skew: float, kurt_raw: float, T: int) -> tuple[float, float]:
    """Bailey 2014 DSR_z + DSR_prob.

    DSR_z = (SR_hat - SR_0) × sqrt((T - 1) / (1 - γ_3 × SR_hat + ((γ_4 - 1) / 4) × SR_hat²))

    Note: 분모 박제는 SR_hat 사용 (Bailey 2014 식 (10)).
    """
    denom = 1.0 - skew * sr_hat + ((kurt_raw - 1.0) / 4.0) * sr_hat ** 2
    if denom <= 0 or T < 2:
        return 0.0, 0.5
    dsr_z = (sr_hat - sr_0) * math.sqrt((T - 1) / denom)
    dsr_prob = float(scs.norm.cdf(dsr_z))
    return float(dsr_z), dsr_prob


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--pool-json", type=Path, required=True, help="C-01 결과 JSON")
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    with open(args.pool_json, encoding="utf-8") as f:
        pool = json.load(f)
    markets: list[str] = pool["passed_markets"]
    print(f"[pool] PASSED markets ({len(markets)}): {markets}")

    print(f"\n[fetch] in-sample {IN_SAMPLE_START.date()} ~ {IN_SAMPLE_END.date()} (warmup {WARMUP_DAYS}d)...")
    cells: list[dict[str, Any]] = []
    for m in markets:
        try:
            df = fetch_in_sample(m)
            print(f"  [{m}] bars={len(df)} ({df.index[0].date()} ~ {df.index[-1].date()})")
            stats = run_cell(m, df)
            cells.append(stats)
        except Exception as e:
            print(f"  [{m}] FAIL: {e}")

    if not cells:
        print("no cells evaluated")
        return 1

    sharpes = np.array([c["sharpe"] for c in cells])
    n_trials = len(cells)
    v_empirical = float(np.var(sharpes, ddof=1)) if len(sharpes) > 1 else 1.0
    sr_0 = compute_sr_0(v_empirical, n_trials)

    print(f"\n[grid] N_trials={n_trials}, V_empirical={v_empirical:.4f}, SR_0={sr_0:.4f}")
    print(f"[Go 기준] Sharpe > {GO_SHARPE_THRESHOLD} AND DSR_z > {GO_DSR_Z_THRESHOLD}\n")

    # cell별 DSR + Go 판정
    print(f"  {'market':<14} {'Sharpe':>8} {'TotRet':>9} {'MDD':>7} {'trades':>7} {'win':>5} {'DSR_z':>8} {'Go':>5}")
    for c in cells:
        dsr_z, dsr_prob = compute_dsr(c["sharpe"], sr_0, c["returns_skew"], c["returns_kurtosis_raw"], c["T"])
        c["dsr_z"] = dsr_z
        c["dsr_prob"] = dsr_prob
        c["go"] = (c["sharpe"] > GO_SHARPE_THRESHOLD) and (dsr_z > GO_DSR_Z_THRESHOLD)
        ret_pct = c["total_return"] * 100
        mdd_pct = c["max_drawdown"] * 100
        print(f"  {c['market']:<14} {c['sharpe']:>8.3f} {ret_pct:>+8.1f}% {mdd_pct:>6.1f}% "
              f"{c['trades_total']:>7} {c['trades_winning']:>5} {dsr_z:>8.3f} {'GO' if c['go'] else '-':>5}")

    go_cells = [c["market"] for c in cells if c["go"]]
    print(f"\n[summary] GO cells ({len(go_cells)}): {go_cells}")

    output_data = {
        "in_sample_start_utc": IN_SAMPLE_START.isoformat(),
        "in_sample_end_utc": IN_SAMPLE_END.isoformat(),
        "n_trials": n_trials,
        "v_empirical": v_empirical,
        "sr_0": sr_0,
        "go_sharpe_threshold": GO_SHARPE_THRESHOLD,
        "go_dsr_z_threshold": GO_DSR_Z_THRESHOLD,
        "go_cells": go_cells,
        "cells": cells,
        "strategy_e_params": STRATEGY_E_PARAMS,
        "portfolio_params": PORTFOLIO_PARAMS,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with open(args.output, "w", encoding="utf-8") as f:
        json.dump(output_data, f, ensure_ascii=False, indent=2)
    print(f"saved: {args.output}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
