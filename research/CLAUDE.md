# research/

## Module Context

Week 1~3 복제 스프린트(원 논문 결과 재현 단기 프로젝트) 작업 공간. Jupyter + pandas + vectorbt 0.28.5 + pyupbit 0.2.34. W1-01 ~ W1-05 완료 (2026-04-17, 다섯 Task 모두 backtest-reviewer APPROVED). W1-06 (Week 1 리포트 + Go/No-Go) 대기.

## Tech Stack & Constraints

- Python 3.11+ / pandas >=2.0 / numpy / matplotlib / seaborn / pyarrow / jupyterlab
- vectorbt **0.28.5** (이 버전 기준 API 검증 완료)
- pyupbit **0.2.34** (이 버전 기준 API 검증 완료)
- ccxt (보조), ta (기술적 지표, Wilder 스무딩)

사용 금지: ta-lib (C 의존성), backtrader/zipline/backtesting.py (Freqtrade로 대체), LSTM/RL (Phase 10+), vectorbtpro (유료).

## Implementation Patterns

### 데이터 수집 (검증된 pyupbit 0.2.34)

```python
import pyupbit, time

def fetch_with_retry(ticker, interval, start, end, max_retries=5):
    for attempt in range(max_retries):
        df = pyupbit.get_ohlcv_from(
            ticker=ticker, interval=interval,
            fromDatetime=start, to=end, period=0.2,
        )
        if df is not None and not df.empty:
            return df
        time.sleep(2 ** attempt)
    raise RuntimeError(f"Failed after {max_retries} retries")

df = fetch_with_retry("KRW-BTC", "day", "2021-01-01", "2026-04-12")
assert df.index.tz is None  # pyupbit는 naive KST 반환
df.index = df.index.tz_localize('Asia/Seoul').tz_convert('UTC')
df.to_parquet('data/KRW-BTC_1d_frozen_20260412.parquet')
```

검증된 사실: `to=` 파라미터 존재, `interval` 옵션 `"day"`/`"minute240"`, period=0.1 = Upbit 한계 (10/s), 0.2 권장. 에러 시 `None` 반환 (예외 없음).

### 기술적 지표 (Wilder 스무딩)

```python
from ta.volatility import AverageTrueRange
from ta.momentum import RSIIndicator
atr = AverageTrueRange(high=high, low=low, close=close, window=14).average_true_range()
rsi = RSIIndicator(close=close, window=4).rsi()
```

직접 구현 금지 (수치 드리프트). `ta` 라이브러리는 Wilder 스무딩.

### vectorbt 백테스트 (검증된 0.28.5)

```python
import vectorbt as vbt
pf = vbt.Portfolio.from_signals(
    close=close, entries=entry_mask, exits=exit_mask,
    sl_stop=0.08,         # fraction (0.08 = 8%)
    sl_trail=False,       # True면 트레일링 (별도 ts_stop 없음)
    init_cash=1_000_000, fees=0.0005, slippage=0.0005, freq='1D',
)
sharpe = pf.sharpe_ratio()       # 메서드 호출 (괄호 필수)
total_return = pf.total_return()
```

### 시간 스톱 (vectorbt 0.28.5에 td_stop 없음)

```python
# entries.shift(N)을 추가 exit으로 OR
time_exits = entries.shift(5).fillna(False).astype(bool)
exits_combined = exit_mask | time_exits
```

### 앙상블 (Week 2+, cash_sharing 패턴)

```python
import pandas as pd
entries = pd.concat({'A': entries_A, 'B': entries_B}, axis=1)
exits   = pd.concat({'A': exits_A, 'B': exits_B}, axis=1)
close2  = pd.concat({'A': close, 'B': close}, axis=1)
pf = vbt.Portfolio.from_signals(
    close=close2, entries=entries, exits=exits,
    sl_stop=0.08, size=0.5, size_type='percent',
    group_by=True, cash_sharing=True,   # 단일 현금 풀, 자본 이중계산 방지
    init_cash=1_000_000, fees=0.0005, freq='1D',
)
```

## Testing Strategy

Week 1은 노트북 단계, 단위 테스트 비중 낮음. 다음만 보장:

