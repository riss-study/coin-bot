# Stage 1 Week 3 — Walk-forward No-Go + 학습 모드 전환 (완료, 2026-04-22)

> 상위 계획: [`../stage1-execution-plan.md`](../stage1-execution-plan.md) (EPIC 뷰)
> Task 상세 sub-plan: [`../stage1-subplans/`](../stage1-subplans/)

## 최종 결과 (2026-04-22)

**No-Go + Stage 1 학습 모드 전환** (사용자 옵션 C 명시 채택 "3").

- **W3-01 자동 결과**: is_go=False, go_cells=[] (0/5 Go cell)
- **사용자 결정**: 옵션 C (감사관 추천) = 프레임 A+B 둘 다 공식 인정 + Stage 1 학습 모드
- **Stage 1 킬 카운터**: +2 소급 가산 → 총 +3 (킬 조건 충족)
- **W3-02 / W3-03 / W4~W8 전부 Cancelled** (Stage 1 종결)

상세: [`../decisions-final.md`](../decisions-final.md) "W3-01 Walk-forward No-Go 결정 + 프레임 C 학습 모드 전환" 섹션 참조.

## 배경

W2-03 Go 결정 (2026-04-20, Option C = V_empirical 채택) → W3 진입. 2차 외부 감사관이 "v8과 cycle 1 #5 본질 구분 어려움" 인정 → **Week 3 결과가 W2-03 Go 결정의 retrospective 재판정**. Week 3 실패 시 Stage 1 킬 카운터 **+2 소급** 박제 (W2-03 v8 WARNING-4).

## 요약

- **기간**: 2026-04-21 ~ 2026-04-22 (Day 1-2)
- **대상**: W2-03 Go cells 5개 (BTC_A/C/D + ETH_A/D) — 집합 고정, 사후 확장 금지
- **의무 (v8 WARNING-3 강제)**: V_empirical 일관 + floor 재도입 금지 + 임계값 변경 금지 + fold별 DSR 재산정

## Task 목록

- [x] **W3-01. Walk-forward analysis** (Feature: BT-004) — **Done No-Go (2026-04-22, 사용자 옵션 C 채택)**
  - **What**: Anchored walk-forward 5 folds × 6개월 test. 5 cell × 5 fold = 25 조합. Fold별 Sharpe + DSR_z 산출. 옵션 A (5/5 stability + 평균 pass) 사용자 직접 선택 "2"
  - **자동 결과**: is_go=False (0/5). 14/25 fold N/A (56%, min_trade_count=2 필터)
  - **외부 감사 1차** (CHANGES REQUIRED, WARNING 8 + NIT 7): v2 반영 완료
  - **외부 감사 2차** (APPROVED with follow-up, WARNING 3 + NIT 2): v3 반영 완료. 프레임 A 60% / B 40% 정직 판정 + 감사관 신규 C 프레임 추천
  - **사용자 최종 결정**: 옵션 C "3" (프레임 A+B 둘 다 공식 인정 + Stage 1 학습 모드)
  - Sub-plan: [`../stage1-subplans/w3-01-walk-forward.md`](../stage1-subplans/w3-01-walk-forward.md) v3

- [ ] ~~**W3-02. Deflated Sharpe + Monte Carlo + Bootstrap**~~ **Cancelled (Stage 1 학습 모드)**
  - W3-01 No-Go 종료. DSR 재산정 / Bootstrap / Monte Carlo 미진행
  - 학습 자료 보존: W3-01 JSON + 리포트 + evidence git 유지

- [ ] ~~**W3-03. 전략 채택 결정 + Stage 1 체크포인트 #1**~~ **Cancelled (Stage 1 학습 모드)**
  - 전략 채택 결정 미진행. Strategy A/C/D 전부 Retained (학습 가치 보존)

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
