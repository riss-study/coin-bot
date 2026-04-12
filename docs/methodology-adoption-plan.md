# food-supply 방법론 분석 + coin-bot 적용 제안

> 사용자의 다른 프로젝트(`food-supply-matching-system`)에서 사용된 AI 협업 방법론을 분석하고, coin-bot에 적용할 패턴을 제안합니다.

---

## Part 1: food-supply 방법론 핵심 발견

### 1-1. 핵심 디렉토리 구조

```
food-supply-matching-system/
├── .sisyphus/                       # 자체 플랜/증거 시스템 (핵심)
│   ├── drafts/                       # 살아있는 문서 (PRD, 아키텍처, Q&A)
│   ├── plans/                        # 실행 플랜 + 태스크 서브플랜
│   │   └── phase1-subplans/          # 11개 태스크 각각의 상세 플랜
│   ├── evidence/                     # 작업 완료 검증 파일
│   │   └── task-1-foundation.txt     # 각 태스크 별 증거 파일
│   ├── notepads/                     # 실험/학습 노트
│   ├── archive/                      # 폐기된 옛 버전
│   ├── phase1-completion-report.md   # Phase 종료 리포트
│   └── phase1-handoff.md             # 다음 Phase 인계 문서
│
├── .opencode/                        # opencode.ai 도구 설정
│   ├── agents/
│   │   └── code-reviewer.md          # 커스텀 AI 코드리뷰 에이전트
│   ├── skills/
│   │   └── session-markdown-documentor/  # 자동 세션 기록 스킬
│   └── oh-my-opencode.json           # 명명된 에이전트 정의 (oracle/sisyphus/momus/prometheus 등)
│
├── DESIGN-BRIEF.md                   # 루트의 첫 번째 산출물
├── IMPLEMENTATION_PLAN_TASKS_*.md    # 핫픽스 작업 플랜
├── LOCAL-RUN-GUIDE.ko.md             # 로컬 개발 가이드
├── opencode.json                     # MCP 설정 (Playwright 등)
│
├── backend/                          # Spring WebFlux + CQRS + DDD
└── frontend/                         # Next.js 모노레포
```

### 1-2. 6단계 라이프사이클

```
Phase 0: 도메인 탐색
  └─ DESIGN-BRIEF.md (사용자 역할 × 화면 × 흐름)
  └─ PRD-v1.0-MVP.md (Feature ID 부여, MVP 범위)
  └─ system-architecture.md, data-model.md, api-spec.md

Phase 1: 의사결정 락 (Policy Lock)
  └─ phase1-pre-coding-questions.md (5~7개 핵심 결정)
  └─ phase1-policy-closure-log.md (Q&A → 공식 정책 + 상태 머신)

Phase 2: 실행 플랜
  └─ phase1-execution-plan.md (11개 태스크 EPIC 뷰)
  └─ phase1-subplans-index.md (태스크별 서브플랜 인덱스)
  └─ phase1-subplans/phase1-task-{N}-*.md (각 태스크 상세)

Phase 3: 구현
  └─ Vertical slice (BE+FE+test+docs를 한 태스크로)
  └─ Feature ID로 traceability (QUOTE-001, AUTH-002 등)
  └─ 커밋 메시지: feat(plan): QUOTE-001 견적 제출 API 구현

Phase 4: 검증 (Evidence Gate)
  └─ .opencode/agents/code-reviewer.md 가 spec 정합성 검증
  └─ evidence/task-N-*.txt 파일에 검증 결과 기록 (서명)
  └─ APPROVED / REQUEST CHANGES / NEEDS DISCUSSION

Phase 5: 종료 + 인계
  └─ phase1-completion-report.md
  └─ phase1-handoff.md (다음 Phase 권고사항)
```

### 1-3. 핵심 혁신 패턴

