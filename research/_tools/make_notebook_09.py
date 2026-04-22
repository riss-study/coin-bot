"""Create notebook 09_walk_forward.ipynb programmatically.

W3-01 Walk-forward analysis:
- 5 cell (W2-03 Go cells 양방향 freeze): BTC_A, BTC_C, BTC_D, ETH_A, ETH_D
- 5 folds (Anchored walk-forward, 6개월 test window)
- Fold별 V_empirical per fold (N_trials=5) + DSR_z 산출
- Go 기준 옵션 A (사용자 직접 선택 2026-04-21): 5/5 fold pass AND 평균 pass

박제 출처:
- docs/stage1-subplans/w3-01-walk-forward.md v2 (사용자 옵션 A 채택)
- docs/stage1-subplans/w2-03-insample-grid.md v9 (V_empirical 일관, year_freq='365 days')
- docs/candidate-pool.md v5 (Strategy A Active + C/D + 파라미터)

강제 명시 (W2-03 v9 + W3-01 v2 박제):
- pf.sharpe_ratio(year_freq='365 days') 명시 호출 (PT-04 신규 노트북 범위 선행 적용, NIT-5)
- Strategy C 방법 B (manual trailing ATR) 구현 (NIT-1)
- min_trade_count=2 Strategy C low-N 처리 (W-7, fold당 < 2 trade 시 N/A = FAIL)
- N_trials=5 per fold sample variance (NIT-2 혼재 인정)
- np.mean aggregation 명시 (median 대체 금지, NIT-3)
- Fold 분할점 freeze: 2023-10-15 / 2024-04-15 / 2024-10-15 / 2025-04-15 / 2025-10-15 UTC (W-1)
- Go cells 양방향 freeze (확장 X + 축소 X, W-3 / NIT-6)
- W3-02 pooled V deferred = Go 판정 번복 근거 X (v2 핵심 원칙 #8)

Run with:
    cd /Users/riss/project/coin-bot
    source research/.venv/bin/activate
    python research/_tools/make_notebook_09.py

Output: research/notebooks/09_walk_forward.ipynb
"""
import nbformat as nbf
from pathlib import Path

nb = nbf.v4.new_notebook()
cells = []

# ============================================================
# Cell 1: Header (markdown)
# ============================================================
cells.append(nbf.v4.new_markdown_cell("""\
# Task W3-01 — Walk-forward Analysis

**Feature ID**: BT-004 W3-01
**Sub-plan**: `docs/stage1-subplans/w3-01-walk-forward.md` v2 (사용자 옵션 A 직접 선택 "2", 2026-04-21)

## 개요

- **대상**: W2-03 Go cells 5개 (양방향 freeze) × 5 folds (Anchored walk-forward, 6개월 test) = **25 조합**
- **Fold 분할점**: 2023-10-15 / 2024-04-15 / 2024-10-15 / 2025-04-15 / 2025-10-15 (UTC, freeze)
- **V_empirical per fold** (N_trials=5, floor 재도입 금지)
- **Go 기준 (옵션 A)**: 5/5 fold에서 Sharpe>0.8 AND DSR_z>0 + 평균 Sharpe>0.8 AND 평균 DSR_z>0

## 박제 원칙 (변경 금지 서약 발효 중)

- W2-03 Go cells 양방향 freeze (확장 X + 축소 X)
- 사전 지정 파라미터 변경 X (W2-02 v5 박제값)
- Strategy C 방법 B (manual trailing ATR) 구현
- `pf.sharpe_ratio(year_freq='365 days')` 명시 호출 (PT-04 신규 범위 선행 적용)
- min_trade_count ≥ 2 (Strategy C low-N 처리, N/A fold = FAIL)
- W3-02 pooled V는 참고만, Go 판정 번복 근거 X

## 검증된 API

- **vectorbt 0.28.5**: `Portfolio.from_signals(..., freq='1D')` + `pf.sharpe_ratio(year_freq='365 days')` 명시
- **ta**: `AverageTrueRange`, `KeltnerChannel(original_version=False, window_atr=14, multiplier=1.5)`, `BollingerBands(window=20, window_dev=2.0)`
- **scipy.stats**: `norm.ppf` (Φ⁻¹) + `skew` + `kurtosis`
"""))

