"""Create notebook 05_4h_porting_experiment.ipynb programmatically.

Run with: python _tools/make_notebook_05.py
Output: notebooks/05_4h_porting_experiment.ipynb
"""
import nbformat as nbf
from pathlib import Path

nb = nbf.v4.new_notebook()
cells = []

# Cell 1: Header (markdown)
cells.append(nbf.v4.new_markdown_cell("""\
# Task W1-05 -- 4시간봉 포팅 실험 (참고용)

**Feature ID**: BT-002
**Sub-plan**: `docs/stage1-subplans/w1-05-4h-experiment.md`

동일 전략(A, B)을 4시간봉에 포팅하여 일봉 결과와 비교.

## 핵심 규칙

> **참고용 only.** Week 1 Go/No-Go 기준 아님. 일봉이 기준.
> Walk-forward 미적용 상태이므로 4h 결과의 절대값은 신뢰하지 않음.

## 윈도우 환산 (일봉 -> 4h, x6)

| 일봉 파라미터 | 값 | 4h 환산 | 설명 |
|-------------|-----|---------|------|
| MA_PERIOD | 200 | 1200 | 200일 x 6 bars/day |
| DONCHIAN_HIGH | 20 | 120 | 20일 x 6 |
| DONCHIAN_LOW | 10 | 60 | 10일 x 6 |
| VOL_AVG_PERIOD | 20 | 120 | 20일 x 6 |
| TIME_STOP_DAYS | 5 | 30 | 5일 x 6 bars |
| RSI_PERIOD | 4 | 4 | bars 단위 (환산 없음, 16h lookback) |

**경고**: 1200 bar warmup -> 첫 ~200일 (~50주) trade 없음 -> 실 백테스트 시작 ~2021-07-20
"""))

# Cell 2: Imports
cells.append(nbf.v4.new_code_cell("""\
import pandas as pd
import numpy as np
import vectorbt as vbt
import json
import hashlib
from pathlib import Path
from datetime import datetime, timezone

from ta.momentum import RSIIndicator

from importlib.metadata import version
print(f"pandas:   {version('pandas')}")
print(f"numpy:    {version('numpy')}")
print(f"vectorbt: {version('vectorbt')}")
print(f"ta:       {version('ta')}")
"""))

# Cell 3: Data hash verification (4h)
cells.append(nbf.v4.new_code_cell("""\
DATA_DIR = Path('../data')
PARQUET_4H = 'KRW-BTC_4h_frozen_20260412.parquet'
PARQUET_1D = 'KRW-BTC_1d_frozen_20260412.parquet'

def sha256_file(path):
    h = hashlib.sha256()
    with open(path, 'rb') as f:
        for chunk in iter(lambda: f.read(65536), b''):
            h.update(chunk)
    return h.hexdigest()

with open(DATA_DIR / 'data_hashes.txt') as f:
    expected_hashes = {}
    for line in f:
        line = line.strip()
        if line and not line.startswith('#') and ':' in line:
            k, v = line.split(': ', 1)
            expected_hashes[k] = v

DATA_HASH_4H = sha256_file(DATA_DIR / PARQUET_4H)
assert DATA_HASH_4H == expected_hashes[PARQUET_4H], "4h hash mismatch!"
print(f"4h data hash verified: {DATA_HASH_4H[:16]}...")

DATA_HASH_1D = sha256_file(DATA_DIR / PARQUET_1D)
assert DATA_HASH_1D == expected_hashes[PARQUET_1D], "1d hash mismatch!"
print(f"1d data hash verified: {DATA_HASH_1D[:16]}...")
"""))

# Cell 4: Load both datasets
cells.append(nbf.v4.new_code_cell("""\
# 4h 데이터
df_4h = pd.read_parquet(DATA_DIR / PARQUET_4H)
assert df_4h.index.tz is not None and str(df_4h.index.tz) == 'UTC'
assert df_4h.index.is_monotonic_increasing
print(f"4h bars: {len(df_4h)} (expected 11561)")
print(f"4h range: {df_4h.index[0]} ~ {df_4h.index[-1]}")

close_4h  = df_4h['close']
high_4h   = df_4h['high']
low_4h    = df_4h['low']
volume_4h = df_4h['volume']

# 1d 데이터 (비교용)
df_1d = pd.read_parquet(DATA_DIR / PARQUET_1D)
assert len(df_1d) == 1927
close_1d  = df_1d['close']
high_1d   = df_1d['high']
low_1d    = df_1d['low']
volume_1d = df_1d['volume']
print(f"1d bars: {len(df_1d)}")
"""))

