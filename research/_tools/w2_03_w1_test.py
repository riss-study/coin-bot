"""
W2-03.1 W-1 미니 테스트: ATR trailing stop sl_stop Series + sl_trail=True 동작 검증

박제 출처:
- W2-02 v5 sub-plan L163 "W-1 추가 박제 (W2-03 책무)"
- W2-03 sub-plan v4 W2-03.1

검증 대상 (Strategy C trailing stop 구현 방법):
- 방법 A: vectorbt sl_stop=Series(ATR_MULT*ATR/close), sl_trail=True
  - entry bar 시점 비율로 trailing stop 적용 (vectorbt 내부 trailing high 추적)
- 방법 B: manual trailing_high - ATR_MULT*ATR(t) exit_mask
  - 매 bar 동적 ATR + trailing high 계산 + Boolean exit_mask

채택 결정 (cycle 2 v5 Strategy C 구현 방법):
- 동작 일치 시 방법 A (간결, vectorbt 내장)
- 차이 발견 시 방법 B (manual 정확)

사용:
    cd /Users/kyounghwanlee/Desktop/coin-bot
    source research/.venv/bin/activate
    python research/_tools/w2_03_w1_test.py
"""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd
import vectorbt as vbt
from ta.volatility import AverageTrueRange

# 박제 (W2-02 v5 Strategy C)
ATR_WINDOW = 14
ATR_MULT = 3.0


def generate_synthetic_trend(n: int = 200, seed: int = 42) -> pd.DataFrame:
    """명확한 trend (linear + noise) 4단계 phase."""
    np.random.seed(seed)
    base = np.concatenate([
        np.linspace(100, 150, 50),   # Phase 1: trend↑ (100→150)
        np.linspace(150, 200, 50),   # Phase 2: trend↑ (150→200)
        np.linspace(200, 100, 50),   # Phase 3: trend↓ (200→100, 반전)
        np.linspace(100, 80, 50),    # Phase 4: stagnant (100→80)
    ])
    noise = np.random.normal(0, 2, n)
    close = base + noise
    high = close + np.abs(np.random.normal(0, 1, n))
    low = close - np.abs(np.random.normal(0, 1, n))

    idx = pd.date_range("2025-01-01", periods=n, freq="D", tz="UTC")
    return pd.DataFrame({"close": close, "high": high, "low": low}, index=idx)


def test_method_a(df: pd.DataFrame) -> dict:
    """방법 A: vectorbt sl_stop=Series + sl_trail=True (entry bar 시점 비율)."""
    atr = AverageTrueRange(df["high"], df["low"], df["close"], window=ATR_WINDOW).average_true_range()
    sl_stop_ratio = (ATR_MULT * atr) / df["close"]

    entries = pd.Series(False, index=df.index)
    entries.iloc[50] = True  # bar 50 entry (trend 명확 시점)
    exits = pd.Series(False, index=df.index)  # ATR trailing stop만으로 exit

    pf = vbt.Portfolio.from_signals(
        close=df["close"],
        entries=entries,
        exits=exits,
        sl_stop=sl_stop_ratio,
        sl_trail=True,
        init_cash=10_000,
        fees=0.0,
        slippage=0.0,
        freq="1D",
    )

    # B-1 정정: records_readable 컬럼명 추측 (KeyError) → records (raw, venv 검증)
    trades = pf.trades.records
    if len(trades) > 0:
        first_trade = trades.iloc[0]
        return {
            "method": "A (vectorbt sl_stop Series + sl_trail=True)",
            "trades": len(trades),
            "entry_idx": int(first_trade["entry_idx"]),
            "entry_price": float(first_trade["entry_price"]),
            "exit_idx": int(first_trade["exit_idx"]),
            "exit_price": float(first_trade["exit_price"]),
            "return_pct": float(first_trade["return"]),
            "_warning": "vectorbt sl_trail=True는 entry bar 시점 비율 freeze. 매 bar 동적 ATR 반영 X (W-2 박제)",
        }
    return {"method": "A", "trades": 0, "error": "no trades"}


def test_method_b(df: pd.DataFrame) -> dict:
    """방법 B: manual trailing_high - ATR_MULT*ATR(t) exit_mask."""
    atr = AverageTrueRange(df["high"], df["low"], df["close"], window=ATR_WINDOW).average_true_range()

    entries = pd.Series(False, index=df.index)
    entries.iloc[50] = True

    exit_mask = pd.Series(False, index=df.index)
    in_position = False
    trailing_high = -np.inf

    for i in range(len(df)):
        if entries.iloc[i] and not in_position:
            in_position = True
            trailing_high = df["close"].iloc[i]
            continue
        if in_position:
            trailing_high = max(trailing_high, df["close"].iloc[i])
            stop_level = trailing_high - ATR_MULT * atr.iloc[i]
            if df["close"].iloc[i] < stop_level:
                exit_mask.iloc[i] = True
                in_position = False

    pf = vbt.Portfolio.from_signals(
        close=df["close"],
        entries=entries,
        exits=exit_mask,
        init_cash=10_000,
        fees=0.0,
        slippage=0.0,
        freq="1D",
    )

    # B-1 정정: records_readable → records (raw)
    trades = pf.trades.records
    if len(trades) > 0:
        first_trade = trades.iloc[0]
        return {
            "method": "B (manual trailing_high - ATR_MULT*ATR(t) exit_mask)",
            "trades": len(trades),
            "entry_idx": int(first_trade["entry_idx"]),
            "entry_price": float(first_trade["entry_price"]),
            "exit_idx": int(first_trade["exit_idx"]),
            "exit_price": float(first_trade["exit_price"]),
            "return_pct": float(first_trade["return"]),
        }
    return {"method": "B", "trades": 0, "error": "no trades"}


