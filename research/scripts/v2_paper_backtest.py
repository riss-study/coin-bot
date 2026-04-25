"""V2-06 비교용 백테스트 — 같은 4주 기간 portfolio.pkl 생성.

박제 출처:
- engine/config.yaml (Strategy A/D 파라미터)
- research/notebooks/08_insample_grid.ipynb (W2-03 검증된 신호 함수)
- docs/v2-06-daemon-guide.md §5.4

설계:
- 3 cells (KRW-BTC_A + KRW-ETH_A + KRW-BTC_D) 동일 파라미터로 vectorbt Portfolio 생성
- group_by + cash_sharing=True 로 단일 portfolio (3 cells 합산 PnL)
- portfolio.save(.pkl) → compare_backtest_paper 도구가 입력으로 사용

사용:
    cd /Users/riss/project/coin-bot
    source research/.venv/bin/activate
    PYTHONPATH=engine python research/scripts/v2_paper_backtest.py \\
        --from 2026-04-26 --to 2026-05-24 \\
        --output research/notebooks/results/v2_paper4w.pkl
"""
from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd
import pyupbit
import vectorbt as vbt
from ta.volatility import BollingerBands, KeltnerChannel


# year_freq는 vbt.settings.returns 글로벌 (Portfolio.from_signals 인자 아님 — 실측 2026-04-26)
vbt.settings.returns["year_freq"] = "365 days"


# 박제 파라미터 (engine/config.yaml + research/notebooks/08 일치)
STRATEGY_A_PARAMS = {
    "MA_PERIOD": 200, "DONCHIAN_HIGH": 20, "DONCHIAN_LOW": 10,
    "VOL_AVG_PERIOD": 20, "VOL_MULT": 1.5, "SL_PCT": 0.08,
}
STRATEGY_D_PARAMS = {
    "KELTNER_WINDOW": 20, "KELTNER_ATR_MULT": 1.5, "ATR_WINDOW": 14,
    "BOLLINGER_WINDOW": 20, "BOLLINGER_SIGMA": 2.0, "SL_HARD": 0.08,
}
PORTFOLIO_PARAMS = {
    "INIT_CASH": 1_000_000, "FEES": 0.0005, "SLIPPAGE": 0.0005,
    "FREQ": "1D",
    # year_freq 는 vbt.settings.returns 글로벌 (위 참조)
}
CELLS = [
    ("KRW-BTC", "A"),
    ("KRW-ETH", "A"),
    ("KRW-BTC", "D"),
]
WARMUP_DAYS = 300  # MA200 + 여유


def fetch_with_warmup(ticker: str, start_utc: pd.Timestamp, end_utc: pd.Timestamp) -> pd.DataFrame:
    """warmup 포함 OHLCV fetch + UTC 변환 (research/CLAUDE.md 박제)."""
    extended_start = start_utc - pd.Timedelta(days=WARMUP_DAYS)
    df = pyupbit.get_ohlcv_from(
        ticker=ticker, interval="day",
        fromDatetime=extended_start.tz_convert("Asia/Seoul").strftime("%Y-%m-%d %H:%M:%S"),
        to=end_utc.tz_convert("Asia/Seoul").strftime("%Y-%m-%d %H:%M:%S"),
    )
    if df is None or df.empty:
        raise RuntimeError(f"get_ohlcv_from 빈 응답: {ticker}")
    if df.index.tz is None:
        df.index = df.index.tz_localize("Asia/Seoul").tz_convert("UTC")
    return df


def strategy_a_signals(df: pd.DataFrame, params=STRATEGY_A_PARAMS) -> tuple[pd.Series, pd.Series]:
    """W2-03 박제 (08_insample_grid.ipynb)."""
    close, high, low, volume = df["close"], df["high"], df["low"], df["volume"]
    ma = close.rolling(window=params["MA_PERIOD"]).mean()
    donchian_high = high.rolling(window=params["DONCHIAN_HIGH"]).max().shift(1)
    donchian_low = low.rolling(window=params["DONCHIAN_LOW"]).min().shift(1)
    vol_avg = volume.rolling(window=params["VOL_AVG_PERIOD"]).mean().shift(1)
    entries = (close > ma) & (close > donchian_high) & (volume > vol_avg * params["VOL_MULT"])
    exits = close < donchian_low
    return entries.fillna(False).astype(bool), exits.fillna(False).astype(bool)


