# 실행계획 → 구현 → 검증 루프 (food-supply 추출)

> food-supply의 핵심은 **3종 문서 + 4단계 루프** 입니다.
> 디렉토리 구조나 도구가 아니라, 작업이 실제로 흘러가는 방식이 핵심.

---

## 핵심: 3종 문서 + 4단계 루프

### 3종 문서

```
1. 실행 계획 (Execution Plan)        — 1개, EPIC 뷰, "전체 그림"
       │
       ├─ Task 01 ──┐
       ├─ Task 02 ──┤
       ├─ Task 03 ──┤
       │   ...      │
       └─ Task 11 ──┘
                    │
                    ▼
2. 서브플랜 (Sub-plan)                — Task당 1개, "어떻게 할 건가"
                    │
                    ▼
3. Evidence 파일 (Evidence)           — Task당 1개, "어떻게 끝났나" (서명)
```

### 4단계 루프 (Task 단위)

```
[1] 서브플랜 읽기   →   [2] 구현 (vertical slice)   →   [3] 검증 + Evidence   →   [4] 다음 Task로
       ↑                                                        │
       └────────  Code Review APPROVED 받기 전까진 못 넘어감  ──┘
```

---

## 문서 1: 실행 계획서 (Execution Plan)

**역할**: 전체 Phase의 spine. 어떤 Task가 있고, 어떤 순서로 가는지.

### 실제 food-supply 구조 (요약)

```markdown
# Phase 1 실행 계획서

## 요약
> 산출물: ...
> 난이도: Large
> 병렬화: YES
> 크리티컬 패스: 1 -> 2/3/4 -> 5/6/7 -> 8/9/10 -> 11

## 배경 / 작업 목표 / 필수 포함 / 포함 금지

## 검증 전략
ZERO HUMAN INTERVENTION - 모든 검증은 agent가 실행 가능

## 실행 전략
### 병렬 참고 그룹
- Group A: foundation
- Group B: auth + 검증
- Group C: discovery + lifecycle
...

### 현재 Task 상태
| Task | 상태 | 상세 문서 |
|------|------|-----------|
| 01 | 🟢 Done | ./phase1-subplans/phase1-task-01-*.md |
| 02 | 🟢 Done | ... |
| 04 | 🟡 Partial | ... |
...

### 의존성 매트릭스
| Task | Depends On | Enables |
| 1 | none | 2-11 |
| 2 | 1 | 3,4,6,7,8 |
| 8 | 1,6,7 | 9,11 |

## 작업 목록
> Implementation + Test + Docs sync = ONE task. Never separate.

- [ ] 1. Task 01 - Foundation
  **What to do**: ...
  **Must NOT do**: ...
  **Parallelization**: Can Parallel: NO | Group A | Blocks: 2-11 | Blocked By: none
  **Acceptance Criteria**:
  - [ ] 기준 1
  - [ ] 기준 2
  **QA Scenarios**:
  ```text
  Scenario: Foundation readiness
    Tool: Bash
    Steps: ...
    Expected: ...
    Evidence: .sisyphus/evidence/task-1-foundation.txt
  ```
  **Commit**: YES | Message: `chore(plan): foundation 정렬`

- [ ] 2. Task 02 - Auth
  **What to do**: ...
  ...

## QA / Evidence Rules
- 모든 slice는 happy path와 denial path를 가진다
- backend는 command/query/projection 필요 요소 포함
- frontend는 화면과 state visibility 규칙 포함
- Evidence 경로: .sisyphus/evidence/task-{N}-{slug}.{ext}

## 최종 검증 그룹 (4 parallel agents, ALL must APPROVE)
- [ ] F1. Plan Compliance Audit
- [ ] F2. Runtime/Architecture Safety Review
- [ ] F3. Slice Reality Check
- [ ] F4. Scope Fidelity Check

## 커밋 전략
- Task 01은 foundation 별도 커밋
- 각 slice는 vertical commit (BE+FE+test+docs 한 묶음)
- 커밋 메시지: prefix: 한글 설명
```

