# Week 1 — 복제 스프린트 Day-by-Day 플랜 (Day 0 적용 후)

> **목표**: Padysak/Vojtko 영감 전략(추세 + 평균회귀)이 업비트 KRW-BTC 일봉에서 작동하는지 1주일 안에 확인.
> **방법**: Jupyter 노트북 + pandas + vectorbt + pyupbit. 프레임워크 없음. 최소 인프라.
> **Deliverable**: Week 1 종료 시 사전 지정 파라미터 Sharpe 측정 결과 + Go/No-Go 결정.
>
> 모르는 단어는 [`glossary.md`](./glossary.md) 참조 (ATR, RSI, MA, Donchian, Sharpe, Wilder, vectorbt 등).
>
> 본 문서는 검증된 vectorbt 0.28.5 + pyupbit 0.2.34 API 기반으로 작성됨.

---

## Week 1 전체 목표

### 성공 기준 (Go to Week 2)

- 5년치 KRW-BTC 일봉 + 4시간봉 데이터 수집 완료 (frozen + SHA256)
- Strategy A (추세) 단독 백테스트 완료 (사전 지정 파라미터)
- Strategy B (평균회귀) 단독 백테스트 완료 (사전 지정 파라미터)
- Strategy A 일봉 Sharpe > 0.8 (수수료/슬리피지 포함)
- Strategy B 일봉 Sharpe > 0.5
- MDD < 50%
- 5개 연도 중 최소 2개 양수 수익
- 4시간봉 결과는 참고용 (Go/No-Go 기준 아님)
- 앙상블은 Week 2로 연기 (Week 1 제외)

### 실패 기준 (Stage 1 킬 카운터 +1주)

- 데이터 수집 실패 OR 두 전략 모두 사전 지정 Sharpe 미달

---

## Day 1 (월요일) — 환경 세팅 + 데이터 수집

### Task 1.1: 프로젝트 구조 + Git

```bash
cd /Users/kyounghwanlee/Desktop/coin-bot
mkdir -p research/{notebooks,data,outputs}
cd research
python3.11 -m venv .venv
source .venv/bin/activate
```

루트에 `.gitignore` 작성:
```
.venv/
__pycache__/
*.pyc
.ipynb_checkpoints/
research/data/
research/outputs/
.env
secrets/
*.log
```

Git 초기화 (아직 안 됐다면):
```bash
cd /Users/kyounghwanlee/Desktop/coin-bot
git init
git add .gitignore CLAUDE.md docs/ research/CLAUDE.md AGENTS_md_Master_Prompt.md
git commit -m "Day 0: docs and CLAUDE.md system"
```

### Task 1.2: 의존성 설치 + 잠금

`research/requirements.txt`:
```
jupyterlab
pandas>=2.0,<3.0
numpy
matplotlib
seaborn
pyupbit==0.2.34
ccxt
vectorbt==0.28.5
ta
pyarrow
```

```bash
cd research
pip install -r requirements.txt
pip install uv
uv pip compile requirements.txt -o requirements.lock
```

Git 커밋:
```bash
cd /Users/kyounghwanlee/Desktop/coin-bot
git add research/requirements.txt research/requirements.lock
git commit -m "Day 1: pin Python dependencies"
```

### Task 1.3: 노트북 `01_data_collection.ipynb` 작성

검증된 pyupbit 0.2.34 API 기반:

```python
import pyupbit
import pandas as pd
import hashlib
import time
from pathlib import Path

# pyupbit 시그니처 (검증됨):
# get_ohlcv_from(ticker, interval, fromDatetime, to, period)
# - to= 파라미터 존재함
# - 인덱스는 timezone-naive KST
# - 에러 시 None 반환 (예외 없음)
# - period=0.1이 기본이지만 0.2 권장 (Upbit rate limit 안전 마진)

def fetch_with_retry(ticker, interval, start, end, max_retries=5):
    for attempt in range(max_retries):
        df = pyupbit.get_ohlcv_from(
            ticker=ticker,
            interval=interval,
            fromDatetime=start,
            to=end,
            period=0.2,  # 5 req/sec, Upbit 10 req/sec 한계의 절반
        )
        if df is not None and not df.empty:
            return df
        wait = 2 ** attempt
        print(f"Attempt {attempt+1} failed, sleeping {wait}s")
        time.sleep(wait)
    raise RuntimeError(f"Failed to fetch {ticker} after {max_retries} retries")

# 1. 일봉 (Week 1 메인)
df_daily = fetch_with_retry(
    ticker="KRW-BTC",
    interval="day",
    start="2021-01-01 00:00:00",
    end="2026-04-12 00:00:00",
)

# 2. 4시간봉 (Day 5 실험용)
df_4h = fetch_with_retry(
    ticker="KRW-BTC",
    interval="minute240",  # 240분 = 4시간
    start="2021-01-01 00:00:00",
    end="2026-04-12 00:00:00",
)

# 3. 타임존 처리 (검증됨: pyupbit는 naive KST 반환)
for df in [df_daily, df_4h]:
    assert df.index.tz is None, "Expected naive timestamps from pyupbit"
    df.index = df.index.tz_localize('Asia/Seoul').tz_convert('UTC')

# 4. Gap detection
def check_gaps(df, freq):
    expected = pd.date_range(start=df.index[0], end=df.index[-1], freq=freq)
    missing = expected.difference(df.index)
    pct = len(missing) / len(expected) * 100
    return len(missing), pct

daily_gaps, daily_pct = check_gaps(df_daily, '1D')
h4_gaps, h4_pct = check_gaps(df_4h, '4h')
print(f"Daily: {len(df_daily)} bars, {daily_gaps} gaps ({daily_pct:.3f}%)")
print(f"4h:    {len(df_4h)} bars, {h4_gaps} gaps ({h4_pct:.3f}%)")

# 5. 저장 (frozen 날짜 포함)
Path('data').mkdir(exist_ok=True)
daily_path = 'data/KRW-BTC_1d_frozen_20260412.parquet'
h4_path = 'data/KRW-BTC_4h_frozen_20260412.parquet'
df_daily.to_parquet(daily_path)
df_4h.to_parquet(h4_path)

# 6. SHA256 해시 기록
def sha256_file(path):
    h = hashlib.sha256()
    with open(path, 'rb') as f:
        for chunk in iter(lambda: f.read(65536), b''):
            h.update(chunk)
    return h.hexdigest()

with open('data/data_hashes.txt', 'w') as f:
    f.write(f"{daily_path}: {sha256_file(daily_path)}\n")
    f.write(f"{h4_path}: {sha256_file(h4_path)}\n")

print("Day 1 완료")
```

### Day 1 체크리스트

- [ ] 환경 세팅 + venv + requirements.lock
- [ ] git init + 첫 커밋
- [ ] 노트북 실행 성공
- [ ] 일봉 ~1,930개, 4시간봉 ~11,600개
- [ ] 갭 < 0.1%
- [ ] Parquet + 해시 파일 생성

---

## Day 2 (화요일) — Strategy A 일봉 백테스트 (추세 추종)

### 노트북 `02_strategy_a_trend_daily.ipynb`

검증된 vectorbt 0.28.5 API 기반:

```python
import pandas as pd
import numpy as np
import vectorbt as vbt
from ta.volatility import AverageTrueRange
import json

# 데이터 로드 + 해시 검증
df = pd.read_parquet('data/KRW-BTC_1d_frozen_20260412.parquet')
close = df['close']
high = df['high']
low = df['low']
volume = df['volume']

# 사전 지정 파라미터 (Padysak 영감, 일봉 기준)
MA_PERIOD = 200       # 일봉 200일 MA (장기 추세 필터)
DONCHIAN_HIGH = 20    # 20일 최고가
DONCHIAN_LOW = 10     # 10일 최저가 (청산용)
VOL_AVG_PERIOD = 20
VOL_MULT = 1.5
ATR_PERIOD = 14
SL_PCT = 0.08         # 하드 손절 -8%
# 주: 트레일링 손절은 Week 2에서 검토. Week 1은 하드 손절만.

# 지표 계산
ma200 = close.rolling(window=MA_PERIOD).mean()
donchian_high = high.rolling(window=DONCHIAN_HIGH).max().shift(1)
donchian_low = low.rolling(window=DONCHIAN_LOW).min().shift(1)
vol_avg = volume.rolling(window=VOL_AVG_PERIOD).mean()

# ATR (Wilder 스무딩, ta 라이브러리)
atr = AverageTrueRange(high=high, low=low, close=close, window=ATR_PERIOD).average_true_range()

# 진입 조건
entries = (
    (close > ma200) &
    (close > donchian_high) &
    (volume > vol_avg * VOL_MULT)
)

# 청산 조건: Donchian 하단 이탈
exits = close < donchian_low

# vectorbt 백테스트 (검증된 파라미터만 사용)
pf = vbt.Portfolio.from_signals(
    close=close,
    entries=entries,
    exits=exits,
    sl_stop=SL_PCT,           # 하드 손절 (fraction, 0.08 = 8%)
    sl_trail=False,           # 하드 손절은 trail 없음
    init_cash=1_000_000,
    fees=0.0005,              # 업비트 0.05%
    slippage=0.0005,
    freq='1D',
)

# 결과
stats = pf.stats()
print(stats)

# 핵심 지표만 저장
results = {
    'strategy': 'A_trend_daily',
    'parameters': {
        'ma_period': MA_PERIOD,
        'donchian_high': DONCHIAN_HIGH,
        'donchian_low': DONCHIAN_LOW,
        'vol_mult': VOL_MULT,
        'sl_pct': SL_PCT,
    },
    'sharpe': float(pf.sharpe_ratio()),  # 메서드 호출 (괄호 필수)
    'total_return': float(pf.total_return()),
    'max_drawdown': float(pf.max_drawdown()),
    'win_rate': float(pf.trades.win_rate()),
    'profit_factor': float(pf.trades.profit_factor()),
    'total_trades': int(pf.trades.count()),
}

with open('outputs/strategy_a_daily.json', 'w') as f:
    json.dump(results, f, indent=2)

print(f"Sharpe: {results['sharpe']:.3f}")
print(f"Total Return: {results['total_return']*100:.1f}%")
print(f"Max Drawdown: {results['max_drawdown']*100:.1f}%")
print(f"Trades: {results['total_trades']}")
```

### Day 2 체크리스트

- [ ] Strategy A 신호 생성 성공
- [ ] vectorbt 백테스트 크래시 없이 실행
- [ ] `outputs/strategy_a_daily.json` 생성
- [ ] Sharpe, MDD, 승률, PF 기록

---

## Day 3 (수요일) — Strategy B 일봉 백테스트 (평균 회귀)

### 노트북 `03_strategy_b_mean_reversion_daily.ipynb`

```python
import pandas as pd
import vectorbt as vbt
from ta.momentum import RSIIndicator
import json

df = pd.read_parquet('data/KRW-BTC_1d_frozen_20260412.parquet')
close = df['close']

# 사전 지정 파라미터
MA_PERIOD = 200
RSI_PERIOD = 4
RSI_BUY = 25
RSI_SELL = 50
TIME_STOP_DAYS = 5
SL_PCT = 0.08

# 지표
ma200 = close.rolling(window=MA_PERIOD).mean()
rsi = RSIIndicator(close=close, window=RSI_PERIOD).rsi()

# 진입: 상승 추세 + 극단 과매도
entries = (close > ma200) & (rsi < RSI_BUY)

# 청산 1: RSI 회복
rsi_exits = rsi > RSI_SELL

# 청산 2: 시간 스톱 (vectorbt 0.28.5에는 td_stop 없음)
# 검증된 패턴: entries.shift(N)을 추가 exit으로 OR
# 주: 이는 "엔트리 신호 N바 후 exit" 근사. 실제 보유 N바 후가 아님 (포지션 재진입 차단 시 약간 차이 가능)
time_exits = entries.shift(TIME_STOP_DAYS).fillna(False).astype(bool)

# 두 청산 조건 결합
exits = rsi_exits | time_exits

pf = vbt.Portfolio.from_signals(
    close=close,
    entries=entries,
    exits=exits,
    sl_stop=SL_PCT,
    sl_trail=False,
    init_cash=1_000_000,
    fees=0.0005,
    slippage=0.0005,
    freq='1D',
)

stats = pf.stats()
print(stats)

results = {
    'strategy': 'B_mean_reversion_daily',
    'parameters': {
        'ma_period': MA_PERIOD,
        'rsi_period': RSI_PERIOD,
        'rsi_buy': RSI_BUY,
        'rsi_sell': RSI_SELL,
        'time_stop_days': TIME_STOP_DAYS,
        'sl_pct': SL_PCT,
    },
    'sharpe': float(pf.sharpe_ratio()),
    'total_return': float(pf.total_return()),
    'max_drawdown': float(pf.max_drawdown()),
    'win_rate': float(pf.trades.win_rate()),
    'profit_factor': float(pf.trades.profit_factor()),
    'total_trades': int(pf.trades.count()),
}

with open('outputs/strategy_b_daily.json', 'w') as f:
    json.dump(results, f, indent=2)
```

