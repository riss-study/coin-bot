# Task W1-04 - 강건성 + 민감도 분석

## 메인 Task 메타데이터

| 항목 | 값 |
|------|-----|
| **메인 Task ID** | W1-04 |
| **Feature ID** | BT-001 |
| **주차** | Week 1 (Day 4) |
| **기간** | 1일 |
| **스토리 포인트** | 5 |
| **작업자** | Solo |
| **우선순위** | P0 |
| **상태** | Done (2026-04-16) |
| **Can Parallel** | NO |
| **Blocks** | W1-06 |
| **Blocked By** | W1-02, W1-03 |

## 개요

W1-02, W1-03 결과의 강건성을 두 측면에서 검증:
1. **연도별 분할**: 5개 연도(2021/2022/2023/2024/2025/2026Q1)별로 결과가 균등한가? 한 해가 전체를 지배하면 과적합 의심.
2. **파라미터 민감도**: 사전 지정 파라미터 주변에서 성과가 평탄(robust)한가, 뾰족(overfit)한가?

**중요**: 민감도 그리드의 최고값을 보고 X. **사전 지정 파라미터만 Go/No-Go 근거**. 그리드는 등고선 시각화로 평탄성 검증용.

## 현재 진행 상태

- 메인 Task 상태: Done
- 완료일: 2026-04-16
- Evidence: `.evidence/w1-04-robustness.txt` (backtest-reviewer APPROVED)

| SubTask | 상태 | 메모 |
|---------|------|------|
| W1-04.1 | Done | 노트북 셋업 + 함수화 + Sharpe 재현 assert |
| W1-04.2 | Done | 연도별 분할 (6년 x 2전략, domination check) |
| W1-04.3 | Done | 민감도 그리드 A (125조합, NaN 0) |
| W1-04.4 | Done | 민감도 그리드 B (125조합, NaN 0) |
| W1-04.5 | Done | Heatmap 2개 (sns.heatmap, pre-reg 빨간 테두리) |
| W1-04.6 | Done | Evidence + review trace 저장 |

## SubTask 목록

### SubTask W1-04.1: 노트북 셋업

**작업자**: Solo
**예상 소요**: 0.1일

- [ ] `research/notebooks/04_robustness_sensitivity.ipynb` 생성
- [ ] import + 데이터 해시 검증
- [ ] W1-02, W1-03의 노트북 코드 함수화 (재사용용). 모든 파라미터 명시:
  - `run_strategy_a(close, high, low, volume, ma_period, donchian_high, donchian_low, vol_avg_period, vol_mult, sl_pct, fees=0.0005, slippage=0.0005)`
  - `run_strategy_b(close, ma_period, rsi_period, rsi_buy, rsi_sell, time_stop_days, sl_pct, fees=0.0005, slippage=0.0005)`
  - 함수는 `(sharpe, total_return, max_drawdown, win_rate, profit_factor, total_trades)` dict 반환

### SubTask W1-04.2: 연도별 분할 분석

**작업자**: Solo
**예상 소요**: 0.2일

- [ ] Strategy A 사전 지정 파라미터로 백테스트
- [ ] Strategy B 사전 지정 파라미터로 백테스트
- [ ] 각 전략의 returns를 연도별 리샘플:
  ```python
  yearly_returns = pf.returns().resample('YS').apply(lambda x: (1+x).prod() - 1)
  yearly_sharpe = pf.returns().resample('YS').apply(
      lambda x: x.mean() / x.std() * np.sqrt(252) if x.std() > 0 else 0
  )
  yearly_mdd = pf.returns().resample('YS').apply(
      lambda x: ((1+x).cumprod() / (1+x).cumprod().cummax() - 1).min()
  )
  ```
- [ ] 표 작성 (5개 연도 × 3개 지표 × 2개 전략)
- [ ] **검증**: 한 해가 전체 수익의 >70% 차지하면 경고

### SubTask W1-04.3: Strategy A 민감도 그리드

**작업자**: Solo
**예상 소요**: 0.2일

```python
ma_grid = [100, 150, 200, 250, 300]
donchian_high_grid = [10, 15, 20, 30, 40]
donchian_low_grid = [5, 7, 10, 15, 20]
# 5 × 5 × 5 = 125 조합

VOL_AVG_PERIOD = 20  # 사전 지정 고정
VOL_MULT = 1.5
SL_PCT = 0.08

results_a = []
for ma in ma_grid:
    for dh in donchian_high_grid:
        for dl in donchian_low_grid:
            stats = run_strategy_a(
                close, high, low, volume,
                ma_period=ma, donchian_high=dh, donchian_low=dl,
                vol_avg_period=VOL_AVG_PERIOD, vol_mult=VOL_MULT, sl_pct=SL_PCT
            )
            results_a.append({'ma': ma, 'dh': dh, 'dl': dl, 'sharpe': stats['sharpe'], 'mdd': stats['mdd']})

df_a = pd.DataFrame(results_a)
df_a.to_csv('outputs/sensitivity_a.csv', index=False)
```

- [ ] 125 조합 백테스트 실행
- [ ] csv 저장
- [ ] **사전 지정 파라미터 위치 표시**: (200, 20, 10) 셀이 평탄 영역에 있는지 확인

### SubTask W1-04.4: Strategy B 민감도 그리드

