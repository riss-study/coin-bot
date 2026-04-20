# coin-bot

## Project Context

업비트 KRW 페어 자동 매매 봇. 학습 프로젝트로 정의됨 (정량 금융 + 시스템 학습). 라이브 트레이딩은 Stage 2 게이트(Week 12) 통과 시 50만원 한정 옵션.

- 시작일: 2026-04
- 사용자: 자바 스프링 백엔드 개발자 (퀀트/크립토 도메인 신규)
- 진행 방식: 12주 단계별 승인, 2단계 킬 크라이테리아 (Stage 1 = Week 8, Stage 2 = Week 12)
- 현재 단계: Day 0 적용 완료. Week 1 Day 1 시작 대기.

### Tech Stack

- Python 3.11+
- Backtest 리서치 (Week 1-3): Jupyter + pandas + vectorbt 0.28.5
- Trading framework (Week 4+): Freqtrade + ccxt + pyupbit 0.2.34
- DB: PostgreSQL + TimescaleDB
- Backend: FastAPI
- Frontend: Next.js
- Container: Docker + docker-compose (Swarm 모드 아님, file 기반 secrets)
- External access: Cloudflare Tunnel (HTTPS 자동, 로컬 포트 미노출)
- Host: macOS 24/7
- Secrets: macOS Keychain → 임시 파일 → Docker secrets file mount
- Notifications: Discord (default), KakaoTalk (urgent only)

## Operational Commands

현재 상태(Day 0 완료, Week 1 Day 1 미시작) 기준 실행 가능한 것만:

- 문서 검토: `ls docs/`
- 결정 진실 문서: `cat docs/decisions-final.md`
- 진행 상황: TaskList 도구 (in-session)

Week 1 Day 1 완료 후 활성화될 명령 (지금은 실행 불가):

- 환경 활성화: `source research/.venv/bin/activate`
- Jupyter: `cd research && jupyter lab`
- Git: `git status && git diff` (Day 1 Task 1.1에서 git init 후)
- 의존성 잠금: `cd research && uv pip compile requirements.txt -o requirements.lock`

## Golden Rules

### Immutable (절대 위반 금지)

- 실제 자금 라이브 트레이딩은 Stage 2 게이트(Week 12) 통과 시에만 가능. 50만원 한도.
- 선물/레버리지 거래 절대 금지. 현물(spot)만.
- API 키, 시크릿, 비밀번호를 git 커밋에 포함 금지. macOS Keychain만.
- LLM은 매매 결정 생성자 아님. 거부권/사후분석/로깅 전용 (Phase 10+에서만 도입).
- 외부 인터넷 노출은 Cloudflare Tunnel 경유 필수. 로컬 포트 직접 노출 금지.
- dashboard-backend는 거래소 API 키에 접근 권한 없음. 매매는 Freqtrade 내부 REST 경유.
- Stage 1 킬(Week 8) 도달 시 무조건 사용자 결정 대기. 자동 라이브 진행 금지.
- 모든 결정은 단일 진실 문서 `docs/decisions-final.md` 외 위치로 분기 금지.
- **중요 문서 수정 후 외부 감사관 관점 자가 재검증 필수.** ChatGPT가 작성했다고 가정하고 비판적 재검토. 감사 결과를 별도 corrections 파일로 정리 후 사용자 보고. (사용자 명시 반복 요구.)
- 외부 라이브러리 API 사용 시 공식 docs 또는 소스 직접 확인 후 코드 작성. 추측으로 작성 금지.

### Do's

- 모든 코드/문서 변경은 사용자 단계별 승인 후 진행 (전략 이터레이션 단위, decisions-v2 Q10 A).
- 백테스트 결과는 사전 지정 파라미터(pre-registered)로만 평가. 민감도 그리드는 참고용.
- 모든 매매 데이터(거래/신호/포지션)는 DB에 영구 저장 (세금 준비).
- 모든 시간 기록은 UTC + KST 동시 보관.
- 모르는 트레이딩 용어는 `docs/glossary.md` 참조. 없으면 즉시 추가.
- 작업 시작 시 TaskUpdate로 in_progress, 완료 시 completed 표시.
- 결정 변경 시 decisions-final.md + 연쇄 문서(architecture, week1-plan, CLAUDE.md) 동시 갱신.

### Don'ts