| 패턴 | 설명 | 효과 |
|------|------|------|
| **Feature ID 태그** | QUOTE-001, AUTH-002 등 모든 산출물에 ID 부여 | PRD ↔ 코드 ↔ 테스트 ↔ 커밋 ↔ Evidence 양방향 추적 |
| **Vertical Slice 태스크** | 한 태스크 = BE + FE + DB + 테스트 + 문서 | "API는 끝났는데 UI는 막힘" 회피 |
| **Pre-Coding Questionnaire** | 코드 시작 전 5~7개 핵심 결정만 명시적으로 | 개발 중 "이거 어떻게 해요?" 질문 차단 |
| **Policy Closure Log** | 질문 답변을 공식 규칙 + 상태 머신으로 변환 | 의사결정의 법적 계약 |
| **Evidence Files** | 각 태스크 완료 시 검증 결과 파일 서명 | "테스트 통과"가 아닌 "spec 충족" 증명 |
| **Custom Code-Reviewer Agent** | spec 정합성 검증 (CQRS, DDD, Feature ID, API spec) | 일반 리뷰 ≠ spec 리뷰 |
| **Session Markdown Documentor** | 매 세션 자동 기록 | 감사 추적 + 온보딩 |
| **Named Agent Roles** | oracle/sisyphus/momus/prometheus 명명 | 작업별 적절 모델 자동 선택 |

### 1-4. 명명된 에이전트 정의 (oh-my-opencode.json)

```json
{
  "agents": {
    "oracle": "high-capability decision/review",
    "librarian": "multi-repo analysis, evidence gathering",
    "sisyphus": "orchestration & planning",
    "metis": "pre-plan analysis",
    "momus": "plan validation (highest stakes)",
    "prometheus": "strategic planning",
    "code-reviewer": "spec-driven code review (custom)"
  }
}
```

---

## Part 2: coin-bot 적용 제안

### 2-1. 채택할 패턴 (Core Methodology)

| 패턴 | 채택 여부 | 적용 방식 |
|------|:--------:|---------|
| `.sisyphus/` 디렉토리 시스템 | ✅ | 우리 docs/ 일부를 .sisyphus/로 재구조화 |
| Pre-Coding Questionnaire + Policy Closure | ✅ | 이미 했음 (decisions-needed.md → decisions-final.md) |
| 실행 플랜 + 서브플랜 | ✅ | week1-plan.md를 .sisyphus/plans/로 |
| Evidence Files | ✅ | 매 태스크 완료 시 evidence/week-N-day-M.txt 작성 |
| Feature ID 태그 | ✅ | STR-A-001(Strategy A), DATA-001(데이터 수집) 등 |
| Vertical Slice 태스크 | ✅ | 각 Day = (코드 + 테스트 + 데이터 + 검증) 한 묶음 |
| Session Markdown Documentor | ✅ | .claude/session-{date}.md 자동 생성 |
| 커스텀 Code-Reviewer 에이전트 | ✅ | 백테스트 룰 검증용 (data snooping, parameter freeze 등) |
| 명명된 에이전트 (oracle/sisyphus 등) | ⚠️ | opencode 도구 의존, Claude Code에선 부분 적용 |
| Phase 종료 보고서 | ✅ | 매 Stage 게이트마다 .sisyphus/stage-N-report.md |

### 2-2. 적용 안 할 패턴 (anti-patterns for our context)

| 패턴 | 거부 이유 |
|------|----------|
| CQRS / DDD | B2B CRUD 플랫폼용. 트레이딩 봇에 과대응. |
| 11개 병렬 태스크 | 솔로 개발자 + 12주 = sequential이 더 현실적 |
| 50+ 마크다운 파일 | 우리는 최대 20~25개로 제한 |
| 하드 워터폴 게이트 | 백테스트 리서치는 반복적이라 부드러운 게이트 필요 |
| 화면별 design system | 우리 대시보드는 5~10개 화면, design-system.md 최소화 |
| `.opencode/` 도구 의존 | Claude Code 사용 중이므로 유사 기능 직접 구현 |

### 2-3. 제안하는 새 디렉토리 구조