### 핵심 설계 원칙

1. **"Implementation + Test + Docs sync = ONE task"** — 절대 분리 금지
2. **상태 표** 맨 위에 (🟢 Done / 🟡 Partial / 🔴 Blocked)
3. **의존성 매트릭스** 명시 (Depends On / Enables)
4. **각 Task에 What to do + Must NOT do + Acceptance + QA Scenario + Commit 메시지** 다 포함
5. **Evidence 경로**가 Task 정의에 직접 적힘
6. **최종 검증 그룹**: 4개 병렬 감사관이 모두 APPROVE 해야 Phase 종료

---

## 문서 2: 서브플랜 (Task Sub-plan)

**역할**: Task 1개를 어떻게 분해해서 구현할지의 상세 가이드.

### 실제 food-supply Task 08 구조

```markdown
# Task 08 - Quote Lifecycle and Comparison

## 메인 Task 메타데이터
| 항목 | 값 |
|------|-----|
| 메인 Task ID | 8 |
| 병렬 그룹 | Group C |
| 기간 | 3-4일 |
| 스토리 포인트 | 13 |
| 작업자 | Full-stack |
| 우선순위 | P1 |
| 상태 | 🟢 Done |
| Can Parallel | YES |
| Blocks | Task 9, 11 |
| Blocked By | Task 1, 6, 7 |

## 개요
{1-paragraph 핵심 요약}

## 현재 진행 상태
- 메인 Task 상태: 🟢 Done
- 메모: {언제 어디까지 검증했는지}

| SubTask | 상태 | 메모 |
| 8.1 | 🟢 Done | Quote aggregate, 상태 전이, versioning |
| 8.2 | 🟢 Done | submit/update API |
| 8.3 | 🟢 Done | withdraw/select/decline API |
...

## SubTask 목록

### 🟢 SubTask 8.1: 견적 도메인 모델
**작업자**: Backend
**예상 소요**: 0.5일

- [x] Quote aggregate
  - [x] Fields: requestId, supplierProfileId, ...
  - [x] State machine: submitted -> (selected | withdrawn | declined)
  - [x] Versioning
- [x] Command handlers
  - [x] SubmitQuote - 중복 제출 guard
  - [x] UpdateQuote (submitted 상태에서만)
  ...
- [x] Invariants
  - [x] 동일 (request, supplier)당 active quote 1개만
  ...

### 🟢 SubTask 8.2: 견적 제출 및 수정 API
... (각 SubTask마다 동일 형식)

## 인수 완료 조건 (Acceptance Criteria)
- [x] 승인된 공급자만 견적 제출 가능 (4037)
- [x] 동일 의뢰에 중복 견적 제출 불가 (4095)
- [x] closed/cancelled 의뢰에는 견적 제출 불가
... (testable한 항목만)

## 병렬 작업 구조
\```
Backend:  [8.1 Domain] -> [8.2 Submit/Update API] -> [8.3 State APIs]
                              -> [8.4 List API] + [8.5 Projection]

Frontend: [8.6 Submit UI] + [8.7 Compare/Select UI]
\```

## 의존성 매트릭스
| From | To | 관계 |
| Task 1 | Task 8 | Foundation 필요 |
| Task 6 | Task 8 | Approved supplier가 quote 제출 |
| Task 8 | Task 9 | Quote 제출 시 thread 생성 |

## 리스크 및 완화 전략
| 리스크 | 영향 | 완화 전략 |
| 중복 견적 제출 | High | DB unique constraint + application guard |
| 선택 시 동시성 | Medium | Transaction 원자 처리 |

## 산출물 (Artifacts)

### Backend
- command-domain-quote: Quote aggregate
- query-model-quote: Quote list/comparison views
- api-server: Quote controller
- Projection: quote state change events
- Evidence: .sisyphus/evidence/task-8-quote-lifecycle.txt

### Frontend
- apps/main-site: Quote submit page, Quote comparison page
- packages/ui: Quote card, comparison table

### 테스트 시나리오
- Happy path: submit -> compare -> select -> request closed
- Update path: submit -> update -> withdraw
- Denial: duplicate quote, unapproved supplier
- Selection cascade: select one -> others auto-declined

## Commit
\```
feat(plan): QUOTE-001 실행 계획 고정

- Quote aggregate with state machine and versioning
- Submit/Update/Withdraw/Select/Decline APIs
- Duplicate prevention and permission guards
...
\```

---
**이전 Task**: [Task 7: Request Lifecycle](./phase1-task-07-request-lifecycle.md)
**다음 Task**: [Task 9: Message Threads](./phase1-task-09-message-threads.md)
```

