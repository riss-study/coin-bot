"""Create notebook 02_strategy_a_trend_daily.ipynb programmatically.

Run with: python _tools/make_notebook_02.py
Output: notebooks/02_strategy_a_trend_daily.ipynb
"""
import nbformat as nbf
from pathlib import Path

nb = nbf.v4.new_notebook()
cells = []

# Cell 1: Header
cells.append(nbf.v4.new_markdown_cell("""\
# Task W1-02 — Strategy A: 추세 추종 일봉 백테스트

**Feature ID**: STR-A-001
**Sub-plan**: `docs/stage1-subplans/w1-02-strategy-a-daily.md`

Padysak/Vojtko 영감 추세 추종 전략을 일봉으로 백테스트.

## 사전 지정 파라미터 (변경 금지)

| 파라미터 | 값 | 설명 |
|---------|-----|------|
| MA_PERIOD | 200 | 장기 추세 필터 |
| DONCHIAN_HIGH | 20 | 돌파 신호 (20일 최고가) |
| DONCHIAN_LOW | 10 | 청산 신호 (10일 최저가) |
| VOL_AVG_PERIOD | 20 | 거래량 평균 윈도우 |
| VOL_MULT | 1.5 | 거래량 필터 배수 |
| SL_PCT | 0.08 | 하드 스톱 -8% (vectorbt sl_stop fraction) |

## 신호 로직

진입 마스크 변수는 `donchian_high`, `donchian_low`, `vol_avg`로 정의되며
이들은 변수 생성 시 이미 `.shift(1)`이 적용됨 (look-ahead 차단).
따라서 마스크 식에서는 추가 shift 없이 사용:

```
진입 (모두 충족):
  close > ma200          (대추세 상승, EOD 시점 신호 → 다음 바 fill semantics)
  AND close > donchian_high  (사전에 .shift(1) 적용된 20일 최고가 돌파)
  AND volume > vol_avg * 1.5 (사전에 .shift(1) 적용된 거래량 평균 동반)

청산 (하나 충족):
  close < donchian_low   (사전에 .shift(1) 적용된 10일 최저가 이탈)
  OR sl_stop=0.08        (-8% 하드 스톱, vectorbt 자동 처리)
```

**Look-ahead 안전성**: `close > ma200`은 EOD 신호 → 다음 바 open/close fill 의미.
`donchian_*`, `vol_avg`는 모두 `.shift(1)` 적용됨.

## 검증된 vectorbt 0.28.5 API

- `sl_stop` fraction (0.08 = 8%)
- `sl_trail=False` (하드 스톱)
- `freq='1D'`
- `pf.sharpe_ratio()` 메서드 호출 (괄호 필수)
- ts_stop / td_stop / max_duration 사용 안 함
"""))