def main() -> None:
    print("=" * 60)
    print("W2-03.1 W-1 미니 테스트: ATR trailing stop 동작 검증")
    print("=" * 60)
    print(f"박제 (W2-02 v5 Strategy C): ATR_WINDOW={ATR_WINDOW}, ATR_MULT={ATR_MULT}")
    print()

    df = generate_synthetic_trend(n=200, seed=42)
    print(f"Synthetic data: {len(df)} bars")
    print(f"  Phase 1 (0~50):   trend↑ 100→150")
    print(f"  Phase 2 (50~100): trend↑ 150→200 (entry @ bar 50)")
    print(f"  Phase 3 (100~150): trend↓ 200→100 (반전, exit 예상)")
    print(f"  Phase 4 (150~200): stagnant")
    print()

    result_a = test_method_a(df)
    print("--- 방법 A 결과 ---")
    for k, v in result_a.items():
        print(f"  {k}: {v}")
    print()

    result_b = test_method_b(df)
    print("--- 방법 B 결과 ---")
    for k, v in result_b.items():
        print(f"  {k}: {v}")
    print()

    # 비교
    print("=" * 60)
    print("=== 비교 ===")
    print("=" * 60)
    if result_a.get("exit_idx") == result_b.get("exit_idx"):
        print(f"exit_idx 일치: {result_a.get('exit_idx')}")
    else:
        print(f"exit_idx 차이: A={result_a.get('exit_idx')}, B={result_b.get('exit_idx')}")

    if result_a.get("exit_price") is not None and result_b.get("exit_price") is not None:
        diff_pct = abs(result_a["exit_price"] - result_b["exit_price"]) / result_b["exit_price"] * 100
        print(f"exit_price 차이: {diff_pct:.2f}% (A={result_a['exit_price']:.2f}, B={result_b['exit_price']:.2f})")

    if result_a.get("return_pct") is not None and result_b.get("return_pct") is not None:
        return_diff = abs(result_a["return_pct"] - result_b["return_pct"])
        print(f"return_pct 차이: {return_diff:.4f} (A={result_a['return_pct']:.4f}, B={result_b['return_pct']:.4f})")

    print()
    print("=" * 60)
    print("=== 채택 결정 권고 ===")
    print("=" * 60)
    if (
        result_a.get("exit_idx") == result_b.get("exit_idx")
        and result_a.get("return_pct") is not None
        and result_b.get("return_pct") is not None
        and abs(result_a["return_pct"] - result_b["return_pct"]) < 0.005
    ):
        recommendation = "A"
        rationale = "동작 일치 (exit_idx 일치 + return_pct 차이 < 0.5%). 방법 A 채택 권고 (간결, vectorbt 내장)"
    else:
        recommendation = "B"
        rationale = "차이 발견. 방법 B 채택 권고 (manual 정확 계산). 사유: vectorbt sl_stop은 entry bar 시점 비율 고정 vs B는 매 bar 동적 ATR"
    print(f"→ {rationale}")

    # NIT N-1 정정: 결과 JSON 저장 (재현성 + W2-03.6 evidence 일관성)
    PROJECT_ROOT = Path(__file__).resolve().parents[2]
    OUTPUT_DIR = PROJECT_ROOT / "research" / "outputs"
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    OUTPUT_PATH = OUTPUT_DIR / "w2_03_w1_test.json"
    payload = {
        "executed_at": datetime.now(timezone.utc).isoformat(),
        "박제": {
            "ATR_WINDOW": ATR_WINDOW,
            "ATR_MULT": ATR_MULT,
            "출처": "W2-02 v5 Strategy C + candidate-pool.md v4",
        },
        "synthetic_data": {
            "n": 200, "seed": 42,
            "phases": "1: trend↑ 100→150 / 2: trend↑ 150→200 (entry @ 50) / 3: trend↓ 200→100 (반전) / 4: stagnant 100→80",
        },
        "result_a": result_a,
        "result_b": result_b,
        "recommendation": recommendation,
        "rationale": rationale,
        "synthetic_data_한계_인정": "synthetic data는 명확한 trend로 방법 A vs B 차이 발견에 적합. 실제 BTC/ETH 일봉 데이터에서 차이 magnitude는 다를 수 있음. W2-03.6 리포트에서 추가 검증 권고",
    }
    OUTPUT_PATH.write_text(json.dumps(payload, indent=2, ensure_ascii=False))
    print(f"\n결과 저장: {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
