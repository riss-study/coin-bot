# Stage 1 실행 계획서 (Week 1~8)

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
- Evidence 파일 14개 (각 Task 완료 서명)
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

## 실행 전략

### 진행 단위
- 작업/리뷰/재시작 단위는 개별 Task
- Week 단위는 보고/리뷰 주기
- Sub-plan reference: `./stage1-subplans/{task-id}-*.md`

### 현재 Task 상태

| Task | 상태 | 주차 | 상세 문서 |
|------|------|:----:|-----------|
| W1-01 | Done | 1 | [데이터 수집](./stage1-subplans/w1-01-data-collection.md) |
| W1-02 | Done | 1 | [Strategy A 일봉](./stage1-subplans/w1-02-strategy-a-daily.md) |
| W1-03 | Done | 1 | [Strategy B 일봉](./stage1-subplans/w1-03-strategy-b-daily.md) |
| W1-04 | Done | 1 | [강건성 + 민감도](./stage1-subplans/w1-04-robustness.md) |
| W1-05 | Done | 1 | [4시간봉 실험](./stage1-subplans/w1-05-4h-experiment.md) |
| W1-06 | Done | 1 | [Week 1 리포트](./stage1-subplans/w1-06-week1-report.md) (No-Go 결정, 2026-04-17) |
| W2-01 | Done (cycle 2, 2026-04-19) | 2 | [데이터 확장 + 페어 선정](./stage1-subplans/w2-01-data-expansion.md) cycle 2 v5 — Tier 2 = [XRP,SOL,TRX,DOGE] |
| W2-02 | Done (v5 사용자 승인 발효, 2026-04-19) | 2 | [새 전략 후보 사전 등록](./stage1-subplans/w2-02-strategy-candidates.md) — Candidate C/D Active/Registered |
| W2-03 | **Done (Go 결정, 2026-04-20)** | 2 | [In-sample 백테스트 grid](./stage1-subplans/w2-03-insample-grid.md) **v8** — 사용자 Option C 명시 채택 ("ㄱㄱ"). V_empirical 채택 후 재평가: **is_go=True (5/6 Go cells)**. BTC_A/C/D, ETH_A/D Go 통과 / ETH_C FAIL. Strategy A Recall 발동 (Retained → Active). 외부 감사 2회 APPROVED with follow-up. Week 3 진입 |
| W3-01 | **Ready (진입 가능, 2026-04-20)** | 3 | Walk-forward analysis (Strategy A/C/D). V_empirical 일관 적용 + floor 재도입 금지 + 임계값 변경 금지 의무 (v8 2차 감사 WARNING-3). 실패 시 Stage 1 킬 카운터 +2 소급 (v8 2차 감사 WARNING-4). **선행 필수: PT-01 W1 sqrt 일관성 정정** (본 문서 "잔존 정정 Task" 참조) |
| W3-02 | Pending | 3 | TBD — DSR + Bootstrap (원래 W2-02에서 이전) |
| W3-03 | Pending | 3 | TBD — 전략 채택 결정 |
| W4-01 | Pending | 4 | TBD |
| W4-02 | Pending | 4 | TBD |
| W6-01 | Pending | 6 | TBD |
| W8-01 | Pending | 8 | **Stage 1 게이트** |

### 의존성 매트릭스

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

## 작업 목록

> Implementation + Test + Docs sync = ONE task. Never separate.
> 모든 Task는 사전 지정 파라미터 + Acceptance + QA + Commit 메시지 명시.

### Week 1 — 일봉 복제 스프린트

- [x] **W1-01. 데이터 수집 + 환경 세팅** (Feature: DATA-001) — Done 2026-04-14
  - **What**: pyupbit로 KRW-BTC 일봉/4h 5년치 다운로드, 타임존 localize, advertised 범위 slicing, Parquet freeze, SHA256 해시 기록. requirements.lock + git init.
  - **Must NOT**: 4시간봉을 Go/No-Go 기준으로 사용 금지. 데이터 인덱스 timezone naive 방치 금지.
  - **Acceptance**:
    - [x] 일봉 1927 bars, 4h 11561 bars 수집 (advertised [2021-01-01, 2026-04-12) UTC)
    - [x] 갭 < 0.1% (daily 0%, 4h 0.0086%)
    - [x] tz_localize KST → UTC 완료
    - [x] data_hashes.txt 생성 (advertised + actual 범위 헤더)
    - [x] requirements.lock 생성 (142 packages)
    - [x] backtest-reviewer APPROVED
  - **QA**: `jupyter nbconvert --to notebook --execute --inplace notebooks/01_data_collection.ipynb` → 산출물 검증
  - **Evidence**: `.evidence/w1-01-data-collection.txt`
  - **Commit**: `feat(plan): DATA-001 Week 1 데이터 수집 + 환경 세팅`

