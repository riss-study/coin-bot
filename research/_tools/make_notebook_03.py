"""Create notebook 03_strategy_b_mean_reversion_daily.ipynb programmatically.

Run with: python _tools/make_notebook_03.py
Output: notebooks/03_strategy_b_mean_reversion_daily.ipynb

Strategy B: Larry Connors-style mean reversion (RSI(4) extreme oversold in uptrend)
Inherits W1-02 v3 schema (nested metrics, deepest/longest_drawdown, edge_case_checks, etc.)
"""
import nbformat as nbf
from pathlib import Path

nb = nbf.v4.new_notebook()
cells = []

# Cell 1: Header
cells.append(nbf.v4.new_markdown_cell("""\
# Task W1-03 — Strategy B: 평균 회귀 일봉 백테스트

**Feature ID**: STR-B-001
**Sub-plan**: `docs/stage1-subplans/w1-03-strategy-b-daily.md`

Larry Connors 스타일 평균 회귀 전략을 일봉으로 백테스트.
- 200일 MA 추세 필터 (상승 추세에서만 역추세 매수)
- RSI(4) < 25 진입 (극단 과매도)
- RSI(4) > 50 청산 또는 5 거래일 시간 스톱 또는 -8% 하드 스톱

## 사전 지정 파라미터 (변경 금지)

| 파라미터 | 값 | 설명 |
|---------|-----|------|
| MA_PERIOD | 200 | 추세 필터 (상승장에서만 진입) |
| RSI_PERIOD | 4 | Connors 스타일 단기 RSI |
| RSI_BUY | 25 | 극단 과매도 진입 임계 |
| RSI_SELL | 50 | RSI 회복 청산 임계 |
| TIME_STOP_DAYS | 5 | 시간 스톱 (5 거래일) |
| SL_PCT | 0.08 | 하드 스톱 -8% (vectorbt sl_stop fraction) |

## 신호 로직

```
진입:
  close > ma200 (대추세 상승, EOD 신호 → 같은 바 fill)
  AND rsi(4) < 25 (극단 과매도)

청산 (하나라도 충족):
  rsi(4) > 50 (RSI 회복)
  OR entries.shift(5) (5 바 후 시간 스톱 근사)
  OR sl_stop=0.08 (-8% 하드 스톱, vectorbt 자동)
```

**시간 스톱 caveat**: `entries.shift(N)` 패턴은 "엔트리 신호 N바 후 exit" 근사.
실제 "보유 N바 후"는 아님 (vectorbt 0.28.5 무료 버전은 td_stop 미지원).
- 포지션 재진입 차단 시 약간 차이 가능
- 평균회귀 청산이 보통 2~6 바 내라 5일 시간 스톱은 거의 발동 안 함 (안전장치)

## 검증된 vectorbt 0.28.5 API (W1-02 v3 best practices 상속)

- sl_stop fraction (0.08), sl_trail=False, freq='1D'
- pf.sharpe_ratio() 메서드 호출
- ts_stop / td_stop / max_duration 사용 안 함
- ta.momentum.RSIIndicator (Wilder smoothing)

## v3 schema 상속 (W1-02 v3에서 도입)

- nested metrics dict
- sharpe_se_return_basis + T_returns=N-1 + sharpe_ci_95_normal (Lo 2002 정규 근사)
- deepest_drawdown / longest_drawdown 분리 (vectorbt drawdowns 두 metric 혼동 방지)
- edge_case_checks 동적 derive
- agent trace 저장 (.evidence/agent-reviews/)
"""))

# Cell 2: Imports
cells.append(nbf.v4.new_code_cell("""\
import pandas as pd
import numpy as np
import vectorbt as vbt
from ta.momentum import RSIIndicator
import json
import hashlib
from pathlib import Path
from datetime import datetime, timezone

from importlib.metadata import version
print(f"pandas:   {version('pandas')}")
print(f"numpy:    {version('numpy')}")
print(f"vectorbt: {version('vectorbt')}")
print(f"ta:       {version('ta')}")
"""))

