"""Create notebook 08_insample_grid.ipynb programmatically.

W2-03 In-sample 백테스트 grid + DSR + Go/No-Go 평가:
- Tier 1 (BTC, ETH) × {A, C, D} = 6셀 Primary grid (Go 평가 대상)
- Tier 2 (XRP, SOL, TRX, DOGE) × {A, C, D} = 12셀 Exploratory grid (Go 기여 X)
- DSR (Bailey & López de Prado 2014) — N_trials=6 (Primary만)
- Go 기준 (decisions-final.md L518): Primary 6셀 중 1+개가 BTC 또는 ETH에서 Sharpe>0.8 AND DSR_z>0

박제 출처:
- docs/stage1-subplans/w2-03-insample-grid.md v5 (W2-03.0 박제 강제)
- docs/stage1-subplans/w2-02-strategy-candidates.md v6 (Strategy C/D 박제)
- docs/pair-selection-criteria-week2-cycle2.md v5 (Tier 1/2 + Common-window)
- docs/candidate-pool.md v4 (Strategy A/C/D Recall + 파라미터)
- docs/decisions-final.md L513-521 + L549-551
- research/_tools/w2_03_w1_test.py (방법 B manual trailing ATR 검증 결과)

강제 명시 (W2-03 v5 박제):
- year_freq='365 days' (sqrt(365) annualization, W-1 정정)
- ta KeltnerChannel(window=20, window_atr=14, original_version=False, multiplier=1.5)
- BollingerBands(window=20, window_dev=2.0)
- Strategy C trailing = manual trailing_high - ATR_MULT × ATR(14)(t) exit_mask (방법 B)
- vectorbt multi-asset 방식 A (페어별 독립 Portfolio, for-loop)
- DSR_z + DSR_prob 동시 산출 (W-N1)

Run with:
    cd /Users/riss/project/coin-bot
    source research/.venv/bin/activate
    python research/_tools/make_notebook_08.py

Output: research/notebooks/08_insample_grid.ipynb
"""
import nbformat as nbf
from pathlib import Path

nb = nbf.v4.new_notebook()
cells = []

# ============================================================
# Cell 1: Header (markdown)
# ============================================================
cells.append(nbf.v4.new_markdown_cell("""\
# Task W2-03 — In-sample 백테스트 grid + DSR + Go/No-Go

**Feature ID**: BT-005 W2-03
**Sub-plan**: `docs/stage1-subplans/w2-03-insample-grid.md` v5 (2026-04-19 사용자 승인 + W2-03.1 방법 B 채택)

## 개요

- **Primary grid**: Tier 1 (BTC, ETH) × {A, C, D} = **6셀** (Go 평가 대상)
- **Exploratory grid**: Tier 2 (XRP, SOL, TRX, DOGE) × {A, C, D} = **12셀** (Go 기여 X, Secondary 마킹 후보)
- **DSR** (Bailey & López de Prado 2014): N_trials=6 (Primary만)
- **Go 기준** (decisions-final.md L518): Primary 6셀 중 **1+개 전략이 BTC 또는 ETH에서 `Sharpe > 0.8 AND DSR_z > 0`** → Go

## 박제 원칙 (변경 금지 서약 발효 중)

- 사전 지정 파라미터 변경 X (cycle 1 학습 #2)
- 알트별 튜닝 절대 금지 (cycle 1 학습 #17)
- Primary metric = 페어별 max-span Sharpe (각 페어 자체 상장일부터 2026-04-12)
- Secondary metric = common-window Sharpe (2021-10-15 ~ 2026-04-12, SOL 기준)
- **cherry-pick 차단**: Go 기준은 max-span 단독. 사후에 common-window로 변경 = cycle 3 강제
- Strategy A/C/D 대칭 재평가 의무 (cherry-pick 차단, B-4 정정)

## W2-03.1 결과 박제 (2026-04-19 사용자 "ㄱㄱ" 채택)

- 방법 A (vectorbt sl_stop + sl_trail=True): entry bar 시점 비율 freeze (박제 의도 "매 bar 동적 ATR" 위반)
- 방법 B (manual `trailing_high - ATR_MULT × ATR(14)(t)` exit_mask): **채택**
- evidence: `research/outputs/w2_03_w1_test.json`

## 검증된 API

- **vectorbt 0.28.5**: `Portfolio.from_signals(..., freq='1D', year_freq='365 days')` 강제
- **ta**: `KeltnerChannel(window=20, window_atr=14, original_version=False, multiplier=1.5)` + `BollingerBands(window=20, window_dev=2.0)` + `AverageTrueRange(high, low, close, window=14)` (research/CLAUDE.md 검증)
- **scipy.stats**: `norm.ppf` (Φ⁻¹) + `norm.cdf` (Φ) + `skew` + `kurtosis`
"""))

# ============================================================
# Cell 2: Imports + version check
# ============================================================
cells.append(nbf.v4.new_code_cell("""\
import hashlib
import json
import math
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd
import scipy.stats as scs
import vectorbt as vbt
from ta.momentum import RSIIndicator
from ta.volatility import AverageTrueRange, BollingerBands, KeltnerChannel

from importlib.metadata import version
print(f"pandas:   {version('pandas')}")
print(f"numpy:    {version('numpy')}")
print(f"vectorbt: {version('vectorbt')}")
print(f"scipy:    {version('scipy')}")
print(f"ta:       {version('ta')}")

# W3-1 책무 (W2-02 v5 박제): ta KeltnerChannel signature 재검증
import inspect
kc_sig = inspect.signature(KeltnerChannel.__init__)
print(f"\\nKeltnerChannel signature: {kc_sig}")
print("박제 호출: window=20, window_atr=14, original_version=False, multiplier=1.5 (ta default와 다름 → 명시 필수)")
"""))