# Cell 2: Imports + version check
cells.append(nbf.v4.new_code_cell("""\
import pandas as pd
import numpy as np
import vectorbt as vbt
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

# Cell 3: Data hash verification (consumer notebook rule)
cells.append(nbf.v4.new_code_cell("""\
# 데이터 해시 검증 (consumer 노트북 첫 셀 룰, research/CLAUDE.md)
DATA_DIR = Path('../data')
PARQUET_NAME = 'KRW-BTC_1d_frozen_20260412.parquet'
PARQUET_PATH = DATA_DIR / PARQUET_NAME

def sha256_file(path):
    h = hashlib.sha256()
    with open(path, 'rb') as f:
        for chunk in iter(lambda: f.read(65536), b''):
            h.update(chunk)
    return h.hexdigest()

# data_hashes.txt에서 expected 해시 읽기
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

# Cell 4: Load data
cells.append(nbf.v4.new_code_cell("""\
df = pd.read_parquet(PARQUET_PATH)
assert df.index.tz is not None and str(df.index.tz) == 'UTC', f"Expected UTC, got {df.index.tz}"

close  = df['close']
high   = df['high']
low    = df['low']
volume = df['volume']

print(f"Bars: {len(df)}")
print(f"Range: {df.index[0]} ~ {df.index[-1]}")
print(f"Columns: {list(df.columns)}")
print(f"NaN total: {df.isna().sum().sum()}")
"""))

# Cell 5: Pre-registered parameters (constants, no tweaking)
cells.append(nbf.v4.new_code_cell("""\
# 사전 지정 파라미터 — 변경 금지 (Go/No-Go는 이 값으로만 평가)
MA_PERIOD       = 200
DONCHIAN_HIGH   = 20
DONCHIAN_LOW    = 10
VOL_AVG_PERIOD  = 20
VOL_MULT        = 1.5
SL_PCT          = 0.08    # vectorbt fraction (8%)

# 백테스트 설정
INIT_CASH = 1_000_000     # 100만원 (테스트용)
FEES      = 0.0005        # 업비트 0.05%
SLIPPAGE  = 0.0005        # 0.05% 슬리피지 추정
FREQ      = '1D'

# 주: ATR/Wilder 지표는 W1-04 강건성 분석에서 사용. W1-02는 고정 -8% 하드 스톱만.
"""))

# Cell 6: Indicator computation
cells.append(nbf.v4.new_code_cell("""\
# MA200 — 장기 추세 필터
ma200 = close.rolling(window=MA_PERIOD).mean()

# Donchian 채널 — .shift(1) 필수 (look-ahead 방지)
donchian_high = high.rolling(window=DONCHIAN_HIGH).max().shift(1)
donchian_low  = low.rolling(window=DONCHIAN_LOW).min().shift(1)

# 거래량 평균 — .shift(1) 필수 (신호 바의 평균은 알 수 없음)
vol_avg = volume.rolling(window=VOL_AVG_PERIOD).mean().shift(1)

# Sanity check
print(f"ma200 NaN (warmup): {ma200.isna().sum()} (expected: {MA_PERIOD - 1})")
print(f"donchian_high NaN: {donchian_high.isna().sum()} (expected: {DONCHIAN_HIGH})")
print(f"donchian_low NaN: {donchian_low.isna().sum()} (expected: {DONCHIAN_LOW})")
print(f"vol_avg NaN: {vol_avg.isna().sum()} (expected: {VOL_AVG_PERIOD})")
"""))

# Cell 7: Entry / exit masks
cells.append(nbf.v4.new_code_cell("""\
# 진입 마스크 (Boolean Series)
# donchian_high, donchian_low, vol_avg는 이미 .shift(1) 적용됨 (cell 6)
# close > ma200: EOD 시점 신호 (close at bar t는 bar t close 시점에만 알려짐)
#   → vectorbt 기본 동작은 신호 발생 바의 close에 fill (next-bar fill 아님)
#   → t 시점 신호 + t 시점 close fill 은 EOD 신호 → 같은 바 close fill 로 해석
entries = (close > ma200) & (close > donchian_high) & (volume > vol_avg * VOL_MULT)

# 청산 마스크 (Donchian low 이탈, 이미 shift 적용됨)
exits = close < donchian_low

# NaN을 False로 명시 (warmup 기간 안전)
entries = entries.fillna(False).astype(bool)
exits = exits.fillna(False).astype(bool)

print(f"Total entries: {entries.sum()}")
print(f"Total exits:   {exits.sum()}")

# === Edge case 1: 200 bar warmup 기간 entries == 0 강제 검증 ===
# .iloc[:MA_PERIOD] 는 정확히 첫 MA_PERIOD개 bar (반-개구간, off-by-one 방지)
warmup_entries = int(entries.iloc[:MA_PERIOD].sum())
warmup_period_end = df.index[MA_PERIOD - 1]  # 마지막 warmup bar
print(f"Warmup entries (first {MA_PERIOD} bars, last warmup bar {warmup_period_end.date()}): {warmup_entries}")
assert warmup_entries == 0, f"Warmup entries must be 0, got {warmup_entries}"
print(f"  PASS")

# === Edge case 2: 거래량 필터가 실제로 신호를 거부하는지 확인 ===
# 거래량 필터 없는 가상 entries와 비교
entries_no_vol = ((close > ma200) & (close > donchian_high)).fillna(False).astype(bool)
filtered_out = int(entries_no_vol.sum() - entries.sum())
print(f"Entries without volume filter: {entries_no_vol.sum()}")
print(f"Entries with volume filter:    {entries.sum()}")
print(f"Filtered by volume (1.5x avg): {filtered_out}")
assert filtered_out > 0, "Volume filter should reject some signals over 5 years; got 0"
print(f"  PASS (volume filter is active)")
"""))

# Cell 8: vectorbt backtest (verified API)
cells.append(nbf.v4.new_code_cell("""\
# vectorbt 0.28.5 검증된 API만 사용
# - sl_stop: fraction (0.08 = 8%)
# - sl_trail: boolean (False = 하드 스톱)
# - freq: '1D' 일봉
# - ts_stop, td_stop, max_duration 사용 안 함

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
# 메서드 호출 (괄호 필수)
stats = pf.stats()
print(stats)
"""))

# Cell 10: Extract key metrics
cells.append(nbf.v4.new_code_cell("""\
# 핵심 지표 추출 (모두 메서드 호출)
sharpe       = float(pf.sharpe_ratio())
total_return = float(pf.total_return())
max_dd       = float(pf.max_drawdown())
total_trades = int(pf.trades.count())

# Max drawdown duration — equity curve로 직접 계산 (peak → recovery까지 일수)
equity = pf.value()
running_max = equity.cummax()
drawdown_pct = (equity / running_max - 1.0)
underwater = drawdown_pct < 0  # 신규 peak 이전까지의 underwater 기간
# 가장 깊은 dd가 일어난 시점 → 직전 peak → recovery 시점 까지의 일수
max_dd_idx = drawdown_pct.idxmin()  # 가장 깊은 시점
peak_before = equity.loc[:max_dd_idx].idxmax()  # 직전 peak
# Recovery: max_dd_idx 이후 equity가 peak_before 수준 회복한 첫 시점 (없으면 마지막 시점까지)
post = equity.loc[max_dd_idx:]
recovery = post[post >= equity.loc[peak_before]]
recovery_idx = recovery.index[0] if len(recovery) > 0 else equity.index[-1]
max_dd_duration_days = (recovery_idx - peak_before).days
mdd_recovered = len(recovery) > 0

# Trades-related (있을 때만)
if total_trades > 0:
    win_rate      = float(pf.trades.win_rate())
    profit_factor = float(pf.trades.profit_factor())
else:
    win_rate = float('nan')
    profit_factor = float('nan')

print(f"Sharpe:        {sharpe:.4f}")
print(f"Total Return:  {total_return*100:.2f}%")
print(f"Max Drawdown:  {max_dd*100:.2f}%")
print(f"MDD Duration:  {max_dd_duration_days} days ({'recovered' if mdd_recovered else 'still underwater'})")
print(f"Win Rate:      {win_rate*100:.2f}%" if total_trades > 0 else "Win Rate:      N/A")
print(f"Profit Factor: {profit_factor:.3f}" if total_trades > 0 else "Profit Factor: N/A")
print(f"Total Trades:  {total_trades}")

# Sharpe 표준오차 — return-basis (Lo 2002, "The Statistics of Sharpe Ratios")
import numpy as np
T = len(close)  # 일일 관측 수
sharpe_se = float(np.sqrt((1 + 0.5 * sharpe**2) / T))
sharpe_ci_lo = sharpe - 1.96 * sharpe_se
sharpe_ci_hi = sharpe + 1.96 * sharpe_se
print(f"Sharpe SE (return-basis, T={T}): {sharpe_se:.4f}")
print(f"Sharpe 95% CI: [{sharpe_ci_lo:.4f}, {sharpe_ci_hi:.4f}]")
print(f"Note: trade-basis (N={total_trades}) SE는 더 큼. Bootstrap CI는 W2-02에서 정량화 예정.")

# Week 1 Go 기준 평가 (W1-06에서 종합, 여기선 기록만)
print()
print("=== Week 1 Go 기준 평가 (참고) ===")
print(f"Sharpe > 0.8: {'PASS' if sharpe > 0.8 else 'FAIL'}")
print(f"MDD < 50%:    {'PASS' if abs(max_dd) < 0.5 else 'FAIL'}")
"""))

# Cell 11: Save results JSON
cells.append(nbf.v4.new_code_cell("""\
out_dir = Path('../outputs')
out_dir.mkdir(exist_ok=True)

results = {
    'feature_id': 'STR-A-001',
    'task_id': 'W1-02',
    'strategy': 'A_trend_daily',
    'description': 'Padysak/Vojtko-inspired trend-following: MA200 + Donchian(20/10) + Volume 1.5x + sl_stop 8%',
    'data_file': PARQUET_NAME,
    'data_hash': DATA_HASH,
    'data_bars': len(df),
    'data_range': [df.index[0].isoformat(), df.index[-1].isoformat()],
    'parameters': {
        'ma_period': MA_PERIOD,
        'donchian_high': DONCHIAN_HIGH,
        'donchian_low': DONCHIAN_LOW,
        'vol_avg_period': VOL_AVG_PERIOD,
        'vol_mult': VOL_MULT,
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
        'sharpe_ci_95': [sharpe_ci_lo, sharpe_ci_hi],
        'total_return': total_return,
        'max_drawdown': max_dd,
        'max_drawdown_duration_days': max_dd_duration_days,
        'max_drawdown_recovered': mdd_recovered,
        'win_rate': win_rate if total_trades > 0 else None,
        'profit_factor': profit_factor if total_trades > 0 else None,
        'total_trades': total_trades,
    },
    'edge_case_checks': {
        'warmup_zero_entries': True,  # asserted above
        'volume_filter_active': True,  # asserted above
    },
    'go_criteria_eval': {
        'sharpe_gt_0.8': sharpe > 0.8,
        'mdd_lt_50pct': abs(max_dd) < 0.5,
    },
    'generated_at': datetime.now(timezone.utc).isoformat(),
}

result_path = out_dir / 'strategy_a_daily.json'
with open(result_path, 'w') as f:
    json.dump(results, f, indent=2)

print(f"Saved: {result_path}")
print(json.dumps(results['metrics'], indent=2))
"""))

# Cell 12: Equity curve plot (참고용)
cells.append(nbf.v4.new_code_cell("""\
import matplotlib
matplotlib.use('Agg')  # non-interactive backend (saves PNG without showing)
import matplotlib.pyplot as plt

equity = pf.value()
fig, axes = plt.subplots(2, 1, figsize=(14, 8), sharex=True, gridspec_kw={'height_ratios': [3, 1]})

axes[0].plot(equity.index, equity.values, label='Strategy A equity', linewidth=1.2)
axes[0].axhline(INIT_CASH, color='gray', linestyle='--', alpha=0.5, label='Initial cash')
axes[0].set_title('Strategy A (Trend-Following Daily) — Equity Curve')
axes[0].set_ylabel('Portfolio Value (KRW)')
axes[0].legend(loc='upper left')
axes[0].grid(True, alpha=0.3)

drawdown = (equity / equity.cummax() - 1) * 100
axes[1].fill_between(drawdown.index, drawdown.values, 0, color='red', alpha=0.3)
axes[1].set_title('Drawdown (%)')
axes[1].set_ylabel('Drawdown %')
axes[1].grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig(out_dir / 'strategy_a_equity.png', dpi=100, bbox_inches='tight')
plt.close()
print(f"Equity curve saved: {out_dir / 'strategy_a_equity.png'}")
"""))

# Cell 13: Final verification summary
cells.append(nbf.v4.new_code_cell("""\
print("=" * 60)
print("W1-02 Strategy A Verification Summary")
print("=" * 60)
print(f"Feature ID:    STR-A-001")
print(f"Data:          {PARQUET_NAME}")
print(f"Data hash:     {DATA_HASH[:16]}...")
print(f"Bars:          {len(df)} (range {df.index[0].date()} ~ {df.index[-1].date()})")
print()
print("Pre-registered parameters:")
print(f"  MA={MA_PERIOD}, Donchian={DONCHIAN_HIGH}/{DONCHIAN_LOW}, Vol={VOL_AVG_PERIOD}*{VOL_MULT}, SL={SL_PCT}")
print()
print("Backtest results:")
print(f"  Sharpe:        {sharpe:.4f} (95% CI [{sharpe_ci_lo:.4f}, {sharpe_ci_hi:.4f}], return-basis)")
print(f"  Total Return:  {total_return*100:.2f}%")
print(f"  Max Drawdown:  {max_dd*100:.2f}% (duration {max_dd_duration_days} days, {'recovered' if mdd_recovered else 'still underwater'})")
print(f"  Total Trades:  {total_trades}")
if total_trades > 0:
    print(f"  Win Rate:      {win_rate*100:.2f}%")
    print(f"  Profit Factor: {profit_factor:.3f}")
print()
print("Edge case checks:")
print(f"  Warmup zero entries: PASS")
print(f"  Volume filter active: PASS")
print()
print("Go criteria (W1-06에서 종합 평가):")
print(f"  Sharpe > 0.8: {'PASS' if sharpe > 0.8 else 'FAIL'} ({sharpe:.4f})")
print(f"  MDD < 50%:    {'PASS' if abs(max_dd) < 0.5 else 'FAIL'} ({max_dd*100:.2f}%)")
"""))

nb.cells = cells

out_path = Path(__file__).parent.parent / 'notebooks' / '02_strategy_a_trend_daily.ipynb'
out_path.parent.mkdir(exist_ok=True)
with open(out_path, 'w') as f:
    nbf.write(nb, f)

print(f"Notebook created: {out_path}")