### Day 3 체크리스트

- [ ] Strategy B 신호 생성 + 시간 스톱 패턴 작동
- [ ] 결과 기록
- [ ] **중간 평가**: A Sharpe > 0.8 OR B Sharpe > 0.5?

---

## Day 4 (목요일) — 강건성 + 민감도 분석

### 노트북 `04_robustness_sensitivity.ipynb`

#### 4-1. 연도별 분할 분석

각 전략의 연도별 성과 (2021/2022/2023/2024/2025/2026Q1):
```python
yearly_returns = pf.returns().resample('YS').apply(lambda x: (1+x).prod() - 1)
yearly_sharpe = pf.returns().resample('YS').apply(
    lambda x: x.mean() / x.std() * np.sqrt(252) if x.std() > 0 else 0
)
```

#### 4-2. 민감도 그리드 (참고용만)

```python
ma_grid = [100, 150, 200, 250, 300]
donchian_grid = [10, 15, 20, 30, 40]

results_grid = []
for ma in ma_grid:
    for dh in donchian_grid:
        # 같은 백테스트 반복
        # 결과 저장
        ...

# 등고선 차트로 평탄(robust) vs 뾰족(overfit) 시각화
```

**중요**: 민감도 그리드의 최고값을 보고 X. **사전 지정 파라미터(MA=200, Donchian=20/10)만 Go/No-Go에 사용**.

### Day 4 체크리스트

- [ ] 연도별 분할 분석 완료
- [ ] 민감도 등고선 차트
- [ ] 사전 지정 파라미터 위치가 평탄 영역에 있나?

---

## Day 5 (금요일) — 4시간봉 포팅 실험 (참고용)

### 노트북 `05_4h_porting_experiment.ipynb`

같은 전략을 4시간봉으로:
- MA 윈도우: 200일 = **1200 바** (200 × 6 bars/day)
- Donchian: 20일 = **120 바**, 10일 = **60 바**
- RSI(4)는 4시간봉의 4 바 = 16시간

```python
df_4h = pd.read_parquet('data/KRW-BTC_4h_frozen_20260412.parquet')
close_4h = df_4h['close']

# 일봉 200일 = 4시간봉 1200 바
ma200_4h = close_4h.rolling(window=1200).mean()

# 일봉 20일/10일 = 4시간봉 120/60 바
donchian_high_4h = df_4h['high'].rolling(window=120).max().shift(1)
donchian_low_4h = df_4h['low'].rolling(window=60).min().shift(1)

# 동일한 사전 지정 파라미터로 백테스트
# freq='4h' (소문자, 검증됨)
pf_4h = vbt.Portfolio.from_signals(
    close=close_4h,
    entries=...,
    exits=...,
    sl_stop=0.08,
    init_cash=1_000_000,
    fees=0.0005,
    slippage=0.0005,
    freq='4h',
)
```

**경고**: 4시간봉 MA1200 → 첫 1200 바(200일) warmup 손실 → 실 백테스트 시작 시점 ~2021-07-20.

**중요**: 4시간봉 결과는 **참고용**, Week 1 Go/No-Go 기준 아님.

---

## Day 6 (토요일) — 종합 리포트 + Go/No-Go

### 노트북 `06_week1_report.ipynb` + `outputs/week1_report.md`

내용:
1. 데이터 개요 (기간, 갭, 해시)
2. Strategy A 일봉 결과 (사전 지정)
3. Strategy B 일봉 결과 (사전 지정)
4. 4시간봉 포팅 결과 (참고)
5. 연도별 분할 분석
6. 민감도 등고선 (사전 지정 파라미터 위치 표시)
7. **Go/No-Go 결정**