### 핵심 설계 원칙

1. **메타데이터 표** 맨 위 (ID, 기간, 우선순위, Blocks/Blocked By)
2. **현재 상태 표** (각 SubTask의 진행도)
3. **SubTask마다 작업자 + 예상 소요 + 체크박스**
4. **Acceptance Criteria 별도 섹션** (testable한 것만)
5. **병렬 작업 구조 다이어그램** (BE/FE 의존성)
6. **리스크 표** (확률 + 완화)
7. **산출물 명시** (BE 모듈, FE 컴포넌트, Evidence 경로)
8. **테스트 시나리오** (happy + denial + edge)
9. **Commit 메시지 템플릿** 미리 작성
10. **이전/다음 Task 링크** (탐색 편의)

---

## 문서 3: Evidence 파일

**역할**: Task 종료 시 "이걸 확실히 끝냈다" 서명. 다음 Task가 이 결과를 신뢰할 근거.

### 실제 food-supply Task 08 Evidence

```text
Task 08 Quote Lifecycle and Comparison - Evidence
=================================================
Date: 2026-03-24
Status: complete, code review approved

Verification Summary
--------------------
1. Backend quote lifecycle
   - POST /api/requests/{requestId}/quotes submits a quote and returns quoteId, threadId, createdAt
   - GET /api/requests/{requestId}/quotes returns comparison rows with pagination
   - PATCH /api/quotes/{quoteId} updates and increments version
   - POST /api/quotes/{quoteId}/withdraw transitions submitted -> withdrawn
   - POST /api/quotes/{quoteId}/select transitions to selected, closes request
   - POST /api/quotes/{quoteId}/decline transitions to declined
   - GET /api/supplier/quotes returns supplier's submitted list

2. Domain / projection / thread linkage
   - relational write tables added: quote, message_thread
   - QuoteCommandService enforces duplicate guard
   - ThreadCommandService creates thread on first quote submit
   - QuoteProjectionService maintains quote_comparison_view
   - request close projection synchronized when quote selected

3. Frontend supplier flow
   - quote submission page: 단가, MOQ, 납기, 샘플 비용
   - supplier quote list: submitted vs finished grouping

4. Frontend requester flow
   - quote comparison page: 필터, 정렬, dialog 기반 detail, select 확인

5. Automated verification
   - Backend: ./gradlew :command-domain-quote:test :command-domain-thread:test -> PASS
   - Backend: ./gradlew build -> PASS
   - Frontend: yarn workspace @fsm/main-site test ... -> PASS
   - Frontend: yarn workspace @fsm/main-site type-check -> PASS
   - Frontend: yarn workspace @fsm/main-site build -> PASS

6. Code review result
   - Task 08 review result: APPROVED FOR PROGRESSION TO TASK 09
   - No blocking mismatches against subplan, API spec, or data model

Notes
-----
- Task 08 creates write-side thread record needed at quote submission;
  optional initial message creation remains Task 09 scope.
- Quote comparison uses implemented sort fields for requester ordering.
```

### Evidence 파일의 6단 구조