# Cell 3: Data hash verification
cells.append(nbf.v4.new_code_cell("""\
DATA_DIR = Path('../data')
PARQUET_NAME = 'KRW-BTC_1d_frozen_20260412.parquet'
PARQUET_PATH = DATA_DIR / PARQUET_NAME

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

DATA_HASH = sha256_file(PARQUET_PATH)
expected_hash = expected_hashes[PARQUET_NAME]
assert DATA_HASH == expected_hash, f"Data hash mismatch! expected={expected_hash}, actual={DATA_HASH}"
print(f"Data hash verified: {DATA_HASH[:16]}...")
"""))

# Cell 4: Load data + integrity checks
cells.append(nbf.v4.new_code_cell("""\
df = pd.read_parquet(PARQUET_PATH)

assert df.index.tz is not None and str(df.index.tz) == 'UTC', f"Expected UTC, got {df.index.tz}"
assert df.index.is_monotonic_increasing, "Index not monotonic"
assert len(df) == 1927, f"Expected 1927 bars (advertised range), got {len(df)}"

close  = df['close']
high   = df['high']
low    = df['low']
volume = df['volume']

print(f"Bars: {len(df)}")
print(f"Range: {df.index[0]} ~ {df.index[-1]}")
print(f"Columns: {list(df.columns)}")
print(f"NaN total: {df.isna().sum().sum()}")
"""))

# Cell 5: Pre-registered parameters
cells.append(nbf.v4.new_code_cell("""\
MA_PERIOD       = 200
RSI_PERIOD      = 4
RSI_BUY         = 25
RSI_SELL        = 50
TIME_STOP_DAYS  = 5
SL_PCT          = 0.08

INIT_CASH = 1_000_000
FEES      = 0.0005
SLIPPAGE  = 0.0005
FREQ      = '1D'
"""))

# Cell 6: Indicators
cells.append(nbf.v4.new_code_cell("""\
ma200 = close.rolling(window=MA_PERIOD).mean()
rsi = RSIIndicator(close=close, window=RSI_PERIOD).rsi()

print(f"ma200 NaN (warmup): {ma200.isna().sum()} (expected: {MA_PERIOD - 1})")
print(f"rsi NaN (warmup):   {rsi.isna().sum()} (expected: ~{RSI_PERIOD})")
print(f"rsi range:          {rsi.min():.2f} ~ {rsi.max():.2f}")
"""))

# Cell 7: Entry / exit masks
cells.append(nbf.v4.new_code_cell("""\
entries = (close > ma200) & (rsi < RSI_BUY)
entries = entries.fillna(False).astype(bool)

rsi_exits = (rsi > RSI_SELL).fillna(False).astype(bool)

# Time stop: entries.shift(N) pattern (vectorbt에 td_stop 없음)
# "엔트리 신호 N바 후 exit" 근사. 실제 "보유 N바 후"는 아님.
time_exits = entries.shift(TIME_STOP_DAYS).fillna(False).astype(bool)

exits = (rsi_exits | time_exits).astype(bool)

print(f"Total entries: {entries.sum()}")
print(f"RSI exits:     {rsi_exits.sum()}")
print(f"Time exits:    {time_exits.sum()}")
print(f"Combined exits: {exits.sum()}")

# Edge case 1: warmup zero entries
warmup_entries = int(entries.iloc[:MA_PERIOD].sum())
warmup_period_end = df.index[MA_PERIOD - 1]
print(f"\\nWarmup entries (first {MA_PERIOD} bars, last warmup bar {warmup_period_end.date()}): {warmup_entries}")
assert warmup_entries == 0, f"Warmup entries must be 0, got {warmup_entries}"
print(f"  PASS")

# Edge case 2: time stop 발동 패턴 (정보용)
time_stop_active_after_warmup = int(time_exits.iloc[MA_PERIOD:].sum())
print(f"\\nTime stop signals after warmup: {time_stop_active_after_warmup}")
print(f"  (정보용 — RSI 평균회귀 특성상 보통 2~6 바 내 청산되어 time stop 발동 적음)")
"""))

