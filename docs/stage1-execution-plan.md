# Stage 1 실행 계획서 (Week 1~8) — EPIC 뷰

> **본 문서 역할**: Stage 1 전체 Task 상태 표 + 의존성 매트릭스 + 검증 전략 + 잔존 Task aggregator
> **Week별 상세**: [`stage1-weekly/`](./stage1-weekly/) 디렉토리 참조
> **Task 상세 sub-plan**: [`stage1-subplans/`](./stage1-subplans/) 디렉토리 참조

## Stage 1 v1 종결 + v2 재시작 (2026-04-22 / 2026-04-24)

### v1 종결 (2026-04-22)

- W3-01 Walk-forward No-Go → 사용자 옵션 C (프레임 A+B 둘 다 공식 인정, 학습 모드 전환) 채택
- Stage 1 v1 킬 카운터 총 +3. W3-02/W3-03/W4~W8 전부 Cancelled
- 학습 자료 git 보존

### **v2 재시작 (2026-04-24, 라이브 경로)**

**사용자 지시 ("그렇게 하자", 2026-04-24)**:
- 본질 목표 = **50만원 한정 라이브 투입**
- 학술 박제 루프 (DSR/stability 5/5/Pardo) 과잉이었음 재인식
- W2-03 Go cells 5개 중 3개 (BTC_A, ETH_A, BTC_D) 채택