| 섹션 | 내용 |
|------|------|
| 1. Backend (또는 핵심 기능) | 각 API/기능을 한 줄로 서술, 어떤 endpoint가 무엇을 하는지 |
| 2. Domain / projection 연동 | 내부 구조 변화, 엔티티 추가, 이벤트 연결 |
| 3. Frontend (해당되면) | 사용자 흐름별 UI 구현 |
| 4. (추가 흐름) | 다른 사용자 역할의 흐름 |
| 5. Automated verification | 실제 명령 + PASS/FAIL |
| 6. Code review result | APPROVED / REQUEST CHANGES + 차단 사항 유무 |
| Notes | 미해결, 다음 Task에 분리된 범위, 가정 |

### 핵심 설계 원칙

1. **Date + Status 헤더** (complete / partial / blocked)
2. **번호 매긴 검증 요약** (1, 2, 3...)
3. **각 항목은 "무엇이 작동함"을 한 문장으로**
4. **Automated verification 섹션은 실제 명령 + 결과** (PASS/FAIL)
5. **Code review 명시적 결과** ("APPROVED FOR PROGRESSION TO TASK N+1")
6. **Notes에 한계/분리된 범위 기록** (다음 Task가 알아야 할 것)
7. **txt 파일** (마크다운 아님 — 명확성 우선)

---

## 4단계 루프 작동 방식

### 단계 1: 서브플랜 읽기

```
실행 계획 status 표 보고 → 다음 Task 결정 → Sub-plan 열기 → 메타데이터/SubTask/Acceptance 확인
```

**Output**: 무엇을 만들지, 어떤 기준을 통과해야 하는지, 어떤 의존성이 있는지 명확

### 단계 2: 구현 (Vertical Slice)

```
SubTask 1.1 → 1.2 → 1.3 → ... → 모든 체크박스 채움
            ↓
        BE + FE + Test + Docs 동시에 진행 (한 묶음)
```

**Rules**:
- "Implementation + Test + Docs sync = ONE task"
- BE만 끝내고 FE 미루는 거 금지
- Test 없이 구현 끝났다고 하지 않음
- Sub-plan의 체크박스를 실제로 체크

### 단계 3: 검증 + Evidence 작성

```
Acceptance Criteria 모두 통과 → 자동 검증 명령 실행 → Code Review 호출 → Evidence 파일 작성
```

**Code Review가 핵심**:
- spec 정합성 검증 (단순 스타일 ≠ spec)
- BLOCKING / WARNING / NIT 등급
- APPROVED 받기 전까진 다음 Task 못 시작

**Evidence 파일은 "서명"**:
- 다음 Task가 이걸 신뢰할 근거
- "테스트 통과" 가 아닌 "Acceptance 충족 + 코드 리뷰 통과"

### 단계 4: 다음 Task로

```
Sub-plan 메타데이터 상태 → 🟢 Done
실행 계획 status 표 → 🟢 Done 업데이트
Commit (vertical commit, sub-plan 메시지 템플릿 사용)
다음 Task의 Sub-plan 열기
```

---

## coin-bot 적용 (Week 1만)

### Week 1을 4단계 루프로 재구성

#### Execution Plan: `docs/stage1-execution-plan.md` (1개)