# ============================================================
# Cell 2: Imports + version check
# ============================================================
cells.append(nbf.v4.new_code_cell("""\
import hashlib
import json
import math
from datetime import datetime, timezone, timedelta
from pathlib import Path

import numpy as np
import pandas as pd
import scipy.stats as scs
import vectorbt as vbt
from ta.volatility import AverageTrueRange, BollingerBands, KeltnerChannel

from importlib.metadata import version
print(f"pandas:   {version('pandas')}")
print(f"numpy:    {version('numpy')}")
print(f"vectorbt: {version('vectorbt')}")
print(f"scipy:    {version('scipy')}")
print(f"ta:       {version('ta')}")
"""))

# ============================================================
# Cell 3: Data load + SHA256 verification (2 페어만: BTC, ETH)
# ============================================================
cells.append(nbf.v4.new_code_cell("""\
# W3-01 대상은 Tier 1 (BTC, ETH)만 (W2-03 Go cells 집합 양방향 freeze)
DATA_DIR = Path('../data')
FREEZE_DATE = '20260412'
PAIRS = ['KRW-BTC', 'KRW-ETH']

def sha256_file(path):
    h = hashlib.sha256()
    with open(path, 'rb') as f:
        for chunk in iter(lambda: f.read(65536), b''):
            h.update(chunk)
    return h.hexdigest()

# data_hashes.txt 파싱
expected_hashes = {}
with open(DATA_DIR / 'data_hashes.txt') as f:
    for line in f:
        line = line.strip()
        if line and not line.startswith('#') and ':' in line:
            k, v = line.split(': ', 1)
            expected_hashes[k] = v

# SHA256 재검증
data = {}
for pair in PAIRS:
    filename = f'{pair}_1d_frozen_{FREEZE_DATE}.parquet'
    path = DATA_DIR / filename
    actual_hash = sha256_file(path)
    expected = expected_hashes.get(filename)
    assert expected is not None, f'data_hashes.txt에 {filename} 항목 없음'
    assert actual_hash == expected, f'SHA256 불일치 ({pair}): W3-01 중단 + 사용자 보고'
    df = pd.read_parquet(path)
    assert df.index.tz is not None and str(df.index.tz) == 'UTC', f'{pair}: UTC 아님'
    assert df.index.is_monotonic_increasing, f'{pair}: monotonic 위반'
    data[pair] = df
    print(f'{pair}: {len(df):5d} bars, {df.index[0].date()} ~ {df.index[-1].date()}, sha={actual_hash[:12]}')

print(f'\\n2 페어 (BTC, ETH) SHA256 무결성 PASS')
"""))