**v2 Tech Stack 전환 (2026-04-24 실측 기반, 사용자 재승인 "ㄱㄱ 그렇게 하자")**:
- ~~Freqtrade + ccxt + pyupbit~~ → **Custom bot with pyupbit 0.2.34** (단일 Python 프로세스, ~1,560 LOC 예상)
- 이유: Freqtrade 공식 Upbit 미지원 + ccxt Upbit 주문 `amount=None` 버그 (#7235) = 라이브 에러 위험. pyupbit 주문 API 실측 완료 (완전 기능)
- 상세: `docs/decisions-final.md` "Stage 1 v2 Tech Stack 전환" 섹션

**Go 기준 완화 (v2 박제)**:
- 학술 기준 제거: ~~DSR~~ / ~~stability 5/5~~ / ~~Bonferroni~~
- 실용 기준: **Sharpe>0.8 + MDD<50% + trades≥10 + 페이퍼 ±30%** (W2-03 3 cells 전부 충족)

**cycle 1 #5 재발 X**: v1 공식 종결 + v2 새 cycle + 본질 목표 재인식. 사후 완화 아님.
**cycle 1 #16 재발 X**: 2026-04-24 pyupbit/Upbit API/Freqtrade/ccxt 모두 실측 기반 검증

상세: [`stage1-v2-relaunch.md`](./stage1-v2-relaunch.md) v2 — Task V2-01 ~ V2-09 (총 5~7주) + Custom bot 모듈 구조 + 숨은 복잡도.

## 요약

> 산출물: Jupyter 노트북 백테스트 + Freqtrade 페이퍼 트레이딩 (4주)
> 난이도: Medium
> 병렬화: NO (sequential, 학습 우선, 솔로 개발자)
> 크리티컬 패스: W1-01 → W1-02/03 → W1-04/05/06 → W2 → W3 → W4 → W6 → W8 게이트
> 기간: 8주 (Stage 1 킬 크라이테리아)

## 배경

### 원래 요청
업비트 KRW-BTC 자동 매매 봇. 학습 + 옵션 라이브 프로젝트로 정의됨.
- Padysak/Vojtko 영감 전략 (200MA + Donchian + RSI(4)) 일봉 검증
- 검증 통과 시 4주 페이퍼 → Stage 2 (Week 12) 라이브 게이트
- 50만원 한정 라이브

### 반영된 판단
- vectorbt 0.28.5 + pyupbit 0.2.34 API 검증 완료
- "Padysak 복제"가 아니라 "영감을 받은" — 일봉 우선, 4시간봉은 참고
- 사전 지정 파라미터로만 Go/No-Go (data snooping 방지)
- 앙상블은 Week 2로 연기 (Week 1에서 ts_stop/td_stop 등 잘못된 vectorbt API 사용 위험 제거 후)

## 작업 목표

### 핵심 목표
8주 내에 (a) 룰 기반 매매 전략의 백테스트가 통계적으로 의미 있고 (b) 실제 시장에서 작동하는지 페이퍼 트레이딩으로 확인하여 (c) 라이브 투입 또는 학습 모드 결정.

### 산출물
- 노트북 6개 (`research/notebooks/0{1..6}_*.ipynb`)
- 백테스트 결과 JSON (`research/outputs/strategy_*.json`)
- Freqtrade 봇 (Week 4+, 별도 리포)
- Evidence 파일 16개 (각 Task 완료 서명: W1×6 + W2×3 + W3×3 + W4×2 + W6×1 + W8×1)
- Stage 1 게이트 결정 보고서 (Week 8)

### 완료 기준 (Stage 1 게이트)
- Week 8: 페이퍼 트레이딩 초기 2주 결과 평가
  - Pass: Week 9~11 페이퍼 유지 + Stage 2 준비
  - Fail: 전략 패밀리 교체 또는 학습 모드 전환

### 필수 포함 사항
- 데이터 freeze (SHA256 해시)
- 사전 지정 파라미터만 평가
- vectorbt 0.28.5 검증된 API만 사용
- 외부 감사관 자가 재검증
- Evidence 파일 (테스트 결과 + Code Review APPROVED)

### 포함하면 안 되는 사항
- LLM 레이어 (Phase 10+ 이후)
- Walk-forward Week 1 (Week 2 이후)
- 4시간봉을 Week 1 Go/No-Go 기준으로 사용
- 앙상블 Week 1 구현 (Week 2 이후)
- 데이터 스누핑 (그리드 sweep 최고값 보고)
- Donchian/MA200 윈도우 잘못 환산

## 검증 전략

ZERO HUMAN INTERVENTION (자동 검증 가능):
- 모든 Task는 Acceptance 기준 + Evidence 경로를 가져야 함
- 모든 백테스트는 사전 지정 파라미터 + 데이터 해시 검증
- backtest-reviewer 에이전트가 룰 준수 검증
- Evidence 경로: `.evidence/{task-id}-{slug}.txt`

## 현재 Task 상태

| Task | 상태 | 주차 | 상세 문서 |
|------|------|:----:|-----------|
| W1-01 | Done | 1 | [Week 1 계획](./stage1-weekly/week1.md) · [sub-plan](./stage1-subplans/w1-01-data-collection.md) |
| W1-02 | Done | 1 | [Week 1 계획](./stage1-weekly/week1.md) · [sub-plan](./stage1-subplans/w1-02-strategy-a-daily.md) |
| W1-03 | Done | 1 | [Week 1 계획](./stage1-weekly/week1.md) · [sub-plan](./stage1-subplans/w1-03-strategy-b-daily.md) |
| W1-04 | Done | 1 | [Week 1 계획](./stage1-weekly/week1.md) · [sub-plan](./stage1-subplans/w1-04-robustness.md) |
| W1-05 | Done | 1 | [Week 1 계획](./stage1-weekly/week1.md) · [sub-plan](./stage1-subplans/w1-05-4h-experiment.md) |
| W1-06 | Done (No-Go 결정, 2026-04-17) | 1 | [Week 1 계획](./stage1-weekly/week1.md) · [sub-plan](./stage1-subplans/w1-06-week1-report.md) |
| W2-01 | Done (cycle 2 v5, 2026-04-19) | 2 | [Week 2 계획](./stage1-weekly/week2.md) · [sub-plan](./stage1-subplans/w2-01-data-expansion.md) |
| W2-02 | Done (v5, 2026-04-19) | 2 | [Week 2 계획](./stage1-weekly/week2.md) · [sub-plan](./stage1-subplans/w2-02-strategy-candidates.md) |
| W2-03 | **Done (Go 결정, 2026-04-20)** | 2 | [Week 2 계획](./stage1-weekly/week2.md) · [sub-plan v9](./stage1-subplans/w2-03-insample-grid.md) |
| W3-01 | **Done (No-Go, 프레임 C 학습 모드, 2026-04-22)** | 3 | [Week 3 계획](./stage1-weekly/week3.md) · [sub-plan v3](./stage1-subplans/w3-01-walk-forward.md) |
| W3-02 | **Cancelled (Stage 1 학습 모드 전환)** | 3 | N/A — W3-01 No-Go 종료, DSR/Bootstrap 미진행 |
| W3-03 | **Cancelled (Stage 1 학습 모드 전환)** | 3 | N/A — 전략 채택 결정 미진행 |
| W4-01 | **Cancelled (Stage 1 학습 모드 전환)** | 4 | N/A — Freqtrade 이식 미진행 |
| W4-02 | **Cancelled (Stage 1 학습 모드 전환)** | 4 | N/A |
| W6-01 | **Cancelled (Stage 1 학습 모드 전환)** | 6 | N/A — 페이퍼 트레이딩 미진입 |
| W8-01 | **Cancelled (Stage 1 학습 모드 전환)** | 8 | N/A — Stage 1 게이트 미진입. 라이브 50만원 옵션 상실 |

## 의존성 매트릭스

| Task | Depends On | Enables |
|------|------------|---------|
| W1-01 | none | W1-02, W1-03 |
| W1-02 | W1-01 | W1-04, W1-05, W1-06 |
| W1-03 | W1-01 | W1-04, W1-05, W1-06 |
| W1-04 | W1-02, W1-03 | W1-06 |
| W1-05 | W1-02, W1-03 | (W1-06에 참고만, 차단 X) |
| W1-06 | W1-02, W1-03, W1-04 | W2-* (재범위 후) |
| W2-01 | W1-06 (결정 완료) | W2-02 |
| W2-02 | W2-01 (데이터 freeze) | W2-03 |
| W2-03 | W2-01, W2-02 | W3-01 (Go 시) |
| W3-01 | W2-03 (Go) | W3-02, W3-03 |
| W3-02 | W3-01 | W3-03 |
| W3-03 | W3-02 | W4-01 |
| W4-01 | W3-01 | W4-02 |
| W4-02 | W4-01 | W6-01 |
| W6-01 | W4-02 | W8-01 |
| W8-01 | W6-01 (2주 결과) | Stage 2 (Week 9+) |

## 주차별 상세

- **Week 1**: [`stage1-weekly/week1.md`](./stage1-weekly/week1.md) — 일봉 복제 스프린트 (Done, No-Go)
- **Week 2**: [`stage1-weekly/week2.md`](./stage1-weekly/week2.md) — 재범위 + 알트 확장 + 전략 재탐색 (Done, Go)
- **Week 3**: [`stage1-weekly/week3.md`](./stage1-weekly/week3.md) — walk-forward + DSR + 전략 채택 (In Progress, W3-01 sub-plan v1 2026-04-21)
- **Week 4~8**: [`stage1-weekly/week4-8-pending.md`](./stage1-weekly/week4-8-pending.md) — Pending (진입 시점에 주차별 분할)

## 잔존 정정 Task (cross-Task, 우선순위 순)

| ID | 설명 | 트리거 | 영향 | 처리 시점 |
|----|------|--------|------|----------|
| ~~**PT-01**~~ | ~~W1 sqrt(252) vs W1-06 sqrt(365) 일관성 정정~~ — **해소 (2026-04-20 실측 반증)** | ~~W2-03 v8 2차 외부 감사 WARNING~~ → **오인 박제**. vectorbt 0.28.5 실측 확인: `vbt.settings.returns['year_freq']` = `'365 days'` (공식 default). 따라서 W1-02/03/04/06 `pf.sharpe_ratio()` default 호출 = 이미 sqrt(365) 기반. W2-03 `year_freq='365 days'` 명시 호출과 **bit-level 일치** (BTC_A Sharpe 1.0353 양쪽 동일) | 불일치 없음 (실측 확인). 재계산 **불필요** | **해소됨 (2026-04-20)**. 절충안: 향후 벡터bt 업그레이드 또는 Freqtrade 이식 시점 (W4+) 에 `year_freq='365 days'` **명시 호출**로 노트북 일괄 갱신 권고 (버전 의존 제거 목적). 현재는 수치 정확하므로 재계산 없음 |
| PT-02 | `.gitignore` vs sub-plan 박제 충돌 | handover #20. W1-01 `data_hashes.txt` + cycle 1 snapshot JSON이 `.gitignore`로 제외되어 있으나 sub-plan은 "git tracked"로 박제 | 감사 시 "박제와 실제 git 상태 불일치" 발견 가능 | W3-01 sub-plan 작성 시 data_hashes 경로 처리 결정 후 일괄 반영 |
| PT-03 | 이전 PC 글로벌 memory 디렉토리 마이그레이션 | 새 PC(riss) 이동 후 `/Users/riss/.claude/projects/-Users-riss-project-coin-bot/memory/`가 빈 디렉토리였음 (handover v12 L25). v13에서 신규 작성 완료 | 이전 PC 글로벌 memory가 남아있다면 병합 필요. 없으면 v13 신규 작성만으로 충분 | 필요 시 별도 마이그레이션 task 작성 (이전 PC 접근 가능 시점). handover v13 작성 시 memory 신규 작성으로 부분 해소 (2026-04-20) |
| PT-04 | **`year_freq='365 days'` 명시 호출 일괄 갱신** | PT-01 해소 후속 (2026-04-20 외부 감사 WARNING-3). 현재 W1-02/03/04/06 노트북은 `pf.sharpe_ratio()` default 호출에 의존 = vectorbt 0.28.5 default `'365 days'`에 의존. 미래 벡터bt 업그레이드 시 default 변경 리스크 존재 | 벡터bt 업그레이드 또는 Freqtrade 이식 시점 (W4+)에 숫자 재현 실패 가능 | **W4-01 Freqtrade 이식 진입 시점** 일괄 갱신. W1-02/03/04/06 + W2-03 + 미래 Week 3 walk-forward 노트북 모두 `pf.sharpe_ratio(year_freq='365 days')` 명시 호출로 전환. 버전 의존 제거 |
| PT-05 | **외부 lib API 추측 박제 방지 기계적 가드 (hook) 검토** | PT-01 해소 감사관 개인 의견 (2026-04-20). cycle 1 학습 #16 "외부 API 추측 금지" **누적 3회째 재발** (vectorbt `td_stop` / `from_signals`의 `year_freq` / default `year_freq`). memory 박제만으로는 부족 | 4회째 재발 가능 | Week 3 walk-forward 진입 이후 여유 시점. claude-code hook 또는 pre-commit hook으로 "외부 lib default/파라미터 박제 시 실측 증거 (`.evidence/`에 `inspect.signature` 또는 `settings` 출력) 필수" 체크. 실제 작성은 별도 사이클 |

## QA / Evidence Rules

- 모든 Task는 happy path와 denial path를 함께 가진다 (denial = "Sharpe < threshold일 때 Fail 처리")
- 모든 백테스트는 (사전 지정 파라미터 + 데이터 해시 + vectorbt API 검증 + Wilder 스무딩) 4가지 룰 준수
- backtest-reviewer 에이전트 호출 → APPROVED 받기 전엔 다음 Task 못 시작
- Evidence 파일 형식: `.evidence/{task-id}-{slug}.txt`
- Evidence 6단 구조: 1) 데이터, 2) 파라미터, 3) 결과, 4) 자동 검증, 5) 룰 준수, 6) Code review