# Cell 8: vectorbt backtest
cells.append(nbf.v4.new_code_cell("""\
pf = vbt.Portfolio.from_signals(
    close=close,
    entries=entries,
    exits=exits,
    sl_stop=SL_PCT,
    sl_trail=False,
    init_cash=INIT_CASH,
    fees=FEES,
    slippage=SLIPPAGE,
    freq=FREQ,
)
print("vectorbt portfolio created successfully (no API errors)")
"""))

# Cell 9: Stats
cells.append(nbf.v4.new_code_cell("""\
stats = pf.stats()
print(stats)
"""))

# Cell 10: Extract metrics with deepest/longest DD + Sharpe SE/CI
cells.append(nbf.v4.new_code_cell("""\
sharpe       = float(pf.sharpe_ratio())
total_return = float(pf.total_return())
max_dd       = float(pf.max_drawdown())
total_trades = int(pf.trades.count())

if total_trades > 0:
    win_rate      = float(pf.trades.win_rate())
    profit_factor = float(pf.trades.profit_factor())
else:
    win_rate = float('nan')
    profit_factor = float('nan')

# Deepest vs longest drawdown 분리 (W1-02 v3 패턴)
records = pf.drawdowns.records_readable
records['DD_pct'] = (records['Valley Value'] - records['Peak Value']) / records['Peak Value']
records['Duration_days'] = (
    pd.to_datetime(records['End Timestamp']) - pd.to_datetime(records['Peak Timestamp'])
).dt.days

if len(records) > 0:
    deepest_idx = records['DD_pct'].idxmin()
    deepest_rec = records.loc[deepest_idx]
    deepest_dd_pct = float(deepest_rec['DD_pct'])
    deepest_dd_duration_days = int(deepest_rec['Duration_days'])
    deepest_dd_status = str(deepest_rec['Status'])
    deepest_dd_recovered = (deepest_dd_status == 'Recovered')
    deepest_dd_peak = pd.to_datetime(deepest_rec['Peak Timestamp']).isoformat()
    deepest_dd_end = pd.to_datetime(deepest_rec['End Timestamp']).isoformat()

    longest_idx = records['Duration_days'].idxmax()
    longest_rec = records.loc[longest_idx]
    longest_dd_pct = float(longest_rec['DD_pct'])
    longest_dd_duration_days = int(longest_rec['Duration_days'])
    longest_dd_status = str(longest_rec['Status'])
    longest_dd_recovered = (longest_dd_status == 'Recovered')

    assert abs(deepest_dd_pct - max_dd) < 1e-9, \\
        f"Deepest DD reconciliation FAILED: {deepest_dd_pct} vs {max_dd}"
    print(f"Deepest DD reconcile PASS: {deepest_dd_pct*100:.4f}% == {max_dd*100:.4f}%")
else:
    deepest_dd_pct = 0.0
    deepest_dd_duration_days = 0
    deepest_dd_status = 'None'
    deepest_dd_recovered = True
    deepest_dd_peak = None
    deepest_dd_end = None
    longest_dd_pct = 0.0
    longest_dd_duration_days = 0
    longest_dd_status = 'None'
    longest_dd_recovered = True
    print("No drawdowns recorded")

# === Exit reason 분류 (bar-based, 타임프레임 독립) ===
# time_exits raw mask bit count ≠ 실제 time-stop 청산 수.
# 정확한 분류를 위해 각 trade의 exit bar에서 어떤 조건이 True였는지 검사.
#
# 중요: hold_bars를 bar count 기반으로 계산 (타임프레임 독립).
#   .dt.days 사용 시 4h 타임프레임에서 silent false negative 발생.
#   index 위치 차이로 계산 → 1D, 4h, 1h 모두 동일하게 작동.
time_stop_exclusive = 0    # exit 바에 time_exits=True, rsi_exits=False → 순수 time stop
time_stop_coincident = 0   # 둘 다 True → ambiguous (time이 기여했을 가능성)
rsi_exclusive = 0          # exit 바에 rsi_exits=True, time_exits=False → 순수 RSI
sl_stop_or_other = 0       # SL priority (return ≈ -sl_pct) 또는 unknown

# SL priority tolerance: sl_stop(8%) + slippage(0.1% RT) + fees(0.1% RT) + intrabar noise 여유
# W1-05 4h 재사용 시 SL↔time_exits 동일 바 충돌 false-positive 방지
SL_RETURN_TOLERANCE = 0.01  # 1% 버퍼 (fees+slippage+body impact)

if total_trades > 0:
    tr = pf.trades.records_readable
    entry_positions = close.index.get_indexer(pd.to_datetime(tr['Entry Timestamp']))
    exit_positions  = close.index.get_indexer(pd.to_datetime(tr['Exit Timestamp']))
    # Bar-based hold count (타임프레임 독립)
    tr['hold_bars'] = exit_positions - entry_positions

    for i in range(len(tr)):
        exit_bar = exit_positions[i]
        if exit_bar == -1:
            sl_stop_or_other += 1
            continue
        # SL priority pre-check: trade return이 -sl_pct 근처면 SL 처리.
        # mask-based 분류보다 우선 → SL이 time_exits 바와 겹쳐도 false-positive 차단.
        trade_ret = float(tr.iloc[i]['Return'])
        if trade_ret <= -(SL_PCT - SL_RETURN_TOLERANCE):
            sl_stop_or_other += 1
            continue
        time_trig = bool(time_exits.iloc[exit_bar])
        rsi_trig = bool(rsi_exits.iloc[exit_bar])
        if time_trig and rsi_trig:
            time_stop_coincident += 1
        elif time_trig:
            time_stop_exclusive += 1
        elif rsi_trig:
            rsi_exclusive += 1
        else:
            sl_stop_or_other += 1

total_time_stop_contrib = time_stop_exclusive + time_stop_coincident
print(f"\\nExit reason 분류 (bar-based, {total_trades} trades 기준):")
print(f"  time_stop_exclusive:  {time_stop_exclusive} (time_exits only)")
print(f"  time_stop_coincident: {time_stop_coincident} (time + rsi, ambiguous)")
print(f"  rsi_exclusive:        {rsi_exclusive} (rsi_exits only)")
print(f"  sl_stop_or_other:     {sl_stop_or_other} (neither — sl_stop or unknown)")
print(f"  Total time_stop contribution (exclusive + coincident): {total_time_stop_contrib}")

print(f"\\nSharpe:        {sharpe:.4f}")
print(f"Total Return:  {total_return*100:.2f}%")
print(f"Max Drawdown:  {max_dd*100:.2f}%")
print(f"  Deepest DD:  {deepest_dd_pct*100:.2f}%, {deepest_dd_duration_days}d, {'recovered' if deepest_dd_recovered else 'still active'}")
print(f"  Longest DD:  {longest_dd_pct*100:.2f}%, {longest_dd_duration_days}d, {'recovered' if longest_dd_recovered else 'still active'}")
print(f"Total Trades:  {total_trades}")
if total_trades > 0:
    print(f"Win Rate:      {win_rate*100:.2f}%")
    print(f"Profit Factor: {profit_factor:.3f}")

# Sharpe SE + 95% CI (Lo 2002 정규 근사)
# 0-trade 가드: sharpe가 NaN일 수 있음
T_returns = len(close) - 1
if total_trades > 0 and not np.isnan(sharpe):
    sharpe_se = float(np.sqrt((1 + 0.5 * sharpe**2) / T_returns))
    sharpe_ci_lo = sharpe - 1.96 * sharpe_se
    sharpe_ci_hi = sharpe + 1.96 * sharpe_se
    print(f"\\nSharpe SE (Lo 2002, return-basis, T_returns={T_returns}): {sharpe_se:.4f}")
    print(f"Sharpe 95% CI (정규 근사): [{sharpe_ci_lo:.4f}, {sharpe_ci_hi:.4f}]")
else:
    sharpe_se = float('nan')
    sharpe_ci_lo = float('nan')
    sharpe_ci_hi = float('nan')
    print(f"\\nSharpe SE: N/A (no trades or NaN sharpe)")

print(f"\\n=== Week 1 Go 기준 평가 (참고) ===")
print(f"Sharpe > 0.5: {'PASS' if sharpe > 0.5 else 'FAIL'} ({sharpe:.4f})")
print(f"MDD < 50%:    {'PASS' if abs(max_dd) < 0.5 else 'FAIL'} ({max_dd*100:.2f}%)")
"""))