**작업자**: Solo
**예상 소요**: 0.1일

```python
ma_grid = [100, 150, 200, 250, 300]
rsi_period_grid = [3, 4, 5, 7, 10]
rsi_buy_grid = [15, 20, 25, 30, 35]
# 5 × 5 × 5 = 125 조합

results_b = []
for ma in ma_grid:
    for rp in rsi_period_grid:
        for rb in rsi_buy_grid:
            stats = run_strategy_b(close, ma, rp, rb, 50, 5, 0.08)
            results_b.append({'ma': ma, 'rsi_p': rp, 'rsi_buy': rb, 'sharpe': stats['sharpe'], 'mdd': stats['mdd']})

df_b = pd.DataFrame(results_b)
df_b.to_csv('outputs/sensitivity_b.csv', index=False)
```

### SubTask W1-04.5: 등고선 시각화

**작업자**: Solo
**예상 소요**: 0.2일

- [ ] Strategy A: ma × donchian_high 등고선 (donchian_low 고정 = 10)
- [ ] Strategy B: ma × rsi_buy 등고선 (rsi_period 고정 = 4)
- [ ] 사전 지정 파라미터 위치를 X 마크로 표시
- [ ] 평탄(robust) vs 뾰족(overfit) 시각적 판단:
  - 평탄: 사전 지정 위치 주변 50% 영역의 Sharpe std < 0.3
  - 뾰족: 사전 지정 위치 주변 50% 영역에 Sharpe 차이 > 1.0
- [ ] 차트 저장: `outputs/sensitivity_a_contour.png`, `outputs/sensitivity_b_contour.png`

### SubTask W1-04.6: Evidence + 리뷰

**작업자**: Solo + backtest-reviewer
**예상 소요**: 0.2일

- [ ] `.evidence/w1-04-robustness.txt` 작성
  - 연도별 분할 결과 표
  - 각 전략의 사전 지정 파라미터가 평탄 영역인지 boolean 결과
  - "한 해 지배" 경고 유무
- [ ] backtest-reviewer 호출
- [ ] APPROVED 받음

## 인수 완료 조건 (Acceptance Criteria)

- [ ] 5개 연도 × 2개 전략 = 10셀 표 작성
- [ ] 한 해 지배(>70%) 경고 유무 명시
- [ ] 125 × 2 = 250 조합 민감도 그리드 실행
- [ ] sensitivity_a.csv, sensitivity_b.csv 생성
- [ ] 등고선 차트 2개 생성
- [ ] **사전 지정 파라미터가 평탄 영역에 위치 boolean 결과 명시**
- [ ] 그리드 결과는 절대 Go/No-Go 기준으로 사용 안 됨 (참고용 only)
- [ ] backtest-reviewer APPROVED

## 의존성 매트릭스

| From | To | 관계 |
|------|-----|------|
| W1-02 | W1-04 | Strategy A 백테스트 함수 재사용 |
| W1-03 | W1-04 | Strategy B 백테스트 함수 재사용 |
| W1-04 | W1-06 | 강건성 결과를 리포트에 포함 |

## 리스크 및 완화 전략

| 리스크 | 영향 | 완화 |
|--------|------|------|
| 사전 지정 파라미터가 뾰족 영역 (overfit) | High | W1-06에서 No-Go 결정 |
| 한 해가 전체 지배 | High | W1-06에서 No-Go |
| 그리드 실행 시간 과다 (250 조합) | Low | vectorbt는 빠름 (~1분 이내) |
| 그리드 결과 유혹 ("이 조합이 더 좋은데?") | High | 룰: "사전 지정만 Go/No-Go" 강제 |

## 산출물 (Artifacts)

### 코드
- `research/notebooks/04_robustness_sensitivity.ipynb`

### 결과
- `research/outputs/yearly_breakdown.csv`
- `research/outputs/sensitivity_a.csv`
- `research/outputs/sensitivity_b.csv`
- `research/outputs/sensitivity_a_contour.png`
- `research/outputs/sensitivity_b_contour.png`

### 검증
- `.evidence/w1-04-robustness.txt`

### 테스트 시나리오

- **Happy**: 사전 지정 파라미터가 평탄 영역 + 5개 연도 균등 → Strategy 견고함 입증
- **Denial 1**: 사전 지정이 뾰족 영역 → 과적합 의심, 사용자 보고
- **Denial 2**: 한 해 지배 (예: 2021 불장) → 시장 의존성 경고
- **Edge**: 그리드 일부 조합에서 vectorbt 크래시 → try/except 처리, 해당 조합 NaN

## Commit

```
feat(plan): BT-001 강건성 + 민감도 분석 완료

연도별 분할 (5개 연도):
- Strategy A: 2021 +XX%, 2022 -X%, 2023 +XX%, 2024 +XX%, 2025 +X%
- Strategy B: ...

민감도 그리드 (250 조합 참고용):
- A 사전 지정 파라미터 (200,20,10): 평탄 영역 PASS
- B 사전 지정 파라미터 (200,4,25): 평탄 영역 PASS

Evidence: w1-04-robustness.txt (APPROVED)
```

---

**이전 Task**: [W1-03 Strategy B 일봉](./w1-03-strategy-b-daily.md)
**다음 Task**: [W1-05 4시간봉 포팅 실험](./w1-05-4h-experiment.md)
