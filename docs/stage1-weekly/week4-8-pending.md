# Stage 1 Week 4~8 — Pending (진입 시점에 주차별 분할)

> 상위 계획: [`../stage1-execution-plan.md`](../stage1-execution-plan.md) (EPIC 뷰)
> Task 상세 sub-plan: [`../stage1-subplans/`](../stage1-subplans/) (직전 Task 완료 후 작성)
> Week 3 진입 완료 (2026-04-21): [`week3.md`](./week3.md) 참조

## 분리 정책

본 파일은 Week 4~8의 placeholder. 각 주차 진입 시점에 별도 파일로 분리 예정:
- `week4.md` (Freqtrade 이식 진입 시)
- `week6.md` (페이퍼 트레이딩 시작 시)
- `week8.md` (Stage 1 게이트 평가 시)
- Week 5, 7은 인근 주차와 병합 또는 개별 분리 (진입 시 결정)

## Task 목록 (현재 TBD, 진입 시점에 상세화)

- [ ] **W4-01. Freqtrade 이식** (Feature: PAPER-001)
  - **선행/병행 필수**: PT-04 (`year_freq='365 days'` 명시 호출 일괄 갱신)
- [ ] **W4-02. Docker + TimescaleDB + 시크릿** (Feature: PAPER-002)
- [ ] **W6-01. 페이퍼 트레이딩 시작** (Feature: PAPER-003)
- [ ] **W8-01. Stage 1 게이트 평가** (Feature: GATE-001) ← **결정적 분기**

각 Task의 sub-plan은 직전 Task 종료 후 작성. Week 3 Go 받은 후 W4-01부터 순차 진입.