```
coin-bot/
├── CLAUDE.md                       # (기존 유지) 루트 거버넌스
├── AGENTS_md_Master_Prompt.md      # (기존, 편집 금지)
│
├── .sisyphus/                      # NEW — food-supply 방법론 시스템
│   ├── drafts/                      # 살아있는 정책/설계 문서
│   │   ├── DESIGN-BRIEF.md          # 봇 사용자/화면/흐름 (NEW)
│   │   ├── PRD-v1.0-MVP.md          # Feature ID + MVP 범위 (NEW)
│   │   ├── pre-coding-questions.md  # 이미 한 결정들 통합 (decisions-needed.md 발췌)
│   │   ├── policy-closure-log.md    # decisions-final.md 핵심 정책만 발췌
│   │   ├── system-architecture.md   # architecture.md 이동
│   │   ├── data-model.md            # DB 스키마 분리
│   │   ├── api-spec.md              # 대시보드 API spec
│   │   └── glossary.md              # glossary.md 이동
│   │
│   ├── plans/                       # 실행 플랜
│   │   ├── 12-week-execution-plan.md   # 전체 12주 EPIC 뷰
│   │   ├── stages-index.md             # Stage 1/2 게이트 인덱스
│   │   └── stage1-subplans/
│   │       ├── stage1-task-01-data-collection.md
│   │       ├── stage1-task-02-strategy-a-backtest.md
│   │       ├── stage1-task-03-strategy-b-backtest.md
│   │       ├── stage1-task-04-robustness.md
│   │       ├── stage1-task-05-4h-experiment.md
│   │       ├── stage1-task-06-week1-report.md
│   │       ├── stage1-task-07-walk-forward.md
│   │       ├── stage1-task-08-strategy-adoption.md
│   │       ├── stage1-task-09-freqtrade-port.md
│   │       └── stage1-task-10-paper-trading.md
│   │
│   ├── evidence/                    # 검증 증거 파일
│   │   └── (각 태스크 완료 시 생성)
│   │       ├── stage1-task-01-data-collection.txt
│   │       ├── stage1-task-02-strategy-a.txt
│   │       └── ...
│   │
│   ├── notepads/                    # 학습/실험 노트
│   │   └── (필요 시 생성)
│   │
│   ├── archive/                     # 옛 버전 (decisions-v2, my-decisions 등 이동)
│   │
│   ├── stage1-completion-report.md  # Week 8 종료 보고
│   └── stage1-handoff.md            # Stage 2로 인계
│
├── .claude/                        # NEW — Claude Code 세션 기록
│   ├── sessions/
│   │   └── session-2026-04-12-day0.md   # 매 세션 자동 생성
│   └── agents/
│       └── backtest-reviewer.md    # 커스텀 backtest 검증 에이전트 (Claude subagent)
│
├── docs/                           # 기존 + 정리
│   ├── CLAUDE.md                    # (기존 유지)
│   ├── decisions-final.md           # (기존 유지, .sisyphus/drafts/policy로 일부 발췌)
│   ├── architecture.md              # (.sisyphus/drafts로 이동 후 stub)
│   ├── glossary.md                  # (.sisyphus/drafts로 이동 후 stub)
│   ├── week1-plan.md                # (.sisyphus/plans/stage1-subplans/에 분할)
│   └── (역사적 문서들은 .sisyphus/archive/로)
│
├── research/                       # (기존 유지) Jupyter 노트북
│   ├── CLAUDE.md
│   ├── notebooks/
│   ├── data/
│   └── outputs/
│
└── (Week 4+: engine/, dashboard/ 별도 리포)
```

### 2-4. Feature ID 체계 제안

food-supply의 `QUOTE-001`, `AUTH-002` 패턴을 우리에 적용:

| 카테고리 | ID 형식 | 예시 |
|---------|--------|------|
| 데이터 수집 | DATA-NNN | DATA-001 (업비트 OHLCV 다운로드) |
| 전략 | STR-A-NNN, STR-B-NNN | STR-A-001 (200MA + Donchian 추세) |
| 리스크 관리 | RISK-NNN | RISK-001 (ATR 손절), RISK-002 (서킷 브레이커) |
| 백테스트 | BT-NNN | BT-001 (vectorbt 기본), BT-002 (Walk-forward) |
| 페이퍼 트레이딩 | PAPER-NNN | PAPER-001 (Freqtrade dry-run 설정) |
| 라이브 트레이딩 | LIVE-NNN | LIVE-001 (50만원 입금 + 라이브 모드) |
| 대시보드 | DASH-NNN | DASH-001 (포지션 조회), DASH-002 (수동 매매) |
| 알림 | NOTIF-NNN | NOTIF-001 (Discord 웹훅), NOTIF-002 (카톡 긴급) |
| 보안 | SEC-NNN | SEC-001 (Cloudflare Tunnel), SEC-002 (Keychain) |
| LLM | LLM-NNN | LLM-001 (Reddit 감성) — Phase 10+ |

### 2-5. Evidence File 표준 형식 (food-supply 모방)

