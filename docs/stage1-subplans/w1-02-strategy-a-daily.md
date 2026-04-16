# Task W1-02 - Strategy A 일봉 백테스트 (추세 추종)

## 메인 Task 메타데이터

| 항목 | 값 |
|------|-----|
| **메인 Task ID** | W1-02 |
| **Feature ID** | STR-A-001 |
| **주차** | Week 1 (Day 2) |
| **기간** | 1일 |
| **스토리 포인트** | 3 |
| **작업자** | Solo |
| **우선순위** | P0 |
| **상태** | Done (v5, 2026-04-15) |
| **Can Parallel** | NO (W1-01 필수 선행) |
| **Blocks** | W1-04, W1-05, W1-06 |
| **Blocked By** | W1-01 |

## 개요

Padysak/Vojtko 영감 추세 추종 전략을 일봉으로 백테스트.
- 200일 MA 추세 필터 + Donchian(20/10) 브레이크아웃 + 거래량 1.5배 + 고정 8% 하드 스톱
- 사전 지정 파라미터만 사용
- vectorbt 0.28.5 검증된 API 사용 (sl_stop fraction, sl_trail boolean)
- ATR은 W1-04 강건성 분석용 참고 지표 (Week 2+에서 ATR 트레일링 검토)
- 목표: Sharpe > 0.8, MDD < 50%

## 현재 진행 상태

- 메인 Task 상태: Done
- 완료일: 2026-04-14
- Evidence: `.evidence/w1-02-strategy-a-daily.txt` (backtest-reviewer agent APPROVED)
- 결과: Sharpe 1.0353, MDD -22.45%, Trades 14, PF 2.956 (Go 기준 PASS, low-N caveat)

| SubTask | 상태 | 메모 |
|---------|------|------|
| W1-02.1 | Done | 노트북 셋업 + 데이터 해시 검증 + 데이터 로드 |
| W1-02.2 | Done | 지표 계산 (MA200, Donchian.shift(1), Volume.shift(1)) |
| W1-02.3 | Done | 진입/청산 신호 마스크 (warmup zero entries 검증) |
| W1-02.4 | Done | vectorbt Portfolio.from_signals (검증된 0.28.5 API) |
| W1-02.5 | Done | strategy_a_daily.json + equity PNG 저장 |
| W1-02.6 | Done | Evidence + agent review APPROVED |

## SubTask 목록

### SubTask W1-02.1: 노트북 셋업

**작업자**: Solo
**예상 소요**: 0.1일

- [ ] `research/notebooks/02_strategy_a_trend_daily.ipynb` 생성
- [ ] 첫 셀: 라이브러리 import (pandas, numpy, vectorbt, ta, json, hashlib)
- [ ] 두 번째 셀: 데이터 해시 계산 + 검증 (변수 보존 필수)
  ```python
  import hashlib
  PARQUET_PATH = '../data/KRW-BTC_1d_frozen_20260412.parquet'
  
  def sha256_file(path):
      h = hashlib.sha256()
      with open(path, 'rb') as f:
          for chunk in iter(lambda: f.read(65536), b''):
              h.update(chunk)
      return h.hexdigest()
  
  sha256_hash = sha256_file(PARQUET_PATH)  # 결과 JSON에 사용
  
  # data_hashes.txt와 매치 검증
  with open('../data/data_hashes.txt') as f:
      hashes = dict(line.strip().split(': ') for line in f if line.strip())
  expected = hashes[PARQUET_PATH.split('/')[-1].split(': ')[0] if False else 'KRW-BTC_1d_frozen_20260412.parquet']
  assert sha256_hash == expected, f"Data hash mismatch: {sha256_hash} != {expected}"
  ```
- [ ] 세 번째 셀: 데이터 로드
  - `df = pd.read_parquet(PARQUET_PATH)`
  - close, high, low, volume 추출

### SubTask W1-02.2: 지표 계산

**작업자**: Solo
**예상 소요**: 0.2일

사전 지정 파라미터 (상수 선언, 변경 금지):