# ============================================================
# Cell 4: W3-01 박제 상수 (Go cells, Fold 분할점, 파라미터)
# ============================================================
cells.append(nbf.v4.new_code_cell("""\
# ============================================================
# W2-03 Go cells 양방향 freeze (확장 X + 축소 X, W-3 + NIT-6)
# ============================================================
CELLS = [
    ('KRW-BTC', 'A'),
    ('KRW-BTC', 'C'),
    ('KRW-BTC', 'D'),
    ('KRW-ETH', 'A'),
    ('KRW-ETH', 'D'),
]
# ETH_C 재포함 X (W2-03 FAIL), Secondary 마킹 (SOL/DOGE/etc) 포함 X = cycle 3 강제

# ============================================================
# Fold 분할점 freeze (v2 핵심 원칙 #9, 2026-04-21 사용자 승인 시점 = freeze)
# ============================================================
TRAIN_START = pd.Timestamp('2021-10-15', tz='UTC')  # Common-window (cycle 2 v5)
FOLD_SPLIT_POINTS = [
    pd.Timestamp('2023-10-15', tz='UTC'),
    pd.Timestamp('2024-04-15', tz='UTC'),
    pd.Timestamp('2024-10-15', tz='UTC'),
    pd.Timestamp('2025-04-15', tz='UTC'),
    pd.Timestamp('2025-10-15', tz='UTC'),
]
TEST_WINDOW_DAYS = 180  # 약 6개월
FREEZE_END = pd.Timestamp('2026-04-12', tz='UTC')  # W1-01 + W2-01.4 freeze

# ============================================================
# 사전 지정 파라미터 (W2-02 v5 + candidate-pool.md v5, 재튜닝 금지)
# ============================================================
STRATEGY_A_PARAMS = {
    'MA_PERIOD': 200, 'DONCHIAN_HIGH': 20, 'DONCHIAN_LOW': 10,
    'VOL_AVG_PERIOD': 20, 'VOL_MULT': 1.5, 'SL_PCT': 0.08,
}
STRATEGY_C_PARAMS = {
    'FAST_MA': 50, 'SLOW_MA': 200, 'ATR_WINDOW': 14, 'ATR_MULT': 3.0,
}
STRATEGY_D_PARAMS = {
    'KELTNER_WINDOW': 20, 'KELTNER_ATR_MULT': 1.5, 'ATR_WINDOW': 14,
    'BOLLINGER_WINDOW': 20, 'BOLLINGER_SIGMA': 2.0, 'SL_HARD': 0.08,
}

# Portfolio (W1-01 박제)
INIT_CASH = 1_000_000
FEES = 0.0005
SLIPPAGE = 0.0005
FREQ = '1D'
YEAR_FREQ = '365 days'  # PT-04 선행 적용 (NIT-5, 명시 호출)

# Go 기준 (옵션 A, v2 박제)
N_TRIALS = 5  # W2-03 Go cells 5개
GO_SHARPE_THRESHOLD = 0.8
GO_DSR_Z_THRESHOLD = 0.0
GO_STABILITY_REQUIRED = 5  # 옵션 A: 5/5 모두 pass (사용자 직접 선택 "2", 2026-04-21)
MIN_TRADE_COUNT = 2  # W-7: fold당 < 2 trade 시 N/A = FAIL

# DSR 상수 (Bailey & López de Prado 2014)
EULER_MASCHERONI = 0.5772156649015329

print('W3-01 박제 상수 로드 완료')
print(f'  CELLS: {CELLS}')
print(f'  Fold 분할점: {[p.date() for p in FOLD_SPLIT_POINTS]}')
print(f'  Train start: {TRAIN_START.date()}, Test window: {TEST_WINDOW_DAYS}d, Freeze end: {FREEZE_END.date()}')
print(f'  Go 기준 (옵션 A): {GO_STABILITY_REQUIRED}/{N_TRIALS} fold + 평균 Sharpe>{GO_SHARPE_THRESHOLD} + 평균 DSR_z>{GO_DSR_Z_THRESHOLD}')
print(f'  Strategy C low-N: min_trade_count>={MIN_TRADE_COUNT}')
"""))

# ============================================================
# Cell 5: Fold 분할 sanity check (W3-01.1)
# ============================================================
cells.append(nbf.v4.new_code_cell("""\
# Fold 분할 계산 + test 기간 bar count sanity
folds = []
for i, split in enumerate(FOLD_SPLIT_POINTS):
    test_start = split
    test_end = min(split + pd.Timedelta(days=TEST_WINDOW_DAYS), FREEZE_END)
    folds.append({
        'fold_id': i + 1,
        'train_start': TRAIN_START,
        'train_end': split,  # exclusive
        'test_start': test_start,
        'test_end': test_end,
    })

# BTC 기준 (ETH도 동일 범위 확인 가능) bar count 검증
btc_idx = data['KRW-BTC'].index
print('Fold 분할 sanity (BTC 기준):')
for f in folds:
    test_slice = btc_idx[(btc_idx >= f['test_start']) & (btc_idx < f['test_end'])]
    train_slice = btc_idx[(btc_idx >= f['train_start']) & (btc_idx < f['train_end'])]
    f['test_bar_count'] = len(test_slice)
    f['train_bar_count'] = len(train_slice)
    print(f"  Fold {f['fold_id']}: train {f['train_start'].date()} ~ {f['train_end'].date()} ({f['train_bar_count']:4d} bars) / test {f['test_start'].date()} ~ {f['test_end'].date()} ({f['test_bar_count']:3d} bars)")
    # sanity: test 기간 180 ±5% 이내 (최소 171, 최대 189). 단 Fold 5는 FREEZE_END 경계에서 절단 가능
    if f['fold_id'] < len(folds):
        assert 171 <= f['test_bar_count'] <= 189, f"Fold {f['fold_id']} test bar count 이탈: {f['test_bar_count']}"

# Warmup 확인 (각 fold train에 200 bar MA warmup 포함)
for f in folds:
    assert f['train_bar_count'] >= STRATEGY_A_PARAMS['MA_PERIOD'], (
        f"Fold {f['fold_id']} train bars={f['train_bar_count']} < MA200 warmup"
    )
print('\\nFold 분할 sanity PASS (test 180±5% + train warmup 200+ 확인)')
"""))

