# Stage 1 Week 3~8 — Pending (진입 시점에 주차별 분할)

> 상위 계획: [`../stage1-execution-plan.md`](../stage1-execution-plan.md) (EPIC 뷰)
> Task 상세 sub-plan: [`../stage1-subplans/`](../stage1-subplans/) (직전 Task 완료 후 작성)

## 분리 정책

본 파일은 Week 3~8의 placeholder. 각 주차 진입 시점에 별도 파일로 분리 예정:
- `week3.md` (Week 3 walk-forward 진입 시)
- `week4.md` (Freqtrade 이식 진입 시)
- `week6.md` (페이퍼 트레이딩 시작 시)
- `week8.md` (Stage 1 게이트 평가 시)
- Week 5, 7은 인근 주차와 병합 또는 개별 분리 (진입 시 결정)

## Task 목록 (현재 TBD, 진입 시점에 상세화)

- [ ] **W3-01. Walk-forward analysis** (Feature: BT-004) — 원래 W2-01에서 이전
  - **상태**: Ready (진입 가능, 2026-04-20). W2-03 Go 결정 + PT-01 해소 후 선행 차단 해제.
  - **의무**: V_empirical 일관 + floor 재도입 금지 + 임계값 변경 금지 (v8 2차 감사 WARNING-3). 실패 시 Stage 1 킬 카운터 +2 소급 (WARNING-4)
  - Sub-plan 작성 시 본 파일을 `week3.md`로 분할

- [ ] **W3-02. Deflated Sharpe + Monte Carlo + Bootstrap** (Feature: BT-006) — 원래 W2-02에서 이전
- [ ] **W3-03. 전략 채택 결정 + Stage 1 체크포인트 #1** (Feature: STR-FINAL-001)
- [ ] **W4-01. Freqtrade 이식** (Feature: PAPER-001)
  - **선행/병행 필수**: PT-04 (`year_freq='365 days'` 명시 호출 일괄 갱신)
- [ ] **W4-02. Docker + TimescaleDB + 시크릿** (Feature: PAPER-002)
- [ ] **W6-01. 페이퍼 트레이딩 시작** (Feature: PAPER-003)
- [ ] **W8-01. Stage 1 게이트 평가** (Feature: GATE-001) ← **결정적 분기**

각 Task의 sub-plan은 직전 Task 종료 후 작성. Week 2 Go 받은 후 W3-01부터 순차 진입.