# ============================================================
# Cell 3: Data hash verification + Load 6 페어 1d
# ============================================================
cells.append(nbf.v4.new_code_cell("""\
# 박제 (cycle 2 v5 + W2-01.4)
DATA_DIR = Path('../data')
FREEZE_DATE = '20260412'
PAIRS_TIER1 = ['KRW-BTC', 'KRW-ETH']
PAIRS_TIER2 = ['KRW-XRP', 'KRW-SOL', 'KRW-TRX', 'KRW-DOGE']
PAIRS_ALL = PAIRS_TIER1 + PAIRS_TIER2  # 6 페어 (Primary 2 + Exploratory 4)

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

# 6 페어 일봉 SHA256 재검증 (W-6 정정: freeze 종료일 일관)
data = {}
for pair in PAIRS_ALL:
    filename = f'{pair}_1d_frozen_{FREEZE_DATE}.parquet'
    path = DATA_DIR / filename
    actual_hash = sha256_file(path)
    expected = expected_hashes.get(filename)
    assert expected is not None, f'data_hashes.txt에 {filename} 항목 없음'
    assert actual_hash == expected, (
        f'SHA256 불일치 ({pair} 1d): expected={expected[:16]}..., actual={actual_hash[:16]}... '
        f'→ W2-03 중단 + 사용자 보고 (cycle 2 패턴 cherry-pick 차단)'
    )
    df = pd.read_parquet(path)
    assert df.index.tz is not None and str(df.index.tz) == 'UTC', (
        f'{pair} 1d: UTC 타임존 아님 ({df.index.tz})'
    )
    assert df.index.is_monotonic_increasing, f'{pair} 1d: monotonic 위반'
    assert not df.index.duplicated().any(), f'{pair} 1d: 중복 인덱스'
    data[pair] = df
    print(f'{pair} 1d: {len(df):5d} bars, {df.index[0].date()} ~ {df.index[-1].date()}, sha={actual_hash[:12]}')

print(f'\\n6 페어 1d 로드 + SHA256 무결성 검증 PASS')
"""))

# ============================================================
# Cell 4: Common-window 박제 재검증 + 페어별 범위 보고
# ============================================================
cells.append(nbf.v4.new_code_cell("""\
# Common-window 박제 (cycle 2 v5 섹션 5: SOL 상장일 = 2021-10-15 UTC 기준)
COMMON_WINDOW_START = '2021-10-15'
ADVERTISED_END = '2026-04-12'

# SOL 실측 actual_start 검증 (cycle 2 v5 박제 위반 시 중단)
sol_actual_start = data['KRW-SOL'].index[0].strftime('%Y-%m-%d')
assert sol_actual_start == COMMON_WINDOW_START, (
    f'cycle 2 v5 박제 위반: SOL actual_start={sol_actual_start} ≠ {COMMON_WINDOW_START}. '
    f'W2-01.4 데이터 vs 박제 불일치 → W2-03 중단 + 사용자 보고'
)

print(f'Common-window 시작 박제 검증 PASS: {COMMON_WINDOW_START} UTC (SOL 기준)')
print(f'Advertised 종료: {ADVERTISED_END} UTC')
print()

# 페어별 max-span 범위 표
print('페어별 max-span 범위 (Primary Sharpe 계산 기준):')
for pair in PAIRS_ALL:
    df = data[pair]
    print(f'  {pair}: {df.index[0].date()} ~ {df.index[-1].date()} ({len(df):5d} bars)')
"""))

# ============================================================
# Cell 5: 사전 지정 파라미터 박제 (변경 금지)
# ============================================================
cells.append(nbf.v4.new_code_cell("""\
# ============================================================
# 사전 지정 파라미터 (변경 금지 서약 발효 중, W2-02 v5 + candidate-pool.md v4)
# ============================================================

# --- Strategy A (Trend Following, Padysak/Vojtko 영감, W1-02 박제) ---
STRATEGY_A_PARAMS = {
    'MA_PERIOD': 200,
    'DONCHIAN_HIGH': 20,
    'DONCHIAN_LOW': 10,
    'VOL_AVG_PERIOD': 20,
    'VOL_MULT': 1.5,
    'SL_PCT': 0.08,
}

# --- Strategy C (Slow Momentum, Faber 2007 + Wilder 1978, candidate-pool.md v4 박제) ---
STRATEGY_C_PARAMS = {
    'FAST_MA': 50,
    'SLOW_MA': 200,
    'ATR_WINDOW': 14,
    'ATR_MULT': 3.0,  # trailing stop multiplier
}

# --- Strategy D (Volatility Breakout, Bollinger 1983 + ChartSchool Keltner 변형 + Wilder 1978) ---
STRATEGY_D_PARAMS = {
    'KELTNER_WINDOW': 20,
    'KELTNER_ATR_MULT': 1.5,
    'ATR_WINDOW': 14,          # Keltner 내부 ATR window (ta default 10과 다름, 명시 필수)
    'BOLLINGER_WINDOW': 20,
    'BOLLINGER_SIGMA': 2.0,
    'SL_HARD': 0.08,
}

# --- Portfolio 공통 (W1-01 박제) ---
INIT_CASH = 1_000_000     # 100만원 (테스트)
FEES = 0.0005             # 업비트 0.05%
SLIPPAGE = 0.0005         # 0.05% 슬리피지
FREQ = '1D'
YEAR_FREQ = '365 days'    # W-1 정정: sqrt(365) annualization 강제 (vectorbt default '252 days' override)

# --- DSR + Go 기준 (decisions-final.md L518 + W2-03 v5) ---
N_TRIALS = 6              # Primary만 (Tier 2 Go 기여 X)
GO_SHARPE_THRESHOLD = 0.8
GO_DSR_Z_THRESHOLD = 0.0
SECONDARY_SHARPE_THRESHOLD = 0.5  # Secondary 마킹 (ensemble 후보)
SECONDARY_PAIR_COUNT = 3  # Tier 1+2 3+ 페어에서 충족 시 Secondary

# DSR 상수 (Bailey & López de Prado 2014)
EULER_MASCHERONI = 0.5772156649015329

print('사전 지정 파라미터 박제 완료 (변경 금지 서약 발효 중)')
print(f'  Strategy A: {STRATEGY_A_PARAMS}')
print(f'  Strategy C: {STRATEGY_C_PARAMS}')
print(f'  Strategy D: {STRATEGY_D_PARAMS}')
print(f'  Portfolio: INIT_CASH={INIT_CASH:,}, FEES={FEES}, SLIPPAGE={SLIPPAGE}, FREQ={FREQ}, YEAR_FREQ={YEAR_FREQ}')
print(f'  Go 기준: Primary Sharpe>{GO_SHARPE_THRESHOLD} AND DSR_z>{GO_DSR_Z_THRESHOLD} (N_trials={N_TRIALS})')
print(f'  Secondary: 전략이 Tier1+2 {SECONDARY_PAIR_COUNT}+ 페어에서 Sharpe>{SECONDARY_SHARPE_THRESHOLD}')
"""))