```text
Stage 1 Task 02 - Strategy A 일봉 백테스트 - Evidence
=================================================
Date: 2026-04-XX
Status: complete | partial | blocked
Reviewer: claude-code session

검증 요약
--------
1. Feature: STR-A-001 (Strategy A 추세 추종)
   - 사전 지정 파라미터: MA=200, Donchian=20/10, RSI=N/A
   - 데이터: KRW-BTC_1d_frozen_20260412.parquet (SHA256: abc123...)
   - Sharpe: 1.23 (목표 > 0.8) ✓
   - CAGR: 35.2%
   - MDD: 38.1% (목표 < 50%) ✓
   - 승률: 42%
   - PF: 1.65
   - 트레이드 수: 47

2. 자동 검증
   - 노트북 실행: 02_strategy_a_trend_daily.ipynb -> PASS
   - 데이터 해시 매치: PASS
   - vectorbt API 호출: TypeError 없음 -> PASS
   - 결과 파일 생성: outputs/strategy_a_daily.json -> PASS

3. 룰 준수 (CLAUDE.md research/CLAUDE.md)
   - sl_stop fraction 형식 사용: ✓
   - 사전 지정 파라미터만 평가: ✓
   - ta 라이브러리 Wilder 스무딩: ✓
   - 타임존 localize 완료: ✓

4. 수동 검토
   - Equity curve 시각적 검증: 합리적 (2022 베어 회복 확인)
   - 트레이드 분포: 연도별 균등 (특정 해 의존 없음)

Notes
-----
- Strategy A는 통과. Strategy B (다음 태스크) 결과 대기 중.
- 4시간봉 결과는 Day 5에 별도 실험.
- 민감도 그리드는 Day 4에 참고용 생성.

Approval
--------
[ ] User sign-off (다음 태스크 시작 전)
```

### 2-6. Custom Backtest Reviewer 에이전트 (Claude subagent)

food-supply의 `code-reviewer.md`를 본떠 우리 백테스트 룰 검증용 에이전트:

```markdown
# Backtest Reviewer Agent

## 역할
백테스트 노트북/코드를 검증. 일반 코드 리뷰 ≠ 백테스트 리뷰.

## 검증 항목

### A. Data Integrity
- [ ] 데이터 freeze 해시 검증 코드 존재
- [ ] 타임존 localize (`tz_localize('Asia/Seoul').tz_convert('UTC')`)
- [ ] 갭 < 0.1%, 이상치 < 0.5%

### B. Pre-registered Parameters
- [ ] 사전 지정 파라미터가 명시적으로 선언됨 (상수)
- [ ] 그리드 sweep 결과가 Go/No-Go에 사용되지 않음
- [ ] DSR 계산 시 N_trials 입력

### C. vectorbt API Correctness
- [ ] sl_stop은 fraction (0.05 = 5%)
- [ ] sl_trail은 boolean
- [ ] ts_stop, td_stop, max_duration 사용 안 함
- [ ] pf.sharpe_ratio() 메서드 호출 (괄호 필수)
- [ ] freq 파라미터 명시
- [ ] entry_price, bars_held 같은 미정의 변수 참조 없음

### D. Wilder Smoothing
- [ ] ATR/RSI는 ta 라이브러리 사용 (직접 구현 금지)

### E. Strategy Logic
- [ ] MA200이 실제 200 윈도우 (일봉=200, 4h=1200)
- [ ] Donchian 윈도우 단위 일치
- [ ] 시간 스톱은 entries.shift(N) 패턴

### F. Output
- [ ] 결과 JSON 저장
- [ ] 사전 지정 파라미터 명시
- [ ] 데이터 해시 명시

## 출력 형식
[BLOCKING] / [WARNING] / [NIT] + 파일:라인 + 설명 + 수정 제안

## Approval Gate
모든 BLOCKING 해결 + WARNING 검토 후 evidence 파일에 서명.
```

### 2-7. Session Markdown Documentor (Claude Code 버전)

```markdown
# 세션 작업 문서

Date: {YYYY-MM-DD HH:mm KST}
Stage: Stage 1 / Stage 2
Task: stage1-task-XX

## 1. 요약
{1-2 paragraph}

## 2. 상세 타임라인
- **Step 1**
  - 사용자 요청: {prompt}
  - Claude 작업: {action}
  - 결과: {outcome}

## 3. 핵심 결정
- {decision + reason}

## 4. 실행 명령어
- {bash command}

## 5. 생성/수정 파일
- created: {files}
- modified: {files}

## 6. 다음 작업
- [ ] {next task}
```

---

## Part 3: 마이그레이션 액션 플랜

### 단계 A: 디렉토리 구조 생성 (저비용)