# Cell 11: Save JSON
cells.append(nbf.v4.new_code_cell("""\
out_dir = Path('../outputs')
out_dir.mkdir(exist_ok=True)

results = {
    'feature_id': 'STR-B-001',
    'task_id': 'W1-03',
    'strategy': 'B_mean_reversion_daily',
    'description': 'Larry Connors-inspired mean reversion: MA200 trend filter + RSI(4)<25 entry + RSI(4)>50 exit + 5d time stop + sl_stop 8%',
    'data_file': PARQUET_NAME,
    'data_hash': DATA_HASH,
    'data_bars': len(df),
    'data_range': [df.index[0].isoformat(), df.index[-1].isoformat()],
    'parameters': {
        'ma_period': MA_PERIOD,
        'rsi_period': RSI_PERIOD,
        'rsi_buy': RSI_BUY,
        'rsi_sell': RSI_SELL,
        'time_stop_days': TIME_STOP_DAYS,
        'sl_pct': SL_PCT,
    },
    'backtest_config': {
        'init_cash': INIT_CASH,
        'fees': FEES,
        'slippage': SLIPPAGE,
        'freq': FREQ,
    },
    'metrics': {
        'sharpe': sharpe,
        'sharpe_se_return_basis': sharpe_se,
        'sharpe_se_t_returns': T_returns,
        'sharpe_ci_95_normal': [sharpe_ci_lo, sharpe_ci_hi],
        'sharpe_ci_method': 'Lo 2002 normal approximation, return-basis',
        'total_return': total_return,
        'max_drawdown': max_dd,
        'deepest_drawdown': {
            'pct': deepest_dd_pct,
            'duration_days': deepest_dd_duration_days,
            'status': deepest_dd_status,  # 'Active' or 'Recovered'
            'recovered': deepest_dd_recovered,
            'peak_timestamp': deepest_dd_peak,
            'end_timestamp': deepest_dd_end,  # Active이면 window boundary
        },
        'longest_drawdown': {
            'pct': longest_dd_pct,
            'duration_days': longest_dd_duration_days,
            'status': longest_dd_status,
            'recovered': longest_dd_recovered,
        },
        'total_drawdown_records': len(records),
        'win_rate': win_rate if total_trades > 0 else None,
        'profit_factor': profit_factor if total_trades > 0 else None,
        'total_trades': total_trades,
    },
    'edge_case_checks': {
        'warmup_zero_entries': bool(int(entries.iloc[:MA_PERIOD].sum()) == 0),
        # raw mask bit count (signal 수, 실제 청산과 다름)
        'time_stop_mask_nonempty': bool(int(time_exits.iloc[MA_PERIOD:].sum()) > 0),
        'time_stop_mask_count_raw': int(time_exits.iloc[MA_PERIOD:].sum()),
        # Exit reason 분류 (bar-based, 타임프레임 독립)
        # 각 trade의 exit bar에서 time_exits / rsi_exits 조건 검사
        'exit_reason_breakdown': {
            'time_stop_exclusive': int(time_stop_exclusive),   # time only (가장 확실한 time-stop 기여)
            'time_stop_coincident': int(time_stop_coincident), # time + rsi 동시 (ambiguous)
            'rsi_exclusive': int(rsi_exclusive),               # rsi only
            'sl_stop_or_other': int(sl_stop_or_other),         # sl_stop 또는 unknown
        },
        'total_time_stop_contribution': int(total_time_stop_contrib),  # exclusive + coincident
        'deepest_dd_reconciles_with_max_drawdown': bool(abs(deepest_dd_pct - max_dd) < 1e-9) if total_trades > 0 else None,
    },
    'go_criteria_eval': {
        'sharpe_gt_0.5': sharpe > 0.5,
        'mdd_lt_50pct': abs(max_dd) < 0.5,
    },
    'generated_at': datetime.now(timezone.utc).isoformat(),
}

result_path = out_dir / 'strategy_b_daily.json'
with open(result_path, 'w') as f:
    json.dump(results, f, indent=2)

print(f"Saved: {result_path}")
print(json.dumps(results['metrics'], indent=2, default=str))
"""))

