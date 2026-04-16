"""Create notebook 04_robustness_sensitivity.ipynb programmatically.

Run with: python _tools/make_notebook_04.py
Output: notebooks/04_robustness_sensitivity.ipynb
"""
import nbformat as nbf
from pathlib import Path

nb = nbf.v4.new_notebook()
cells = []

# Cell 1: Header (markdown)
cells.append(nbf.v4.new_markdown_cell("""\
# Task W1-04 -- 강건성 + 민감도 분석

**Feature ID**: BT-001
**Sub-plan**: `docs/stage1-subplans/w1-04-robustness.md`

W1-02 (Strategy A)와 W1-03 (Strategy B) 결과의 강건성을 두 측면에서 검증:

1. **연도별 분할**: 5개 연도(2021~2025) + 2026Q1별 결과가 균등한가?
2. **파라미터 민감도**: 사전 지정 파라미터 주변에서 성과가 평탄(robust)한가?

## 핵심 규칙

> **민감도 그리드의 최고값을 보고하지 않는다.**
> **사전 지정 파라미터만 Go/No-Go 근거.** 그리드는 등고선 시각화로 평탄성 검증용.
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

from ta.momentum import RSIIndicator

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import seaborn as sns

from importlib.metadata import version
print(f"pandas:   {version('pandas')}")
print(f"numpy:    {version('numpy')}")
print(f"vectorbt: {version('vectorbt')}")
print(f"ta:       {version('ta')}")
print(f"seaborn:  {version('seaborn')}")
"""))

# Cell 3: Data hash verification
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
assert df.index.is_monotonic_increasing, "Index not monotonic"
assert len(df) == 1927, f"Expected 1927 bars, got {len(df)}"

close  = df['close']
high   = df['high']
low    = df['low']
volume = df['volume']

print(f"Bars: {len(df)}")
print(f"Range: {df.index[0]} ~ {df.index[-1]}")
print(f"NaN total: {df.isna().sum().sum()}")
"""))

# Cell 5: Constants
cells.append(nbf.v4.new_code_cell("""\
# === 공통 백테스트 설정 ===
INIT_CASH = 1_000_000
FEES      = 0.0005
SLIPPAGE  = 0.0005
FREQ      = '1D'

# === Strategy A 사전 지정 파라미터 ===
A_MA_PERIOD      = 200
A_DONCHIAN_HIGH  = 20
A_DONCHIAN_LOW   = 10
A_VOL_AVG_PERIOD = 20
A_VOL_MULT       = 1.5
A_SL_PCT         = 0.08

# === Strategy B 사전 지정 파라미터 ===
B_MA_PERIOD      = 200
B_RSI_PERIOD     = 4
B_RSI_BUY        = 25
B_RSI_SELL       = 50
B_TIME_STOP_DAYS = 5
B_SL_PCT         = 0.08

print("Pre-registered parameters loaded (constants, no tweaking)")
"""))

# Cell 6: Strategy functions + metric extractor
cells.append(nbf.v4.new_code_cell("""\
def run_strategy_a(close, high, low, volume, ma_period, donchian_high, donchian_low,
                   vol_avg_period, vol_mult, sl_pct, fees=0.0005, slippage=0.0005):
    \"\"\"Run Strategy A (trend-following) backtest. Returns vectorbt Portfolio.\"\"\"
    ma = close.rolling(window=ma_period).mean()
    dh = high.rolling(window=donchian_high).max().shift(1)
    dl = low.rolling(window=donchian_low).min().shift(1)
    va = volume.rolling(window=vol_avg_period).mean().shift(1)

    entries = ((close > ma) & (close > dh) & (volume > va * vol_mult)).fillna(False).astype(bool)
    exits = (close < dl).fillna(False).astype(bool)

    pf = vbt.Portfolio.from_signals(
        close=close, entries=entries, exits=exits,
        sl_stop=sl_pct, sl_trail=False,
        init_cash=INIT_CASH, fees=fees, slippage=slippage, freq=FREQ,
    )
    return pf