# ============================================================
# Cell 6: Strategy A 신호 함수 (W1-02 패턴 재사용)
# ============================================================
cells.append(nbf.v4.new_code_cell("""\
def strategy_a_signals(df, params=STRATEGY_A_PARAMS):
    '''Strategy A (Trend Following) entry/exit masks.

    W1-02 박제 패턴 (make_notebook_02.py):
    - donchian_high/low + vol_avg 모두 .shift(1) 적용 (look-ahead 차단)
    - entry: (close > ma200) AND (close > donchian_high) AND (volume > vol_avg × VOL_MULT)
    - exit: close < donchian_low
    - SL: sl_stop=0.08 (vectorbt 자동 처리, fraction)
    '''
    close = df['close']
    high = df['high']
    low = df['low']
    volume = df['volume']

    ma = close.rolling(window=params['MA_PERIOD']).mean()
    donchian_high = high.rolling(window=params['DONCHIAN_HIGH']).max().shift(1)
    donchian_low = low.rolling(window=params['DONCHIAN_LOW']).min().shift(1)
    vol_avg = volume.rolling(window=params['VOL_AVG_PERIOD']).mean().shift(1)

    entries = (close > ma) & (close > donchian_high) & (volume > vol_avg * params['VOL_MULT'])
    exits = close < donchian_low

    entries = entries.fillna(False).astype(bool)
    exits = exits.fillna(False).astype(bool)

    return entries, exits


# 검증 (BTC)
entries_test, exits_test = strategy_a_signals(data['KRW-BTC'])
print(f'Strategy A (BTC): entries={entries_test.sum()}, exits={exits_test.sum()}')
# Warmup (MA200 + shift) 기간 entries=0 sanity
warmup_entries = entries_test.iloc[:STRATEGY_A_PARAMS['MA_PERIOD']].sum()
assert warmup_entries == 0, f'Strategy A warmup entries != 0 (got {warmup_entries})'
print(f'  Warmup (first {STRATEGY_A_PARAMS[\"MA_PERIOD\"]} bars) entries=0 PASS')
"""))

# ============================================================
# Cell 7: Strategy C 신호 함수 (방법 B manual trailing ATR)
# ============================================================
cells.append(nbf.v4.new_code_cell("""\
def strategy_c_signals(df, params=STRATEGY_C_PARAMS):
    '''Strategy C (Slow Momentum) entry + exit masks.

    박제 (candidate-pool.md v4 L37 + W2-03.1 W-1 방법 B 채택):
    - entry: strict golden cross = (MA50 > MA200) AND (MA50.shift(1) <= MA200.shift(1))
    - exit: strict death cross OR 방법 B manual trailing stop (매 bar 동적 ATR)
      - trailing_high - ATR_MULT × ATR(14)(t) exit_mask
      - 방법 A (vectorbt sl_trail=True)는 entry bar 시점 비율 freeze → 박제 의도 위반 (W-2)
    - 청산 후 동일 추세 내 재진입 X (long-only, 다음 골든 크로스까지 대기)

    Returns: entries (bool), exits (bool) — vectorbt Portfolio.from_signals에 전달
    '''
    close = df['close']
    high = df['high']
    low = df['low']

    ma_short = close.rolling(window=params['FAST_MA']).mean()
    ma_long = close.rolling(window=params['SLOW_MA']).mean()
    atr = AverageTrueRange(high, low, close, window=params['ATR_WINDOW']).average_true_range()

    # Strict crossover (== 케이스 false)
    golden_cross = (ma_short > ma_long) & (ma_short.shift(1) <= ma_long.shift(1))
    death_cross = (ma_short < ma_long) & (ma_short.shift(1) >= ma_long.shift(1))

    entries_raw = golden_cross.fillna(False).astype(bool)

    # 방법 B: manual trailing stop (매 bar 동적 ATR(14)(t))
    # In-position 상태 관리 + 청산 후 동일 추세 내 재진입 차단
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
            # 진입 조건: golden cross 발생 + ATR 값 존재 (warmup 이후)
            if golden_values[i] and not np.isnan(atr_values[i]):
                in_position = True
                trailing_high = close_values[i]
                entry_mask.iloc[i] = True
        else:
            # trailing_high 갱신
            if close_values[i] > trailing_high:
                trailing_high = close_values[i]
            # exit 조건: death cross OR 매 bar 동적 trailing ATR stop
            stop_level = trailing_high - atr_mult * atr_values[i]
            triggered_death = bool(death_values[i])
            triggered_atr = (not np.isnan(atr_values[i])) and close_values[i] < stop_level
            if triggered_death or triggered_atr:
                exit_mask.iloc[i] = True
                in_position = False
                trailing_high = -np.inf

    return entry_mask, exit_mask


# 검증 (BTC)
entries_test, exits_test = strategy_c_signals(data['KRW-BTC'])
print(f'Strategy C (BTC): entries={entries_test.sum()}, exits={exits_test.sum()}')
# Warmup (SLOW_MA) 기간 entries=0 sanity
warmup_c = entries_test.iloc[:STRATEGY_C_PARAMS['SLOW_MA']].sum()
assert warmup_c == 0, f'Strategy C warmup entries != 0 (got {warmup_c})'
print(f'  Warmup (first {STRATEGY_C_PARAMS[\"SLOW_MA\"]} bars) entries=0 PASS')
# 청산 후 동일 추세 내 재진입 X sanity: entries <= exits + 1 (마지막 open trade 허용)
assert entries_test.sum() <= exits_test.sum() + 1, (
    f'Strategy C: 재진입 차단 위반 (entries={entries_test.sum()} > exits+1={exits_test.sum()+1})'
)
print(f'  재진입 차단 sanity PASS')
"""))