# Cell 5: Constants
cells.append(nbf.v4.new_code_cell("""\
INIT_CASH = 1_000_000
FEES      = 0.0005
SLIPPAGE  = 0.0005

# === 4h 환산 파라미터 (일봉 x 6) ===
A_MA_4H       = 1200      # 200일 x 6
A_DH_4H       = 120       # 20일 x 6
A_DL_4H       = 60        # 10일 x 6
A_VOL_AVG_4H  = 120       # 20일 x 6
A_VOL_MULT    = 1.5       # 배수 (환산 없음)
A_SL_PCT      = 0.08

B_MA_4H       = 1200      # 200일 x 6
B_RSI_PERIOD  = 4         # bars 단위, 환산 없음 (16h lookback)
B_RSI_BUY     = 25
B_RSI_SELL    = 50
B_TIME_STOP_4H = 30       # 5일 x 6 bars
B_SL_PCT      = 0.08

# === 일봉 사전 지정 파라미터 (비교 기준) ===
A_MA_1D = 200; A_DH_1D = 20; A_DL_1D = 10; A_VOL_AVG_1D = 20
B_MA_1D = 200; B_RSI_P_1D = 4; B_RSI_BUY_1D = 25; B_TIME_STOP_1D = 5

print("4h converted parameters loaded")
print(f"  WARNING: 1200 bar warmup = ~200 trading days, first trade ~2021-07-20")
"""))

# Cell 6: Strategy functions (same logic as W1-04, freq parameterized)
cells.append(nbf.v4.new_code_cell("""\
def run_strategy_a(close, high, low, volume, ma_period, donchian_high, donchian_low,
                   vol_avg_period, vol_mult, sl_pct, freq,
                   init_cash=INIT_CASH, fees=0.0005, slippage=0.0005):
    \"\"\"Strategy A (trend-following). freq 파라미터로 타임프레임 지정.\"\"\"
    ma = close.rolling(window=ma_period).mean()
    dh = high.rolling(window=donchian_high).max().shift(1)
    dl = low.rolling(window=donchian_low).min().shift(1)
    va = volume.rolling(window=vol_avg_period).mean().shift(1)

    entries = ((close > ma) & (close > dh) & (volume > va * vol_mult)).fillna(False)
    entries = entries.astype(bool)
    exits = (close < dl).fillna(False)
    exits = exits.astype(bool)

    pf = vbt.Portfolio.from_signals(
        close=close, entries=entries, exits=exits,
        sl_stop=sl_pct, sl_trail=False,
        init_cash=init_cash, fees=fees, slippage=slippage, freq=freq,
    )
    return pf


def run_strategy_b(close, ma_period, rsi_period, rsi_buy, rsi_sell, time_stop_bars,
                   sl_pct, freq, init_cash=INIT_CASH, fees=0.0005, slippage=0.0005):
    \"\"\"Strategy B (mean-reversion). time_stop_bars는 bar 단위 (4h=30, 1d=5).
    주: entries.shift(time_stop_bars)는 "엔트리 신호 N바 후 exit" 근사.
    실제 보유 N바 후가 아님 (포지션 재진입 차단 시 약간 차이 가능).\"\"\"
    ma = close.rolling(window=ma_period).mean()
    rsi = RSIIndicator(close=close, window=rsi_period).rsi()

    entries = ((close > ma) & (rsi < rsi_buy)).fillna(False)
    entries = entries.astype(bool)
    rsi_exits = (rsi > rsi_sell).fillna(False)
    rsi_exits = rsi_exits.astype(bool)
    time_exits = entries.shift(time_stop_bars).fillna(False)
    time_exits = time_exits.astype(bool)
    exits = (rsi_exits | time_exits).astype(bool)

    pf = vbt.Portfolio.from_signals(
        close=close, entries=entries, exits=exits,
        sl_stop=sl_pct, sl_trail=False,
        init_cash=init_cash, fees=fees, slippage=slippage, freq=freq,
    )
    return pf


def extract_metrics(pf):
    \"\"\"Extract summary metrics from Portfolio.\"\"\"
    total_trades = int(pf.trades.count())
    sharpe = float(pf.sharpe_ratio())
    total_return = float(pf.total_return())
    max_dd = float(pf.max_drawdown())
    if total_trades > 0:
        win_rate = float(pf.trades.win_rate())
        profit_factor = float(pf.trades.profit_factor())
    else:
        win_rate = float('nan')
        profit_factor = float('nan')
    return {
        'sharpe': sharpe, 'total_return': total_return, 'max_drawdown': max_dd,
        'win_rate': win_rate, 'profit_factor': profit_factor, 'total_trades': total_trades,
    }


print("Strategy functions defined (freq-parameterized)")
"""))