1. `.sisyphus/{drafts,plans,evidence,notepads,archive}/` 생성
2. `.claude/{sessions,agents}/` 생성
3. `.sisyphus/plans/stage1-subplans/` 생성

### 단계 B: 기존 문서 이동 + 분할

1. `docs/architecture.md` → `.sisyphus/drafts/system-architecture.md`
2. `docs/glossary.md` → `.sisyphus/drafts/glossary.md` (또는 둘 다 유지)
3. `docs/week1-plan.md` → `.sisyphus/plans/stage1-subplans/stage1-task-{01~10}-*.md` 분할
4. `docs/decisions-final.md`의 정책 부분 → `.sisyphus/drafts/policy-closure-log.md` 발췌
5. 역사적 문서 8개 (`docs/decisions-needed.md`, `my-decisions.md` 등) → `.sisyphus/archive/`

### 단계 C: 새 문서 생성

1. `.sisyphus/drafts/DESIGN-BRIEF.md` — 사용자 역할 + 화면 + 흐름 (코인봇용)
2. `.sisyphus/drafts/PRD-v1.0-MVP.md` — Feature ID + Stage 1/2 범위
3. `.sisyphus/plans/12-week-execution-plan.md` — 전체 12주 EPIC 뷰
4. `.sisyphus/plans/stages-index.md` — Stage 1/2 게이트 인덱스
5. `.claude/agents/backtest-reviewer.md` — 백테스트 검증 에이전트

### 단계 D: 링크 업데이트

1. 루트 `CLAUDE.md`의 Context Map에 `.sisyphus/`, `.claude/agents/` 추가
2. `docs/CLAUDE.md`에서 이동된 문서 링크 업데이트
3. `research/CLAUDE.md`에서 evidence 경로 명시

### 단계 E: Feature ID 부여

1. 기존 결정사항/태스크에 ID 부여
2. 태스크 목록 (#1~17)을 Feature ID로 매핑
3. evidence 파일 형식에 ID 포함

---

## Part 4: 결정 필요

### Q1. 적용 범위

- [ ] **A. 전체 마이그레이션** (권장) — 단계 A~E 모두 진행, 4~6시간
- [ ] B. 부분 적용 — `.sisyphus/` 구조만, 새 문서는 안 만듦, 1~2시간
- [ ] C. 미니멀 — Evidence 파일 + Feature ID 만 도입, 30분
- [ ] D. 풀 자동 — Day 1 시작 전에 모든 구조 자동 생성

### Q2. food-supply의 Stage/Phase 명명 채택?

- [ ] **A. 그대로 사용** — Stage 1 (Week 8), Stage 2 (Week 12)
- [ ] B. food-supply처럼 Phase 1, Phase 2, ... 로 변경
- [ ] C. 혼합

### Q3. .opencode/ 디렉토리 만들기?

food-supply는 opencode.ai 도구를 쓰는데, 우리는 Claude Code 사용. opencode 도구를 쓰진 않지만 디렉토리 구조와 에이전트 정의는 의미 있을 수 있음.

- [ ] A. 만들지 않음 — Claude Code는 .claude/agents/ 사용
- [ ] **B. .claude/agents/만 만들고 .opencode/는 생략** (권장)
- [ ] C. 둘 다 만듦

### Q4. 기존 docs/ 폴더 처리

- [ ] **A. 그대로 두고 .sisyphus/는 추가만** (안전)
- [ ] B. docs/ 내용을 .sisyphus/로 완전 이동, docs/ 비움
- [ ] C. 핵심 4개(decisions-final, architecture, glossary, week1-plan)는 docs/에 stub 유지, 본문은 .sisyphus/로

### Q5. Feature ID 부여 시점

- [ ] **A. 지금 즉시** (마이그레이션 단계에서 한꺼번에)
- [ ] B. Week 1 작업 시작 시 점진적
- [ ] C. Week 2부터

---

## 답변 후

Q1~Q5 답변 주시면:
1. 마이그레이션 작업 시작
2. 외부 감사관 관점 자가 재검증
3. Day 1 시작 준비 완료

**가장 권장**: Q1=A, Q2=A, Q3=B, Q4=C, Q5=A (전체 마이그레이션, 우리 명명 유지, .claude/agents만, hybrid stub, 즉시 ID 부여)

이 권장안으로 진행할까요? 다른 조합 원하시면 알려주세요.
