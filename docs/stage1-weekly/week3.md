# Stage 1 Week 3 — Walk-forward + DSR + 전략 채택 결정

> 상위 계획: [`../stage1-execution-plan.md`](../stage1-execution-plan.md) (EPIC 뷰)
> Task 상세 sub-plan: [`../stage1-subplans/`](../stage1-subplans/)

## 배경

W2-03 Go 결정 (2026-04-20, Option C = V_empirical 채택) → W3 진입. 2차 외부 감사관이 "v8과 cycle 1 #5 본질 구분 어려움" 인정 → **Week 3 결과가 W2-03 Go 결정의 retrospective 재판정**. Week 3 실패 시 Stage 1 킬 카운터 **+2 소급** 박제 (W2-03 v8 WARNING-4).

## 요약

- **기간**: 2026-04-21 ~ 약 Week 3 종료 (Day 1-7)
- **대상**: W2-03 Go cells 5개 (BTC_A/C/D + ETH_A/D) — 집합 고정, 사후 확장 금지
- **의무 (v8 WARNING-3 강제)**: V_empirical 일관 + floor 재도입 금지 + 임계값 변경 금지 + fold별 DSR 재산정

## Task 목록

- [ ] **W3-01. Walk-forward analysis** (Feature: BT-004) — v1 sub-plan 작성 중 (2026-04-21)
  - **What**: Anchored walk-forward 5 folds × 6개월 test. 5 cell × 5 fold = 25 조합. Fold별 Sharpe + DSR_z 산출. Go 이중 조건 (4+/5 fold pass AND 평균 pass).
  - **Must NOT**: V_reported floor 재도입 / 임계값 완화 / Go cells 집합 확장 / Fold 분할점 사후 조정 / Strategy 파라미터 재튜닝
  - Sub-plan: [`../stage1-subplans/w3-01-walk-forward.md`](../stage1-subplans/w3-01-walk-forward.md) v1
  - Depends: W2-03 Go 결정 (2026-04-20 완료)

- [ ] **W3-02. Deflated Sharpe + Monte Carlo + Bootstrap** (Feature: BT-006)
  - **What**: W3-01 Go 통과 cell들에 대한 DSR 재산정 (pooled V, fold-aware) + Bootstrap 신뢰구간 + Monte Carlo 검증
  - **사전 지정 임계값**: DSR_prob > 0.95 (표준). Bootstrap Sharpe 95% CI 하한 > 0.5
  - Sub-plan: W3-01 종료 후 작성
  - Depends: W3-01 Go

- [ ] **W3-03. 전략 채택 결정 + Stage 1 체크포인트 #1** (Feature: STR-FINAL-001)
  - **What**: W3-01 + W3-02 결과 통합 + 최종 전략 채택 + ensemble 여부 결정. Stage 1 체크포인트 #1 (Week 4 Freqtrade 이식 전 마지막 리서치 판단)
  - **Must NOT**: 결과 보고 파라미터 재조정 / Secondary 마킹 사후 포함
  - Sub-plan: W3-02 종료 후 작성
  - Depends: W3-02

## Week 3 진입 의무 (v8 박제 강제)

1. **V_empirical 일관 적용**: 각 fold별 sample variance 산출. 5-fold-aggregate V도 참고용 계산 가능
2. **Floor 재도입 금지**: v6 C-1 `V_reported=max(V_empirical, 1.0)` 복귀 X
3. **임계값 변경 금지**: Sharpe > 0.8 AND DSR_z > 0 고정
4. **Fold별 DSR 재산정 의무**
5. **W2-03 Go cells 집합 고정**: {BTC_A, BTC_C, BTC_D, ETH_A, ETH_D}. ETH_C 재포함 or Secondary 마킹 추가 = cherry-pick = cycle 3 강제
6. **Strategy 파라미터 재튜닝 금지**: W2-02 v5 박제값 그대로 사용
7. **실패 시 Stage 1 킬 카운터 +2 소급**: W2-03 Go 결정을 사후에 "실패"로 재분류 + 외부 감사 재수행 + 사용자 명시 결정

## Week 3 관련 박제 출처

- [`../decisions-final.md`](../decisions-final.md) L690+ "W2-03 In-sample grid Go 결정" (v8 WARNING-3/-4 박제)
- [`../candidate-pool.md`](../candidate-pool.md) v5 (Strategy A Active 전이 + Recall 시 의무)
- [`../stage1-subplans/w2-03-insample-grid.md`](../stage1-subplans/w2-03-insample-grid.md) v9 (vectorbt default year_freq 실측)

## 잔존 정정 Task (Week 3 관련)

- **PT-04** `year_freq='365 days'` 명시 호출 일괄 갱신 — W3-01 노트북부터 **선행 적용** (신규 노트북이므로 default 의존 방지). 기존 노트북 (W1-*, W2-03) 일괄 갱신은 W4-01 Freqtrade 이식 시점 (기존 박제)
- **PT-02** `.gitignore` vs sub-plan 박제 충돌 — W3-01 sub-plan 작성 시 data_hashes 경로 결정 (기존 박제)
