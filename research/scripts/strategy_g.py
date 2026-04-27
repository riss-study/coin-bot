"""Strategy G (Active Multi-pair) — 사전 박제 signals.

박제 출처: docs/stage1-subplans/v2-strategy-g-active.md §2

진입 (3 AND):
    (1) close >= open × 1.02
    (2) volume > volume.rolling(20).mean().shift(1) × 1.2
    (3) close > high.rolling(3).max().shift(1)

청산 (어느 하나라도):
    (a) Hard SL: vectorbt sl_stop=0.03 (-3%)         ← Portfolio.from_signals
    (b) TP:      vectorbt tp_stop=0.05 (+5%)         ← Portfolio.from_signals
    (c) time stop: bars_held >= 3                    ← Portfolio.from_signals max_duration / exit_mask

본 함수는 (b)/(c) 외 exit_mask 추가 없음 (TP/SL/time은 vectorbt 내장).
exit_mask는 항상 False (TP/SL/time만 사용).
"""
from __future__ import annotations

import pandas as pd


STRATEGY_G_PARAMS = {
    "ENTRY_BAR_PCT": 0.02,    # +2% 양봉
    "VOL_AVG": 20,
    "VOL_MULT": 1.2,
    "SHORT_BREAK": 3,         # 3일 고가 돌파
    "SL_STOP": 0.03,          # -3%
    "TP_STOP": 0.05,          # +5%
    "TIME_STOP_BARS": 3,      # 3일 timeout
}


def strategy_g_signals(df: pd.DataFrame, params=STRATEGY_G_PARAMS) -> tuple[pd.Series, pd.Series]:
    """Strategy G entry/exit masks.

    Returns:
        (entries, exits) — entries는 박제 신호. exits는 항상 False (TP/SL/time은 vbt 내장 처리).
    """
    required = {"open", "high", "low", "close", "volume"}
    missing = required - set(df.columns)
    if missing:
        raise ValueError(f"missing columns: {missing}")

    close = df["close"]
    open_ = df["open"]
    high = df["high"]
    volume = df["volume"]

    strong_bull = close >= open_ * (1 + params["ENTRY_BAR_PCT"])
    vol_avg = volume.rolling(window=params["VOL_AVG"]).mean().shift(1)
    vol_spike = volume > vol_avg * params["VOL_MULT"]
    short_high = high.rolling(window=params["SHORT_BREAK"]).max().shift(1)
    short_break = close > short_high
    entries = strong_bull & vol_spike & short_break

    exits = pd.Series(False, index=df.index)  # TP/SL/time만 사용

    return entries.fillna(False).astype(bool), exits.astype(bool)


if __name__ == "__main__":
    import numpy as np

    np.random.seed(42)
    n = 60
    base = 1000.0
    close = pd.Series(base + np.random.normal(0, 5, n).cumsum(),
                      index=pd.date_range("2025-01-01", periods=n, freq="D", tz="UTC"))
    open_ = close.shift(1).fillna(base)
    high = pd.concat([open_, close], axis=1).max(axis=1) * 1.005
    low = pd.concat([open_, close], axis=1).min(axis=1) * 0.995
    volume = pd.Series(np.abs(np.random.normal(1000, 200, n)) + 100, index=close.index)
    df = pd.DataFrame({"open": open_, "high": high, "low": low, "close": close, "volume": volume})

    # Sanity 1: warmup 미충족 (첫 20 bars) entries 0
    entries, exits = strategy_g_signals(df)
    assert entries.iloc[:20].sum() == 0
    print("[sanity 1] warmup PASS")

    # Sanity 2: 강제 진입 시나리오 (마지막 bar +3% 양봉 + 거래량 1.5배 + 신고가)
    df.loc[df.index[-1], "open"] = 1000.0
    df.loc[df.index[-1], "close"] = 1030.0
    df.loc[df.index[-1], "high"] = 1035.0
    df.loc[df.index[-1], "low"] = 999.0
    df.loc[df.index[-1], "volume"] = volume.iloc[-21:-1].mean() * 2
    df.iloc[-4:-1, df.columns.get_loc("high")] = 1015.0  # 3일 고가 = 1015 → 1030 돌파
    entries, exits = strategy_g_signals(df)
    assert entries.iloc[-1], f"forced entry FAIL: bull={df['close'].iloc[-1]>=df['open'].iloc[-1]*1.02}"
    print("[sanity 2] forced entry PASS")

    # Sanity 3: missing columns
    try:
        strategy_g_signals(pd.DataFrame({"close": [1, 2, 3]}))
    except ValueError:
        print("[sanity 3] missing columns rejected PASS")

    # Sanity 4: exits 항상 False
    assert not exits.any(), "exits should be all False (TP/SL/time only)"
    print("[sanity 4] exits=False PASS")

    print("\nstrategy_g.py sanity OK")