## 최종 검증 (Stage 1 종료 시)

- [x] F1. 모든 16개 Task Evidence 파일 서명됨 — 9개 Done (W1-01~W1-06, W2-01~W2-03), 7개 Pending (W3-01~W8-01)
- [x] F2. Week 1 Go 통과 → Week 2 진행 — ~~Go~~ No-Go (2026-04-17) → Week 2 재범위로 전환
- [ ] F3. Week 3 전략 채택 결정 명시
- [ ] F4. Week 8 페이퍼 2주 결과 평가 → Stage 2 진행 또는 학습 모드

## 커밋 전략

- 각 Task는 vertical commit (노트북 + 결과 + Evidence + status 업데이트)
- 커밋 메시지 형식: `prefix(plan): Feature-ID Task-ID 기능명 — 작업 내용` (2026-04-21 사용자 명시 요청)
  - `feat(plan)`: 새 Task 완료
  - `docs(plan)`: 문서 변경
  - `chore(plan)`: 환경/세팅
  - `fix(plan)`: 버그 수정
  - `refactor(plan)`: 구조 개선
- **필수 포함 (제목)**: (1) `Feature-ID` (예: BT-004, STR-A-001) + (2) `Task-ID` (예: W3-01, PT-01) + (3) **기능명** (예: Walk-forward analysis, Strategy A Recall) + (4) 작업 내용 간략
- 예시 (좋음): `feat(plan): BT-004 W3-01 Walk-forward sub-plan v2 — Anchored 5-fold + 옵션 A 5/5 Go 기준 + WARNING 8/NIT 7 반영`
- 예시 (나쁨, 기능명 누락): `fix(plan): W3-01 재검증 정정`
- Evidence 파일은 같은 commit에 포함

## 성공 기준

- 8주 내 페이퍼 트레이딩 초기 2주 데이터가 백테스트 결과와 ±30% 이내 일치
- 사용자가 "Stage 2 진행해도 좋다"고 명시 승인
- 모든 Evidence 파일 서명 + git 커밋 완료
