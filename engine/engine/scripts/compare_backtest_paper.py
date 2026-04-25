"""백테스트 ↔ 페이퍼 비교 도구 (V2-06 1주차 마감 시점부터 사용).

박제 출처:
- docs/v2-06-daemon-guide.md §4.2 / §5
- docs/stage1-v2-relaunch.md §1.2 paper_live_tolerance: 0.30

설계:
- 입력 1 (필수): engine/logs/trades-YYYY.jsonl (페이퍼 거래 기록)
- 입력 2 (선택): vectorbt portfolio.pkl (동일 기간 백테스트). 없으면 페이퍼 통계만.
- 출력: trade count / 누적 PnL / ±tolerance 검증

사용:
    python -m engine.scripts.compare_backtest_paper --days 7
    python -m engine.scripts.compare_backtest_paper \\
        --paper-trades engine/logs/trades-2026.jsonl \\
        --backtest-portfolio /path/to/bt.pkl --tolerance 0.30
"""
from __future__ import annotations

import argparse
import json
import sys
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from pathlib import Path

ENGINE_ROOT = Path(__file__).parent.parent.parent  # engine/engine/scripts/ → engine/


@dataclass
class PaperStats:
    trade_count: int          # exit 거래 수 (entry+exit 2행 / 2)
    total_realized_krw: float
    total_invested_krw: float
    cumulative_return_pct: float
    win_count: int
    loss_count: int


def load_paper_trades(path: Path, since_utc: datetime | None = None) -> list[dict]:
    """trades-YYYY.jsonl 로드 + 시점 필터.

    각 줄은 {"side": "buy"|"sell", "ts_utc": ..., "realized_pnl_krw": ...}.
    """
    if not path.exists():
        return []
    rows = []
    for line in path.read_text().splitlines():
        line = line.strip()
        if not line:
            continue
        rec = json.loads(line)
        if since_utc is not None:
            ts = datetime.fromisoformat(rec.get("ts_utc", "1970-01-01T00:00:00+00:00"))
            if ts < since_utc:
                continue
        rows.append(rec)
    return rows


def compute_paper_stats(trades: list[dict]) -> PaperStats:
    """sell 거래 누적 — entry+exit JSONL 중 sell만 realized_pnl 보유."""
    sells = [t for t in trades if t.get("side") == "sell" and "realized_pnl_krw" in t]
    total_realized = sum(t["realized_pnl_krw"] for t in sells)
    # invested = entry_price × volume (sell 행에 entry_price_krw 기록됨)
    total_invested = sum(t["entry_price_krw"] * t["volume"] for t in sells)
    cum_return = (total_realized / total_invested) if total_invested > 0 else 0.0
    win = sum(1 for t in sells if t["realized_pnl_krw"] > 0)
    loss = sum(1 for t in sells if t["realized_pnl_krw"] <= 0)
    return PaperStats(
        trade_count=len(sells),
        total_realized_krw=total_realized,
        total_invested_krw=total_invested,
        cumulative_return_pct=cum_return,
        win_count=win,
        loss_count=loss,
    )


def load_backtest_portfolio_stats(pkl_path: Path) -> dict | None:
    """vectorbt Portfolio.pickle 로드 + 핵심 통계 추출. 미존재/import 실패 시 None.

    호출 시점 (V2-06 1주차 마감)에 사용자가 노트북에서:
        portfolio.save("/path/to/bt.pkl")
    실행하여 미리 export 필요.
    """
    if not pkl_path.exists():
        return None
    try:
        import vectorbt as vbt
    except ImportError:
        print(f"[warn] vectorbt 미설치 — 백테스트 비교 skip. pip install vectorbt", file=sys.stderr)
        return None
    try:
        portfolio = vbt.Portfolio.load(pkl_path)
    except Exception as e:
        print(f"[warn] portfolio.load 실패: {e}", file=sys.stderr)
        return None

    # vectorbt 0.28.5 기준 stats 항목 (research/CLAUDE.md 박제)
    stats = portfolio.stats() if hasattr(portfolio, "stats") else {}
    return {
        "total_return_pct": float(stats.get("Total Return [%]", 0)) / 100,
        "trade_count": int(stats.get("Total Closed Trades", 0)),
        "win_rate_pct": float(stats.get("Win Rate [%]", 0)),
        "max_drawdown_pct": float(stats.get("Max Drawdown [%]", 0)) / 100,
        "sharpe": float(stats.get("Sharpe Ratio", 0)),
    }


