"""pytest 공통 fixtures."""
from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd
import pytest

from engine.state import StateStore


@pytest.fixture
def tmp_state(tmp_path: Path) -> StateStore:
    """격리된 SQLite state DB."""
    db = tmp_path / "test_state.sqlite"
    return StateStore(db)


@pytest.fixture
def synth_ohlcv() -> pd.DataFrame:
    """합성 일봉 OHLCV (300 bars). Strategy A/D warmup 충족 + 변동성 조절 가능."""
    np.random.seed(42)
    n = 300
    base = 100_000_000.0  # ₩100M (BTC-like)
    # 트렌드 + 노이즈
    drift = np.linspace(0, 0.5, n)
    noise = np.random.normal(0, 0.02, n).cumsum()
    close = base * np.exp(drift * 0.001 + noise * 0.01)
    open_ = close * (1 + np.random.normal(0, 0.005, n))
    high = np.maximum(close, open_) * (1 + np.abs(np.random.normal(0, 0.005, n)))
    low = np.minimum(close, open_) * (1 - np.abs(np.random.normal(0, 0.005, n)))
    volume = np.abs(np.random.normal(1000, 500, n)) + 100

    idx = pd.date_range("2025-01-01", periods=n, freq="D", tz="UTC")
    return pd.DataFrame(
        {"open": open_, "high": high, "low": low, "close": close,
         "volume": volume, "value": volume * close},
        index=idx,
    )


@pytest.fixture
def breakout_ohlcv(synth_ohlcv: pd.DataFrame) -> pd.DataFrame:
    """Strategy A/D entry 조건 충족용: 마지막 bar에서 강한 상향 돌파 + 거래량 spike."""
    df = synth_ohlcv.copy()
    # 마지막 30 bar를 평탄하게 만들고 마지막 bar에서 brutal breakout
    last_close = df["close"].iloc[-30]
    df.loc[df.index[-30:-1], "close"] = last_close * (1 + np.random.uniform(-0.005, 0.005, 29))
    df.loc[df.index[-30:-1], "open"] = df["close"].iloc[-30:-1].values * (1 + np.random.uniform(-0.002, 0.002, 29))
    df.loc[df.index[-30:-1], "high"] = df[["open", "close"]].iloc[-30:-1].max(axis=1) * 1.01
    df.loc[df.index[-30:-1], "low"] = df[["open", "close"]].iloc[-30:-1].min(axis=1) * 0.99
    df.loc[df.index[-30:-1], "volume"] = 800

    # 마지막 bar: 강한 상승 + 큰 거래량
    breakout_close = last_close * 1.15
    df.loc[df.index[-1], "open"] = last_close * 1.01
    df.loc[df.index[-1], "high"] = breakout_close * 1.005
    df.loc[df.index[-1], "low"] = last_close * 1.0
    df.loc[df.index[-1], "close"] = breakout_close
    df.loc[df.index[-1], "volume"] = 5000  # vol_avg(20)≈800 × 1.5 = 1200, breakout > 1200 OK
    df["value"] = df["volume"] * df["close"]
    return df


@pytest.fixture
def sl_ohlcv(synth_ohlcv: pd.DataFrame) -> pd.DataFrame:
    """SL 터치 시나리오: 마지막 bar low가 entry × 0.92 이하."""
    df = synth_ohlcv.copy()
    df.loc[df.index[-1], "low"] = df["close"].iloc[-1] * 0.85
    return df