def run_strategy_b(close, ma_period, rsi_period, rsi_buy, rsi_sell, time_stop_days,
                   sl_pct, fees=0.0005, slippage=0.0005):
    \"\"\"Run Strategy B (mean-reversion) backtest. Returns vectorbt Portfolio.\"\"\"
    ma = close.rolling(window=ma_period).mean()
    rsi = RSIIndicator(close=close, window=rsi_period).rsi()

    entries = ((close > ma) & (rsi < rsi_buy)).fillna(False).astype(bool)
    rsi_exits = (rsi > rsi_sell).fillna(False).astype(bool)
    time_exits = entries.shift(time_stop_days).fillna(False).astype(bool)
    exits = (rsi_exits | time_exits).astype(bool)

    pf = vbt.Portfolio.from_signals(
        close=close, entries=entries, exits=exits,
        sl_stop=sl_pct, sl_trail=False,
        init_cash=INIT_CASH, fees=fees, slippage=slippage, freq=FREQ,
    )
    return pf


def extract_metrics(pf):
    \"\"\"Extract summary metrics dict from Portfolio. NaN-safe for 0-trade case.\"\"\"
    total_trades = int(pf.trades.count())
    sharpe = float(pf.sharpe_ratio())
    total_return = float(pf.total_return())
    max_dd = float(pf.max_drawdown())
    if total_trades > 0:
        win_rate = float(pf.trades.win_rate())
        pf_val = float(pf.trades.profit_factor())
    else:
        win_rate = float('nan')
        pf_val = float('nan')
    return {
        'sharpe': sharpe, 'total_return': total_return, 'max_drawdown': max_dd,
        'win_rate': win_rate, 'profit_factor': pf_val, 'total_trades': total_trades,
    }


print("Strategy functions defined: run_strategy_a, run_strategy_b, extract_metrics")
"""))

# Cell 7: Validation — reproduce W1-02 / W1-03 Sharpe
cells.append(nbf.v4.new_code_cell("""\
# === 검증: 함수화된 전략이 W1-02/W1-03 결과를 정확히 재현하는지 확인 ===
# 재현 실패 시 함수 로직에 버그가 있다는 뜻이므로 assert로 강제.

pf_a = run_strategy_a(close, high, low, volume,
    ma_period=A_MA_PERIOD, donchian_high=A_DONCHIAN_HIGH, donchian_low=A_DONCHIAN_LOW,
    vol_avg_period=A_VOL_AVG_PERIOD, vol_mult=A_VOL_MULT, sl_pct=A_SL_PCT)

pf_b = run_strategy_b(close,
    ma_period=B_MA_PERIOD, rsi_period=B_RSI_PERIOD, rsi_buy=B_RSI_BUY,
    rsi_sell=B_RSI_SELL, time_stop_days=B_TIME_STOP_DAYS, sl_pct=B_SL_PCT)

sharpe_a = float(pf_a.sharpe_ratio())
sharpe_b = float(pf_b.sharpe_ratio())

# W1-02 known: 1.0352900037639534, W1-03 known: 0.13615418374262483
EXPECTED_A = 1.0352900037639534
EXPECTED_B = 0.13615418374262483
TOL = 1e-4

assert abs(sharpe_a - EXPECTED_A) < TOL, f"Strategy A Sharpe mismatch: {sharpe_a} vs expected {EXPECTED_A}"
assert abs(sharpe_b - EXPECTED_B) < TOL, f"Strategy B Sharpe mismatch: {sharpe_b} vs expected {EXPECTED_B}"