# Cell 7: Validate — reproduce 1d Sharpe
cells.append(nbf.v4.new_code_cell("""\
# 검증: 1d 함수가 W1-02/W1-03 Sharpe를 재현하는지 확인
pf_a_1d = run_strategy_a(close_1d, high_1d, low_1d, volume_1d,
    ma_period=A_MA_1D, donchian_high=A_DH_1D, donchian_low=A_DL_1D,
    vol_avg_period=A_VOL_AVG_1D, vol_mult=A_VOL_MULT, sl_pct=A_SL_PCT, freq='1D')

pf_b_1d = run_strategy_b(close_1d,
    ma_period=B_MA_1D, rsi_period=B_RSI_P_1D, rsi_buy=B_RSI_BUY_1D,
    rsi_sell=B_RSI_SELL, time_stop_bars=B_TIME_STOP_1D, sl_pct=B_SL_PCT, freq='1D')

EXPECTED_A = 1.0352900037639534
EXPECTED_B = 0.13615418374262483
TOL = 1e-4

sharpe_a_1d = float(pf_a_1d.sharpe_ratio())
sharpe_b_1d = float(pf_b_1d.sharpe_ratio())
assert abs(sharpe_a_1d - EXPECTED_A) < TOL, f"A 1d mismatch: {sharpe_a_1d}"
assert abs(sharpe_b_1d - EXPECTED_B) < TOL, f"B 1d mismatch: {sharpe_b_1d}"
print(f"1d validation: A={sharpe_a_1d:.10f} B={sharpe_b_1d:.10f} -- MATCH")

metrics_a_1d = extract_metrics(pf_a_1d)
metrics_b_1d = extract_metrics(pf_b_1d)
"""))

# Cell 8: Strategy A 4h backtest
cells.append(nbf.v4.new_code_cell("""\
# === Strategy A 4h 백테스트 ===
pf_a_4h = run_strategy_a(close_4h, high_4h, low_4h, volume_4h,
    ma_period=A_MA_4H, donchian_high=A_DH_4H, donchian_low=A_DL_4H,
    vol_avg_period=A_VOL_AVG_4H, vol_mult=A_VOL_MULT, sl_pct=A_SL_PCT, freq='4h')

metrics_a_4h = extract_metrics(pf_a_4h)

# Warmup 검증
entries_a_4h = ((close_4h > close_4h.rolling(A_MA_4H).mean())
    & (close_4h > high_4h.rolling(A_DH_4H).max().shift(1))
    & (volume_4h > volume_4h.rolling(A_VOL_AVG_4H).mean().shift(1) * A_VOL_MULT)
    ).fillna(False)
warmup_entries = int(entries_a_4h.iloc[:A_MA_4H].sum())
assert warmup_entries == 0, f"4h warmup entries should be 0, got {warmup_entries}"

print(f"Strategy A 4h:")
print(f"  Sharpe:       {metrics_a_4h['sharpe']:.4f}")
print(f"  Total Return: {metrics_a_4h['total_return']*100:.2f}%")
print(f"  Max Drawdown: {metrics_a_4h['max_drawdown']*100:.2f}%")
print(f"  Trades:       {metrics_a_4h['total_trades']}")
print(f"  Win Rate:     {metrics_a_4h['win_rate']*100:.2f}%" if metrics_a_4h['total_trades'] > 0 else "  Win Rate:     N/A")
print(f"  Warmup 0 entries (first {A_MA_4H} bars): PASS")
"""))

