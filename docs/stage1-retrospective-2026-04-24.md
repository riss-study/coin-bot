# Stage 1 학습 회고 보고서 (2026-04-24)

> **Feature ID**: LEARN-001
> **작성 시점**: Stage 1 학습 모드 전환 직후 (W3-01 No-Go 결정 2026-04-22로부터 2일 경과)
> **범위**: Day 0 (2026-04-13) ~ Stage 1 종결 (2026-04-22), 약 10일간
> **목적**: 실수/패턴/교훈을 휘발되기 전 문서화 + 다음 사이클 시사점 박제

---

## 0. 요약 (TL;DR)

- **Stage 1 결과**: No-Go (Week 1) → 재범위 Go (W2-03) → 재판정 No-Go (W3-01) → 학습 모드 전환
- **Stage 1 킬 카운터**: +3 (W1 +1, W2-03→W3-01 소급 +2)
- **라이브 투입(Stage 2) 포기**. 학습 자산 전부 git 보존.
- **핵심 학습**: cycle 1 #16 "외부 API 추측" **3회 재발**, V 선택 논쟁, retrospective 재판정 메커니즘 검증, 박제 체계 자체 루프 패턴 발견/차단

---

## 1. Stage 1 타임라인

| 시점 | 사건 | 결과 |
|------|------|------|
| 2026-04-13 | Day 0 (기획 + 박제 체계 확립) | decisions-final.md 통합 |
| 2026-04-14 ~ 04-17 | W1 (일봉 복제) | **No-Go (Option B)** — Strategy B 구조적 엣지 부재, A regime decay |
| 2026-04-17 | Week 2 재범위 | walk-forward → 전략 재탐색 + 알트 확장 |
| 2026-04-18 ~ 04-19 | W2-01 cycle 1→2 (페어 선정) | Fallback (ii) 발동, cycle 2 v5 완료 (Tier 2 TRX) |
| 2026-04-19 | W2-02 (전략 C/D 사전 등록) | Active/Registered |
| 2026-04-20 | W2-03 (In-sample grid) | **Go (Option C, V_empirical 채택)** — 5/6 Go cells |
| 2026-04-20 ~ 04-21 | W2-03 재검증 7회 + 구조 개선 | handover 축소, Week별 분리 |
| 2026-04-21 | W3-01 sub-plan v1→v2 | 외부 감사 1차 CHANGES REQUIRED → 반영 |
| 2026-04-22 | W3-01 실행 + No-Go | **옵션 C 채택, Stage 1 종결** |

---

## 2. 핵심 실수 패턴

### 2.1 cycle 1 학습 #16 "외부 lib API 추측" **3회 재발**