```python
MA_PERIOD = 200
DONCHIAN_HIGH = 20
DONCHIAN_LOW = 10
VOL_AVG_PERIOD = 20
VOL_MULT = 1.5
SL_PCT = 0.08
# 주: ATR은 Week 1에서 사용 안 함 (참고용으로 W1-04 강건성 분석에서 계산).
# Week 2+에서 ATR 트레일링 도입 시 ATR_PERIOD = 14 사용 예정.
```

- [ ] MA200: `close.rolling(window=MA_PERIOD).mean()`
- [ ] Donchian high: `high.rolling(window=DONCHIAN_HIGH).max().shift(1)`
- [ ] Donchian low: `low.rolling(window=DONCHIAN_LOW).min().shift(1)` (`.shift(1)` 필수, 미래 정보 차단)
- [ ] 거래량 평균: `volume.rolling(window=VOL_AVG_PERIOD).mean().shift(1)` (`.shift(1)` 필수, 신호 바의 평균은 알 수 없음)

### SubTask W1-02.3: 진입/청산 신호

**작업자**: Solo
**예상 소요**: 0.1일

- [ ] 진입 마스크 (Boolean Series):
  ```python
  entries = (close > ma200) & (close > donchian_high) & (volume > vol_avg_shifted * VOL_MULT)
  # vol_avg_shifted는 .shift(1) 적용된 거래량 평균 (look-ahead 방지)
  ```
- [ ] 청산 마스크:
  ```python
  exits = close < donchian_low
  ```
- [ ] 신호 카운트 출력 (entries.sum(), exits.sum()) — sanity check

### SubTask W1-02.4: vectorbt 백테스트

**작업자**: Solo
**예상 소요**: 0.2일

- [ ] vectorbt Portfolio.from_signals 호출 (검증된 파라미터만):
  ```python
  import vectorbt as vbt
  pf = vbt.Portfolio.from_signals(
      close=close,
      entries=entries,
      exits=exits,
      sl_stop=SL_PCT,        # fraction (0.08 = 8%)
      sl_trail=False,         # 하드 스톱
      init_cash=1_000_000,
      fees=0.0005,
      slippage=0.0005,
      freq='1D',
  )
  ```
- [ ] `pf.stats()` 출력 (sanity check)
- [ ] 크래시 없이 실행 확인 (TypeError 등 없음)

### SubTask W1-02.5: 결과 저장

**작업자**: Solo
**예상 소요**: 0.1일

- [ ] 핵심 지표 추출 (모두 메서드 호출, 괄호 필수). ATR은 W1-02 미사용 (W1-04에서 도입), atr_period 필드 없음:
  ```python
  results = {
      'feature_id': 'STR-A-001',
      'task_id': 'W1-02',
      'data_hash': sha256_hash,
      'parameters': {
          'ma_period': MA_PERIOD,
          'donchian_high': DONCHIAN_HIGH,
          'donchian_low': DONCHIAN_LOW,
          'vol_avg_period': VOL_AVG_PERIOD,
          'vol_mult': VOL_MULT,
          'sl_pct': SL_PCT,
      },
      'metrics': {
          'sharpe': float(pf.sharpe_ratio()),
          'total_return': float(pf.total_return()),
          'max_drawdown': float(pf.max_drawdown()),
          'max_drawdown_duration_days': int(...),  # 추가
          'win_rate': float(pf.trades.win_rate()),
          'profit_factor': float(pf.trades.profit_factor()),
          'total_trades': int(pf.trades.count()),
      },
  }
  ```
- [ ] `outputs/strategy_a_daily.json` 저장
- [ ] equity curve 차트 저장 (참고용): `outputs/strategy_a_equity.png`

### SubTask W1-02.6: Evidence + 리뷰

**작업자**: Solo + backtest-reviewer
**예상 소요**: 0.1일

- [ ] `.evidence/w1-02-strategy-a-daily.txt` 작성 (6단 구조)
- [ ] backtest-reviewer 에이전트 호출
- [ ] BLOCKING 항목 모두 해결
- [ ] APPROVED 받음
- [ ] sub-plan 상태 → Done
- [ ] execution-plan status 표 업데이트