# ============================================================
# Cell 8: Strategy D 신호 함수 (ta Keltner + Bollinger)
# ============================================================
cells.append(nbf.v4.new_code_cell("""\
def strategy_d_signals(df, params=STRATEGY_D_PARAMS):
    '''Strategy D (Volatility Breakout) entry/exit masks.

    박제 (candidate-pool.md v4 + W2-02 v5 W2-02.2):
    - entry: strict 동시 돌파 = (close > kc_upper) crossover AND (close > bb_upper) crossover
    - exit: strict Keltner mid 하향 crossover OR sl_stop=0.08
    - ta KeltnerChannel(window=20, window_atr=14, original_version=False, multiplier=1.5)
      → original_version=False 시 mid = EMA(close, 20), upper = mid + multiplier × ATR(14)
    - ta BollingerBands(window=20, window_dev=2.0)
    '''
    close = df['close']
    high = df['high']
    low = df['low']

    # ta KeltnerChannel (original_version=False + window_atr + multiplier 모두 명시 필수, ta default와 다름)
    kc = KeltnerChannel(
        high=high, low=low, close=close,
        window=params['KELTNER_WINDOW'],
        window_atr=params['ATR_WINDOW'],
        original_version=False,
        multiplier=params['KELTNER_ATR_MULT'],
    )
    kc_upper = kc.keltner_channel_hband()
    kc_mid = kc.keltner_channel_mband()  # EMA(close, 20)

    # ta BollingerBands
    bb = BollingerBands(close=close, window=params['BOLLINGER_WINDOW'], window_dev=params['BOLLINGER_SIGMA'])
    bb_upper = bb.bollinger_hband()

    # Strict 동시 돌파
    kc_break = (close > kc_upper) & (close.shift(1) <= kc_upper.shift(1))
    bb_break = (close > bb_upper) & (close.shift(1) <= bb_upper.shift(1))
    entries = kc_break & bb_break

    # Exit: Keltner mid 하향 strict crossover (Hard SL은 vectorbt sl_stop으로 처리)
    mid_exit = (close < kc_mid) & (close.shift(1) >= kc_mid.shift(1))

    entries = entries.fillna(False).astype(bool)
    exits = mid_exit.fillna(False).astype(bool)

    return entries, exits


# 검증 (BTC)
entries_test, exits_test = strategy_d_signals(data['KRW-BTC'])
print(f'Strategy D (BTC): entries={entries_test.sum()}, exits={exits_test.sum()}')
warmup_d = entries_test.iloc[:STRATEGY_D_PARAMS['KELTNER_WINDOW']].sum()
assert warmup_d == 0, f'Strategy D warmup entries != 0 (got {warmup_d})'
print(f'  Warmup (first {STRATEGY_D_PARAMS[\"KELTNER_WINDOW\"]} bars) entries=0 PASS')
"""))

# ============================================================
# Cell 9: Portfolio 실행 함수 (vectorbt 방식 A, year_freq='365 days')
# ============================================================
cells.append(nbf.v4.new_code_cell("""\
def run_portfolio(df, entries, exits, strategy_name, pair):
    '''vectorbt Portfolio 실행 (방식 A: 페어별 독립 Portfolio).

    박제 강제 (W-1 정정):
    - freq='1D', year_freq='365 days' (sqrt(365) annualization)
    - Strategy C는 exits_mask에 이미 trailing + death 포함 (방법 B)
    - Strategy A는 sl_stop=SL_PCT=0.08
    - Strategy D는 sl_stop=SL_HARD=0.08

    Returns: pf (vectorbt Portfolio 객체)
    '''
    close = df['close']
    # Strategy별 sl_stop 정책
    if strategy_name == 'A':
        sl_stop = STRATEGY_A_PARAMS['SL_PCT']
        sl_trail = False
    elif strategy_name == 'C':
        sl_stop = None  # 방법 B (manual trailing) 사용 → sl_stop 불필요
        sl_trail = False
    elif strategy_name == 'D':
        sl_stop = STRATEGY_D_PARAMS['SL_HARD']
        sl_trail = False
    else:
        raise ValueError(f'Unknown strategy: {strategy_name}')

    kwargs = dict(
        close=close,
        entries=entries,
        exits=exits,
        init_cash=INIT_CASH,
        fees=FEES,
        slippage=SLIPPAGE,
        freq=FREQ,
    )
    if sl_stop is not None:
        kwargs['sl_stop'] = sl_stop
        kwargs['sl_trail'] = sl_trail

    pf = vbt.Portfolio.from_signals(**kwargs)
    return pf


def extract_metrics(pf, df, common_window_start=None):
    '''메트릭 추출 (max-span + common-window 이원).

    cycle 2 v5 박제:
    - Primary metric = max-span Sharpe (각 페어 자체 범위)
    - Secondary metric = common-window Sharpe (2021-10-15~ 부분)

    Returns: dict with max_span + common_window metrics
    '''
    # 메서드 호출 (괄호 필수, W1-02 박제 패턴)
    sharpe_max_span = float(pf.sharpe_ratio(year_freq=YEAR_FREQ))
    total_return = float(pf.total_return())
    max_dd = float(pf.max_drawdown())
    total_trades = int(pf.trades.count())

    if total_trades > 0:
        win_rate = float(pf.trades.win_rate())
        profit_factor = float(pf.trades.profit_factor())
    else:
        win_rate = float('nan')
        profit_factor = float('nan')

    # 연도별 Sharpe (daily returns 기반, year_freq 적용)
    returns = pf.returns()
    yearly_sharpe = {}
    if len(returns) > 0:
        returns_ts = returns.copy()
        if not isinstance(returns_ts.index, pd.DatetimeIndex):
            returns_ts.index = pd.to_datetime(returns_ts.index)
        for year, grp in returns_ts.groupby(returns_ts.index.year):
            if len(grp) < 2 or grp.std() == 0:
                yearly_sharpe[int(year)] = None
            else:
                # sqrt(365) annualization (year_freq 박제 일관)
                yearly_sharpe[int(year)] = float(np.sqrt(365) * grp.mean() / grp.std())

    # Common-window Sharpe (secondary metric, cycle 2 v5 박제)
    # B-2/B-3 정정: tz-aware 비교 위해 pd.Timestamp(tz='UTC') 변환 필수
    common_window_sharpe = None
    if common_window_start is not None and len(returns) > 0:
        cw_start_ts = pd.Timestamp(common_window_start, tz='UTC')
        returns_cw = returns[returns.index >= cw_start_ts]
        if len(returns_cw) >= 2 and returns_cw.std() > 0:
            common_window_sharpe = float(np.sqrt(365) * returns_cw.mean() / returns_cw.std())

    return {
        'sharpe_max_span': sharpe_max_span,
        'sharpe_common_window': common_window_sharpe,
        'total_return': total_return,
        'max_drawdown': max_dd,
        'total_trades': total_trades,
        'win_rate': win_rate,
        'profit_factor': profit_factor,
        'yearly_sharpe': yearly_sharpe,
        'T_returns': int(len(returns)),
        'returns_skew': float(scs.skew(returns.values)) if len(returns) > 2 else None,
        'returns_kurtosis': float(scs.kurtosis(returns.values, fisher=True)) if len(returns) > 2 else None,
    }


STRATEGY_FUNCS = {
    'A': strategy_a_signals,
    'C': strategy_c_signals,
    'D': strategy_d_signals,
}

print('Portfolio 실행 함수 + extract_metrics 정의 완료')
print(f'  vectorbt year_freq={YEAR_FREQ} 강제 (W-1 정정)')
print(f'  방식 A: 페어별 독립 Portfolio (for-loop)')
"""))

