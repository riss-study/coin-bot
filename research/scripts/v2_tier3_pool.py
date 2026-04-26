"""V2-Strategy-E Tier 3 후보 풀 자동 필터 (C-01).

박제 출처:
- docs/stage1-subplans/v2-strategy-e-momentum.md §3.1 필터 규칙
- cycle 1 #5 회피: 추정 리스트 박제 X, 자동 필터만

필터 규칙 (사전 박제):
- (1) CoinGecko 시총 top 30 (KRW 환산, 측정 시점 스냅샷)
- (2) Upbit KRW 마켓 교집합 (CoinGecko 심볼 ↔ Upbit ticker)
- (3) 측정 창 6개월 (2025-10-26 ~ 2026-04-25 UTC) OHLCV
- (4) 일평균 거래대금 ≥ 100억 KRW
- (5) 일별 return 표준편차 ≥ 0.03 (3%)
- (6) bar 수 ≥ 180 (상장 ≥ 180일)
- (7) Upbit market_warning != "CAUTION" (투자유의 제외)

사용:
    cd /Users/riss/project/coin-bot
    source research/.venv/bin/activate
    python research/scripts/v2_tier3_pool.py \\
        --window-end 2026-04-25 \\
        --output research/notebooks/results/v2_tier3_pool.json
"""
from __future__ import annotations

import argparse
import json
import time
from dataclasses import asdict, dataclass
from datetime import datetime, timedelta, timezone
from pathlib import Path

import numpy as np
import pandas as pd
import pyupbit
import requests


COINGECKO_BASE = "https://api.coingecko.com/api/v3"
UPBIT_BASE = "https://api.upbit.com/v1"
WINDOW_DAYS = 180  # 측정 창 6개월
TURNOVER_THRESHOLD = 10_000_000_000  # 100억 KRW
VOLATILITY_THRESHOLD = 0.03  # 3% 일별 std
MIN_BARS = 180


@dataclass
class CandidateRow:
    market: str                    # "KRW-XXX"
    symbol: str
    name: str
    market_cap_krw: float
    avg_turnover_krw: float        # 일평균 거래대금
    daily_return_std: float        # 일별 return 표준편차
    bar_count: int
    market_warning: str            # "NONE" | "CAUTION"
    passed: bool
    fail_reasons: list[str]


def fetch_coingecko_top(n: int = 30) -> list[dict]:
    resp = requests.get(
        f"{COINGECKO_BASE}/coins/markets",
        params={
            "vs_currency": "krw",
            "order": "market_cap_desc",
            "per_page": n,
            "page": 1,
        },
        timeout=15,
    )
    resp.raise_for_status()
    return resp.json()


def fetch_upbit_krw_markets() -> dict[str, dict]:
    """Upbit KRW 마켓 + market_warning."""
    resp = requests.get(
        f"{UPBIT_BASE}/market/all",
        params={"isDetails": "true"},
        timeout=10,
    )
    resp.raise_for_status()
    out = {}
    for m in resp.json():
        market = m.get("market", "")
        if not market.startswith("KRW-"):
            continue
        out[market] = {
            "korean_name": m.get("korean_name", ""),
            "market_warning": m.get("market_warning", "NONE"),
        }
    return out


