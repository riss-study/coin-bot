# Task W1-05 - 4시간봉 포팅 실험 (참고용)

## 메인 Task 메타데이터

| 항목 | 값 |
|------|-----|
| **메인 Task ID** | W1-05 |
| **Feature ID** | BT-002 |
| **주차** | Week 1 (Day 5) |
| **기간** | 0.5일 |
| **스토리 포인트** | 2 |
| **작업자** | Solo |
| **우선순위** | P2 (참고용) |
| **상태** | Done (2026-04-17) |
| **Can Parallel** | YES (W1-04와 별개) |
| **Blocks** | (없음, W1-06에 참고로만 입력) |
| **Blocked By** | W1-02, W1-03 |

## 개요

동일 전략(A, B)을 4시간봉에 포팅하여 일봉 결과와 비교. 중요: **참고용 only**, Week 1 Go/No-Go 기준 아님.

윈도우 환산:
- 일봉 200일 = 4시간봉 1200 bars (200 × 6)
- 일봉 20일 = 4시간봉 120 bars
- 일봉 10일 = 4시간봉 60 bars
- RSI(4) 4시간봉 = 4 bars × 4시간 = 16시간 lookback

**경고**: 4시간봉 1200 bar warmup → 첫 200일 (~50주) trade 없음 → 실 백테스트 시작 ~2021-07-20

## 현재 진행 상태

- 메인 Task 상태: Done
- 완료일: 2026-04-17
- Evidence: `.evidence/w1-05-4h-experiment.txt` (backtest-reviewer APPROVED)

| SubTask | 상태 | 메모 |
|---------|------|------|
| W1-05.1 | Done | 노트북 셋업 + 4h/1d 데이터 로드 + 해시 검증 |
| W1-05.2 | Done | Strategy A 4h: Sharpe 1.12, 20 trades |
| W1-05.3 | Done | Strategy B 4h: Sharpe -0.61, 207 trades (실패) |
| W1-05.4 | Done | 비교 표 + 해석 + JSON 저장 |
| W1-05.5 | Done | Evidence + review trace |

## SubTask 목록

### SubTask W1-05.1: 노트북 셋업

**작업자**: Solo
**예상 소요**: 0.05일

- [ ] `research/notebooks/05_4h_porting_experiment.ipynb`
- [ ] 4h Parquet 로드 (`KRW-BTC_4h_frozen_20260412.parquet`)
- [ ] 데이터 해시 검증

### SubTask W1-05.2: Strategy A 4h 백테스트

**작업자**: Solo
**예상 소요**: 0.15일

사전 지정 파라미터 (4h 환산):
```python
MA_PERIOD_4H = 1200       # 200일 × 6 bars
DONCHIAN_HIGH_4H = 120    # 20일 × 6
DONCHIAN_LOW_4H = 60      # 10일 × 6
VOL_AVG_PERIOD_4H = 120
VOL_MULT = 1.5
SL_PCT = 0.08
# 주: ATR은 Strategy A에서 사용 안 함 (W1-02와 동일, W1-04 참조)
```

- [ ] vectorbt 백테스트 (`freq='4h'`)
- [ ] **경고 출력**: 첫 1200 bar warmup으로 trade 없음
- [ ] 결과 저장

### SubTask W1-05.3: Strategy B 4h 백테스트

**작업자**: Solo
**예상 소요**: 0.1일

```python
MA_PERIOD_4H = 1200
RSI_PERIOD = 4            # 4 bars × 4h = 16h
RSI_BUY = 25
RSI_SELL = 50
TIME_STOP_BARS = 30       # 5일 × 6 bars = 30 bars
SL_PCT = 0.08
```

- [ ] entries.shift(30) 패턴 (5일 × 6 bars)
- [ ] vectorbt 백테스트 freq='4h'

### SubTask W1-05.4: 비교 표

**작업자**: Solo
**예상 소요**: 0.1일

- [ ] 일봉 vs 4시간봉 비교 표:

| 전략 | 타임프레임 | Sharpe | CAGR | MDD | 트레이드 수 |
|------|----------|--------|------|-----|-----------|
| A | 일봉 | X.XX | XX% | XX% | N |
| A | 4h | X.XX | XX% | XX% | N |
| B | 일봉 | X.XX | XX% | XX% | N |
| B | 4h | X.XX | XX% | XX% | N |

- [ ] 차이의 해석 (4h가 더 나쁘면 일봉 우위 확정, 더 좋으면 W2 walk-forward에서 재검증)
- [ ] `outputs/strategy_4h_comparison.json` 저장

### SubTask W1-05.5: Evidence + 리뷰

**작업자**: Solo + backtest-reviewer
**예상 소요**: 0.1일

- [ ] `.evidence/w1-05-4h-experiment.txt`
  - 비교 표 포함
  - "참고용, W1 Go/No-Go에 영향 없음" 명시
- [ ] backtest-reviewer 호출 (4h 윈도우 환산 정확성 중점)
- [ ] APPROVED 받음

## 인수 완료 조건 (Acceptance Criteria)

- [ ] 4h Parquet 데이터 로드 + 해시 검증
- [ ] **윈도우 환산 정확**: MA1200 (=200일), Donchian 120/60, 시간스톱 30 bars (=5일)
- [ ] freq='4h' 사용 (소문자, vectorbt 0.28.5 권장)
- [ ] vectorbt 크래시 없이 실행
- [ ] 일봉 vs 4h 비교 표 작성
- [ ] outputs/strategy_4h_comparison.json 생성
- [ ] **결과는 W1-06 리포트에 "참고용"으로만 포함**
- [ ] backtest-reviewer APPROVED

## 의존성 매트릭스

| From | To | 관계 |
|------|-----|------|
| W1-01 | W1-05 | 4h Parquet 데이터 |
| W1-02 | W1-05 | Strategy A 비교 기준 |
| W1-03 | W1-05 | Strategy B 비교 기준 |
| W1-05 | W1-06 | 참고 결과 입력 |

## 리스크 및 완화 전략

| 리스크 | 영향 | 완화 |
|--------|------|------|
| 4h 윈도우 환산 잘못 (MA200 → 200, not 1200) | High | 사전 지정 상수에 주석으로 환산 명시 |
| 1200 bar warmup으로 데이터 손실 | Known | 경고 출력, 백테스트 시작 시점 명시 |
| 4h가 일봉보다 좋아 보임 | Medium | walk-forward 미적용 상태이므로 신뢰 X, W2에서 재검증 |
| Go/No-Go에 4h 결과 사용 유혹 | High | 룰: 룰: "참고용 only" 강제 |

## 산출물 (Artifacts)

### 코드
- `research/notebooks/05_4h_porting_experiment.ipynb`

### 결과
- `research/outputs/strategy_4h_comparison.json`

### 검증
- `.evidence/w1-05-4h-experiment.txt`

### 테스트 시나리오

- **Happy**: 4h 결과가 일봉과 ±20% 이내 → 시장 시간프레임 견고성
- **Denial 1**: 4h가 일봉보다 훨씬 나쁨 → 일봉 우위 확정
- **Denial 2**: 4h가 일봉보다 훨씬 좋음 → W2 walk-forward 필수
- **Edge**: 1200 bar warmup으로 첫 50주 trade 없음 → 알려진 동작

## Commit

```
feat(plan): BT-002 4시간봉 포팅 실험 (참고용)

윈도우 환산:
- MA1200 (= 일봉 200일)
- Donchian 120/60
- 시간 스톱 30 bars (= 5일)

비교:
- Strategy A: 일봉 X.XX vs 4h Y.YY
- Strategy B: 일봉 X.XX vs 4h Y.YY

참고용, W1 Go/No-Go에 영향 없음.

Evidence: w1-05-4h-experiment.txt (APPROVED)
```

---

**이전 Task**: [W1-04 강건성 + 민감도](./w1-04-robustness.md)
**다음 Task**: [W1-06 Week 1 리포트 + Go/No-Go](./w1-06-week1-report.md)