# ============================================================
# Cell 10: Primary grid 실행 (Tier 1 × {A,C,D} = 6셀)
# ============================================================
cells.append(nbf.v4.new_code_cell("""\
# Primary grid: Tier 1 (BTC, ETH) × {A, C, D} = 6셀 (Go 평가 대상)
primary_results = {}

for pair in PAIRS_TIER1:
    for strategy in ['A', 'C', 'D']:
        cell_id = f'{pair}_{strategy}'
        df = data[pair]
        signal_fn = STRATEGY_FUNCS[strategy]
        entries, exits = signal_fn(df)
        pf = run_portfolio(df, entries, exits, strategy, pair)
        metrics = extract_metrics(pf, df, common_window_start=COMMON_WINDOW_START)
        primary_results[cell_id] = {
            'pair': pair,
            'strategy': strategy,
            'tier': 'Tier 1',
            **metrics,
        }
        # B-1 정정: nested f-string 제거 (Python 3.11 SyntaxError 차단)
        cw_val = metrics['sharpe_common_window']
        cw_str = f'{cw_val:7.4f}' if cw_val is not None else '   None'
        print(f'{cell_id:20s}: Sharpe_max={metrics[\"sharpe_max_span\"]:7.4f}, '
              f'Sharpe_cw={cw_str}, '
              f'Return={metrics[\"total_return\"]*100:7.2f}%, '
              f'MDD={metrics[\"max_drawdown\"]*100:6.2f}%, '
              f'Trades={metrics[\"total_trades\"]:3d}')

print(f'\\nPrimary grid 실행 완료: {len(primary_results)} 셀')
"""))

# ============================================================
# Cell 11: Exploratory grid 실행 (Tier 2 × {A,C,D} = 12셀)
# ============================================================
cells.append(nbf.v4.new_code_cell("""\
# Exploratory grid: Tier 2 (XRP, SOL, TRX, DOGE) × {A, C, D} = 12셀 (Go 기여 X, Secondary 마킹 후보)
exploratory_results = {}

for pair in PAIRS_TIER2:
    for strategy in ['A', 'C', 'D']:
        cell_id = f'{pair}_{strategy}'
        df = data[pair]
        signal_fn = STRATEGY_FUNCS[strategy]
        entries, exits = signal_fn(df)
        pf = run_portfolio(df, entries, exits, strategy, pair)
        metrics = extract_metrics(pf, df, common_window_start=COMMON_WINDOW_START)
        exploratory_results[cell_id] = {
            'pair': pair,
            'strategy': strategy,
            'tier': 'Tier 2',
            **metrics,
        }
        # B-1 정정: nested f-string 제거 (Python 3.11 SyntaxError 차단)
        cw_val = metrics['sharpe_common_window']
        cw_str = f'{cw_val:7.4f}' if cw_val is not None else '   None'
        print(f'{cell_id:20s}: Sharpe_max={metrics[\"sharpe_max_span\"]:7.4f}, '
              f'Sharpe_cw={cw_str}, '
              f'Return={metrics[\"total_return\"]*100:7.2f}%, '
              f'MDD={metrics[\"max_drawdown\"]*100:6.2f}%, '
              f'Trades={metrics[\"total_trades\"]:3d}')

print(f'\\nExploratory grid 실행 완료: {len(exploratory_results)} 셀')
print(f'주: Tier 2 결과는 Go 기여 X (decisions-final.md L519 + 사용자 #4 결정 박제)')
"""))