```markdown
# Stage 1 실행 계획서 (Week 1~8)

## 요약
> 산출물: 노트북 백테스트 + Freqtrade 페이퍼 트레이딩
> 난이도: Medium
> 병렬화: NO (sequential, 학습 우선)
> 크리티컬 패스: 데이터 → A/B 백테스트 → 검증 → 페이퍼

## 현재 Task 상태
| Task | 상태 | 상세 문서 |
|------|------|-----------|
| W1-01 | 🔴 Pending | ./stage1-subplans/w1-01-data-collection.md |
| W1-02 | 🔴 Pending | ./stage1-subplans/w1-02-strategy-a.md |
| W1-03 | 🔴 Pending | ./stage1-subplans/w1-03-strategy-b.md |
| W1-04 | 🔴 Pending | ./stage1-subplans/w1-04-robustness.md |
| W1-05 | 🔴 Pending | ./stage1-subplans/w1-05-4h-experiment.md |
| W1-06 | 🔴 Pending | ./stage1-subplans/w1-06-week1-report.md |
| W2-01 | 🔴 Pending | ./stage1-subplans/w2-01-walk-forward.md |
| W2-02 | 🔴 Pending | ./stage1-subplans/w2-02-dsr.md |
| W2-03 | 🔴 Pending | ./stage1-subplans/w2-03-alt-extension.md |
| W3-01 | 🔴 Pending | ./stage1-subplans/w3-01-strategy-adoption.md |
| W4-01 | 🔴 Pending | ./stage1-subplans/w4-01-freqtrade-port.md |
| W4-02 | 🔴 Pending | ./stage1-subplans/w4-02-docker-setup.md |
| W6-01 | 🔴 Pending | ./stage1-subplans/w6-01-paper-trading.md |
| W8-01 | 🔴 Pending | ./stage1-subplans/w8-01-stage1-gate.md |

## 의존성 매트릭스
| Task | Depends On | Enables |
| W1-01 | none | W1-02, W1-03 |
| W1-02 | W1-01 | W1-04, W1-06 |
| W1-03 | W1-01 | W1-04, W1-06 |
| W1-04 | W1-02, W1-03 | W1-06 |
| W1-05 | W1-02, W1-03 | (참고용) |
| W1-06 | W1-02..W1-05 | W2-* |
...

## 작업 목록
- [ ] W1-01. Task W1-01 - 데이터 수집 + 환경 세팅
  **What**: pyupbit로 KRW-BTC 일봉/4h 5년치 다운로드, Parquet freeze, SHA256 기록
  **Must NOT**: 4시간봉을 Go/No-Go 기준으로 사용 금지
  **Acceptance**:
  - [ ] 일봉 ~1930개, 4h ~11600개 수집
  - [ ] 갭 < 0.1%
  - [ ] SHA256 해시 기록
  - [ ] tz_localize KST → UTC
  **QA Scenario**:
    Tool: Jupyter notebook
    Steps: 01_data_collection.ipynb 실행
    Expected: data/*.parquet + data/data_hashes.txt 생성
    Evidence: .sisyphus/evidence/w1-01-data-collection.txt
  **Commit**: feat(plan): DATA-001 Week 1 데이터 수집 완료

- [ ] W1-02. Task W1-02 - Strategy A 일봉 백테스트
  **What**: 200MA + Donchian(20/10) + ATR 손절, vectorbt 백테스트
  **Must NOT**: ts_stop, td_stop 사용 금지, 데이터 스누핑 금지
  **Acceptance**:
  - [ ] 사전 지정 파라미터로 백테스트 완료
  - [ ] Sharpe > 0.8 (수수료 포함)
  - [ ] MDD < 50%
  - [ ] outputs/strategy_a_daily.json 생성
  **Commit**: feat(plan): STR-A-001 Strategy A 일봉 백테스트
...
```

#### Sub-plan 예시: `docs/stage1-subplans/w1-02-strategy-a.md`