# ============================================================
# Cell 6: Strategy A 신호 함수 (W1-02 패턴 재사용)
# ============================================================
cells.append(nbf.v4.new_code_cell("""\
def strategy_a_signals(df, params=STRATEGY_A_PARAMS):
    '''Strategy A (Trend Following): MA200 + Donchian + Volume'''
    close = df['close']; high = df['high']; low = df['low']; volume = df['volume']
    ma = close.rolling(window=params['MA_PERIOD']).mean()
    donchian_high = high.rolling(window=params['DONCHIAN_HIGH']).max().shift(1)
    donchian_low = low.rolling(window=params['DONCHIAN_LOW']).min().shift(1)
    vol_avg = volume.rolling(window=params['VOL_AVG_PERIOD']).mean().shift(1)
    entries = (close > ma) & (close > donchian_high) & (volume > vol_avg * params['VOL_MULT'])
    exits = close < donchian_low
    return entries.fillna(False).astype(bool), exits.fillna(False).astype(bool)


def strategy_c_signals(df, params=STRATEGY_C_PARAMS):
    '''Strategy C (Slow Momentum) 방법 B: manual trailing ATR (NIT-1 명시)'''
    close = df['close']; high = df['high']; low = df['low']
    ma_short = close.rolling(window=params['FAST_MA']).mean()
    ma_long = close.rolling(window=params['SLOW_MA']).mean()
    atr = AverageTrueRange(high, low, close, window=params['ATR_WINDOW']).average_true_range()

    golden_cross = (ma_short > ma_long) & (ma_short.shift(1) <= ma_long.shift(1))
    death_cross = (ma_short < ma_long) & (ma_short.shift(1) >= ma_long.shift(1))
    entries_raw = golden_cross.fillna(False).astype(bool)

    atr_mult = params['ATR_MULT']
    exit_mask = pd.Series(False, index=df.index)
    entry_mask = pd.Series(False, index=df.index)
    in_position = False
    trailing_high = -np.inf

    close_values = close.values
    atr_values = atr.values
    golden_values = entries_raw.values
    death_values = death_cross.fillna(False).values

    for i in range(len(df)):
        if not in_position:
            if golden_values[i] and not np.isnan(atr_values[i]):
                in_position = True
                trailing_high = close_values[i]
                entry_mask.iloc[i] = True
        else:
            if close_values[i] > trailing_high:
                trailing_high = close_values[i]
            stop_level = trailing_high - atr_mult * atr_values[i]
            triggered_death = bool(death_values[i])
            triggered_atr = (not np.isnan(atr_values[i])) and close_values[i] < stop_level
            if triggered_death or triggered_atr:
                exit_mask.iloc[i] = True
                in_position = False
                trailing_high = -np.inf
    return entry_mask, exit_mask


def strategy_d_signals(df, params=STRATEGY_D_PARAMS):
    '''Strategy D (Volatility Breakout): Keltner + Bollinger'''
    close = df['close']; high = df['high']; low = df['low']
    kc = KeltnerChannel(
        high=high, low=low, close=close,
        window=params['KELTNER_WINDOW'], window_atr=params['ATR_WINDOW'],
        original_version=False, multiplier=params['KELTNER_ATR_MULT'],
    )
    kc_upper = kc.keltner_channel_hband()
    kc_mid = kc.keltner_channel_mband()
    bb = BollingerBands(close=close, window=params['BOLLINGER_WINDOW'], window_dev=params['BOLLINGER_SIGMA'])
    bb_upper = bb.bollinger_hband()
    kc_break = (close > kc_upper) & (close.shift(1) <= kc_upper.shift(1))
    bb_break = (close > bb_upper) & (close.shift(1) <= bb_upper.shift(1))
    entries = kc_break & bb_break
    mid_exit = (close < kc_mid) & (close.shift(1) >= kc_mid.shift(1))
    return entries.fillna(False).astype(bool), mid_exit.fillna(False).astype(bool)


# Sanity check (BTC)
ea, xa = strategy_a_signals(data['KRW-BTC'])
ec, xc = strategy_c_signals(data['KRW-BTC'])
ed, xd = strategy_d_signals(data['KRW-BTC'])
print(f'BTC 전체 기간 signal sanity: A entries={ea.sum()} / C entries={ec.sum()} / D entries={ed.sum()}')
"""))