# Cell 9: Strategy B 4h backtest
cells.append(nbf.v4.new_code_cell("""\
# === Strategy B 4h 백테스트 ===
# 주: RSI_PERIOD=4 bars는 환산 없음 (4 x 4h = 16h lookback)
# TIME_STOP=30 bars = 5일 x 6 bars
pf_b_4h = run_strategy_b(close_4h,
    ma_period=B_MA_4H, rsi_period=B_RSI_PERIOD, rsi_buy=B_RSI_BUY,
    rsi_sell=B_RSI_SELL, time_stop_bars=B_TIME_STOP_4H, sl_pct=B_SL_PCT, freq='4h')

metrics_b_4h = extract_metrics(pf_b_4h)

# Warmup 검증
ma_4h_b = close_4h.rolling(B_MA_4H).mean()
rsi_4h_b = RSIIndicator(close=close_4h, window=B_RSI_PERIOD).rsi()
entries_b_4h = ((close_4h > ma_4h_b) & (rsi_4h_b < B_RSI_BUY)).fillna(False)
warmup_b = int(entries_b_4h.iloc[:B_MA_4H].sum())
assert warmup_b == 0, f"4h B warmup entries should be 0, got {warmup_b}"

print(f"Strategy B 4h:")
print(f"  Sharpe:       {metrics_b_4h['sharpe']:.4f}")
print(f"  Total Return: {metrics_b_4h['total_return']*100:.2f}%")
print(f"  Max Drawdown: {metrics_b_4h['max_drawdown']*100:.2f}%")
print(f"  Trades:       {metrics_b_4h['total_trades']}")
print(f"  Win Rate:     {metrics_b_4h['win_rate']*100:.2f}%" if metrics_b_4h['total_trades'] > 0 else "  Win Rate:     N/A")
print(f"  Warmup 0 entries (first {B_MA_4H} bars): PASS")
"""))

# Cell 10: Comparison table
cells.append(nbf.v4.new_code_cell("""\
# === 일봉 vs 4시간봉 비교 ===
comparison = pd.DataFrame([
    {'strategy': 'A', 'timeframe': '1D', **metrics_a_1d},
    {'strategy': 'A', 'timeframe': '4h', **metrics_a_4h},
    {'strategy': 'B', 'timeframe': '1D', **metrics_b_1d},
    {'strategy': 'B', 'timeframe': '4h', **metrics_b_4h},
])

print("=" * 80)
print("일봉 vs 4시간봉 비교 (참고용, Go/No-Go에 영향 없음)")
print("=" * 80)
print(f"{'Strategy':<10} {'TF':<5} {'Sharpe':>8} {'Return':>10} {'MDD':>8} {'Trades':>7} {'WinRate':>8} {'PF':>6}")
print("-" * 80)
for _, r in comparison.iterrows():
    wr = f"{r['win_rate']*100:.1f}%" if not pd.isna(r['win_rate']) else "N/A"
    pf_str = f"{r['profit_factor']:.2f}" if not pd.isna(r['profit_factor']) else "N/A"
    print(f"{r['strategy']:<10} {r['timeframe']:<5} {r['sharpe']:>8.4f} {r['total_return']*100:>9.2f}% {r['max_drawdown']*100:>7.2f}% {r['total_trades']:>7.0f} {wr:>8} {pf_str:>6}")

# 해석
print("\\n--- 해석 ---")
sharpe_diff_a = metrics_a_4h['sharpe'] - metrics_a_1d['sharpe']
sharpe_diff_b = metrics_b_4h['sharpe'] - metrics_b_1d['sharpe']
print(f"Strategy A: 4h - 1d Sharpe = {sharpe_diff_a:+.4f}")
print(f"Strategy B: 4h - 1d Sharpe = {sharpe_diff_b:+.4f}")

if abs(sharpe_diff_a) < 0.2:
    print("  A: 시간프레임 간 Sharpe 차이 작음 (±0.2 이내)")
elif sharpe_diff_a < -0.2:
    print("  A: 4h가 일봉보다 나쁨 -> 일봉 우위")
else:
    print("  A: 4h가 일봉보다 좋아 보임 -> W2 walk-forward에서 재검증 필요")

if abs(sharpe_diff_b) < 0.2:
    print("  B: 시간프레임 간 Sharpe 차이 작음 (±0.2 이내)")
elif sharpe_diff_b < -0.2:
    print("  B: 4h가 일봉보다 나쁨 -> 일봉 우위")
else:
    print("  B: 4h가 일봉보다 좋아 보임 -> W2 walk-forward에서 재검증 필요")
"""))