```markdown
# Task W1-02 - Strategy A 일봉 백테스트

## 메인 Task 메타데이터
| 항목 | 값 |
| Task ID | W1-02 |
| 그룹 | Week 1 (리서치) |
| 기간 | 1일 |
| 스토리 포인트 | 3 |
| 작업자 | Solo |
| 우선순위 | P0 |
| 상태 | 🔴 Pending |
| Can Parallel | NO (W1-01 필수 선행) |
| Blocks | W1-04, W1-06 |
| Blocked By | W1-01 |

## 개요
Padysak/Vojtko 영감 추세 추종 전략(200MA + Donchian + ATR 손절)을 일봉으로 백테스트.
사전 지정 파라미터만 사용. Sharpe > 0.8 목표.

## SubTask 목록

### 🔴 SubTask W1-02.1: 노트북 셋업
**작업자**: Solo
**예상 소요**: 0.1일

- [ ] notebooks/02_strategy_a_trend_daily.ipynb 생성
- [ ] data/data_hashes.txt 검증 코드 (첫 셀)
- [ ] 데이터 로드: KRW-BTC_1d_frozen_20260412.parquet

### 🔴 SubTask W1-02.2: 지표 계산
**작업자**: Solo
**예상 소요**: 0.2일

- [ ] MA200: close.rolling(window=200).mean()
- [ ] Donchian: high.rolling(20).max().shift(1), low.rolling(10).min().shift(1)
- [ ] Volume avg: volume.rolling(20).mean()
- [ ] ATR: ta.volatility.AverageTrueRange (Wilder)

### 🔴 SubTask W1-02.3: 진입/청산 신호
**작업자**: Solo
**예상 소요**: 0.1일

- [ ] entries = (close > ma200) & (close > donchian_high) & (volume > vol_avg * 1.5)
- [ ] exits = close < donchian_low

### 🔴 SubTask W1-02.4: vectorbt 백테스트
**작업자**: Solo
**예상 소요**: 0.2일

- [ ] vbt.Portfolio.from_signals(sl_stop=0.08, sl_trail=False, freq='1D')
- [ ] fees=0.0005, slippage=0.0005, init_cash=1_000_000
- [ ] pf.stats() 출력 확인

### 🔴 SubTask W1-02.5: 결과 저장
**작업자**: Solo
**예상 소요**: 0.1일

- [ ] outputs/strategy_a_daily.json 생성
- [ ] sharpe, total_return, max_drawdown, win_rate, profit_factor, total_trades
- [ ] 사전 지정 파라미터 명시 (재현성)

### 🔴 SubTask W1-02.6: Evidence 작성
**작업자**: Solo
**예상 소요**: 0.1일

- [ ] .sisyphus/evidence/w1-02-strategy-a.txt 작성
- [ ] 자동 검증 결과 기록
- [ ] backtest-reviewer 에이전트 호출

## 인수 완료 조건 (Acceptance Criteria)
- [ ] 사전 지정 파라미터 (MA=200, DH=20, DL=10, RSI=N/A) 명시적으로 선언
- [ ] 데이터 해시 검증 통과
- [ ] vectorbt 크래시 없이 실행
- [ ] Sharpe > 0.8 (수수료/슬리피지 포함)
- [ ] MDD < 50%
- [ ] outputs/strategy_a_daily.json 생성
- [ ] backtest-reviewer 에이전트 APPROVED

## 의존성 매트릭스
| From | To | 관계 |
| W1-01 | W1-02 | 데이터 필요 |
| W1-02 | W1-04 | 강건성 분석 입력 |
| W1-02 | W1-06 | Week 1 리포트 입력 |

## 리스크 및 완화
| 리스크 | 영향 | 완화 |
| Sharpe < 0.8 | High | No-Go, 전략 패밀리 재검토 |
| vectorbt API 오용 | Medium | research/CLAUDE.md 룰 준수, backtest-reviewer 검증 |
| 데이터 갭 | Low | W1-01에서 이미 검증 |

## 산출물
### 코드
- research/notebooks/02_strategy_a_trend_daily.ipynb

### 결과
- research/outputs/strategy_a_daily.json
- .sisyphus/evidence/w1-02-strategy-a.txt

### 테스트 시나리오
- Happy: 사전 지정 파라미터 → Sharpe > 0.8
- Edge: warmup 기간(첫 200일) trade 없음 확인

## Commit
\```
feat(plan): STR-A-001 Strategy A 일봉 백테스트 완료

- 사전 지정 파라미터: MA200, Donchian(20/10), 거래량 1.5x
- vectorbt sl_stop=0.08 하드 손절
- 결과: Sharpe X.XX, MDD XX%, PF X.XX
- Evidence: w1-02-strategy-a.txt
\```

---
**이전 Task**: [W1-01 데이터 수집](./w1-01-data-collection.md)
**다음 Task**: [W1-03 Strategy B 일봉](./w1-03-strategy-b.md)
```