# ============================================================
# Cell 7: Walk-forward Portfolio runner (fold별 slice)
# ============================================================
cells.append(nbf.v4.new_code_cell("""\
SIG_FUNCS = {'A': strategy_a_signals, 'C': strategy_c_signals, 'D': strategy_d_signals}

def run_fold_portfolio(pair, strategy, fold):
    '''전체 데이터로 signal 계산 → test 기간만 slice → Portfolio 실행.

    Walk-forward 원칙: train 기간은 signal warmup 용도 (MA200 등). Portfolio는 test 기간만.
    fold별 독립 Portfolio.

    Returns: dict (fold_id, pair, strategy, metrics + daily_returns)
    '''
    df_full = data[pair]
    # 전체 기간 signal 생성 (warmup 포함)
    entries_full, exits_full = SIG_FUNCS[strategy](df_full)

    # Test 기간만 slice
    test_mask = (df_full.index >= fold['test_start']) & (df_full.index < fold['test_end'])
    df_test = df_full[test_mask]
    entries_test = entries_full[test_mask]
    exits_test = exits_full[test_mask]

    # Strategy별 sl_stop
    if strategy == 'A':
        sl_stop = STRATEGY_A_PARAMS['SL_PCT']
    elif strategy == 'C':
        sl_stop = None  # 방법 B manual trailing in exit_mask
    elif strategy == 'D':
        sl_stop = STRATEGY_D_PARAMS['SL_HARD']

    kwargs = dict(
        close=df_test['close'], entries=entries_test, exits=exits_test,
        init_cash=INIT_CASH, fees=FEES, slippage=SLIPPAGE, freq=FREQ,
    )
    if sl_stop is not None:
        kwargs['sl_stop'] = sl_stop
        kwargs['sl_trail'] = False

    pf = vbt.Portfolio.from_signals(**kwargs)

    # Trade count
    trade_count = int(pf.trades.count())

    # min_trade_count 필터 (W-7, NIT N/A fold = FAIL)
    if trade_count < MIN_TRADE_COUNT:
        return {
            'fold_id': fold['fold_id'],
            'pair': pair, 'strategy': strategy,
            'cell_key': f'{pair}_{strategy}',
            'trade_count': trade_count,
            'na': True,  # N/A = FAIL 처리
            'sharpe': None, 'dsr_z': None, 'dsr_prob': None,
            'total_return': None, 'max_drawdown': None, 'win_rate': None, 'profit_factor': None,
            'daily_returns': None,
            'note': f'trade_count={trade_count} < {MIN_TRADE_COUNT} → N/A (FAIL)',
        }

    # Metric 산출 (pf.sharpe_ratio(year_freq='365 days') 명시, PT-04 선행)
    sharpe = float(pf.sharpe_ratio(year_freq=YEAR_FREQ))
    daily_returns = pf.returns()

    return {
        'fold_id': fold['fold_id'],
        'pair': pair, 'strategy': strategy,
        'cell_key': f'{pair}_{strategy}',
        'trade_count': trade_count,
        'na': False,
        'sharpe': sharpe,
        'total_return': float(pf.total_return()),
        'max_drawdown': float(pf.max_drawdown()),
        'win_rate': float(pf.trades.win_rate()) if trade_count > 0 else 0.0,
        'profit_factor': float(pf.trades.profit_factor()) if trade_count > 0 else 0.0,
        'daily_returns': daily_returns,  # DSR 산출용
        'note': '',
    }


# 전체 실행: 5 cell × 5 fold = 25 조합
print('Walk-forward 백테스트 실행 중 (5 cell × 5 fold = 25 조합)...')
results = []
for pair, strategy in CELLS:
    for fold in folds:
        r = run_fold_portfolio(pair, strategy, fold)
        results.append(r)
        status = 'N/A' if r['na'] else f"Sharpe={r['sharpe']:+.3f}"
        print(f"  {r['cell_key']} fold {r['fold_id']}: trades={r['trade_count']:3d}, {status}")

print(f'\\n25 조합 실행 완료')
"""))