print(f"Strategy A Sharpe: {sharpe_a:.10f} (expected {EXPECTED_A:.10f}) -- MATCH")
print(f"Strategy B Sharpe: {sharpe_b:.10f} (expected {EXPECTED_B:.10f}) -- MATCH")
print(f"Strategy A trades: {pf_a.trades.count()}, Strategy B trades: {pf_b.trades.count()}")
print("\\nValidation PASSED: refactored functions reproduce W1-02/W1-03 exactly")

sharpe_a_match = True
sharpe_b_match = True
"""))

# Cell 8: Yearly breakdown computation
cells.append(nbf.v4.new_code_cell("""\
# === 연도별 분할 분석 ===
# daily returns를 연도별로 리샘플하여 return, sharpe, mdd 계산

def yearly_breakdown(pf, label):
    \"\"\"Compute yearly return, sharpe, MDD from portfolio daily returns.\"\"\"
    rets = pf.returns()

    yearly_return = rets.resample('YS').apply(lambda x: (1 + x).prod() - 1)
    yearly_sharpe = rets.resample('YS').apply(
        lambda x: x.mean() / x.std() * np.sqrt(252) if len(x) > 1 and x.std() > 0 else 0.0
    )
    yearly_mdd = rets.resample('YS').apply(
        lambda x: ((1 + x).cumprod() / (1 + x).cumprod().cummax() - 1).min() if len(x) > 0 else 0.0
    )

    rows = []
    for ts in yearly_return.index:
        year = ts.year
        # 2026은 partial (Q1만 존재)
        year_label = f"{year}" if year < 2026 else f"{year}Q1*"
        rows.append({
            'strategy': label,
            'year': year_label,
            'year_int': year,
            'return': float(yearly_return.loc[ts]),
            'sharpe': float(yearly_sharpe.loc[ts]),
            'mdd': float(yearly_mdd.loc[ts]),
            'trading_days': int(rets.loc[ts.strftime('%Y'):ts.strftime('%Y')].shape[0]),
            'partial': year >= 2026,
        })
    return rows

rows_a = yearly_breakdown(pf_a, 'A')
rows_b = yearly_breakdown(pf_b, 'B')

yearly_df = pd.DataFrame(rows_a + rows_b)
print(f"Yearly breakdown: {len(yearly_df)} rows ({len(rows_a)} A + {len(rows_b)} B)")
"""))

# Cell 9: Yearly breakdown display + domination check + CSV
cells.append(nbf.v4.new_code_cell("""\
# === 연도별 결과 표 출력 ===
out_dir = Path('../outputs')
out_dir.mkdir(exist_ok=True)

for strat in ['A', 'B']:
    sub = yearly_df[yearly_df['strategy'] == strat]
    print(f"\\n=== Strategy {strat} 연도별 분할 ===")
    print(f"{'Year':<10} {'Return':>10} {'Sharpe':>10} {'MDD':>10} {'Days':>6}")
    print("-" * 50)
    for _, r in sub.iterrows():
        print(f"{r['year']:<10} {r['return']*100:>9.2f}% {r['sharpe']:>10.4f} {r['mdd']*100:>9.2f}% {r['trading_days']:>6d}")

# === 70% 지배 경고 (full year만, 2021-2025) ===
domination_warning_a = False
domination_warning_b = False
domination_details = []

for strat, pf_obj in [('A', pf_a), ('B', pf_b)]:
    sub = yearly_df[(yearly_df['strategy'] == strat) & (~yearly_df['partial'])]
    total_return_full = float((1 + pf_obj.returns().loc[:'2025']).prod() - 1)

    if abs(total_return_full) > 1e-6:
        for _, r in sub.iterrows():
            contribution = r['return'] / total_return_full
            if abs(contribution) > 0.70:
                msg = f"Strategy {strat}: {r['year']} contributes {contribution*100:.1f}% of full-year total return"
                domination_details.append(msg)
                print(f"\\n*** WARNING: {msg}")
                if strat == 'A':
                    domination_warning_a = True
                else:
                    domination_warning_b = True