#### Evidence 예시: `.sisyphus/evidence/w1-02-strategy-a.txt`

```text
Task W1-02 Strategy A 일봉 백테스트 - Evidence
=================================================
Date: 2026-04-XX
Status: complete | partial | blocked
Reviewer: claude-code session

Verification Summary
--------------------
1. 데이터 입력
   - File: research/data/KRW-BTC_1d_frozen_20260412.parquet
   - SHA256: abc123... (matches data_hashes.txt)
   - Bars: 1932 (2021-01-01 ~ 2026-04-12)
   - Gaps: 0
   - Timezone: UTC (localized from KST)

2. 사전 지정 파라미터
   - MA_PERIOD = 200
   - DONCHIAN_HIGH = 20
   - DONCHIAN_LOW = 10
   - VOL_AVG_PERIOD = 20
   - VOL_MULT = 1.5
   - SL_PCT = 0.08

3. 백테스트 결과
   - Sharpe: 1.23 (목표 > 0.8) ✓
   - CAGR: 35.2%
   - Max Drawdown: 38.1% (목표 < 50%) ✓
   - Win Rate: 42%
   - Profit Factor: 1.65
   - Total Trades: 47

4. 자동 검증
   - 노트북 실행: 02_strategy_a_trend_daily.ipynb -> PASS
   - 데이터 해시 매치 -> PASS
   - vectorbt API: TypeError 없음 -> PASS
   - 결과 파일 생성: outputs/strategy_a_daily.json -> PASS

5. 룰 준수 (research/CLAUDE.md)
   - sl_stop fraction 형식: ✓
   - sl_trail boolean: ✓
   - ts_stop, td_stop 미사용: ✓
   - 사전 지정 파라미터만 평가: ✓
   - ta 라이브러리 Wilder 스무딩: ✓

6. Code review (backtest-reviewer agent)
   - APPROVED FOR PROGRESSION TO W1-03
   - No blocking issues
   - 1 NIT: 변수명 magic number → 상수로 (수정 완료)

Notes
-----
- 사전 지정 파라미터에서 Sharpe 1.23. 민감도 그리드(W1-04)에서 평탄성 확인 예정.
- 4시간봉 결과는 W1-05에서 별도 실험.
- 다음 Task W1-03(Strategy B)는 같은 데이터 사용.

Approval
--------
[ ] User sign-off (다음 Task 시작 전)
```

---

## 4단계 루프 작동 시나리오 (Week 1 Day 2)

```
[09:00] 사용자: "W1-02 시작해줘"
        ↓
[09:01] Claude: 
        - docs/stage1-execution-plan.md status 표 확인 → W1-01 🟢 Done, W1-02 🔴 Pending
        - docs/stage1-subplans/w1-02-strategy-a.md 열기
        - 메타데이터/Acceptance/SubTask 확인
        ↓
[09:05] Claude: 단계 2 (구현)
        - SubTask W1-02.1 시작
        - notebook 생성, 데이터 로드 코드 작성
        - W1-02.1 ✓ 체크
        - SubTask W1-02.2 (지표) ...
        - 모든 SubTask 완료
        ↓
[10:30] Claude: 단계 3 (검증 + Evidence)
        - Acceptance Criteria 체크리스트 검증
        - 자동 검증 명령 실행 (jupyter execute, hash 비교)
        - backtest-reviewer 에이전트 호출
        - Evidence 파일 작성: .sisyphus/evidence/w1-02-strategy-a.txt
        - "APPROVED" 받음
        ↓
[10:45] Claude: 단계 4 (다음 Task로)
        - sub-plan 메타데이터 상태 → 🟢 Done
        - execution-plan status 표 → 🟢 Done
        - git commit (template 사용)
        - 사용자에게 보고:
          "W1-02 완료. Sharpe 1.23. Evidence 서명됨. W1-03 시작할까?"
        ↓
[10:46] 사용자: "ㅇㅇ 시작해"
        ↓
        루프 처음으로
```