# ============================================================
# Cell 8: Fold별 V_empirical + SR_0 + DSR_z 산출 (W3-01.3)
# ============================================================
cells.append(nbf.v4.new_code_cell("""\
def compute_sr_0(V, n_trials):
    '''Bailey 2014 eq. 9: SR_0 = sqrt(V) × ((1-γ)·Φ⁻¹(1-1/N) + γ·Φ⁻¹(1-1/(N·e)))'''
    gamma = EULER_MASCHERONI
    e = math.e
    term1 = (1 - gamma) * scs.norm.ppf(1 - 1 / n_trials)
    term2 = gamma * scs.norm.ppf(1 - 1 / (n_trials * e))
    return math.sqrt(V) * (term1 + term2)


def compute_dsr_z(sr_hat, sr_0, daily_returns, T):
    '''Bailey 2014 eq. 10 (z-score form): DSR_z = (SR_hat - SR_0) × sqrt((T-1)/denom)

    daily_returns: pandas Series. skew/kurtosis Fisher form → +3 변환 (Bailey 원문 raw 전제)
    '''
    ret = daily_returns.dropna()
    gamma_3 = float(scs.skew(ret))
    gamma_4_fisher = float(scs.kurtosis(ret, fisher=True))
    gamma_4_raw = gamma_4_fisher + 3  # Bailey 원문 raw form 변환
    denom = 1 - gamma_3 * sr_0 + ((gamma_4_raw - 1) / 4) * sr_0 ** 2
    if denom <= 0:
        return float('nan'), gamma_3, gamma_4_raw
    dsr_z = (sr_hat - sr_0) * math.sqrt((T - 1) / denom)
    return dsr_z, gamma_3, gamma_4_raw


# Fold별 V_empirical + SR_0 산출 (W-3: 5 cell Sharpe sample variance, N/A 제외)
fold_dsr = {}
for fold in folds:
    fid = fold['fold_id']
    fold_results = [r for r in results if r['fold_id'] == fid]
    # 해당 fold의 non-NA Sharpe 값만
    sharpes = [r['sharpe'] for r in fold_results if not r['na']]
    if len(sharpes) < 2:
        fold_dsr[fid] = {
            'V_empirical': None, 'SR_0': None, 'note': f'non-NA cells = {len(sharpes)} < 2 → DSR 산출 불가',
        }
        print(f'Fold {fid}: non-NA cells={len(sharpes)} → DSR 산출 불가 (전체 FAIL 처리)')
        continue
    V_emp = float(np.var(sharpes, ddof=1))
    sr_0 = compute_sr_0(V_emp, N_TRIALS)
    fold_dsr[fid] = {'V_empirical': V_emp, 'SR_0': sr_0, 'n_non_na': len(sharpes)}
    print(f'Fold {fid}: V_empirical={V_emp:.6f}, SR_0={sr_0:.4f} (non-NA cells={len(sharpes)})')

# 각 결과에 DSR_z 산출 (fold별 V_empirical 적용)
for r in results:
    if r['na']:
        r['dsr_z'] = None
        r['dsr_prob'] = None
        continue
    fd = fold_dsr[r['fold_id']]
    if fd['V_empirical'] is None:
        r['dsr_z'] = None
        r['dsr_prob'] = None
        r['note'] = (r['note'] + ' | fold V 산출 불가').strip(' |')
        continue
    T = len(r['daily_returns'].dropna())
    dsr_z, skew, kurt = compute_dsr_z(r['sharpe'], fd['SR_0'], r['daily_returns'], T)
    r['dsr_z'] = dsr_z
    r['dsr_prob'] = float(scs.norm.cdf(dsr_z)) if not math.isnan(dsr_z) else None
    r['skew'] = skew
    r['kurtosis_raw'] = kurt
    r['T'] = T

print('\\n=== Fold별 DSR_z 산출 완료 ===')
"""))