| 회차 | 박제 | 실측 반증 |
|------|------|-----------|
| 1회 | vectorbt `td_stop` / `ts_stop` / `max_duration` 파라미터 (초기 week1-plan.md) | `inspect.signature` 확인 결과 부재. TypeError 발생 위험 |
| 2회 | vectorbt `Portfolio.from_signals(year_freq=...)` 파라미터 (W2-03 v6 B-1) | `inspect.signature` 실측: `from_signals`에 없음, `sharpe_ratio` 메서드에만 존재 |
| 3회 | vectorbt **default** `year_freq='252 days'` (handover #21 + W2-03 v6 B-1) | `vbt.settings.returns['year_freq']` = **`'365 days'`** 실측. PT-01 오인 박제 전체 반증 |

**교훈**:
- 감사관도 실측 안 하면 간과. W2-03 v6 2차 외부 감사관이 3회차 추측 박제를 발견하지 못하고 APPROVED 판정 → PT-01 실행 단계에서 실측으로 반증
- **대응 박제**: `memory/feedback_api_empirical_verification.md` 신설, PT-05 (기계적 가드 hook 검토) 잔존 task 박제
- **근본**: "default는 X" 박제 전에 반드시 `inspect.signature` + `settings` + venv 호출 비교 필요

### 2.2 V 선택 논쟁 (self-imposed floor vs Bailey 원문 default)

- **v6 C-1 (2026-04-20)**: `V_reported = max(V_empirical, 1.0) = 1.0` "Bailey 2014 conservative 취지" 박제
- **v7 외부 감사 WARNING-1**: 이는 **Bailey 원문 절차 아님**. 프로젝트 self-imposed defensive floor. 정량적으로 V를 **9.78배 부풀리고 SR_0을 3.13배 엄격화**
- **v8 사용자 Option C 선택**: V_empirical default 복귀. Go cells 0→5로 전환 (BTC_A/C/D + ETH_A/D)
- **W3-01 결과**: 5 Go cells 중 0개 통과 → W2-03 Go 결정의 retrospective 재판정 성격 드러남

**교훈**:
- "Bailey 2014 권고"처럼 포장된 **self-imposed 조치**에 주의. 원문 참조와 프로젝트 자체 선택을 서술에서 명확히 구분
- 서술 정직화: "원문 해석 오류 교정" overclaim 아닌 **"서술 오류 인정 + default 복귀"** 프레이밍 사용 (v8 2차 감사 WARNING-1)
- **N=5 per fold sample variance 변동성 실측: 3-10배** (v2 "2배" 과소평가). 감사 2차에서 정량화. 이 정보가 사용자 옵션 A 선택 시점(2026-04-21)에 없었음 → 2026-04-22 재고려 권리 박제 (감사관 명시)

### 2.3 Retrospective 재판정 메커니즘 (검증 완료)

- **W2-03 v8 WARNING-4 박제**: Week 3 실패 시 Stage 1 킬 카운터 **+2 소급** + 외부 감사 재수행 + 사용자 명시 결정
- **2차 감사관 선제 박제**: "v8과 cycle 1 #5 본질 구분 어려움" 인정 → Week 3 결과가 W2-03 Go 정당성 소급 결정
- **W3-01 결과**: 자동 No-Go → +2 소급 발동 (현재 킬 카운터 +3, 킬 조건 충족)

**교훈**:
- Retrospective 재판정 메커니즘은 **cycle 1 #5 "Go 기준 사후 완화" 방어의 핵심**. 결과를 선판단하지 않고 후속 단계에서 사후 재판정하는 구조.
- Week 3 결과 0/5 Go cell은 "어느 기준으로든 실패"임을 확인 (옵션 B 4+/5로 완화해도 0). **사후 완화 필요성 없음 = cycle 1 #5 재발 위험도 자연 소멸**.
- 교훈의 정직화: 2차 감사관이 **"본질 구분 어려움"을 공식 인정**한 것 자체가 학술적 진전. 프레임 A/B 둘 다 부분 성립을 인정하는 프레임 C (감사관 추천 + 사용자 채택) 는 학습 프로젝트 정직성 모델.

### 2.4 박제 체계 자체가 만든 루프 패턴 (3종)

#### 2.4.1 "커밋 해시" 루프 (옵션 A로 차단)

- handover 본문에 미래 커밋 해시 박제 → 매 커밋 후 stale → 재검증에서 발견 → 정정 커밋 → 또 stale → **무한 루프**
- 3차 재검증까지 동일 패턴 재발
- **옵션 A (해시 박제 금지)**: 커밋 trail = `git log main` 참조로 단순화. handover 본문 박제 원칙 신설

#### 2.4.2 "잔존 task 개수" 루프 (옵션 나로 차단)

- handover 본문 + execution-plan 양쪽에 잔존 task 개수 중복 박제 → SSO 원칙 위반
- PT-* 신설/해소 시 handover 수동 갱신 누락 → 개수 불일치 재발 (2회)
- **옵션 나 (잔존 task 서술 삭제)**: handover는 "execution-plan 참조" 한 줄만 유지

#### 2.4.3 "재검증 자체" 루프 (handover 대폭 축소로 완화)

- 매 커밋 후 재검증 → 서술 수준 WARNING/NIT 발견 → 정정 → 또 재검증 → ...
- 7차 재검증까지 diminishing returns 구간 도달 (실질 위험 없는 서술 이슈만)
- **handover 387→68줄 축소 + archive 분리**: 유지보수 부담 최소화. 재검증 대상이 줄어들면 자연 완화

**교훈**:
- 박제가 **실질 가치**를 만드는지 **메타 유지보수**를 만드는지 주기적 점검 필요
- **Single Source of Truth 원칙** 엄격 적용: 동일 정보를 두 곳에 중복 박제 금지
- 사용자 명시 지적 ("인수인계 파일인데 누굴 인수인계할 필요 없는데 그렇게까지 필요해?") 에서 배워야 함 — 박제 체계 자체를 비판적으로 재평가

### 2.5 Strategy 개별 교훈

| Strategy | 실수/발견 | 교훈 |
|----------|-----------|------|
| A (Trend Following) | W1 2024년 단년 집중 + 2024-12-17 이후 481일 Sharpe -1.14 | Single strategy 의존 + regime decay 관측 시 stability 의심 |
| A (W3-01) | Donchian breakout 진입 희소 → fold 단위 N/A 다수 (BTC 2, ETH 4) | Walk-forward 설계 시 전략 진입 빈도 사전 검증 필수 |
| B (Mean Reversion) | Sharpe 0.14, 구조적 엣지 부재 → W1 Deprecated | 같은 철학(4일 RSI) 재도입 금지 박제 |
| C (Slow Momentum) | W2-03 5 trade (5년) → W3-01 5/5 fold N/A | 연 1 trade 수준 전략은 fold 단위 평가 부적합. Long-term 평균으로만 판단 가능 |
| D (Vol Breakout) | 상대적 최선 (BTC_D 3/5 fold pass). 단 fold 2/5 음수 | 엣지 있으나 stability 5/5 미달. 학습 자료 가치 |

### 2.6 사용자가 명시 지적한 Claude (나의) 과잉 해석

- "프로젝트 종결"을 **Stage 1 종결**과 혼동 (2026-04-24 사용자 지적)
- 재검증 루프 "더 해야 한다"고 반복 제안 → 사용자가 "근데 handover 그거 어차피 인수인계 파일 아니야?" 지적으로 축소
- handover 갱신 반복 제안 시점에 "기능명 + Task ID 필수" 원칙 박제 (사용자 명시 요청)

**교훈**:
- **사용자 질문의 날카로움**에서 지속 학습 필요. 내 답변이 과잉 확대인지 확인 후 응답
- CLAUDE.md 룰: "사용자에게 '직접 판단'을 무책임하게 떠넘기지 말 것" — 다만 내 추천도 편향 체크 필요

---

## 3. 박제 체계 진화 기록

### 3.1 신설/변경된 박제 시스템

| 시점 | 항목 | 영향 |
|------|------|------|
| Day 0 | decisions-final.md 단일 진실 + CLAUDE.md 룰 | 전체 박제 기반 |
| Week 1 말 | candidate-pool.md 신설 | Strategy 상태 물리적 저장 |
| W2-01 | cycle 진화 체계 (cycle 1→2) + Fallback (ii) 누적 한도 | cherry-pick 차단 |
| W2-03 | 외부 감사관 페르소나 정례화 + DSR 공식 Bailey 2014 박제 | 학술 정확성 |
| W2-03 재검증 | 옵션 A (해시 루프 차단) + 옵션 나 (잔존 task 서술 삭제) | SSO 일관 |
| Week별 분리 | stage1-weekly/ 신설 | EPIC 뷰 ↔ 주차 상세 분리 |
| 커밋 메시지 | Feature-ID + Task-ID + 기능명 필수 | trail 추적성 |
| Memory 시스템 | 글로벌 memory 6개 신규 작성 | 미래 세션 컨텍스트 복구 |
| PT-01 해소 | feedback_api_empirical_verification.md + PT-04/PT-05 신설 | cycle 1 #16 재발 대응 |

### 3.2 재발 방지 박제 정리

- **cycle 1 #5 "Go 기준 사후 완화"**: 변경 금지 서약 체계 + cycle N 강제 mechanism + retrospective 재판정 메커니즘
- **cycle 1 #16 "외부 API 추측"**: memory `feedback_api_empirical_verification.md` + PT-05 기계적 가드 hook 검토
- **감사관 자체 간과**: "API default 실측 확인 필수" 감사관 호출 시 명시 지시 추가 박제
- **handover 변동성 정보 루프**: "본문 박제 원칙" 섹션 신설 (허용/금지 대상 명시)

---

## 4. 다음 사이클 시사점

### 4.1 Stage 1 재시작 시 반드시 반영할 것

1. **Walk-forward 설계 전 전략 진입 빈도 사전 검증**: Strategy A/C처럼 fold당 0-1 trade 수준 전략은 fold 단위 평가 부적합. Long-term 평균으로만 평가 가능하거나, min_trade_count 필터 대신 다른 aggregation 방식 고려
2. **V 선택 원칙 사전 박제**: N=5 per fold sample variance는 본질적으로 3-10배 변동. Pooled V or per-fold V 선택을 **설계 단계에서 명시** (결과 보기 전)
3. **다중 검정 보정 재산정 의무**: W3-02에서 Bonferroni cutoff (25 trial → 0.2% → DSR_z ≈2.88) 사전 박제 후 진행
4. **프레임 C 중간 입장 옵션 상시 고려**: 단순 A/B 양자택일이 아닌 "둘 다 부분 성립" 가능성 사전 박제

### 4.2 박제 체계 지속 개선안

1. **Handover 본문 박제 원칙 강화**: 이미 옵션 A/나 적용. 새로운 변동성 정보 타입 발견 시 금지 목록 추가
2. **재검증 루프 차단 원칙**: diminishing returns 구간 도달 시 "자연스러운 재검증 포인트" (sub-plan 완성 / Go-No-Go 결정 전)로 제한
3. **외부 감사관 지시에 "실측 확인 필수" 상시 포함**: 메모리 반영 완료, 매 호출 시 활용
4. **결정 문서 프레이밍 정직화**: "원문 복귀" overclaim 경계, "서술 오류 인정 + 변경" 프레이밍 선호

### 4.3 학술적/방법론적 학습

- **Bailey & López de Prado 2014 DSR 실제 적용**: 이론 → 구현 → 감사 검증 + 정정 사이클 경험
- **Anchored walk-forward 설계 trade-off**: test 6개월 / 5 folds / min_trade_count 선택이 결과에 미치는 영향 실증
- **암호화폐 regime 변화 + 전략 엣지 유지 어려움**: W1 Strategy A 2024년 집중 + 2025 regime decay 사례가 reproduce 됨 (W3-01에서 fold 4/5 stability 낮음)
- **Pardo 2008 70-80% stability 기준 vs 극단 조건 (5/5)**: 옵션 A (5/5) vs B (4+/5) 결과 동일 (0/5) = 설계 문제 > 기준 문제

---

## 5. 보존된 학습 자산

### 5.1 코드 + 결과 (git 유지)

- 노트북 9개: `research/notebooks/0{1..9}_*.ipynb`
- 노트북 생성기: `research/_tools/make_notebook_0{1..9}.py`
- 백테스트 결과 JSON: `research/outputs/strategy_*.json`, `w2_03_*.json`, `w3_01_walk_forward.json`
- 데이터 freeze: 6 페어 × 1d + BTC 4h (SHA256 박제, gitignored but data_hashes.txt 유지)

### 5.2 박제 문서 (git 유지)

- `docs/decisions-final.md` (모든 결정 통합, 700+ lines)
- `docs/architecture.md` (시스템 설계)
- `docs/glossary.md` (용어집 + 자바 비유)
- `docs/candidate-pool.md` v6 (Strategy A/B/C/D 상태)
- `docs/stage1-execution-plan.md` (EPIC 뷰)
- `docs/stage1-weekly/week1.md` / `week2.md` / `week3.md` / `week4-8-pending.md`
- `docs/stage1-subplans/w1-01~w1-06, w2-01~w2-03, w3-01` sub-plans (변경 이력 전체)

### 5.3 검증 trace (git 유지)

- `.evidence/w*-*-*.md` (6단 구조 evidence)
- `.evidence/agent-reviews/` (backtest-reviewer + 외부 감사관 trace 20+)

### 5.4 세션 인수인계 (git 유지)

- `.claude/handover-2026-04-17.md` (v13 축소판, 68 lines)
- `.claude/handover-archive-2026-04-17.md` (전체 역사, 387 lines)

### 5.5 글로벌 memory (git 밖, `~/.claude/projects/.../memory/`)

- `MEMORY.md` + `user_profile.md` + `feedback_external_audit.md` + `feedback_cherry_pick_guard.md` + `feedback_handover_warning_flow.md` + `feedback_api_empirical_verification.md` + `project_stage1_status.md` + `reference_docs.md`

---

## 6. 감정적/비기술적 학습 (솔직)

### 6.1 Claude 측 (나의 정직한 회고)

- **과잉 확대 해석 재발**: "프로젝트 종결" ↔ "Stage 1 종결" 혼동. 사용자가 즉시 지적
- **재검증 루프 자동 제안 경향**: "diminishing returns 구간"이라는 개념을 뒤늦게 인지. 사용자 지적 "그렇게까지 필요해?"로 각성
- **추측 박제 3회 재발**: cycle 1 #16 학습했다고 생각했으나 실제로는 완전 학습 X. 실측 습관 자체가 부족
- **외부 감사관 페르소나 효용**: 적대적 관점이 제대로 작동 (V floor overclaim 발견, BTC_D 3/5 단독 Go 통로 차단 등)

### 6.2 프로젝트 측 (사용자 관점)

- **학습 프로젝트 북극성 유지**: Stage 1 No-Go여도 학습 자산 보존 + 박제 체계 진화로 가치 회수
- **cycle 1 학습 #5 방어 성공**: Go 기준 사후 완화 없이 깨끗한 종결
- **정직성 모델 확립**: 프레임 C (둘 다 공식 인정)는 단순 A/B 양자택일보다 학술적으로 진전

### 6.3 개선 여지

- 박제 체계 자체의 유지보수 부담 주기적 점검 (옵션 A/나 패턴 정기 적용)
- 재검증 횟수 상한선 암묵 설정 (예: 3회 이상 재발 시 구조 변경 필수)
- "N=5 V 3-10배 변동" 같은 정량적 실측을 **설계 단계**에서 시뮬레이션하는 관행 (W3-01 sub-plan v1 작성 시 이를 알았더라면 옵션 A 5/5 선택이 달랐을 가능성)

---

## 7. Stage 1 재시작 가능 조건 (미래 시점)

본 회고는 "Stage 1 재시작 여부" 결정에 시사점을 제공하나, **본 결정은 지금 하지 않음** (사용자 옵션 C 채택에 따라 학습 모드 유지).

재시작 시 사전 검토할 것:

1. **시장 환경 변화**: W1/W2/W3 데이터 freeze(2026-04-12) 이후 추가 관측 데이터 확보
2. **설계 재조정**: test 기간 확장 (6개월 → 12개월), min_trade_count 기준 재검토, per-fold V vs pooled V 사전 박제
3. **전략 재탐색**: Strategy A/C/D Retained 상태 재평가 + 새 전략 패밀리 (예: cross-sectional momentum, mean-reversion with different lookback) 후보
4. **학술 방법론 보강**: Pardo 2008 + López de Prado 2018 "Advances in Financial Machine Learning" Chapter 7 (Cross-Validation in Finance) 재검토
5. **기계적 가드 (PT-05) 구현**: 외부 lib API 추측 방지 hook 작성 — cycle 1 #16 재발 물리적 차단

---

## 8. 이 회고의 한계

- **Stage 1 종결 직후 작성 = hot take 성격**. 시간이 지나 관점이 변할 수 있음
- **Claude 자기 회고 bias**: 적대적 감사관 페르소나로 재검토하면 추가 발견 가능
- **수치/통계 분석 심화 부족**: Strategy D BTC_D fold 2/5 음수 원인 분석, N=5 V 변동성 시뮬레이션 등은 별도 심화 분석 필요 (본 회고에서는 언급만)

---

**End of Stage 1 retrospective. Generated 2026-04-24 by claude-opus-4-7.**

관련 문서:
- 결정 원본: [`decisions-final.md`](./decisions-final.md) "W1 No-Go 결정" + "W2-03 Go 결정" + "W3-01 No-Go 결정 + 프레임 C"
- EPIC 뷰: [`stage1-execution-plan.md`](./stage1-execution-plan.md)
- 주차별 상세: [`stage1-weekly/week1.md`](./stage1-weekly/week1.md) + [`week2.md`](./stage1-weekly/week2.md) + [`week3.md`](./stage1-weekly/week3.md)
- 감사 trace: `.evidence/agent-reviews/` 디렉토리