# ============================================================
# Cell 12: DSR 단위 테스트 (재현성 + Wikipedia 예시 대조)
# ============================================================
cells.append(nbf.v4.new_code_cell("""\
def compute_sr_0(variance_sr, n_trials, euler=EULER_MASCHERONI):
    '''Expected maximum Sharpe ratio under H_0 (Bailey & López de Prado 2014, eq. 9).

    SR_0 = sqrt(V[SR_n]) × ((1-γ) × Φ⁻¹(1 - 1/N) + γ × Φ⁻¹(1 - 1/(N·e)))

    Args:
        variance_sr: V[SR_n] — Sharpe ratio sample variance across N_trials
        n_trials: N — number of independent strategy configurations tested
        euler: Euler-Mascheroni constant (default 0.5772...)

    Returns:
        SR_0 (expected maximum SR under null hypothesis)
    '''
    term1 = (1 - euler) * scs.norm.ppf(1 - 1.0 / n_trials)
    term2 = euler * scs.norm.ppf(1 - 1.0 / (n_trials * math.e))
    sr_0 = math.sqrt(variance_sr) * (term1 + term2)
    return sr_0


def compute_dsr(sr_hat, sr_0, returns, T=None):
    '''Deflated Sharpe Ratio z-score form (Bailey & López de Prado 2014, eq. 10).

    DSR_z = (SR_hat - SR_0) × sqrt((T - 1) / (1 - γ_3 × SR_0 + ((γ_4 - 1) / 4) × SR_0²))

    Args:
        sr_hat: observed annualized Sharpe ratio
        sr_0: expected maximum SR under H_0 (from compute_sr_0)
        returns: daily returns Series (for skewness + kurtosis)
        T: optional override for T (default: len(returns))

    Returns:
        (DSR_z, DSR_prob) where DSR_prob = Φ(DSR_z)
    '''
    if T is None:
        T = len(returns)
    gamma_3 = scs.skew(returns)
    gamma_4 = scs.kurtosis(returns, fisher=True) + 3  # Fisher kurtosis → raw kurtosis (Bailey 2014 공식)

    denom = 1 - gamma_3 * sr_0 + ((gamma_4 - 1) / 4.0) * sr_0 ** 2
    if denom <= 0 or T <= 1:
        return float('nan'), float('nan')

    dsr_z = (sr_hat - sr_0) * math.sqrt((T - 1) / denom)
    dsr_prob = float(scs.norm.cdf(dsr_z))
    return float(dsr_z), dsr_prob


# --- 단위 테스트 1: SR_0 재현성 (임의 V[SR_n]=1.0, N=6) ---
unit_test_variance = 1.0
unit_test_n = 6
sr_0_unit = compute_sr_0(unit_test_variance, unit_test_n)
print(f'DSR unit test 1 (V=1.0, N=6): SR_0 = {sr_0_unit:.6f}')

# --- 단위 테스트 2: Φ⁻¹(1 - 1/6) + Φ⁻¹(1 - 1/(6e)) sanity ---
phi_inv_6 = scs.norm.ppf(1 - 1.0 / 6)
phi_inv_6e = scs.norm.ppf(1 - 1.0 / (6 * math.e))
print(f'  Φ⁻¹(1 - 1/6) = {phi_inv_6:.6f}')
print(f'  Φ⁻¹(1 - 1/(6e)) = {phi_inv_6e:.6f}')
manual_sr_0 = (1 - EULER_MASCHERONI) * phi_inv_6 + EULER_MASCHERONI * phi_inv_6e
print(f'  Manual composition = {manual_sr_0:.6f} (should match {sr_0_unit:.6f})')
assert abs(manual_sr_0 - sr_0_unit) < 1e-9, 'compute_sr_0 자체 일관성 실패'

# --- 단위 테스트 3: DSR_z with synthetic data (SR_hat > SR_0 → DSR_z > 0) ---
rng = np.random.default_rng(42)
synthetic_returns = rng.normal(0.001, 0.02, 1000)  # positive mean
synthetic_sr = np.sqrt(365) * synthetic_returns.mean() / synthetic_returns.std()
dsr_z_test, dsr_prob_test = compute_dsr(synthetic_sr, sr_0_unit, synthetic_returns)
print(f'\\nDSR unit test 3 (synthetic, SR_hat={synthetic_sr:.4f}, SR_0={sr_0_unit:.4f}):')
print(f'  DSR_z = {dsr_z_test:.4f}')
print(f'  DSR_prob = Φ(DSR_z) = {dsr_prob_test:.4f}')
print(f'  상식: SR_hat > SR_0 → DSR_z > 0 → {\"PASS\" if dsr_z_test > 0 else \"FAIL\"}')

# 결과 JSON 저장 (재현성 + 외부 감사 검증 가능성, NIT-3 evidence)
dsr_unit_test_result = {
    'generated_at': datetime.now(timezone.utc).isoformat(),
    'euler_mascheroni': EULER_MASCHERONI,
    'test_1_sr_0': {
        'variance_sr': unit_test_variance,
        'n_trials': unit_test_n,
        'sr_0': sr_0_unit,
        'phi_inv_1_minus_1_over_N': phi_inv_6,
        'phi_inv_1_minus_1_over_Ne': phi_inv_6e,
    },
    'test_3_dsr_synthetic': {
        'sr_hat': float(synthetic_sr),
        'sr_0': sr_0_unit,
        'dsr_z': dsr_z_test,
        'dsr_prob': dsr_prob_test,
        'passed': bool(dsr_z_test > 0),
    },
    'formula': {
        'sr_0': 'sqrt(V[SR_n]) × ((1-γ) × Φ⁻¹(1 - 1/N) + γ × Φ⁻¹(1 - 1/(N·e)))',
        'dsr_z': '(SR_hat - SR_0) × sqrt((T - 1) / (1 - γ_3 × SR_0 + ((γ_4 - 1) / 4) × SR_0²))',
        'source': 'Bailey & López de Prado (2014), SSRN 2460551',
    },
}
out_dir = Path('../outputs')
out_dir.mkdir(exist_ok=True)
(out_dir / 'w2_03_dsr_unit_test.json').write_text(json.dumps(dsr_unit_test_result, indent=2, ensure_ascii=False))
print(f'\\nDSR unit test 저장: {out_dir / \"w2_03_dsr_unit_test.json\"}')
"""))