## 인수 완료 조건 (Acceptance Criteria)

- [ ] 사전 지정 파라미터가 상수로 명시 선언됨
- [ ] 데이터 해시 검증 통과
- [ ] vectorbt 크래시 없이 실행 (TypeError, AttributeError, NameError 없음)
- [ ] 진입 마스크에 정의 안 된 변수 (`entry_price`, `bars_held` 등) 참조 없음
- [ ] sl_stop fraction 형식 사용 (0.08, not 8)
- [ ] sl_trail boolean (True/False)
- [ ] freq='1D' 사용
- [ ] pf.sharpe_ratio() 메서드 호출 (괄호 필수)
- [ ] outputs/strategy_a_daily.json 생성
- [ ] backtest-reviewer 에이전트 APPROVED
- [ ] (목표 달성 여부와 무관하게) 결과 정확히 기록

**Week 1 Go 기준 (W1-06에서 평가, 여기선 기록만)**:
- Sharpe > 0.8
- MDD < 50%

## 의존성 매트릭스

| From | To | 관계 |
|------|-----|------|
| W1-01 | W1-02 | 일봉 Parquet 데이터 필요 |
| W1-02 | W1-04 | 강건성 분석 입력 |
| W1-02 | W1-05 | 4시간봉 비교 기준 |
| W1-02 | W1-06 | Week 1 리포트 입력 |

## 리스크 및 완화 전략

| 리스크 | 영향 | 완화 |
|--------|------|------|
| Sharpe < 0.8 | High | W1-06에서 No-Go 결정, 전략 패밀리 재검토 |
| vectorbt API 오용 | Medium | research/CLAUDE.md 룰 + backtest-reviewer 검증 |
| 거래 횟수 과소 (< 20) | Medium | 통계적 의미 부족 (실제 결과 14), W2 bootstrap CI에서 정량화 |
| MDD 1.3년 이상 underwater | High | Deepest DD가 still active 시 심리적/자금 압박. W1-06 Go 결정 시 명시 |
| Deepest vs longest DD 혼동 | Low | JSON에 두 metric 분리 저장 (deepest_drawdown, longest_drawdown) |
| 200 bar warmup으로 첫 200일 trade 없음 | Low | 알려진 동작, assert로 강제 |

## 산출물 (Artifacts)

### 코드
- `research/notebooks/02_strategy_a_trend_daily.ipynb`

### 결과
- `research/outputs/strategy_a_daily.json`
- `research/outputs/strategy_a_equity.png`

### 검증
- `.evidence/w1-02-strategy-a-daily.txt`

### 테스트 시나리오

- **Happy**: 사전 지정 파라미터 → Sharpe X.XX 기록 (목표 달성 여부 별개)
- **Edge**: 200 bar warmup 기간 (2021-01-01 ~ 2021-07-19) entries.sum() == 0 확인
- **Edge**: 거래량 필터 (1.5x 평균)로 인해 신호 일부 거부됨 확인
- **Denial (수동)**: 만약 ts_stop 사용하면 reviewer가 BLOCKING 발견 → 수정 후 재제출

## Commit

```
feat(plan): STR-A-001 Strategy A 일봉 백테스트 완료

사전 지정 파라미터:
- MA200, Donchian(20/10), Volume 1.5x
- vectorbt sl_stop=0.08 (하드 스톱)
- 수수료 0.0005, 슬리피지 0.0005

결과:
- Sharpe: X.XX (목표 > 0.8)
- MDD: XX.X% (목표 < 50%)
- Total Return: XX.X%
- 트레이드: N

Evidence: w1-02-strategy-a-daily.txt (APPROVED)
```

---

**이전 Task**: [W1-01 데이터 수집 + 환경 세팅](./w1-01-data-collection.md)
**다음 Task**: [W1-03 Strategy B 일봉 백테스트](./w1-03-strategy-b-daily.md)