- 데이터 스누핑 금지. "100가지 조합 중 최고값" 보고 형태 금지.
- 미승인 결정을 사실로 인코딩 금지 (Day 0 적용 전 결정을 사실로 가정한 사례 있음).
- 결정 변경 시 기존 결정 문서를 무성의하게 덮어쓰지 말 것. 변경 이유 + 감사 결과 첨부.
- 사용자에게 "직접 판단"을 무책임하게 떠넘기지 말 것. 판단 시 근거 명시.
- 논문/벤치마크 인용 시 2차 소스 의존 금지. 직접 확인된 내용만.
- 자바 개발자가 모를 만한 용어를 풀이/glossary 링크 없이 사용 금지.
- vectorbt에 `ts_stop`, `td_stop`, `max_duration` 등 검증되지 않은 파라미터 사용 금지 (감사 발견 사례).
- vectorbt Boolean exit mask에 `entry_price`, `bars_held` 같은 정의되지 않은 변수 사용 금지.
- pyupbit 데이터 받은 후 타임존 localize 누락 금지 (naive KST → UTC 변환 필수).
- 보안 설정과 모순되는 외부 노출 구조 설계 금지 (HTTP + 외부 IP + 평문 비밀번호 사례).

## Context Map

- **[문서 / 결정 편집](./docs/CLAUDE.md)** — 결정사항, 아키텍처, 용어집, 플랜, sub-plan 등 docs/* 내 모든 문서 작업 시.
- **[리서치 / 노트북 / 백테스트](./research/CLAUDE.md)** — Jupyter 노트북, 데이터 수집, vectorbt 백테스트 작업 시 (Week 1+).
- **[실행 계획 (Stage 1 EPIC)](./docs/stage1-execution-plan.md)** — 전체 14개 Task 상태, 의존성, Acceptance Criteria. Task 시작 전 항상 먼저 확인.
- **[주차별 상세 (Week 1/2/3~8)](./docs/stage1-weekly/)** — Week 단위 Task 목록 + 의사결정 흐름. EPIC 뷰의 주차 섹션 상세.
- **[Sub-plan (Task 상세)](./docs/stage1-subplans/)** — Task 단위 상세 작업 계획. 각 Task 시작 시 해당 sub-plan 읽기 필수.
- **[Evidence 파일 (검증 서명)](./.evidence/)** — Task 완료 시 작성. 6단 구조 (데이터/파라미터/결과/자동검증/룰준수/리뷰).
- **[Backtest Reviewer 에이전트](./.claude/agents/backtest-reviewer.md)** — 백테스트 spec 정합성 검증. Task 종료 직전 호출.
- **[Master Prompt 템플릿 (편집 금지)](./AGENTS_md_Master_Prompt.md)** — CLAUDE.md 시스템의 원본 템플릿. 참조만.

추후 별도 GitHub 리포로 분리 예정:

- engine/ — Freqtrade 봇 (Week 4+ 활성화)
- dashboard/ — FastAPI + Next.js + Cloudflare Tunnel (Week 10+ 활성화)

## Standards & References

### 단일 진실 문서

- 결정사항: `docs/decisions-final.md`
- 시스템 설계: `docs/architecture.md`
- 용어집 (자바 개발자용): `docs/glossary.md`
- 실행 계획 (EPIC): `docs/stage1-execution-plan.md`
- 현재 Task 작업: `docs/stage1-subplans/{task-id}.md`
- 검증 증거: `.evidence/{task-id}.txt`

### Git 전략

- 비공개 GitHub 리포 × 3 예정 (메인/엔진/대시보드)
- 커밋 메시지 접두사: `Day 0:`, `Week N Day M:`, `Phase N:` 등 단계 명시
- 한국어 또는 영어 자유
- `.gitignore`에 `.venv/`, `data/`, `*.parquet`, `.env`, `secrets/`, `__pycache__/`, `.ipynb_checkpoints/` 필수 포함
- API 키, 시크릿이 포함된 파일 절대 git add 금지

### 단계별 킬 크라이테리아

- **Stage 1 (Week 8)**: 페이퍼 트레이딩 초기 2주 결과 평가. Fail 시 전략 패밀리 교체 또는 학습 모드 유지. (페이퍼 시작 Week 6)
- **Stage 2 (Week 12)**: 라이브 투입 게이트. 모든 조건 충족(Sharpe > 1.0, DSR > 0.5, 페이퍼 4주 70%+, 사용자 명시 OK) 시에만 50만원 입금.
- 라이브 진행은 사용자 명시적 승인 없이 절대 자동 진행 금지.

### Maintenance Policy

이 `CLAUDE.md` 또는 하위 `CLAUDE.md`와 실제 코드/문서 사이에 괴리가 발생하면 즉시 사용자에게 보고하고 업데이트 제안. 결정 변경 시 외부 감사관 관점 자가 재검증 후 반영.

매주 세션 시작 시 root CLAUDE.md vs decisions-final.md vs architecture.md 간 모순 점검.

### 사용자 커뮤니케이션

- 사용자는 한국어. 응답도 한국어.
- 사용자는 자바 스프링 개발자, 트레이딩/Python/크립토 도메인 신규.
- 전문용어 첫 등장 시 풀이 또는 glossary 링크 필수.
- 사용자는 외부 감사관 관점 자가 검증을 명시적으로 반복 요구함. 중요 결정 후 자기 작업 비판적 재검토 필수.
