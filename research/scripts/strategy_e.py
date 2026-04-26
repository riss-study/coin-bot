"""Strategy E (Momentum 추격) — 사전 박제 signals 함수.

박제 출처: docs/stage1-subplans/v2-strategy-e-momentum.md §2

진입 (모두 AND):
    (1) close >= open × 1.05      (당일 +5% 양봉)
    (2) volume > volume.rolling(20).mean().shift(1) × 2.0   (거래량 spike)
    (3) close > high.rolling(5).max().shift(1)              (5일 고가 돌파)

청산 (어느 하나라도):
    (a) Hard SL: vectorbt sl_stop=0.05 (-5%)               ← Portfolio.from_signals에서 처리
    (b) close < low.rolling(5).min().shift(1)              (5일 저가 하향 돌파)
    (c) close < open × 0.97                                (당일 -3% 음봉)

본 함수는 (b) + (c) 만 exit_mask로 반환. SL은 Portfolio sl_stop으로 처리.
"""
from __future__ import annotations

import pandas as pd


STRATEGY_E_PARAMS = {
    "ENTRY_BAR_PCT": 0.05,    # 당일 +5% 양봉
    "VOL_AVG": 20,            # 거래량 평균 윈도우
    "VOL_MULT": 2.0,          # 거래량 spike 배수
    "SHORT_BREAK": 5,         # 단기 고가 돌파 윈도우
    "SHORT_LOW": 5,           # 단기 저가 하향 돌파 윈도우
    "WEAK_BAR_PCT": 0.03,     # 당일 -3% 음봉 (청산)
    "SL_STOP": 0.05,          # Hard SL -5% (Portfolio.from_signals sl_stop)
}


def strategy_e_signals(df: pd.DataFrame, params=STRATEGY_E_PARAMS) -> tuple[pd.Series, pd.Series]:
    """Strategy E entry/exit masks.

    Args:
        df: DataFrame with columns ['open', 'high', 'low', 'close', 'volume'], index=tz-aware datetime
        params: STRATEGY_E_PARAMS 또는 같은 키의 dict

    Returns:
        (entries, exits) — Boolean Series, NaN은 False, 길이 == len(df)
    """
    required = {"open", "high", "low", "close", "volume"}
    missing = required - set(df.columns)
    if missing:
        raise ValueError(f"missing columns: {missing}")

    close = df["close"]
    open_ = df["open"]
    high = df["high"]
    low = df["low"]
    volume = df["volume"]

    # 진입 (3 AND)
    strong_bull = close >= open_ * (1 + params["ENTRY_BAR_PCT"])
    vol_avg = volume.rolling(window=params["VOL_AVG"]).mean().shift(1)
    vol_spike = volume > vol_avg * params["VOL_MULT"]
    short_high = high.rolling(window=params["SHORT_BREAK"]).max().shift(1)
    short_break = close > short_high
    entries = strong_bull & vol_spike & short_break

    # 청산 (b + c). (a) Hard SL은 vectorbt sl_stop=0.05 으로 처리
    short_low = low.rolling(window=params["SHORT_LOW"]).min().shift(1)
    trend_exit = close < short_low
    weak_close = close < open_ * (1 - params["WEAK_BAR_PCT"])
    exits = trend_exit | weak_close

    return entries.fillna(False).astype(bool), exits.fillna(False).astype(bool)


if __name__ == "__main__":
    # Sanity (격리 데이터 + 시나리오별 검증)
    import numpy as np

    np.random.seed(42)
    n = 100
    base = 1000.0
    close = pd.Series(base + np.random.normal(0, 10, n).cumsum(),
                      index=pd.date_range("2025-01-01", periods=n, freq="D", tz="UTC"))
    open_ = close.shift(1).fillna(base)
    high = pd.concat([open_, close], axis=1).max(axis=1) * 1.005
    low = pd.concat([open_, close], axis=1).min(axis=1) * 0.995
    volume = pd.Series(np.abs(np.random.normal(1000, 200, n)) + 100, index=close.index)
    df = pd.DataFrame({"open": open_, "high": high, "low": low, "close": close, "volume": volume})

    # Sanity 1: warmup 미충족 (첫 20 bars) entries 0
    entries, exits = strategy_e_signals(df)
    assert entries.iloc[:20].sum() == 0, f"warmup entries should be 0, got {entries.iloc[:20].sum()}"
    print(f"[sanity 1] warmup PASS")

    # Sanity 2: 강제 진입 시나리오 (마지막 bar에 +6% 양봉 + 거래량 5배 + 신고가)
    df.loc[df.index[-1], "open"] = 1000.0
    df.loc[df.index[-1], "close"] = 1060.0
    df.loc[df.index[-1], "high"] = 1080.0
    df.loc[df.index[-1], "low"] = 990.0
    df.loc[df.index[-1], "volume"] = volume.iloc[-22:-2].mean() * 5  # 5배
    df.loc[df.index[-2], "high"] = 1010.0  # 5일 고가가 1010 정도라고 가정
    # 5일 고가가 1060 미만이어야 돌파
    df.iloc[-7:-1, df.columns.get_loc("high")] = 1010.0
    entries, exits = strategy_e_signals(df)
    print(f"[sanity 2] last bar entry={entries.iloc[-1]} (expect True 같은 시나리오)")

    # Sanity 3: 약화 음봉 청산
    df2 = df.copy()
    df2.loc[df2.index[-1], "open"] = 1100.0
    df2.loc[df2.index[-1], "close"] = 1050.0  # -4.5% 음봉
    entries, exits = strategy_e_signals(df2)
    assert exits.iloc[-1] == True, "weak close should trigger exit"
    print(f"[sanity 3] weak close exit PASS")

    # Sanity 4: 5일 저가 하향 돌파 청산
    df3 = df.copy()
    df3.iloc[-7:-1, df3.columns.get_loc("low")] = 990.0
    df3.loc[df3.index[-1], "close"] = 985.0  # 5일 저가(990) 하향
    df3.loc[df3.index[-1], "open"] = 988.0   # weak close X (close/open = 99.7%)
    entries, exits = strategy_e_signals(df3)
    assert exits.iloc[-1] == True, "5d low break should trigger exit"
    print(f"[sanity 4] 5d low break exit PASS")

    # Sanity 5: missing columns
    try:
        strategy_e_signals(pd.DataFrame({"close": [1, 2, 3]}))
        print("[sanity 5] FAIL: should raise")
    except ValueError as e:
        print(f"[sanity 5] missing columns 거부 PASS: {str(e)[:60]}")

    print("\nstrategy_e.py sanity OK")