- [x] **W1-02. Strategy A 일봉 백테스트** (Feature: STR-A-001) — Done 2026-04-14
  - **What**: 200MA + Donchian(20/10) + 거래량 1.5x + 고정 8% 하드 스톱(sl_stop=0.08). 사전 지정 파라미터로 vectorbt 백테스트.
  - **Must NOT**: ts_stop, td_stop 사용 금지. 데이터 스누핑 금지. MA200 윈도우 ≠ 200 금지.
  - **Acceptance**:
    - [x] 사전 지정 파라미터 명시 선언
    - [x] 데이터 해시 검증 통과
    - [x] vectorbt 크래시 없이 실행
    - [x] outputs/strategy_a_daily.json 생성
    - [x] backtest-reviewer 에이전트 APPROVED
  - **결과**: Sharpe 1.0353 (PASS > 0.8), MDD -22.45% (PASS < 50%), Trades 14, PF 2.956, Win Rate 50%
  - **WARNING**: Trade 수 14 < 20 (sub-plan 리스크), W1-06에서 low-N caveat 명시 필요
  - **Evidence**: `.evidence/w1-02-strategy-a-daily.txt`
  - **Commit**: `feat(plan): STR-A-001 Strategy A 일봉 백테스트`

- [x] **W1-03. Strategy B 일봉 백테스트** (Feature: STR-B-001) — Done 2026-04-14
  - **What**: 200MA + RSI(4)<25 진입 + RSI(4)>50 청산 + entries.shift(5) 시간 스톱 + sl_stop=0.08.
  - **Must NOT**: bars_held 변수 참조 금지. RSI 직접 구현 금지 (ta 라이브러리 사용).
  - **Acceptance**:
    - [x] 사전 지정 파라미터 명시
    - [x] 시간 스톱 entries.shift(N) 패턴 사용
    - [x] outputs/strategy_b_daily.json 생성 (v3 schema)
    - [x] backtest-reviewer 에이전트 APPROVED (trace 저장)
  - **결과**: Sharpe 0.1362 (**FAIL < 0.5**), MDD -21.27% (PASS), Trades 39, PF 1.092
  - **해석**: Method 정확, 결과는 W1-06 Go/No-Go 영역. Strategy A 단독 채택 가능성 높음.
  - **Evidence**: `.evidence/w1-03-strategy-b-daily.txt`

- [x] **W1-04. 강건성 + 민감도 분석** (Feature: BT-001) — Done 2026-04-16
  - **What**: 연도별 분할 (2021~2026Q1) + 파라미터 민감도 그리드 (참고용)
  - **Must NOT**: 그리드 최고값을 Go/No-Go에 사용 금지. 사전 지정 파라미터만 결정 근거.
  - **Acceptance**:
    - [x] 5개 연도별 Sharpe/MDD/Return 계산
    - [x] 민감도 등고선 차트 (MA, Donchian, RSI 임계)
    - [x] 사전 지정 파라미터가 평탄 영역에 위치 확인
  - **결과**: A 평탄성 std=0.044 PASS, B std=0.170 PASS. A 3/5년 양수, B 4/5년 양수.
  - **목표**: 5개 연도 중 최소 2개 양수 수익 — Strategy A PASS (3개), B PASS (4개)
  - **Evidence**: `.evidence/w1-04-robustness.txt`
  - **Commit**: `feat(plan): BT-001 강건성 + 민감도 분석`

- [x] **W1-05. 4시간봉 포팅 실험** (Feature: BT-002) — Done 2026-04-17
  - **What**: 동일 전략을 4시간봉으로 (MA1200, Donchian 120/60, RSI(4))
  - **Must NOT**: Week 1 Go/No-Go 기준으로 사용 금지 (참고용 only)
  - **Acceptance**:
    - [x] 4h 윈도우 환산 정확 (200일 = 1200 bars)
    - [x] 일봉 결과와 비교 표
    - [x] outputs/strategy_4h_comparison.json
  - **결과**: A 4h Sharpe 1.12 (robust), B 4h Sharpe -0.61 (실패). 참고용.
  - **Evidence**: `.evidence/w1-05-4h-experiment.txt`
  - **Commit**: `feat(plan): BT-002 4시간봉 포팅 실험`

- [ ] **W1-06. Week 1 리포트 + Go/No-Go** (Feature: REPORT-001)
  - **What**: 모든 결과 통합 + Go/No-Go 결정 + 사용자 보고
  - **Must NOT**: 결과 부풀리기 금지. 한계/경고 명시.
  - **Acceptance**:
    - [ ] week1_report.md 작성
    - [ ] 사전 지정 파라미터 결과만 평가
    - [ ] Go 기준 모두 충족 여부 명시
    - [ ] 사용자 명시적 승인
  - **Go 기준 (모두 충족)**:
    - Strategy A 일봉 Sharpe > 0.8
    - Strategy B 일봉 Sharpe > 0.5
    - 두 전략 중 하나라도 MDD < 50%
    - 두 전략 중 하나라도 5개 연도 중 최소 2개 양수
    - 사전 지정 파라미터가 민감도 평탄 영역
  - **Evidence**: `.evidence/w1-06-week1-report.txt`
  - **Commit**: `docs(plan): Week 1 리포트 + Go/No-Go 결정`