def compare(paper: PaperStats, backtest: dict | None, tolerance: float) -> dict:
    """페이퍼 vs 백테스트 비교 + ±tolerance 검증."""
    out = {
        "paper": {
            "trade_count": paper.trade_count,
            "total_realized_krw": paper.total_realized_krw,
            "total_invested_krw": paper.total_invested_krw,
            "cumulative_return_pct": paper.cumulative_return_pct,
            "win_count": paper.win_count,
            "loss_count": paper.loss_count,
        },
    }
    if backtest is None:
        out["backtest"] = None
        out["verdict"] = "no_backtest_portfolio_provided"
        return out

    out["backtest"] = backtest
    bt_ret = backtest["total_return_pct"]
    pp_ret = paper.cumulative_return_pct

    # ±tolerance 일치 검증 (절대 차이가 |bt_ret| × tolerance 이내)
    if abs(bt_ret) < 1e-6:
        # 백테스트 0% — 페이퍼도 ±1% 이내면 PASS
        ok = abs(pp_ret) < 0.01
    else:
        rel_diff = abs(pp_ret - bt_ret) / abs(bt_ret)
        ok = rel_diff <= tolerance
        out["relative_diff"] = rel_diff

    out["abs_diff_pct"] = pp_ret - bt_ret
    out["tolerance"] = tolerance
    out["verdict"] = "PASS" if ok else "FAIL"
    return out


def format_report(result: dict) -> str:
    """사람이 읽기 쉬운 텍스트 리포트."""
    p = result["paper"]
    lines = [
        "=" * 60,
        "백테스트 ↔ 페이퍼 비교",
        "=" * 60,
        "[페이퍼]",
        f"  trades:        {p['trade_count']}",
        f"  realized PnL:  {p['total_realized_krw']:+,.0f} KRW",
        f"  invested:      {p['total_invested_krw']:,.0f} KRW",
        f"  return:        {p['cumulative_return_pct']*100:+.2f}%",
        f"  win/loss:      {p['win_count']} / {p['loss_count']}",
    ]
    if result["backtest"] is None:
        lines += [
            "",
            "[백테스트] 미제공 — --backtest-portfolio 옵션으로 .pkl 경로 지정 필요.",
            f"verdict: {result['verdict']}",
        ]
        return "\n".join(lines)

    bt = result["backtest"]
    lines += [
        "",
        "[백테스트]",
        f"  trades:        {bt['trade_count']}",
        f"  return:        {bt['total_return_pct']*100:+.2f}%",
        f"  Sharpe:        {bt['sharpe']:.3f}",
        f"  MDD:           {bt['max_drawdown_pct']*100:.2f}%",
        f"  win rate:      {bt['win_rate_pct']:.1f}%",
        "",
        f"[비교] tolerance ±{result['tolerance']*100:.0f}%",
        f"  abs diff:      {result['abs_diff_pct']*100:+.2f}% (페이퍼 - 백테스트)",
    ]
    if "relative_diff" in result:
        lines.append(f"  rel diff:      {result['relative_diff']*100:.1f}%")
    lines.append(f"  verdict:       {result['verdict']}")
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="백테스트 ↔ 페이퍼 ±30% 비교")
    parser.add_argument(
        "--paper-trades",
        type=Path,
        default=ENGINE_ROOT / "logs" / f"trades-{datetime.now(timezone.utc).strftime('%Y')}.jsonl",
        help="페이퍼 trades-YYYY.jsonl (기본: 올해)",
    )
    parser.add_argument(
        "--backtest-portfolio",
        type=Path,
        default=None,
        help="vectorbt Portfolio.pkl (미지정 시 페이퍼 통계만)",
    )
    parser.add_argument("--days", type=int, default=None,
                        help="최근 N일 페이퍼 trades만 (default: 전체)")
    parser.add_argument("--tolerance", type=float, default=0.30,
                        help="±tolerance (default 0.30 = ±30%%, v2 박제)")
    args = parser.parse_args(argv)

    since = None
    if args.days is not None:
        since = datetime.now(timezone.utc) - timedelta(days=args.days)

    trades = load_paper_trades(args.paper_trades, since_utc=since)
    paper_stats = compute_paper_stats(trades)
    backtest_stats = (
        load_backtest_portfolio_stats(args.backtest_portfolio)
        if args.backtest_portfolio else None
    )
    result = compare(paper_stats, backtest_stats, tolerance=args.tolerance)
    print(format_report(result))
    return 0 if result["verdict"] in ("PASS", "no_backtest_portfolio_provided") else 1


if __name__ == "__main__":
    sys.exit(main())