# Cell 12: Equity curve
cells.append(nbf.v4.new_code_cell("""\
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

equity = pf.value()
fig, axes = plt.subplots(2, 1, figsize=(14, 8), sharex=True, gridspec_kw={'height_ratios': [3, 1]})

axes[0].plot(equity.index, equity.values, label='Strategy B equity', linewidth=1.2, color='steelblue')
axes[0].axhline(INIT_CASH, color='gray', linestyle='--', alpha=0.5, label='Initial cash')
axes[0].set_title('Strategy B (Mean Reversion Daily) — Equity Curve')
axes[0].set_ylabel('Portfolio Value (KRW)')
axes[0].legend(loc='upper left')
axes[0].grid(True, alpha=0.3)

drawdown = (equity / equity.cummax() - 1) * 100
axes[1].fill_between(drawdown.index, drawdown.values, 0, color='red', alpha=0.3)
axes[1].set_title('Drawdown (%)')
axes[1].set_ylabel('Drawdown %')
axes[1].grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig(out_dir / 'strategy_b_equity.png', dpi=100, bbox_inches='tight')
plt.close()
print(f"Equity curve saved: {out_dir / 'strategy_b_equity.png'}")
"""))

# Cell 13: Summary
cells.append(nbf.v4.new_code_cell("""\
print("=" * 60)
print("W1-03 Strategy B Verification Summary")
print("=" * 60)
print(f"Feature ID:    STR-B-001")
print(f"Data:          {PARQUET_NAME}")
print(f"Data hash:     {DATA_HASH[:16]}...")
print(f"Bars:          {len(df)} (range {df.index[0].date()} ~ {df.index[-1].date()})")
print()
print("Pre-registered parameters:")
print(f"  MA={MA_PERIOD}, RSI({RSI_PERIOD}) buy<{RSI_BUY} sell>{RSI_SELL}, time_stop={TIME_STOP_DAYS}d, SL={SL_PCT}")
print()
print("Backtest results:")
print(f"  Sharpe:        {sharpe:.4f} (95% CI [{sharpe_ci_lo:.4f}, {sharpe_ci_hi:.4f}], 정규 근사)")
print(f"  Total Return:  {total_return*100:.2f}%")
print(f"  Max Drawdown:  {max_dd*100:.2f}%")
print(f"    Deepest DD:  {deepest_dd_pct*100:.2f}%, {deepest_dd_duration_days}d, {'recovered' if deepest_dd_recovered else 'still active'}")
print(f"    Longest DD:  {longest_dd_pct*100:.2f}%, {longest_dd_duration_days}d, {'recovered' if longest_dd_recovered else 'still active'}")
print(f"  Total Trades:  {total_trades}")
if total_trades > 0:
    print(f"  Win Rate:      {win_rate*100:.2f}%")
    print(f"  Profit Factor: {profit_factor:.3f}")
print()
print("Edge case checks:")
print(f"  Warmup zero entries: PASS")
print(f"  Time stop mask count (raw): {int(time_exits.iloc[MA_PERIOD:].sum())}")
print(f"  Exit reason breakdown:")
print(f"    time_stop_exclusive:  {time_stop_exclusive}")
print(f"    time_stop_coincident: {time_stop_coincident}")
print(f"    rsi_exclusive:        {rsi_exclusive}")
print(f"    sl_stop_or_other:     {sl_stop_or_other}")
print()
print("Go criteria (W1-06에서 종합 평가):")
print(f"  Sharpe > 0.5: {'PASS' if sharpe > 0.5 else 'FAIL'} ({sharpe:.4f})")
print(f"  MDD < 50%:    {'PASS' if abs(max_dd) < 0.5 else 'FAIL'} ({max_dd*100:.2f}%)")
"""))

nb.cells = cells

out_path = Path(__file__).parent.parent / 'notebooks' / '03_strategy_b_mean_reversion_daily.ipynb'
out_path.parent.mkdir(exist_ok=True)
with open(out_path, 'w') as f:
    nbf.write(nb, f)

print(f"Notebook created: {out_path}")