# ============================================================
# Cell 9: Cell별 aggregation (fold_pass_count + np.mean)
# ============================================================
cells.append(nbf.v4.new_code_cell("""\
# Cell별 aggregation (NIT-3: np.mean 명시, median 대체 금지)
cell_summary = {}
for pair, strategy in CELLS:
    key = f'{pair}_{strategy}'
    cell_results = sorted([r for r in results if r['cell_key'] == key], key=lambda r: r['fold_id'])

    # Fold pass count (Sharpe>0.8 AND DSR_z>0, N/A는 FAIL 처리)
    fold_passes = []
    for r in cell_results:
        if r['na'] or r['sharpe'] is None or r['dsr_z'] is None:
            fold_passes.append(False)
        else:
            fold_passes.append(r['sharpe'] > GO_SHARPE_THRESHOLD and r['dsr_z'] > GO_DSR_Z_THRESHOLD)

    fold_pass_count = int(sum(fold_passes))

    # 평균 Sharpe/DSR_z (np.mean, N/A 제외, 모두 N/A면 None)
    valid_sharpes = [r['sharpe'] for r in cell_results if not r['na'] and r['sharpe'] is not None]
    valid_dsr_zs = [r['dsr_z'] for r in cell_results if not r['na'] and r['dsr_z'] is not None]
    mean_sharpe = float(np.mean(valid_sharpes)) if valid_sharpes else None
    mean_dsr_z = float(np.mean(valid_dsr_zs)) if valid_dsr_zs else None

    # Go 기준 옵션 A: 5/5 stability AND mean pass
    stability_pass = fold_pass_count >= GO_STABILITY_REQUIRED
    magnitude_pass = (
        mean_sharpe is not None and mean_dsr_z is not None and
        mean_sharpe > GO_SHARPE_THRESHOLD and mean_dsr_z > GO_DSR_Z_THRESHOLD
    )
    cell_go = stability_pass and magnitude_pass

    cell_summary[key] = {
        'cell_key': key,
        'pair': pair,
        'strategy': strategy,
        'fold_passes': fold_passes,
        'fold_pass_count': fold_pass_count,
        'mean_sharpe': mean_sharpe,
        'mean_dsr_z': mean_dsr_z,
        'stability_pass': stability_pass,
        'magnitude_pass': magnitude_pass,
        'cell_go': cell_go,
        'na_fold_count': sum(1 for r in cell_results if r['na']),
    }

print('=== Cell별 Aggregation (옵션 A: 5/5 fold + 평균 pass) ===\\n')
header = f"{'Cell':<12}{'fold pass':<12}{'mean Sharpe':<14}{'mean DSR_z':<14}{'Stability':<12}{'Magnitude':<12}{'Go':<6}{'N/A':<6}"
print(header)
for key, s in cell_summary.items():
    ms = f"{s['mean_sharpe']:+.3f}" if s['mean_sharpe'] is not None else 'None'
    md = f"{s['mean_dsr_z']:+.3f}" if s['mean_dsr_z'] is not None else 'None'
    row = f"{key:<12}{s['fold_pass_count']}/5{'':<8}{ms:<14}{md:<14}{str(s['stability_pass']):<12}{str(s['magnitude_pass']):<12}{str(s['cell_go']):<6}{s['na_fold_count']:<6}"
    print(row)
"""))