### Week 2 — 재범위 (Week 1 No-Go 후, 2026-04-17 결정)

**원래 Week 2** (walk-forward/DSR 중심)는 Strategy A/B 확정 엣지 전제였으나 Week 1에서 엣지 확보 실패. Week 2를 **"전략 후보 재탐색 + 메이저 알트 확장"**으로 재설계. Walk-forward는 Week 3로 이전. DSR은 Week 2 Go 기준에 **부분 포함** (B-3 CRITICAL 이슈 해소).

- [ ] **W2-01. 데이터 확장 + 페어 선정 사전 지정** (Feature: BT-003)
  - 페어 선정 기준 사전 지정 (시총 상위, 상장 3년+, 유동성)
  - Tier 1 필수: BTC (W1 재사용), ETH
  - Tier 2 후보 (cycle 1 박제, **cycle 2 v5에서 ADA → TRX 정정** 2026-04-19): **XRP, SOL, TRX, DOGE**
  - 영구 제외: 상장 <3년 (PEPE), 시총 <50위
  - SHIB는 옵션 (밈 특성으로 Week 2 불포함, 추후 별도 실험 트랙 검토)
  - 5년 일봉/4h 데이터 수집 + SHA256 freeze + data_hashes.txt 갱신
  - Sub-plan: `stage1-subplans/w2-01-data-expansion.md`
  - Depends: W1-06 (No-Go 결정 완료)
  - **상태**: cycle 1 v4 사이클 중단 (Fallback ii) → cycle 2 v5 완료 (2026-04-19, Tier 2 = [XRP, SOL, TRX, DOGE], Common-window = 2021-10-15 UTC)

- [ ] **W2-02. 새 전략 후보 사전 등록** (Feature: STR-NEW-001)
  - Candidate C: Slow Momentum (MA50/200 crossover + ATR(14)×3 trailing stop) - Moskowitz et al. 2012 시계열 모멘텀 기반
  - Candidate D: Volatility Breakout (Keltner Channel + Bollinger Band 동시 돌파)
  - (옵션) Candidate E: BTC/ETH 스프레드 차익거래 - 복잡도 높아 Week 4+로 이전 가능
  - 파라미터 freeze (BTC 데이터 보지 않고 문헌 근거로 결정)
  - Strategy A 파라미터는 **후보 풀에 보관** (W2-03 grid 포함)
  - Strategy B는 구조적 엣지 부재 확인으로 폐기 (grid 미포함)
  - 사전 등록 문서: `docs/strategy-preregistration-week2.md`
  - Sub-plan: `stage1-subplans/w2-02-strategy-preregistration.md` (W2-01 완료 후 작성)
  - Depends: W2-01

- [ ] **W2-03. In-sample 백테스트 grid + Week 2 리포트** (Feature: BT-005)
  - **Primary 대상 (Go 기준 적용)**: Tier 1 {BTC, ETH} × {A, C, D} = **6셀**
  - **Exploratory 대상 (참고용, Go 기여 X)**: Tier 2 {XRP, SOL, **TRX**, DOGE} × {A, C, D} = 12셀 (cycle 2 v5 박제 ADA → TRX 정정)
  - 사전 지정 파라미터 고정 (알트별 튜닝 금지, data snooping 금지)
  - 결과 표: Sharpe, MDD, PF, Trades + **DSR (Bailey & López de Prado 2014)** per primary cell
  - **Week 2 게이트 기준 (사전 지정, 다중 검정 보정 포함)**:
    - Primary: Primary 6셀 중 적어도 **1개 전략이 BTC 또는 ETH에서 Sharpe > 0.8 AND DSR > 0**
    - Secondary (마킹용, Go 기여 X): 동일 전략이 Tier 1+2 3+ 페어에서 Sharpe > 0.5 → ensemble 후보로 표시
    - 미달 → Stage 1 킬 카운터 +1, Week 3 재탐색
  - **다중 검정 한계 인정**: 6 primary 셀은 여전히 family-wise 오류 여지 있음. DSR은 이를 부분적으로 완화. 최종 엣지 검증은 Week 3 walk-forward에서 이뤄짐.
  - 사용자 명시적 Go/No-Go 승인
  - Sub-plan: `stage1-subplans/w2-03-in-sample-grid.md` (W2-02 완료 후 작성)
  - Depends: W2-01, W2-02