# ============================================================
# Cell 13: DSR 계산 (Primary 6셀) + V[SR_n] 이원 보고
# ============================================================
cells.append(nbf.v4.new_code_cell("""\
# W2-03.4 DSR 계산 박제
# N_trials = 6 (Primary만, Tier 2 Go 기여 X → multiple testing 분모 제외)

# Primary 6셀 Sharpe 수집
primary_sharpes = np.array([
    primary_results[cell_id]['sharpe_max_span']
    for cell_id in primary_results.keys()
])
primary_sharpes = primary_sharpes[~np.isnan(primary_sharpes)]  # NaN 제외

# V[SR_n] 이원 보고 (W-2 alarm)
# 1. Empirical: 6 primary 셀 Sharpe sample variance
v_empirical = float(np.var(primary_sharpes, ddof=1)) if len(primary_sharpes) > 1 else 1.0
# 2. Normalized: 1.0 (보수적, N=6 협소성 감안)
v_normalized = 1.0
v_reported = max(v_empirical, v_normalized)  # 보수적 = 둘 중 큰 값

print(f'Primary 6셀 Sharpe sample variance (W-2 alarm):')
print(f'  Empirical V[SR_n] = {v_empirical:.6f}')
print(f'  Normalized V[SR_n] = {v_normalized:.6f}')
print(f'  Reported (conservative, max) = {v_reported:.6f}')
print()

# SR_0 (각 variance 버전별 동시 산출)
sr_0_empirical = compute_sr_0(v_empirical, N_TRIALS) if v_empirical > 0 else float('nan')
sr_0_normalized = compute_sr_0(v_normalized, N_TRIALS)
sr_0_reported = compute_sr_0(v_reported, N_TRIALS)
print(f'SR_0 (N_trials={N_TRIALS}, Bailey 2014 eq. 9):')
print(f'  SR_0 (V_empirical) = {sr_0_empirical:.6f}')
print(f'  SR_0 (V_normalized=1.0) = {sr_0_normalized:.6f}')
print(f'  SR_0 (V_reported conservative) = {sr_0_reported:.6f}')
print()

# DSR 각 셀별 계산 (SR_0 reported = 보수적)
print(f'DSR_z + DSR_prob 산출 (SR_0={sr_0_reported:.4f}, N_trials={N_TRIALS}):')
print(f'{"cell_id":20s}  {"SR_hat":>8s}  {"DSR_z":>8s}  {"DSR_prob":>8s}  {"Go":>5s}')
for cell_id, result in primary_results.items():
    pair = result['pair']
    strategy = result['strategy']
    sr_hat = result['sharpe_max_span']
    df = data[pair]
    signal_fn = STRATEGY_FUNCS[strategy]
    entries, exits = signal_fn(df)
    pf = run_portfolio(df, entries, exits, strategy, pair)
    returns = pf.returns()

    if np.isnan(sr_hat) or len(returns) < 2:
        dsr_z = float('nan')
        dsr_prob = float('nan')
        is_go = False
    else:
        dsr_z, dsr_prob = compute_dsr(sr_hat, sr_0_reported, returns.values)
        # Go 판정: Primary 셀 중 pair in {BTC, ETH} (이미 보장) × Sharpe > 0.8 × DSR_z > 0
        is_go = (sr_hat > GO_SHARPE_THRESHOLD) and (dsr_z > GO_DSR_Z_THRESHOLD)

    result['dsr_z'] = dsr_z
    result['dsr_prob'] = dsr_prob
    result['sr_0_reported'] = sr_0_reported
    result['v_reported'] = v_reported
    result['is_go_cell'] = bool(is_go)

    print(f'{cell_id:20s}  {sr_hat:8.4f}  {dsr_z:8.4f}  {dsr_prob:8.4f}  {"GO" if is_go else "-":>5s}')

print()
print(f'Multiple testing 한계 (decisions-final.md L521): 6 primary 셀도 family-wise 오류 여지. DSR 부분 완화 + Week 3 walk-forward 최종 검증.')
"""))

# ============================================================
# Cell 14: Go/No-Go 평가 + Secondary 마킹
# ============================================================
cells.append(nbf.v4.new_code_cell("""\
# W2-03.5 Go/No-Go 평가
# 사전 지정 Go 기준 (decisions-final.md L518):
#   Primary 6셀 중 1+개 전략이 BTC 또는 ETH에서 Sharpe > 0.8 AND DSR_z > 0 → Go

go_cells = [cell_id for cell_id, r in primary_results.items() if r.get('is_go_cell', False)]
is_go = len(go_cells) > 0

print('=' * 60)
print('W2-03.5 Go/No-Go 평가')
print('=' * 60)
print(f'Go 기준: Sharpe > {GO_SHARPE_THRESHOLD} AND DSR_z > {GO_DSR_Z_THRESHOLD} (pair in Tier 1)')
print(f'Go 통과 셀: {len(go_cells)}개')
for cell_id in go_cells:
    r = primary_results[cell_id]
    print(f'  {cell_id}: Sharpe={r[\"sharpe_max_span\"]:.4f}, DSR_z={r[\"dsr_z\"]:.4f}, Strategy={r[\"strategy\"]}')
print()
print(f'결정: {\"GO\" if is_go else \"NO-GO\"}')
if is_go:
    print('  → Week 3 walk-forward 진입')
    print('  → Go 통과 전략은 Strategy A/C/D 구분 없이 DSR-adjusted + Week 3 walk-forward 재검증 의무 (B-4 대칭)')
else:
    print('  → Stage 1 킬 카운터 +1')
    print('  → 사용자 결정 필요: Week 3 재탐색 vs Stage 1 종료')
print()

# Secondary 마킹: 동일 전략이 Tier 1+2 3+ 페어에서 Sharpe > 0.5
print('Secondary 마킹 (ensemble 후보, Go 기여 X):')
all_results = {**primary_results, **exploratory_results}
strategy_secondary = {'A': [], 'C': [], 'D': []}
for cell_id, r in all_results.items():
    if r['sharpe_max_span'] > SECONDARY_SHARPE_THRESHOLD:
        strategy_secondary[r['strategy']].append(r['pair'])

for strategy, pairs in strategy_secondary.items():
    count = len(pairs)
    marked = count >= SECONDARY_PAIR_COUNT
    print(f'  Strategy {strategy}: {count} 페어 Sharpe>{SECONDARY_SHARPE_THRESHOLD} ({pairs}) → {\"SECONDARY 마킹\" if marked else \"미달\"}')

print()
print('사용자 명시 Go/No-Go 결정 필요 (W2-03.6). 자동 진행 X.')
"""))