if not domination_details:
    print("\\nNo year-domination warnings (no single year > 70% of total return)")

# CSV 저장
yearly_df.to_csv(out_dir / 'yearly_breakdown.csv', index=False)
print(f"\\nSaved: yearly_breakdown.csv")
"""))

# Cell 10: Strategy A sensitivity grid
cells.append(nbf.v4.new_code_cell("""\
# === Strategy A 민감도 그리드 (125 조합) ===
# 변동 파라미터: ma, donchian_high, donchian_low
# 고정 파라미터: vol_avg=20, vol_mult=1.5, sl=0.08
# 주: 결과는 참고용. Go/No-Go는 사전 지정 파라미터(200, 20, 10)만.

ma_grid_a = [100, 150, 200, 250, 300]
dh_grid   = [10, 15, 20, 30, 40]
dl_grid   = [5, 7, 10, 15, 20]

results_a = []
total_a = len(ma_grid_a) * len(dh_grid) * len(dl_grid)
count = 0

for ma in ma_grid_a:
    for dh in dh_grid:
        for dl in dl_grid:
            count += 1
            try:
                pf_tmp = run_strategy_a(close, high, low, volume,
                    ma_period=ma, donchian_high=dh, donchian_low=dl,
                    vol_avg_period=A_VOL_AVG_PERIOD, vol_mult=A_VOL_MULT, sl_pct=A_SL_PCT)
                m = extract_metrics(pf_tmp)
                results_a.append({'ma': ma, 'dh': dh, 'dl': dl, **m})
            except Exception as e:
                results_a.append({'ma': ma, 'dh': dh, 'dl': dl,
                    'sharpe': float('nan'), 'total_return': float('nan'),
                    'max_drawdown': float('nan'), 'win_rate': float('nan'),
                    'profit_factor': float('nan'), 'total_trades': 0})
            if count % 25 == 0:
                print(f"  Progress: {count}/{total_a}")

df_sens_a = pd.DataFrame(results_a)
df_sens_a.to_csv(out_dir / 'sensitivity_a.csv', index=False)
print(f"\\nStrategy A grid: {len(df_sens_a)} combos, {df_sens_a['sharpe'].isna().sum()} NaN")
print(f"Saved: sensitivity_a.csv")
"""))

# Cell 11: Strategy B sensitivity grid
cells.append(nbf.v4.new_code_cell("""\
# === Strategy B 민감도 그리드 (125 조합) ===
# 변동 파라미터: ma, rsi_period, rsi_buy
# 고정 파라미터: rsi_sell=50, time_stop=5, sl=0.08
# 주: 결과는 참고용.

ma_grid_b    = [100, 150, 200, 250, 300]
rsi_p_grid   = [3, 4, 5, 7, 10]
rsi_buy_grid = [15, 20, 25, 30, 35]

results_b = []
total_b = len(ma_grid_b) * len(rsi_p_grid) * len(rsi_buy_grid)
count = 0

for ma in ma_grid_b:
    for rp in rsi_p_grid:
        for rb in rsi_buy_grid:
            count += 1
            try:
                pf_tmp = run_strategy_b(close,
                    ma_period=ma, rsi_period=rp, rsi_buy=rb,
                    rsi_sell=B_RSI_SELL, time_stop_days=B_TIME_STOP_DAYS, sl_pct=B_SL_PCT)
                m = extract_metrics(pf_tmp)
                results_b.append({'ma': ma, 'rsi_p': rp, 'rsi_buy': rb, **m})
            except Exception as e:
                results_b.append({'ma': ma, 'rsi_p': rp, 'rsi_buy': rb,
                    'sharpe': float('nan'), 'total_return': float('nan'),
                    'max_drawdown': float('nan'), 'win_rate': float('nan'),
                    'profit_factor': float('nan'), 'total_trades': 0})
            if count % 25 == 0:
                print(f"  Progress: {count}/{total_b}")