def strategy_d_signals(df: pd.DataFrame, params=STRATEGY_D_PARAMS) -> tuple[pd.Series, pd.Series]:
    """W2-03 박제 (08_insample_grid.ipynb)."""
    close, high, low = df["close"], df["high"], df["low"]
    kc = KeltnerChannel(
        high=high, low=low, close=close,
        window=params["KELTNER_WINDOW"], window_atr=params["ATR_WINDOW"],
        original_version=False, multiplier=params["KELTNER_ATR_MULT"],
    )
    kc_upper = kc.keltner_channel_hband()
    kc_mid = kc.keltner_channel_mband()
    bb = BollingerBands(close=close, window=params["BOLLINGER_WINDOW"], window_dev=params["BOLLINGER_SIGMA"])
    bb_upper = bb.bollinger_hband()
    kc_break = (close > kc_upper) & (close.shift(1) <= kc_upper.shift(1))
    bb_break = (close > bb_upper) & (close.shift(1) <= bb_upper.shift(1))
    entries = kc_break & bb_break
    mid_exit = (close < kc_mid) & (close.shift(1) >= kc_mid.shift(1))
    return entries.fillna(False).astype(bool), mid_exit.fillna(False).astype(bool)


def main() -> int:
    parser = argparse.ArgumentParser(description="V2-06 비교용 4주 백테스트 portfolio.pkl 생성")
    parser.add_argument("--from", dest="from_date", required=True, help="YYYY-MM-DD (UTC)")
    parser.add_argument("--to", dest="to_date", required=True, help="YYYY-MM-DD (UTC)")
    parser.add_argument("--output", required=True, type=Path, help="portfolio.pkl 저장 경로")
    args = parser.parse_args()

    start_utc = pd.Timestamp(args.from_date, tz="UTC")
    end_utc = pd.Timestamp(args.to_date, tz="UTC")
    print(f"window: {start_utc} ~ {end_utc}")

    # 3 cells 신호 계산 + 비교 기간 slice
    closes = {}
    entries_dict = {}
    exits_dict = {}
    for ticker, strategy in CELLS:
        cell_key = f"{ticker}_{strategy}"
        print(f"[{cell_key}] fetching...")
        df = fetch_with_warmup(ticker, start_utc, end_utc)
        if strategy == "A":
            entries, exits = strategy_a_signals(df)
        else:
            entries, exits = strategy_d_signals(df)
        closes[cell_key] = df["close"].loc[start_utc:end_utc]
        entries_dict[cell_key] = entries.loc[start_utc:end_utc]
        exits_dict[cell_key] = exits.loc[start_utc:end_utc]
        print(f"  bars={len(closes[cell_key])} entries={entries_dict[cell_key].sum()} exits={exits_dict[cell_key].sum()}")

    # DataFrame 결합 (columns=cell_key)
    close_df = pd.DataFrame(closes)
    entries_df = pd.DataFrame(entries_dict)
    exits_df = pd.DataFrame(exits_dict)

    # SL: 모든 cells 동일 0.08
    sl_stop = STRATEGY_A_PARAMS["SL_PCT"]

    # vectorbt Portfolio (group_by=True + cash_sharing=True → 3 cells 합산 단일 portfolio)
    pf = vbt.Portfolio.from_signals(
        close_df,
        entries=entries_df, exits=exits_df,
        sl_stop=sl_stop,
        init_cash=PORTFOLIO_PARAMS["INIT_CASH"],
        fees=PORTFOLIO_PARAMS["FEES"],
        slippage=PORTFOLIO_PARAMS["SLIPPAGE"],
        freq=PORTFOLIO_PARAMS["FREQ"],
        group_by=True, cash_sharing=True,
    )

    # 저장
    args.output.parent.mkdir(parents=True, exist_ok=True)
    pf.save(args.output)
    print(f"\nsaved: {args.output}")

    stats = pf.stats()
    print(f"\n[stats] return={stats.get('Total Return [%]', 0):.2f}% / "
          f"trades={int(stats.get('Total Closed Trades', 0))} / "
          f"Sharpe={stats.get('Sharpe Ratio', 0):.3f} / "
          f"MDD={stats.get('Max Drawdown [%]', 0):.2f}%")
    return 0


if __name__ == "__main__":
    import sys
    sys.exit(main())
