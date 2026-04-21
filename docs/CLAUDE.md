# docs/

## Module Context

프로젝트의 모든 결정사항, 시스템 설계, 용어집, 플랜 문서. 단일 진실 문서(Single Source of Truth) 원칙으로 운영. 모든 결정은 `decisions-final.md`에 통합되며, 다른 문서는 그것을 보조하거나 역사적 맥락을 보존.

## Tech Stack & Constraints

- 형식: Markdown (`.md`)
- 언어: 한국어 (코드 블록은 영어 가능)
- 이모지: 금지 (CLAUDE.md 시스템 정책, 모든 docs/* 파일에 적용)
- 표/리스트/코드 블록: GitHub 표준 마크다운 문법
- 헤더 구조: H1 한 번, H2 주요 섹션, H3 하위, H4 최하위 (남발 금지)
- 인용/강조: `> blockquote`, `**굵게**`, `` `인라인 코드` ``, ``` ```코드 블록``` ```
- 외부 링크: `[label](url)`, 로컬 링크: `[label](./path.md)`

## Implementation Patterns

### 결정 변경 패턴

```
1. decisions-final.md를 직접 수정 (새 파일 만들지 말 것)
2. 변경 이유 + 외부 감사 결과를 commit 메시지에 명시
3. 연쇄 영향 받는 문서(architecture.md, stage1-execution-plan.md, stage1-weekly/, CLAUDE.md) 동시 갱신
4. 외부 감사관 관점 자가 재검증
5. 사용자 보고 후 commit
```

### 용어 추가 패턴

```
1. glossary.md의 적절한 카테고리 찾기
2. 형식: ### 용어명 (영어, 한국어)
   - **뜻**: 한국어 정의
   - **자바 비유**: Java/Spring 개념으로 빗대기
   - **우리 프로젝트**: 어떻게 쓰이는지
3. Section 8 약어 표에도 추가 (약어인 경우)
```

### 결정 표기 패턴

```markdown
| 항목 | 결정 |
|------|------|
| 거래소 | 업비트 (pyupbit + ccxt) |
```

## Testing Strategy

문서는 코드가 아니므로 단위 테스트 대신 다음 검증 단계 적용:

- 외부 감사관 관점 자가 재검증 (ChatGPT가 작성했다고 가정)
- 다른 문서와의 cross-reference 일관성 확인
- 모순 감지: 같은 사실이 두 문서에 다르게 기재되었나?
- 이모지/표 안 이모지 grep으로 검출
- 링크 유효성: 참조한 파일이 실제 존재하나?
- 용어 검증: glossary에 없는 용어가 다른 문서에 등장하나?

## Active Documents

다음 문서가 현재 유효한 단일 진실 출처:

- `decisions-final.md` — 모든 프로젝트 결정사항 통합 (11개 Part)
- `architecture.md` — 시스템 설계도 (Phase별 진화)
- `glossary.md` — 자바 개발자를 위한 용어집
- **`stage1-execution-plan.md`** — Stage 1 EPIC 뷰 (16개 Task 상태 표 + 의존성 + 잔존 정정 Task aggregator)
- **`stage1-weekly/`** — Week 단위 Task 상세 (`week1.md`, `week2.md`, `week3-8-pending.md`. Week 3~8 진입 시 분할). Week 1 EPIC 상세는 본 디렉토리의 `week1.md`가 유일한 active 문서 (`week1-plan.md`는 Historical로 이동됨)
- **`stage1-subplans/`** — Task 상세 sub-plan (Week 1 6개 + Week 2 3개 작성 완료, Week 3+ 작성 대기)
- **`execution-loop-pattern.md`** — food-supply 방법론 추출 (3종 문서 + 4단계 루프)

## Historical Documents (참조만, 편집 금지)

이미 통합 완료된 문서들. 역사적 맥락과 결정 흐름을 보존하기 위해 유지:

- `planning-questionnaire.md` — 초기 기획 질문지
- `research-report.md` — 초기 리서치
- `algorithm-validation.md` — 알고리즘 심층 검증
- `decisions-needed.md` — 1차 결정 질문지
- `my-decisions.md` — 1차 결정 (오류 다수, 교정됨)
- `critical-corrections.md` — 외부 감사관 1차 교정
- `decisions-v2.md` — 2차 결정 질문지
- `decisions-remaining.md` — 잔여 결정
- `day0-corrections.md` — Day 0 발견 사항
- `day0-proposed-diffs.md` — Day 0 적용 완료 이력
- `critical-corrections-v2.md` — CLAUDE.md 시스템 재감사
- `week1-plan.md` — Week 1 일별 계획 (Day 1~Day 7 timeline). W1-01~W1-06 sub-plan으로 분할 완료 + EPIC Week 섹션을 `stage1-weekly/week1.md`로 이동 (2026-04-21). 역사적 참조용으로만 유지
- `methodology-adoption-plan.md` — food-supply 방법론 적용 제안서 (2026-04 초안). **미채택**: coin-bot은 `.sisyphus/` 구조 대신 자체 진화한 `stage1-execution-plan.md` + `stage1-weekly/` + `stage1-subplans/` 구조 사용. 본문 내 week1-plan/.sisyphus/ 참조는 당시 제안 원문으로 역사 보존 (Historical로 이동 2026-04-21). food-supply 방법론 학습 자료로만 참고

## Local Golden Rules

### Do's

- 결정 변경 시 `decisions-final.md` 직접 수정. 새 결정 문서를 만들지 말 것.
- 새 전문용어 도입 시 `glossary.md`에 자바 비유 포함하여 즉시 추가.
- 문서 작성/수정 후 외부 감사관 관점으로 재검증 (사용자 명시 반복 요구).
- 마크다운 헤더, 표, 코드 블록 등 표준 마크다운 문법 준수.
- 모든 문서 한국어 작성. 코드 예시는 영어 가능.
- 변경 이유를 문서 내 또는 커밋 메시지에 명시.
- 새 전문용어 도입 즉시 glossary 추가 (블로킹).

### Don'ts

- 역사적 문서(`Historical Documents` 섹션) 편집 금지. 새 정보는 `decisions-final.md`로.
- 같은 결정을 두 문서에 중복 기재 금지. 한 곳만 진실, 다른 곳은 링크.
- 자바 개발자가 모를 만한 용어를 풀이/glossary 링크 없이 사용 금지.
- 이모지 사용 금지 (CLAUDE.md 시스템 정책, 모든 docs/* 파일에 적용).
- 표 안에 이모지 또는 컬러 마크업 사용 금지.
- 과거 결정을 무성의하게 덮어쓰지 말 것. 변경 이유 + 감사 결과 첨부 필수.
- 단일 결정 문서를 새로 분기시키지 말 것 (`decisions-v3.md` 같은 거 금지).
- 미승인 결정을 사실로 기재 금지. 결정은 반드시 사용자 승인 후 본문에 반영.

## Audit Pattern (외부 감사관 자가 재검증)

중요 문서 작성 또는 수정 후 다음 단계 필수 (Immutable, 사용자 반복 요구):

1. 작성자 본인이 한 번 검토.
2. 외부 감사관 관점("ChatGPT가 썼다고 가정")으로 재검토.
3. 사실 오류, 논리 모순, 누락 항목, 자기-확증 편향, API/사실 검증 누락 확인.
4. 발견 사항을 별도 corrections 문서로 정리 후 사용자 보고.
5. 사용자 승인 후 본 문서에 반영.

이 패턴을 생략하여 발견된 과거 사례:
- `my-decisions.md`의 논문 오독 (arXiv:2410.12464 — Reddit vs 뉴스 비교 가짜)
- `week1-plan.md`의 5개 코드 버그 (MA200 = 30일, entry_price 미정의, bars_held 미정의, 앙상블 자본 이중계산, Donchian 윈도우)
- 대시보드 보안 모순 (HTTP + RSA + 외부 IP)
- CLAUDE.md 1차 작성 시 미승인 day0 결정을 사실로 인코딩
- vectorbt `td_stop`, `ts_stop` 미존재 파라미터 사용
- pyupbit 타임존 처리 누락

## File Naming

- 결정 문서: `decisions-*.md` (역사적), `decisions-final.md` (현행)
- 설계 문서: `architecture.md`, `glossary.md`
- 플랜 문서: `week{N}-plan.md`, `day{N}-*.md`
- 교정 문서: `*-corrections.md`, `critical-corrections-v{N}.md`
- 검증 문서: `*-validation.md`, `*-verification.md`