---

## 핵심 통찰

1. **3종 문서가 결합되어야 작동함**
   - 실행 계획만 있으면 추상적
   - 서브플랜만 있으면 큰 그림 없음
   - Evidence만 있으면 무엇을 했는지는 알지만 왜 했는지 모름

2. **루프가 닫혀야 함**
   - Sub-plan 체크박스 → Evidence 검증 → 실행 계획 status 업데이트
   - 한 단계 빠지면 추적성 깨짐

3. **Vertical slice 강제**
   - "Implementation + Test + Docs sync = ONE task"
   - BE만 끝내고 FE 미루는 패턴이 식별되면 sub-plan 분할 잘못된 것

4. **Code Review가 게이트**
   - "테스트 통과" 자체로 Done 아님
   - "APPROVED FOR PROGRESSION TO TASK N+1" 받아야 다음

5. **Evidence는 미래 자기 자신에게 보내는 메시지**
   - 한 달 후 "왜 이렇게 했지?" 답할 자료
   - 검증 가능한 사실만 기록 (의견 X)

---

## 우리에게 적용 시 차이점

| 항목 | food-supply | coin-bot |
|------|------------|---------|
| Task 수 | 11개 (병렬) | ~15개 (sequential) |
| Vertical slice 단위 | BE+FE+Test+Docs | 노트북+데이터+결과+Evidence |
| Code Reviewer | 일반 코드리뷰 (CQRS/DDD) | backtest-reviewer (data snooping, parameter freeze, vectorbt API) |
| Evidence 형식 | API + 흐름 + 명령 | 백테스트 결과 + 룰 준수 + Sharpe/MDD/PF |
| 병렬 그룹 | YES | NO (학습 우선, 순차) |
| Phase | 1, 2, 3 | Stage 1 (Week 8), Stage 2 (Week 12) |

---

## 적용 제안

### 최소 적용 (가장 쉬움)

1. `docs/stage1-execution-plan.md` 1개 작성 (15개 Task의 EPIC 뷰)
2. Week 1 6개 Task만 sub-plan 작성 (`docs/stage1-subplans/w1-*.md`)
3. `.evidence/` 디렉토리 생성 (Task 완료 시 채움)
4. `.claude/agents/backtest-reviewer.md` 작성

→ 새 디렉토리 1개 (.evidence/), 새 파일 ~10개

### 중간 적용

위 + Week 2~8 sub-plan도 미리 골격 작성 (15개 Task 모두)

### 풀 적용

food-supply 처럼 `.sisyphus/` 전체 구조 + Phase 종료 보고서 + Handoff 문서

---

## 결정 필요

### Q. 어느 수준으로 적용?

- [ ] **A. 최소 적용** (권장) — 1주차만 sub-plan, 나머지는 Task 시작 직전에 작성
- [ ] B. 중간 적용 — 15개 Task 모두 sub-plan 미리 작성
- [ ] C. 풀 적용 — `.sisyphus/` 전체 구조

### 권장: A (최소 적용)

**이유**:
- Week 1 결과 보고 전엔 Week 2+ 상세 계획이 의미 없음 (Go/No-Go 분기)
- 한꺼번에 15개 sub-plan 만들면 stale 문서 양산 위험
- food-supply의 `.sisyphus/` 전체 구조는 **그들이 11개 병렬 작업**을 했기 때문에 필요했음. 우리는 sequential이므로 단순화 가능
- Evidence 파일 패턴과 4단계 루프 자체가 핵심 가치

**A 선택 시 즉시 작업**:
1. `docs/stage1-execution-plan.md` 작성 (15개 Task EPIC)
2. `docs/stage1-subplans/` 디렉토리 + Week 1 6개 sub-plan 작성
3. `.evidence/` 디렉토리 생성
4. `.claude/agents/backtest-reviewer.md` 작성 (추후 사용)
5. 외부 감사 후 commit
6. Day 1 (W1-01) 시작 가능 상태

승인 부탁드립니다.