df_sens_b = pd.DataFrame(results_b)
df_sens_b.to_csv(out_dir / 'sensitivity_b.csv', index=False)
print(f"\\nStrategy B grid: {len(df_sens_b)} combos, {df_sens_b['sharpe'].isna().sum()} NaN")
print(f"Saved: sensitivity_b.csv")
"""))

# Cell 12: Flatness analysis
cells.append(nbf.v4.new_code_cell("""\
# === 평탄성 분석 ===
# 사전 지정 파라미터 주변 50% 이웃의 Sharpe std를 계산.
# std < 0.3 → PASS (평탄/robust), >= 0.3 → WARNING (뾰족/overfit 의심)

# Strategy A: 2D slice where dl=10 (pre-registered), pivot ma x dh
slice_a = df_sens_a[df_sens_a['dl'] == A_DONCHIAN_LOW].pivot(index='ma', columns='dh', values='sharpe')
# 50% 이웃: ma in [150,250], dh in [15,30]
neighborhood_a = slice_a.loc[[150, 200, 250], [15, 20, 30]]
flatness_std_a = float(neighborhood_a.values.flatten()[~np.isnan(neighborhood_a.values.flatten())].std())
flatness_pass_a = flatness_std_a < 0.3

print("=== Strategy A 평탄성 ===")
print(f"2D slice (dl={A_DONCHIAN_LOW} fixed):")
print(slice_a.to_string())
print(f"\\n50% 이웃 (ma=[150,200,250], dh=[15,20,30]):")
print(neighborhood_a.to_string())
print(f"\\nNeighborhood Sharpe std: {flatness_std_a:.4f}")
print(f"Flatness PASS (< 0.3): {flatness_pass_a}")

# Strategy B: 2D slice where rsi_p=4 (pre-registered), pivot ma x rsi_buy
slice_b = df_sens_b[df_sens_b['rsi_p'] == B_RSI_PERIOD].pivot(index='ma', columns='rsi_buy', values='sharpe')
# 50% 이웃: ma in [150,200,250], rsi_buy in [20,25,30]
neighborhood_b = slice_b.loc[[150, 200, 250], [20, 25, 30]]
flatness_std_b = float(neighborhood_b.values.flatten()[~np.isnan(neighborhood_b.values.flatten())].std())
flatness_pass_b = flatness_std_b < 0.3

print("\\n=== Strategy B 평탄성 ===")
print(f"2D slice (rsi_p={B_RSI_PERIOD} fixed):")
print(slice_b.to_string())
print(f"\\n50% 이웃 (ma=[150,200,250], rsi_buy=[20,25,30]):")
print(neighborhood_b.to_string())
print(f"\\nNeighborhood Sharpe std: {flatness_std_b:.4f}")
print(f"Flatness PASS (< 0.3): {flatness_pass_b}")

# 사전 지정 파라미터 위치의 Sharpe 값
pre_reg_sharpe_a = float(slice_a.loc[A_MA_PERIOD, A_DONCHIAN_HIGH])
pre_reg_sharpe_b = float(slice_b.loc[B_MA_PERIOD, B_RSI_BUY])
print(f"\\nPre-registered param Sharpe: A={pre_reg_sharpe_a:.4f}, B={pre_reg_sharpe_b:.4f}")
"""))

# Cell 13: Strategy A heatmap
cells.append(nbf.v4.new_code_cell("""\
# === Strategy A Heatmap: MA x Donchian High (Donchian Low=10 고정) ===
fig, ax = plt.subplots(figsize=(10, 7))

# slice_a: index=ma, columns=dh, values=sharpe
annot_data = slice_a.copy()
sns.heatmap(annot_data, annot=True, fmt='.2f', cmap='RdYlGn', center=0,
            ax=ax, linewidths=0.5,
            xticklabels=annot_data.columns, yticklabels=annot_data.index)