# ============================================================
# Cell 10: Go/No-Go 자동 평가 + 결과 저장
# ============================================================
cells.append(nbf.v4.new_code_cell("""\
# Go 판정 (5 cell 중 1+개 cell이 Go)
go_cells = [key for key, s in cell_summary.items() if s['cell_go']]
is_go = len(go_cells) > 0

print('=' * 60)
print(f'Go/No-Go 자동 평가')
print('=' * 60)
print(f'Go 통과 cells: {go_cells} ({len(go_cells)}/5)')
print(f'is_go = {is_go}')
print(f'Go 기준 (옵션 A, v2 박제): Stability 5/5 fold pass + Magnitude 평균 pass')

if is_go:
    print('\\n→ W3-02 (DSR + Bootstrap + Monte Carlo) 진입 대기')
    print('   Stage 1 킬 카운터: +1 유지 (가산 X)')
else:
    print('\\n→ No-Go. Stage 1 킬 카운터 +2 소급 가산 예정 (W2-03 v8 WARNING-4)')
    print('   W2-03 retrospective 해석 프레임 사용자 선택 필요 (A/B)')
    print('     A: cycle 1 #5 재발 확정 → Stage 1 학습 모드 전환 권고')
    print('     B: 극단 조건 + V_empirical 불안정 원인 → 재탐색 or 설계 재조정')
    print('   Strategy A Active → Retained 역방향 복귀 (NIT-4, candidate-pool.md v6 전이)')

# JSON 저장
OUTPUT_PATH = Path('../outputs/w3_01_walk_forward.json')
OUTPUT_PATH.parent.mkdir(exist_ok=True)

# daily_returns는 JSON 직렬화 불가, 제외
results_for_json = []
for r in results:
    r_copy = {k: v for k, v in r.items() if k != 'daily_returns'}
    results_for_json.append(r_copy)

# folds도 pd.Timestamp 직렬화 준비
folds_for_json = []
for f in folds:
    folds_for_json.append({
        'fold_id': f['fold_id'],
        'train_start': f['train_start'].isoformat(),
        'train_end': f['train_end'].isoformat(),
        'test_start': f['test_start'].isoformat(),
        'test_end': f['test_end'].isoformat(),
        'train_bar_count': f['train_bar_count'],
        'test_bar_count': f['test_bar_count'],
    })

output_data = {
    'generated_at': datetime.now(timezone.utc).isoformat(),
    'task_id': 'W3-01',
    'feature_id': 'BT-004',
    'sub_plan_version': 'v2',
    'cells': [{'pair': p, 'strategy': s} for p, s in CELLS],
    'folds': folds_for_json,
    'parameters': {
        'strategy_a': STRATEGY_A_PARAMS,
        'strategy_c': STRATEGY_C_PARAMS,
        'strategy_d': STRATEGY_D_PARAMS,
        'portfolio': {
            'INIT_CASH': INIT_CASH, 'FEES': FEES, 'SLIPPAGE': SLIPPAGE,
            'FREQ': FREQ, 'YEAR_FREQ': YEAR_FREQ,
        },
        'go_criteria': {
            'option': 'A (5/5 stability + mean pass)',
            'sharpe_threshold': GO_SHARPE_THRESHOLD,
            'dsr_z_threshold': GO_DSR_Z_THRESHOLD,
            'stability_required': GO_STABILITY_REQUIRED,
            'n_trials': N_TRIALS,
            'min_trade_count': MIN_TRADE_COUNT,
        },
    },
    'fold_dsr': fold_dsr,
    'fold_results': results_for_json,
    'cell_summary': cell_summary,
    'is_go': is_go,
    'go_cells': go_cells,
    'multiple_testing_note': '25 trial (5 cell × 5 fold) family-wise 오류 부분 완화만. W3-02 Bootstrap/Bonferroni 재검증 책무. W3-02는 참고 metric만, W3-01 Go 판정 번복 근거 X (v2 핵심 원칙 #8)',
}

with open(OUTPUT_PATH, 'w') as f:
    json.dump(output_data, f, indent=2, default=str)

print(f'\\n결과 저장: {OUTPUT_PATH}')
print(f'  총 {len(results)} fold 결과 + fold_dsr + cell_summary + is_go 박제')
"""))

# ============================================================
# Write notebook
# ============================================================
nb['cells'] = cells
nb['metadata'] = {
    'kernelspec': {'display_name': 'Python 3', 'language': 'python', 'name': 'python3'},
    'language_info': {'name': 'python', 'version': '3.11'},
}

OUTPUT_PATH = Path('research/notebooks/09_walk_forward.ipynb')
OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
nbf.write(nb, OUTPUT_PATH)
print(f'Notebook 작성 완료: {OUTPUT_PATH} ({len(cells)} cells)')