### Week 3~8 — Sub-plan 미정 (Week 2 Go 후 작성)

- [ ] **W3-01. Walk-forward analysis** (Feature: BT-004) — 원래 W2-01에서 이전
- [ ] **W3-02. Deflated Sharpe + Monte Carlo + Bootstrap** (Feature: BT-006) — 원래 W2-02에서 이전
- [ ] **W3-03. 전략 채택 결정 + Stage 1 체크포인트 #1** (Feature: STR-FINAL-001)
- [ ] **W4-01. Freqtrade 이식** (Feature: PAPER-001)
- [ ] **W4-02. Docker + TimescaleDB + 시크릿** (Feature: PAPER-002)
- [ ] **W6-01. 페이퍼 트레이딩 시작** (Feature: PAPER-003)
- [ ] **W8-01. Stage 1 게이트 평가** (Feature: GATE-001) ← **결정적 분기**

각 Task의 sub-plan은 직전 Task 종료 후 작성. Week 2 Go 못 받으면 W3~ 추가 재탐색.

## 잔존 정정 Task (cross-Task, 우선순위 순)

| ID | 설명 | 트리거 | 영향 | 처리 시점 |
|----|------|--------|------|----------|
| **PT-01** | **W1 sqrt(252) vs W1-06 sqrt(365) 일관성 정정** | W2-03 v8 2차 외부 감사 WARNING (handover #21). W1-04 robustness / W1-02·03 strategy JSON은 vectorbt default `year_freq='252 days'` 적용. W1-06 리포트와 W2-03은 sqrt(365) 채택 | W3-01 walk-forward에서 W1 산출물 재인용 시 cross-comparison 불일치. Stage 1 게이트 평가 숫자 오독 위험 | **W3-01 진입 전** 필수 정정. strategy_a_daily.json + strategy_b_daily.json + robustness_sensitivity.json Sharpe 재계산 + sqrt(365) 재저장 + week1_report.md 갱신 + evidence 정정 |
| PT-02 | `.gitignore` vs sub-plan 박제 충돌 | handover #20. W1-01 `data_hashes.txt` + cycle 1 snapshot JSON이 `.gitignore`로 제외되어 있으나 sub-plan은 "git tracked"로 박제 | 감사 시 "박제와 실제 git 상태 불일치" 발견 가능 | W3-01 sub-plan 작성 시 data_hashes 경로 처리 결정 후 일괄 반영 |
| PT-03 | 이전 PC 글로벌 memory 디렉토리 마이그레이션 | 새 PC(riss) 이동 후 `/Users/riss/.claude/projects/-Users-riss-project-coin-bot/memory/`가 빈 디렉토리였음 (handover v12 L25). v13에서 신규 작성 완료 | 이전 PC 글로벌 memory가 남아있다면 병합 필요. 없으면 v13 신규 작성만으로 충분 | 필요 시 별도 마이그레이션 task 작성 (이전 PC 접근 가능 시점). handover v13 작성 시 memory 신규 작성으로 부분 해소 (2026-04-20) |

## QA / Evidence Rules

- 모든 Task는 happy path와 denial path를 함께 가진다 (denial = "Sharpe < threshold일 때 Fail 처리")
- 모든 백테스트는 (사전 지정 파라미터 + 데이터 해시 + vectorbt API 검증 + Wilder 스무딩) 4가지 룰 준수
- backtest-reviewer 에이전트 호출 → APPROVED 받기 전엔 다음 Task 못 시작
- Evidence 파일 형식: `.evidence/{task-id}-{slug}.txt`
- Evidence 6단 구조: 1) 데이터, 2) 파라미터, 3) 결과, 4) 자동 검증, 5) 룰 준수, 6) Code review

## 최종 검증 (Stage 1 종료 시)

- [ ] F1. 모든 14개 Task Evidence 파일 서명됨
- [ ] F2. Week 1 Go 통과 → Week 2 진행
- [ ] F3. Week 3 전략 채택 결정 명시
- [ ] F4. Week 8 페이퍼 2주 결과 평가 → Stage 2 진행 또는 학습 모드

## 커밋 전략

- 각 Task는 vertical commit (노트북 + 결과 + Evidence + status 업데이트)
- 커밋 메시지 형식: `prefix: 한글 설명`
  - `feat(plan)`: 새 Task 완료
  - `docs(plan)`: 문서 변경
  - `chore(plan)`: 환경/세팅
  - `fix(plan)`: 버그 수정
- Feature ID 명시: `feat(plan): STR-A-001 ...`
- Evidence 파일은 같은 commit에 포함

## 성공 기준

- 8주 내 페이퍼 트레이딩 초기 2주 데이터가 백테스트 결과와 ±30% 이내 일치
- 사용자가 "Stage 2 진행해도 좋다"고 명시 승인
- 모든 Evidence 파일 서명 + git 커밋 완료