# 사전 지정 파라미터 위치에 빨간 테두리
# slice_a index: [100,150,200,250,300], columns: [10,15,20,30,40]
pre_reg_row = list(annot_data.index).index(A_MA_PERIOD)
pre_reg_col = list(annot_data.columns).index(A_DONCHIAN_HIGH)
ax.add_patch(plt.Rectangle((pre_reg_col, pre_reg_row), 1, 1,
             fill=False, edgecolor='red', linewidth=3))

ax.set_title(f'Strategy A Sensitivity: MA x Donchian High\\n(Donchian Low={A_DONCHIAN_LOW} fixed, pre-registered marked in red)')
ax.set_xlabel('Donchian High')
ax.set_ylabel('MA Period')

plt.tight_layout()
plt.savefig(out_dir / 'sensitivity_a_contour.png', dpi=150)
print("Saved: sensitivity_a_contour.png")
plt.close()
"""))

# Cell 14: Strategy B heatmap
cells.append(nbf.v4.new_code_cell("""\
# === Strategy B Heatmap: MA x RSI Buy (RSI Period=4 고정) ===
fig, ax = plt.subplots(figsize=(10, 7))

annot_data = slice_b.copy()
sns.heatmap(annot_data, annot=True, fmt='.2f', cmap='RdYlGn', center=0,
            ax=ax, linewidths=0.5,
            xticklabels=annot_data.columns, yticklabels=annot_data.index)

pre_reg_row = list(annot_data.index).index(B_MA_PERIOD)
pre_reg_col = list(annot_data.columns).index(B_RSI_BUY)
ax.add_patch(plt.Rectangle((pre_reg_col, pre_reg_row), 1, 1,
             fill=False, edgecolor='red', linewidth=3))

ax.set_title(f'Strategy B Sensitivity: MA x RSI Buy\\n(RSI Period={B_RSI_PERIOD} fixed, pre-registered marked in red)')
ax.set_xlabel('RSI Buy Threshold')
ax.set_ylabel('MA Period')

plt.tight_layout()
plt.savefig(out_dir / 'sensitivity_b_contour.png', dpi=150)
print("Saved: sensitivity_b_contour.png")
plt.close()
"""))

# Cell 15: Save JSON
cells.append(nbf.v4.new_code_cell("""\
# === 결과 JSON 저장 ===
# W1-04 schema: 메타분석 (개별 백테스트와 구별되는 schema)

yearly_dict = {}
for strat in ['A', 'B']:
    sub = yearly_df[yearly_df['strategy'] == strat]
    yearly_dict[f'strategy_{strat.lower()}'] = {}
    for _, r in sub.iterrows():
        yearly_dict[f'strategy_{strat.lower()}'][r['year']] = {
            'return': r['return'],
            'sharpe': r['sharpe'],
            'mdd': r['mdd'],
            'trading_days': r['trading_days'],
            'partial': r['partial'],
        }