### Go 기준 (모두 충족 필요)

- [ ] Strategy A 일봉 사전 지정 Sharpe > 0.8
- [ ] Strategy B 일봉 사전 지정 Sharpe > 0.5
- [ ] 두 전략 중 하나라도 MDD < 50%
- [ ] 두 전략 중 하나라도 5개 연도 중 최소 2개 양수 수익
- [ ] 사전 지정 파라미터가 민감도 그리드의 평탄 영역에 위치

### No-Go 시 조치

- 근본 원인 분석 (데이터? 전략? 파라미터?)
- Week 2를 "전략 패밀리 탐색"에 사용 (Stage 1 킬 카운터 +1주)
- 8주 안에 새 전략을 못 찾으면 Stage 1 킬 발동

---

## Day 7 (일요일) — 사용자 리뷰 + Week 2 계획

### 사용자 보고 형식

```
## Week 1 결과 요약

### 데이터
- 기간: 2021-01-01 ~ 2026-04-12
- 일봉: N개, 갭 X%
- 4h봉: N개, 갭 X%
- SHA256 해시: ...

### Strategy A (일봉, 사전 지정)
- Sharpe: X.XX
- CAGR: XX.X%
- MDD: XX.X%
- 승률: XX.X%
- PF: X.XX
- 트레이드: N

### Strategy B (일봉, 사전 지정)
(동일)

### 4h 비교 (참고용)
(요약)

### Go/No-Go
[ Go ] / [ No-Go ] + 이유

### Week 2 제안
...
```

### Day 7 체크리스트

- [ ] 리포트 사용자 전달
- [ ] 사용자 승인 대기
- [ ] Week 2 상세 계획 (`docs/week2-plan.md`)

---

## Week 1 산출물 체크리스트

```
research/
├── .venv/                                  (gitignore)
├── requirements.txt
├── requirements.lock
├── notebooks/
│   ├── 01_data_collection.ipynb
│   ├── 02_strategy_a_trend_daily.ipynb
│   ├── 03_strategy_b_mean_reversion_daily.ipynb
│   ├── 04_robustness_sensitivity.ipynb
│   ├── 05_4h_porting_experiment.ipynb
│   └── 06_week1_report.ipynb
├── data/                                   (gitignore)
│   ├── KRW-BTC_1d_frozen_20260412.parquet
│   ├── KRW-BTC_4h_frozen_20260412.parquet
│   └── data_hashes.txt
└── outputs/                                (gitignore)
    ├── strategy_a_daily.json
    ├── strategy_b_daily.json
    ├── strategy_4h_comparison.json
    ├── sensitivity_grid.csv
    ├── yearly_breakdown.csv
    └── week1_report.md
```

---

## 주의 사항 (감사관 발견 사항 인코딩)

### 코드 패턴 — 사용하지 말 것

- `ts_stop=...` (vectorbt 0.28.5에 없음. `sl_stop + sl_trail=True` 사용)
- `td_stop=pd.Timedelta('5d')` (없음. `entries.shift(N)`으로 사전 계산)
- `pf.sharpe_ratio` (괄호 없이 호출. 메서드이므로 `pf.sharpe_ratio()`)
- `pyupbit.get_ohlcv(to=...)` 후 타임존 처리 누락 (반드시 `tz_localize('Asia/Seoul').tz_convert('UTC')`)
- 100조합 그리드 sweep 후 "최고값" 보고 (사전 지정 파라미터만 Go/No-Go)

### 코드 패턴 — 사용해야 할 것

- `vbt.Portfolio.from_signals(..., sl_stop=0.08, sl_trail=False, freq='1D')`
- 시간 스톱: `time_exits = entries.shift(N).fillna(False).astype(bool)` 후 `exits | time_exits`
- ATR: `ta.volatility.AverageTrueRange(...).average_true_range()` (Wilder)
- pyupbit: `period=0.2` (rate limit 안전 마진)
- 데이터 freeze: 파일명에 날짜 + SHA256 해시 기록
- "Padysak 복제" 아니라 "**Padysak 영감을 받은**" 표기