# ============================================================
# Cell 15: 결과 저장 (JSON)
# ============================================================
cells.append(nbf.v4.new_code_cell("""\
# 결과 저장 (research/outputs/)
out_dir = Path('../outputs')
out_dir.mkdir(exist_ok=True)

# 페어별 SHA256 박제
data_hashes_recorded = {}
for pair in PAIRS_ALL:
    filename = f'{pair}_1d_frozen_{FREEZE_DATE}.parquet'
    data_hashes_recorded[filename] = expected_hashes[filename]

# Primary grid 저장
primary_out = {
    'generated_at': datetime.now(timezone.utc).isoformat(),
    'task_id': 'W2-03',
    'feature_id': 'BT-005',
    'subtask': 'W2-03.2 Primary grid',
    'pairs_tier1': PAIRS_TIER1,
    'strategies': ['A', 'C', 'D'],
    'total_cells': len(primary_results),
    'data_hashes': data_hashes_recorded,
    'parameters': {
        'strategy_a': STRATEGY_A_PARAMS,
        'strategy_c': STRATEGY_C_PARAMS,
        'strategy_d': STRATEGY_D_PARAMS,
        'portfolio': {'INIT_CASH': INIT_CASH, 'FEES': FEES, 'SLIPPAGE': SLIPPAGE, 'FREQ': FREQ, 'YEAR_FREQ': YEAR_FREQ},
    },
    'common_window_start': COMMON_WINDOW_START,
    'advertised_end': ADVERTISED_END,
    'cells': primary_results,
}
(out_dir / 'w2_03_primary_grid.json').write_text(json.dumps(primary_out, indent=2, ensure_ascii=False, default=str))
print(f'Primary grid 저장: {out_dir / \"w2_03_primary_grid.json\"}')

# Exploratory grid 저장
exploratory_out = {
    'generated_at': datetime.now(timezone.utc).isoformat(),
    'task_id': 'W2-03',
    'feature_id': 'BT-005',
    'subtask': 'W2-03.3 Exploratory grid',
    'pairs_tier2': PAIRS_TIER2,
    'strategies': ['A', 'C', 'D'],
    'total_cells': len(exploratory_results),
    'go_contribution': False,  # decisions-final.md L519 + 사용자 #4 결정
    'data_hashes': data_hashes_recorded,
    'cells': exploratory_results,
}
(out_dir / 'w2_03_exploratory_grid.json').write_text(json.dumps(exploratory_out, indent=2, ensure_ascii=False, default=str))
print(f'Exploratory grid 저장: {out_dir / \"w2_03_exploratory_grid.json\"}')

# DSR + Go/No-Go 종합 저장
dsr_out = {
    'generated_at': datetime.now(timezone.utc).isoformat(),
    'task_id': 'W2-03',
    'feature_id': 'BT-005',
    'subtask': 'W2-03.4 DSR + W2-03.5 Go/No-Go',
    'formula_source': 'Bailey & López de Prado (2014), SSRN 2460551',
    'n_trials': N_TRIALS,
    'v_empirical': v_empirical,
    'v_normalized': v_normalized,
    'v_reported': v_reported,
    'sr_0': {
        'empirical': sr_0_empirical,
        'normalized': sr_0_normalized,
        'reported': sr_0_reported,
    },
    'go_criteria': {
        'sharpe_threshold': GO_SHARPE_THRESHOLD,
        'dsr_z_threshold': GO_DSR_Z_THRESHOLD,
        'pair_scope': 'Tier 1 (BTC, ETH)',
    },
    'primary_cells_dsr': {cid: {'sharpe_max_span': r['sharpe_max_span'], 'dsr_z': r.get('dsr_z'), 'dsr_prob': r.get('dsr_prob'), 'is_go_cell': r.get('is_go_cell')} for cid, r in primary_results.items()},
    'go_cells': go_cells,
    'is_go': is_go,
    'secondary_marked': {s: pairs for s, pairs in strategy_secondary.items() if len(pairs) >= SECONDARY_PAIR_COUNT},
    'multiple_testing_note': 'Family-wise 오류 여지 잔존. DSR로 부분 완화. Week 3 walk-forward 최종 검증 (decisions-final.md L521).',
}
(out_dir / 'w2_03_dsr.json').write_text(json.dumps(dsr_out, indent=2, ensure_ascii=False, default=str))
print(f'DSR + Go/No-Go 저장: {out_dir / \"w2_03_dsr.json\"}')
"""))

# ============================================================
# Cell 16: 요약 출력
# ============================================================
cells.append(nbf.v4.new_code_cell("""\
print('=' * 70)
print('W2-03 In-sample grid + DSR + Go/No-Go 실행 요약')
print('=' * 70)
print(f'데이터: 6 페어 × 일봉 (SHA256 무결성 검증 PASS)')
print(f'  Tier 1: {PAIRS_TIER1}')
print(f'  Tier 2: {PAIRS_TIER2}')
print(f'Common-window 시작: {COMMON_WINDOW_START} UTC (SOL 기준)')
print(f'Advertised 종료: {ADVERTISED_END} UTC')
print()
print(f'Grid 실행: Primary 6셀 + Exploratory 12셀 = 18셀')
print(f'  Strategy: A (Trend), C (Slow Momentum 방법 B trailing), D (Vol Breakout Keltner+BB)')
print(f'  vectorbt year_freq={YEAR_FREQ} (W-1 sqrt(365) 강제)')
print()
print(f'DSR (Bailey & López de Prado 2014):')
print(f'  N_trials = {N_TRIALS} (Primary만)')
print(f'  V[SR_n] reported = {v_reported:.4f} (conservative)')
print(f'  SR_0 reported = {sr_0_reported:.4f}')
print()
print(f'Go/No-Go: {\"GO\" if is_go else \"NO-GO\"}')
if is_go:
    print(f'  Go 통과 셀 {len(go_cells)}개: {go_cells}')
    print(f'  → W3 walk-forward 진입 (사용자 컨펌 필요)')
else:
    print(f'  Go 통과 셀 0개')
    print(f'  → Stage 1 킬 카운터 +1 (사용자 결정 필요)')
print()
print('산출물:')
print(f'  {out_dir / \"w2_03_primary_grid.json\"}')
print(f'  {out_dir / \"w2_03_exploratory_grid.json\"}')
print(f'  {out_dir / \"w2_03_dsr.json\"}')
print(f'  {out_dir / \"w2_03_dsr_unit_test.json\"}')
print()
print('다음 단계:')
print('  W2-03.6 Week 2 리포트 + backtest-reviewer + 사용자 Go/No-Go 결정')
print('  W2-03.7 외부 감사 (결과 정합성 + cherry-pick 통로 검증)')
"""))

# ============================================================
# Save notebook
# ============================================================
nb['cells'] = cells
nb['metadata'] = {
    'kernelspec': {
        'display_name': 'Python 3 (ipykernel)',
        'language': 'python',
        'name': 'python3',
    },
    'language_info': {'name': 'python'},
}

OUT = Path(__file__).resolve().parent.parent / 'notebooks' / '08_insample_grid.ipynb'
OUT.parent.mkdir(exist_ok=True)
nbf.write(nb, str(OUT))
print(f'Wrote {OUT}')