results = {
    'feature_id': 'BT-001',
    'task_id': 'W1-04',
    'analysis_type': 'robustness_sensitivity',
    'data_file': PARQUET_NAME,
    'data_hash': DATA_HASH,
    'data_bars': len(df),
    'data_range': [df.index[0].isoformat(), df.index[-1].isoformat()],

    'validation': {
        'strategy_a_sharpe_match': sharpe_a_match,
        'strategy_b_sharpe_match': sharpe_b_match,
    },

    'yearly_breakdown': {
        **yearly_dict,
        'domination_warning_a': domination_warning_a,
        'domination_warning_b': domination_warning_b,
        'domination_details': domination_details if domination_details else None,
    },

    'sensitivity': {
        'strategy_a': {
            'grid_dimensions': {
                'ma': ma_grid_a, 'donchian_high': list(map(int, dh_grid)),
                'donchian_low': list(map(int, dl_grid)),
            },
            'fixed_params': {
                'vol_avg_period': A_VOL_AVG_PERIOD, 'vol_mult': A_VOL_MULT, 'sl_pct': A_SL_PCT,
            },
            'total_combos': len(df_sens_a),
            'nan_combos': int(df_sens_a['sharpe'].isna().sum()),
            'pre_registered': {'ma': A_MA_PERIOD, 'donchian_high': A_DONCHIAN_HIGH, 'donchian_low': A_DONCHIAN_LOW},
            'pre_registered_sharpe': pre_reg_sharpe_a,
            'flatness_neighborhood_std': flatness_std_a,
            'flatness_pass': flatness_pass_a,
        },
        'strategy_b': {
            'grid_dimensions': {
                'ma': ma_grid_b, 'rsi_period': list(map(int, rsi_p_grid)),
                'rsi_buy': list(map(int, rsi_buy_grid)),
            },
            'fixed_params': {
                'rsi_sell': B_RSI_SELL, 'time_stop_days': B_TIME_STOP_DAYS, 'sl_pct': B_SL_PCT,
            },
            'total_combos': len(df_sens_b),
            'nan_combos': int(df_sens_b['sharpe'].isna().sum()),
            'pre_registered': {'ma': B_MA_PERIOD, 'rsi_period': B_RSI_PERIOD, 'rsi_buy': B_RSI_BUY},
            'pre_registered_sharpe': pre_reg_sharpe_b,
            'flatness_neighborhood_std': flatness_std_b,
            'flatness_pass': flatness_pass_b,
        },
    },

    'generated_at': datetime.now(timezone.utc).isoformat(),
}

result_path = out_dir / 'robustness_sensitivity.json'
with open(result_path, 'w') as f:
    json.dump(results, f, indent=2)

print(f"Saved: {result_path}")
"""))

# Cell 16: Summary (markdown-style)
cells.append(nbf.v4.new_code_cell("""\
# === 최종 요약 ===
print("=" * 60)
print("W1-04 강건성 + 민감도 분석 최종 결과")
print("=" * 60)

print(f"\\n[검증] Strategy A Sharpe 재현: {'PASS' if sharpe_a_match else 'FAIL'}")
print(f"[검증] Strategy B Sharpe 재현: {'PASS' if sharpe_b_match else 'FAIL'}")

print(f"\\n[연도별] 한 해 지배 경고 A: {'WARNING' if domination_warning_a else 'NONE'}")
print(f"[연도별] 한 해 지배 경고 B: {'WARNING' if domination_warning_b else 'NONE'}")
if domination_details:
    for d in domination_details:
        print(f"  -> {d}")

print(f"\\n[민감도] Strategy A grid: {len(df_sens_a)} combos, {df_sens_a['sharpe'].isna().sum()} NaN")
print(f"[민감도] Strategy B grid: {len(df_sens_b)} combos, {df_sens_b['sharpe'].isna().sum()} NaN")

print(f"\\n[평탄성] Strategy A neighborhood std: {flatness_std_a:.4f} -> {'PASS' if flatness_pass_a else 'WARNING (peaked)'}")
print(f"[평탄성] Strategy B neighborhood std: {flatness_std_b:.4f} -> {'PASS' if flatness_pass_b else 'WARNING (peaked)'}")

print(f"\\n[사전지정] A Sharpe at (200,20,10): {pre_reg_sharpe_a:.4f}")
print(f"[사전지정] B Sharpe at (200,4,25):  {pre_reg_sharpe_b:.4f}")

print(f"\\n*** 민감도 그리드 결과는 참고용. Go/No-Go는 사전 지정 파라미터만. ***")
print("=" * 60)
"""))

# Assemble and write
nb.cells = cells
out_path = Path(__file__).resolve().parent.parent / 'notebooks' / '04_robustness_sensitivity.ipynb'
with open(out_path, 'w') as f:
    nbf.write(nb, f)
print(f"Notebook created: {out_path}")