# Cell 11: Save JSON
cells.append(nbf.v4.new_code_cell("""\
out_dir = Path('../outputs')
out_dir.mkdir(exist_ok=True)

results = {
    'feature_id': 'BT-002',
    'task_id': 'W1-05',
    'analysis_type': '4h_porting_experiment',
    'note': 'Reference only. NOT Go/No-Go basis. Walk-forward not applied.',
    'data': {
        '4h': {
            'file': PARQUET_4H,
            'hash': DATA_HASH_4H,
            'bars': len(df_4h),
            'range': [df_4h.index[0].isoformat(), df_4h.index[-1].isoformat()],
        },
        '1d': {
            'file': PARQUET_1D,
            'hash': DATA_HASH_1D,
            'bars': len(df_1d),
            'range': [df_1d.index[0].isoformat(), df_1d.index[-1].isoformat()],
        },
    },
    'parameters_4h': {
        'strategy_a': {
            'ma_period': A_MA_4H, 'donchian_high': A_DH_4H, 'donchian_low': A_DL_4H,
            'vol_avg_period': A_VOL_AVG_4H, 'vol_mult': A_VOL_MULT, 'sl_pct': A_SL_PCT,
            'conversion': 'daily x 6',
        },
        'strategy_b': {
            'ma_period': B_MA_4H, 'rsi_period': B_RSI_PERIOD, 'rsi_buy': B_RSI_BUY,
            'rsi_sell': B_RSI_SELL, 'time_stop_bars': B_TIME_STOP_4H, 'sl_pct': B_SL_PCT,
            'conversion': 'daily x 6 (except rsi_period = bars, no conversion)',
        },
    },
    'comparison': {
        'strategy_a': {
            '1d': metrics_a_1d,
            '4h': metrics_a_4h,
            'sharpe_diff': sharpe_diff_a,
        },
        'strategy_b': {
            '1d': metrics_b_1d,
            '4h': metrics_b_4h,
            'sharpe_diff': sharpe_diff_b,
        },
    },
    'generated_at': datetime.now(timezone.utc).isoformat(),
}

result_path = out_dir / 'strategy_4h_comparison.json'
with open(result_path, 'w') as f:
    json.dump(results, f, indent=2)
print(f"Saved: {result_path}")
"""))

# Cell 12: Summary
cells.append(nbf.v4.new_code_cell("""\
print("=" * 60)
print("W1-05 4시간봉 포팅 실험 요약")
print("=" * 60)
print(f"\\n*** 참고용 only. Week 1 Go/No-Go에 영향 없음. ***")
print(f"\\nStrategy A: 1d Sharpe {metrics_a_1d['sharpe']:.4f} vs 4h Sharpe {metrics_a_4h['sharpe']:.4f} (diff {sharpe_diff_a:+.4f})")
print(f"Strategy B: 1d Sharpe {metrics_b_1d['sharpe']:.4f} vs 4h Sharpe {metrics_b_4h['sharpe']:.4f} (diff {sharpe_diff_b:+.4f})")
print(f"\\n4h warmup: {A_MA_4H} bars (~200 trading days, first trade ~2021-07-20)")
print(f"4h trades: A={metrics_a_4h['total_trades']}, B={metrics_b_4h['total_trades']}")
print("=" * 60)
"""))

# Assemble and write
nb.cells = cells
out_path = Path(__file__).resolve().parent.parent / 'notebooks' / '05_4h_porting_experiment.ipynb'
with open(out_path, 'w') as f:
    nbf.write(nb, f)
print(f"Notebook created: {out_path}")