def evaluate_market(
    market: str,
    cg: dict,
    upbit_meta: dict,
    window_end_utc: pd.Timestamp,
) -> CandidateRow:
    """단일 market 측정 창 OHLCV 분석 + 필터 평가."""
    fail: list[str] = []
    bar_count = 0
    avg_turnover = 0.0
    return_std = 0.0

    # OHLCV fetch (warmup 포함하지 않음 — 측정 창만)
    try:
        end_kst = window_end_utc.tz_convert("Asia/Seoul")
        df = pyupbit.get_ohlcv_from(
            ticker=market, interval="day",
            fromDatetime=(end_kst - timedelta(days=WINDOW_DAYS + 5)).strftime("%Y-%m-%d %H:%M:%S"),
            to=end_kst.strftime("%Y-%m-%d %H:%M:%S"),
            period=0.2,
        )
    except Exception as e:
        fail.append(f"ohlcv_fetch_error: {str(e)[:60]}")
        df = None

    if df is None or df.empty:
        fail.append("ohlcv_empty")
    else:
        if df.index.tz is None:
            df.index = df.index.tz_localize("Asia/Seoul").tz_convert("UTC")
        # 측정 창 정확히 slice
        start_utc = window_end_utc - timedelta(days=WINDOW_DAYS)
        df = df.loc[start_utc:window_end_utc]
        bar_count = len(df)
        if bar_count < MIN_BARS:
            fail.append(f"bar_count<{MIN_BARS} ({bar_count})")
        if bar_count > 0:
            turnover = (df["volume"] * df["close"]).mean()
            avg_turnover = float(turnover)
            if avg_turnover < TURNOVER_THRESHOLD:
                fail.append(f"turnover<{TURNOVER_THRESHOLD/1e8:.0f}억 ({avg_turnover/1e8:.1f}억)")
            ret = df["close"].pct_change().dropna()
            return_std = float(ret.std()) if len(ret) > 1 else 0.0
            if return_std < VOLATILITY_THRESHOLD:
                fail.append(f"std<{VOLATILITY_THRESHOLD} ({return_std:.4f})")

    warning = upbit_meta.get("market_warning", "NONE")
    if warning != "NONE":
        fail.append(f"market_warning={warning}")

    return CandidateRow(
        market=market,
        symbol=cg.get("symbol", "").upper(),
        name=cg.get("name", ""),
        market_cap_krw=float(cg.get("market_cap", 0) or 0),
        avg_turnover_krw=avg_turnover,
        daily_return_std=return_std,
        bar_count=bar_count,
        market_warning=warning,
        passed=(len(fail) == 0),
        fail_reasons=fail,
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--window-end", default="2026-04-25", help="측정 창 끝 (YYYY-MM-DD UTC)")
    parser.add_argument("--top-n", type=int, default=30, help="CoinGecko top N (default 30)")
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()

    window_end = pd.Timestamp(args.window_end, tz="UTC")
    print(f"[window] end={window_end} (-{WINDOW_DAYS}d 측정)")

    # 1. CoinGecko top 30
    print(f"[step 1] CoinGecko top {args.top_n} 시총 fetch...")
    cg_data = fetch_coingecko_top(args.top_n)
    print(f"  {len(cg_data)} coins")

    # 2. Upbit KRW 마켓
    print(f"[step 2] Upbit KRW 마켓 + market_warning fetch...")
    upbit_markets = fetch_upbit_krw_markets()
    print(f"  {len(upbit_markets)} KRW markets")

    # 3. 교집합 (CoinGecko 심볼 → Upbit "KRW-{SYMBOL}")
    candidates_meta: list[tuple[str, dict]] = []
    for cg in cg_data:
        symbol = cg.get("symbol", "").upper()
        if not symbol:
            continue
        market = f"KRW-{symbol}"
        if market in upbit_markets:
            candidates_meta.append((market, cg))
    print(f"[step 3] 교집합 (CoinGecko ∩ Upbit KRW): {len(candidates_meta)}")
    for market, cg in candidates_meta:
        print(f"  {market} ({cg.get('symbol','?').upper()})")

    # 4. 각 market OHLCV + 필터 평가
    print(f"\n[step 4] 측정 창 OHLCV 분석 (rate limit: ~5/s)...")
    rows: list[CandidateRow] = []
    for i, (market, cg) in enumerate(candidates_meta):
        time.sleep(0.25)  # Upbit rate limit
        row = evaluate_market(market, cg, upbit_markets[market], window_end)
        rows.append(row)
        status = "PASS" if row.passed else "FAIL"
        print(f"  [{i+1}/{len(candidates_meta)}] {row.market:<12} {status} "
              f"(turnover={row.avg_turnover_krw/1e8:.1f}억, std={row.daily_return_std:.4f}, "
              f"bars={row.bar_count}, warn={row.market_warning}) {' / '.join(row.fail_reasons[:2])}")

    # 5. 결과 박제
    passed = [r for r in rows if r.passed]
    failed = [r for r in rows if not r.passed]
    print(f"\n[step 5] 결과: PASSED={len(passed)} / FAILED={len(failed)}")

    args.output.parent.mkdir(parents=True, exist_ok=True)
    output_data = {
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "window_end_utc": window_end.isoformat(),
        "window_days": WINDOW_DAYS,
        "thresholds": {
            "turnover_krw": TURNOVER_THRESHOLD,
            "volatility_std": VOLATILITY_THRESHOLD,
            "min_bars": MIN_BARS,
        },
        "passed_markets": [r.market for r in passed],
        "passed": [asdict(r) for r in passed],
        "failed": [asdict(r) for r in failed],
        "fallback_required": len(passed) <= 3,  # sub-plan §3.2
    }
    with open(args.output, "w", encoding="utf-8") as f:
        json.dump(output_data, f, ensure_ascii=False, indent=2)
    print(f"saved: {args.output}")

    if output_data["fallback_required"]:
        print(f"\n[FALLBACK] passed ≤ 3. sub-plan §3.2: Tier 1+2 그대로 + Strategy E 평가")

    return 0


if __name__ == "__main__":
    import sys
    sys.exit(main())