- 데이터 무결성: 갭 < 0.1%, SHA256 해시 검증
- 지표 sanity: 상수 입력 → RSI ≈ NaN/50, ATR ≈ 0
- Reproducibility: 동일 노트북 두 번 실행 → 동일 결과
- API 검증: vectorbt/pyupbit 호출 시 TypeError 없음

Week 2부터 `pytest` 단위 테스트 도입.

## Local Golden Rules

### Do's

- 데이터 수집 직후 `assert df.index.tz is None` → `tz_localize('Asia/Seoul').tz_convert('UTC')`.
- 파일명에 freeze 날짜 포함 (`KRW-BTC_1d_frozen_20260412.parquet`).
- `data/data_hashes.txt`에 SHA256 기록.
- 사전 지정 파라미터로만 Go/No-Go 평가. 민감도 그리드는 참고용.
- ATR/RSI는 `ta` 라이브러리 사용 (Wilder).
- 손절: `sl_stop` (fraction) + `sl_trail` (boolean).
- 시간 스톱: `entries.shift(N).fillna(False).astype(bool)` 사전 계산.
- pyupbit `period=0.2` (rate limit 안전 마진).
- 외부 라이브러리 신규 사용 시 공식 docs/소스 직접 확인.
- 노트북 첫 셀에 데이터 해시 검증 코드.
- 시간프레임 변경 시 윈도우 수도 비례 (일봉 200 = 4h 1200).

### Don'ts

- vectorbt에 `ts_stop`, `td_stop`, `max_duration`, `time_stop`, `dt_stop` 사용 금지 (0.28.5 무료 버전에 없음, 검증됨).
- vectorbt Boolean exit mask에 `entry_price`, `bars_held` 미정의 변수 참조 금지 (NameError).
- `pf.sharpe_ratio` 괄호 없이 사용 금지. 메서드: `pf.sharpe_ratio()`.
- "MA200"이라 쓰면서 윈도우 ≠ 200 금지. 일봉=200, 4h=1200.
- 캔들 데이터 후 타임존 처리 누락 금지 (9시간 silent 오프셋).
- 100조합 sweep 후 "최고값" 보고 금지 (data snooping).
- 노트북 outputs/data를 git 커밋 금지.
- 직접 구현 RSI/ATR/MACD 금지.
- 데이터 freeze 안 한 상태로 결과 보고 금지.
- 앙상블(Strategy C) Week 1 구현 금지 (Week 2로 이동, decisions-final Part 11).
- "Padysak 복제" 금지. "Padysak 영감을 받은" 표기.
- 4시간봉을 Week 1 Go/No-Go 기준으로 사용 금지 (일봉이 기준).
- pyupbit None 반환 가능성 무시 금지 (재시도 wrapper 필수).
- 외부 라이브러리 API 추측으로 코드 작성 금지 (감사 발견 사례).

## Backtest Rigor

### Go 기준 (사전 지정 파라미터, 일봉 기반)

- Strategy A 일봉 Sharpe > 0.8 (수수료 0.1% 왕복 + 슬리피지 0.05% 포함)
- Strategy B 일봉 Sharpe > 0.5
- MDD < 50% (BTC 자체 75% drawdown 감안)
- 5개 연도 중 최소 2개 양수 수익
- 4시간봉은 참고용, Go/No-Go 기준 아님

### 데이터 (frozen)

- 기간: 2021-01-01 ~ 2026-04-12
- 페어: KRW-BTC (Week 1) → 알트 확장 (Week 2+)
- 해상도: 일봉 + 4시간봉 (Week 1은 일봉 우선)

## Notebook Conventions

- 파일명 prefix: `01_`, `02_`, ...
- 첫 셀: import + 데이터 해시 검증
- 마지막 셀: 결과 저장 (`outputs/*.json`)
- 한국어 주석, .ipynb는 출력 포함하여 git 커밋

## References

- `../CLAUDE.md` — 프로젝트 전체 규칙
- `../docs/decisions-final.md` — 모든 결정사항
- `../docs/week1-plan.md` — Week 1 일별 작업
- `../docs/glossary.md` — 용어 풀이
- `../docs/architecture.md` — 시스템 설계
