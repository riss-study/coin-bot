# Task W2-03 — In-sample 백테스트 grid + Week 2 리포트 + Go/No-Go

**상태**: **v6** (B-1 vectorbt API 사실 오류 정정 + C-1 Go 기준 DSR V[SR_n] 선택 박제 명시화 + W2-03.0 노트북 빌드/실행 검증 완료, 2026-04-20). **변경 금지 서약 발효 중** (W2-03.0~.7 박제 + 방법 B 채택 + DSR conservative V_reported 채택). 의미 변경 X (사실 오류 정정 + 모호성 해소), **변경 금지 서약 위반 X**.

## 변경 이력

| 버전 | 날짜 | 변경 | 트리거 |
|------|------|------|--------|
| v1 | 2026-04-19 | 첫 작성. W2-02 v5 사용자 승인 발효 직후. Tier 1 6 primary + Tier 2 12 exploratory + DSR + Go/No-Go 평가 박제 | sub-plan 신설 |
| **v2** | **2026-04-19** | **1차 외부 감사 BLOCKING 4 + WARNING 6 + NIT 5 정정**: B-1/B-2 (DSR 공식 Bailey & López de Prado 2014 원문 정확 박제 + Φ⁻¹/γ Euler-Mascheroni + V[SR_n] sample variance + DSR_z form "DSR > 0" 의미 명확화) / B-3 (5 페어 → 6 페어) / B-4 (Strategy A vs C/D 재평가 의무 대칭 박제) / W-1 (sqrt(365) annualization + W1 sqrt(252) 일관성 깨짐 발견 → handover #21 신규 패턴 별도 task) / W-2 (V[SR_n] 협소성 alarm + Stage 2 재산정 의무) / W-3 (vectorbt multi-asset 방식 A/B 박제) / W-4 (Common-window vs max-span 비대칭 cherry-pick 차단) / W-5 (ta KeltnerChannel API 호출 본 sub-plan 직접 박제) / W-6 (BTC W1-01 + W2-01.4 데이터 출처 + freeze 종료일 박제) / NIT-1~5 (외부 감사 단계 W2-03.7 신설 + Stage 1 킬 카운터 정의 + 6단 evidence + 파일명 확정) | 1차 외부 감사 |
| **v3** | **2026-04-19** | **2차 외부 감사 APPROVED with follow-up + 옵션 A 정정 (NIT-N1/N2/N3 + NIT-1~4 + W-N1)**: NIT-N1 (L94 "5 페어" → "신규 5 + BTC 재사용 = 6 페어 총") / NIT-N2 (candidate-pool.md L41/L55 Strategy C/D Recall 의무 cross-document 박제) / NIT-N3 (decisions-final.md L515 Tier 2 ADA → TRX cycle 2 정정) / NIT-1 (W2-03.7 외부 감사 SubTask 신설) / NIT-2 (Stage 1 킬 카운터 정의 + 현재 값 박제) / NIT-3 (6단 evidence 항목 명시) / NIT-4 (evidence 파일명 placeholder 실행 시점 결정) / W-N1 (DSR_z + DSR_prob 동시 보고 책무) | 2차 외부 감사 + 사용자 결정 (옵션 A) |
| **v4** | **2026-04-19** | **3차 외부 감사 APPROVED (BLOCKING 0 + WARNING 0) + NIT-3rd-1 정정 (stage1-execution-plan.md L207/L227 + w2-01-data-expansion.md L281 ADA → TRX cycle 2 v5 cross-document 정정) + NIT-3rd-2 정정 (candidate-pool.md v3 변경 이력 행 추가) + 사용자 최종 승인 발효** ("ㄱㄱㄱㄱ"). 변경 금지 서약 발효 + W2-03.0 진입 가능 | 3차 외부 감사 + 사용자 명시 승인 |
| **v5** | **2026-04-19** | **W2-03.1 W-1 미니 테스트 완료 + 방법 B 사용자 채택 박제** ("ㄱㄱ"). 결과: 방법 A return 23.51% vs 방법 B 26.52% (차이 3.01%p > 임계값 0.5%p) + 외부 감사 W-2 발견 (vectorbt sl_trail=True는 entry bar 시점 비율 freeze, 박제 의도 "매 bar 동적 ATR trailing"과 본질적으로 다름) → **방법 B (manual trailing_high - ATR_MULT × ATR(t) exit_mask) 채택**. Strategy C 구현 박제 정확화 + candidate-pool.md L37 cross-document 정정. **synthetic data 한계 인정 W2-03.6 리포트 박제 추가 (자가 검증 라운드 10 신규 발견)** | W2-03.1 + 외부 감사 + 사용자 채택 |
| **v6** | **2026-04-20** | **외부 감사관 페르소나 재검증 + 노트북 실행 검증 + 2건 정정**: **B-1** (vectorbt 0.28.5 `Portfolio.from_signals`에 `year_freq` 파라미터 **실측 부재** 확인, `inspect.signature`로 cycle 1 학습 #16 "외부 API 추측" 재발 차단). L53/L98/L130 박제 정정 = `from_signals`에 `freq='1D'`만 전달 + `pf.sharpe_ratio(year_freq='365 days')` 메서드 호출로 연율화 적용. **C-1** (sub-plan L161-163 Go 기준 DSR V[SR_n] 선택 모호성 = cycle 1 학습 #7 "사전 지정 기준 미정의" 재발 소지). Go 기준 DSR = **v_reported = max(v_empirical, 1.0) 적용 (Bailey 2014 conservative 취지)** 박제 명시화 + v_empirical 결과는 투명 보고 목적 병기. **W2-03.0 노트북 빌드 + dry-run 실행 검증 완료** (`research/notebooks/08_insample_grid.ipynb` exit 0, 18셀 grid + DSR unit test 정상). 부수 효과로 W2-03.2~.5 자동 실행 결과 생성 (결과: **is_go=False, conservative 기준 Go 통과 셀 0개, Secondary 마킹 A/C/D 모두**) — W2-03.6 사용자 결정 시점에 병기 보고 | 외부 감사 재검증 + API 실측 + 노트북 실행 검증 |

## 메인 Task 메타데이터

| 항목 | 값 |
|------|-----|
| **메인 Task ID** | W2-03 |
| **Feature ID** | BT-005 |
| **주차** | Week 2 (Day 5-7) |
| **기간** | 2.5일 (SubTask 순효용 ~2.4일 + buffer) |
| **스토리 포인트** | 8 |
| **작업자** | Solo + backtest-reviewer + 외부 감사관 + 사용자 Go/No-Go 결정 |
| **우선순위** | P0 (Stage 1 Week 8 킬 게이트 직접 입력) |
| **상태** | Pending |
| **Can Parallel** | NO (W2-03.1 → .2 → .3 → .4 → .5 → .6 순차) |
| **Blocks** | W3-* (walk-forward), Stage 1 게이트 평가 |
| **Blocked By** | W2-01 cycle 2 완료 + W2-02 v5 사용자 승인 발효 (모두 2026-04-19) |

## 배경

### Week 2 흐름

- W2-01 cycle 1 → cycle 2: Tier 1 [BTC, ETH] + Tier 2 [XRP, SOL, TRX, DOGE] 확정 + Common-window = 2021-10-15 UTC (SOL 기준)
- W2-02 v5: Candidate C (Slow Momentum, MA50/200 + ATR×3 trail) + Candidate D (Volatility Breakout, Keltner+Bollinger) Active/Registered + 변경 금지 서약 발효
- candidate-pool.md v2: Strategy A Retained (재진입 조건 충족 시 Active) + B Deprecated + C/D Active

### 박제 출처

- `docs/decisions-final.md`:
  - L513-521 "Week 2 게이트" (Primary 6셀 Sharpe>0.8 AND DSR>0 + Secondary Sharpe>0.5 ensemble + 다중 검정 한계)
  - L549-551 "Strategy A 후보 풀 물리적 정의 + Recall mechanism"
  - L595-611 "cycle 1 격리 양성 목록" + "Fallback (ii) 누적 한도 = 3회"
- `docs/pair-selection-criteria-week2-cycle2.md` v5 (Tier 1+2 + Common-window)
- `docs/stage1-subplans/w2-02-strategy-candidates.md` v5 (Candidate C/D 박제)
- `docs/candidate-pool.md` v2 (Strategy A/C/D 진입/청산 + ta API 박제)

### 핵심 원칙

- **사전 지정 파라미터 고정 (튜닝 X)**: W2-02 v5 변경 금지 서약 발효 중. 알트별 튜닝 절대 금지 (cycle 1 학습 #2 + #17)
- **Primary vs Secondary 분리**: Tier 1 = Primary Go 평가 / Tier 2 = Secondary 마킹 (Go 기여 X, 사용자 #4 결정 박제)
- **SR annualization 박제 (W-1 정정 + B-1 v6 정정)**: **`annualized_SR = sqrt(365) × daily_SR`** (W1-06 패턴 채택, freq=1D 기준). vectorbt 0.28.5 default `year_freq='252 days'`와 다름 → **vectorbt API 실측 (v6 `inspect.signature`)**: `Portfolio.from_signals`에는 `year_freq` 파라미터 **없음** (B-1 정정). 연율화는 `pf.sharpe_ratio(year_freq='365 days')` 메서드 호출로 전달 (sharpe_ratio에는 year_freq 인자 존재) 또는 manual `np.sqrt(365) × pf.returns().mean() / pf.returns().std()` 산출. **W1-06 sqrt(365) vs W1-04 sqrt(252) 일관성 깨짐 발견** (handover 신규 패턴 #21 박제 권고, 별도 task로 W1 산출물 정정 필요). 본 W2-03은 sqrt(365) 채택 강제
- **DSR 계산 (Bailey & López de Prado 2014)**: Multiple testing 부분 완화. N_trials = 18 (6 primary + 12 exploratory) 또는 6만 (Primary만)? **본 sub-plan에서 박제 결정 필요 (외부 감사 검증 포커스)**
- **Common-window vs max-span 이원 metric**: Primary = 페어별 max-span Sharpe / Secondary = common-window Sharpe (cycle 2 v5 박제)
- **Strategy A 재등장 시 Recall mechanism**: candidate-pool.md L69-80 박제 강제 적용
- **Go/No-Go 결정은 사용자 명시**: 자동 진행 X (cycle 1 학습)

## 개요

**6 페어** (Tier 1 BTC+ETH = 2 + Tier 2 XRP+SOL+TRX+DOGE = 4) × 3 전략 (A, C, D) = **18셀** In-sample grid 실행 (B-3 산술 정정). Primary 6셀 (Tier 1 × 3 전략) + Exploratory 12셀 (Tier 2 4 페어 × 3 전략). DSR 계산 + Multiple testing 한계 인정 + Go/No-Go 평가 + Week 2 리포트 + 사용자 결정.

## 현재 진행 상태

| SubTask | 상태 | 메모 |
|---------|------|------|
| W2-03.0 | **완료 (2026-04-20)** | `make_notebook_08.py` 작성 + `08_insample_grid.ipynb` 빌드 + dry-run 실행 검증 (exit 0). 자가 검증 5라운드 + 외부 감사관 페르소나 재검증 → B-1 (vectorbt API 사실 오류) + C-1 (DSR V 선택 모호성) 발견 + 정정 (v6 박제). 노트북 실행 결과로 W2-03.2~.5 자동 생성 (`research/outputs/w2_03_*.json`) |
| **W2-03.1** | **완료 (2026-04-19)** | **W-1 미니 테스트 결과: 방법 B 채택 박제** (return 차이 3.01%p > 임계값 + W-2 vectorbt sl_trail freeze 발견 → 박제 의도 위반). evidence: `.evidence/agent-reviews/w2-03-w1-test-review-2026-04-19.md` + `research/outputs/w2_03_w1_test.json` |
| W2-03.2 | **결과 생성 (2026-04-20, v6 자동 실행)** | Primary grid 6셀 실행 완료. 결과 JSON = `research/outputs/w2_03_primary_grid.json`. Sharpe (max-span): BTC_A 1.0353, BTC_C 0.9380, BTC_D 1.1818, ETH_A 1.1445, ETH_C 0.3237, ETH_D 1.0928. W2-03.6 분석 대기 |
| W2-03.3 | **결과 생성 (2026-04-20, v6 자동 실행)** | Exploratory grid 12셀 실행 완료. 결과 JSON = `research/outputs/w2_03_exploratory_grid.json`. Tier 2 Go 기여 X. W2-03.6 Secondary 마킹 분석 대기 |
| W2-03.4 | **결과 생성 (2026-04-20, v6 자동 실행)** | DSR 계산 완료. V_empirical=0.1023, V_reported=1.0 (conservative, Bailey 2014). SR_0 (reported) = 1.3001. 모든 Primary 6셀 DSR_z < 0. 결과 JSON = `research/outputs/w2_03_dsr.json` + unit test `w2_03_dsr_unit_test.json`. W2-03.6 분석 대기 |
| W2-03.5 | **결과 생성 (2026-04-20, v6 자동 실행)** | Go/No-Go 자동 평가 = **is_go=False** (conservative 기준, Go 통과 셀 0개). Secondary 마킹: A [BTC,ETH,SOL,DOGE] / C [BTC,XRP,SOL] / D [BTC,ETH,SOL,TRX,DOGE]. **사용자 명시 결정 (자동 진행 X)은 W2-03.6에서** |
| W2-03.6 | Pending | Week 2 리포트 + backtest-reviewer + **사용자 Go/No-Go 결정** (현 자동 결과 = No-Go, Stage 1 킬 카운터 +1 옵션 또는 Week 3 재탐색 vs Stage 1 종료) |
| **W2-03.7** | **Pending** | **외부 감사 (적대적, sub-plan + 결과 정합성, NIT-1 정정)**: cycle 1/2 W2-01.1/W2-02 패턴 = 1차/2차/3차 감사 사이클. 본 sub-plan은 v1 → v2 → v3 (1차+2차 감사 + 옵션 A 정정) 거침. W2-03.6 결과 사용자 Go/No-Go 결정 직전에 **추가 외부 감사 1회** (결과 정합성 + cherry-pick 통로 검증) 호출 |

## SubTask 목록

### SubTask W2-03.0: 노트북 08 생성기 작성

**작업자**: Solo
**예상 소요**: 0.3일

- [ ] `research/_tools/make_notebook_08.py` 작성 (W1-01/W2-01.4 nbformat 패턴 재사용)
- [ ] `research/notebooks/08_insample_grid.ipynb` 빌드
- [ ] 박제 상수:
  - `PAIRS_TIER1 = ["KRW-BTC", "KRW-ETH"]`
  - `PAIRS_TIER2 = ["KRW-XRP", "KRW-SOL", "KRW-TRX", "KRW-DOGE"]`
  - `STRATEGIES = ["A", "C", "D"]`
  - `RANGE = ("2021-01-01", "2026-04-12")` (W1-01 + W2-01.4 동일 advertised)
  - `COMMON_WINDOW_START = "2021-10-15"` (cycle 2 v5 박제, SOL 기준)
  - `YEAR_FREQ = "365 days"` (W-1 정정, sqrt(365) annualization)
  - Strategy A 파라미터 (candidate-pool.md L23 인용)
  - Strategy C 파라미터 (candidate-pool.md + W2-02 v5 인용)
  - **Strategy D 파라미터 + ta KeltnerChannel API 호출 본 sub-plan 직접 박제 (W-5 정정)**:
    - `KELTNER_WINDOW = 20`, `KELTNER_ATR_MULT = 1.5`, `BOLLINGER_WINDOW = 20`, `BOLLINGER_SIGMA = 2.0`, `ATR_WINDOW = 14`, `SL_HARD = 0.08`
    - `KeltnerChannel(window=20, window_atr=14, original_version=False, multiplier=1.5)` 명시 필수 (ta default와 다름, W2-02 v5 W3-1 박제)
- [ ] 데이터 로드 + SHA256 무결성 재검증 (W1-01 BTC + W2-01.4 신규 5 페어 = **총 6 페어**, W-6 + NIT-N1 정정)
- [x] vectorbt 0.28.5 검증된 API만 사용 (research/CLAUDE.md L73-95 패턴) + **`year_freq='365 days'` 메서드 호출 명시 강제 (W-1 정정 + B-1 v6 정정: `from_signals`에는 `freq='1D'`만, `pf.sharpe_ratio(year_freq='365 days')` 호출로 전달)**

### SubTask W2-03.1: W-1 미니 테스트 (ATR trailing stop)

**작업자**: Solo + backtest-reviewer
**예상 소요**: 0.2일
**박제 출처**: W2-02 v5 sub-plan L163 "W-1 추가 박제 (W2-03 책무)"

- [ ] **synthetic 데이터 생성**: 명확한 trend (linear + noise) 200 bars
- [ ] **방법 A 테스트**: vectorbt `sl_stop=Series(ATR_MULT*ATR/close)` + `sl_trail=True`
  - entry → trailing high 추적 → exit 시점 검증
  - 예상 동작: trailing high에서 ATR_MULT × ATR(14) 만큼 떨어진 시점 exit
- [ ] **방법 B 테스트 (방법 A 부정확 시)**: manual `trailing_high - ATR_MULT × ATR(14)` exit_mask 계산
- [ ] **결과 비교**: 방법 A vs B의 exit 시점/PnL 차이 측정
- [ ] **채택 결정**: 동작 일치 시 방법 A (간결), 차이 발견 시 방법 B (정확)
- [ ] **backtest-reviewer 호출**: 미니 테스트 결과 검증
- [ ] 채택 방법을 W2-03.2 Strategy C 구현에 박제

### SubTask W2-03.2: Primary grid 실행 (Tier 1 × {A,C,D} = 6셀)

**작업자**: Solo
**예상 소요**: 0.5일

- [ ] **데이터 로드 + SHA256 무결성 재검증 (W-6 정정)**:
  - BTC: `research/data/KRW-BTC_1d_frozen_20260412.parquet` (W1-01 freeze, SHA256 W1-01 evidence 박제값)
  - ETH/XRP/SOL/TRX/DOGE: `research/data/KRW-{X}_1d_frozen_20260412.parquet` (W2-01.4 cycle 2 freeze, SHA256 W2-01.4 evidence 박제값 6개)
  - **freeze 종료일 일관**: 모두 2026-04-12 UTC (W1-01 + W2-01.4 동일)
  - 불일치 시 W2-03 중단 + 사용자 보고 (cycle 2 패턴 cherry-pick 차단)
- [ ] **vectorbt multi-asset Portfolio 패턴 (W-3 정정)**:
  - **방식 A (각 페어 독립 Portfolio, 박제 채택)**: for-loop으로 페어별 Portfolio 산출 → metric 페어별 별도. 단순 + cash_sharing 무관 (단일 페어 평가)
  - **방식 B (multi-asset cash_sharing Portfolio)**: pd.concat으로 다중 close + entries/exits → group_by + cash_sharing=True. ensemble 시 사용
  - 본 박제 v2: **방식 A 채택** (Primary 6셀 = 페어별 단일 전략 평가, Go 기준 페어별 검증). 방식 B는 W3 ensemble 평가 시 적용
  - vectorbt API (B-1 v6 정정, `inspect.signature` 실측 기반): `vbt.Portfolio.from_signals(close=close_pair, entries=entries, exits=exits, sl_stop=..., sl_trail=..., init_cash=1_000_000, fees=0.0005, slippage=0.0005, freq='1D')` 강제 명시. **`year_freq`는 `pf.sharpe_ratio(year_freq='365 days')` 메서드 호출로 전달** (sharpe_ratio signature에 year_freq 파라미터 존재 실측 확인, from_signals에는 부재). W-1 sqrt(365) 박제 의도는 이 메서드 경로로 이행
- [ ] 6셀 vectorbt Portfolio 생성 (방식 A):
  - BTC × A, BTC × C, BTC × D
  - ETH × A, ETH × C, ETH × D
- [ ] **두 metric 동시 계산** (cycle 2 v5 박제):
  - **Primary metric**: 페어별 max-span Sharpe (각 페어 자체 상장일부터 2026-04-12 UTC)
  - **Secondary metric**: common-window Sharpe (2021-10-15 ~ 2026-04-12 UTC)
  - **W-4 정정 (cherry-pick 차단)**: 두 metric 비대칭 발생 시 (예: max-span Sharpe > 0.8 but common-window Sharpe < 0.5) **둘 다 사용자에게 보고**. **Go 기준 평가는 max-span (Primary) 단독**. common-window는 secondary 분석용. **사후에 common-window를 Go 기준으로 변경 = cherry-pick = cycle 3 강제**
- [ ] 추가 산출:
  - Total return, MDD, Win rate, # trades, Profit factor
  - 연도별 Sharpe (2021/2022/2023/2024/2025/2026 부분)
- [ ] 결과 저장: `research/outputs/w2_03_primary_grid.json`

### SubTask W2-03.3: Exploratory grid 실행 (Tier 2 × {A,C,D} = 12셀)

**작업자**: Solo
**예상 소요**: 0.5일

- [ ] 12셀 vectorbt Portfolio 생성:
  - XRP × {A,C,D}, SOL × {A,C,D}, TRX × {A,C,D}, DOGE × {A,C,D}
- [ ] 동일 metric 계산 (Primary + Secondary)
- [ ] **Go 평가 기여 X 명시 박제**: exploratory 결과는 참고용. Strategy 결정에 직접 영향 X
- [ ] Secondary 마킹 후보 식별: 동일 전략이 Tier 1+2 3+ 페어에서 `Sharpe > 0.5` → ensemble 후보 (W2-02 v5 박제)
- [ ] 결과 저장: `research/outputs/w2_03_exploratory_grid.json`

### SubTask W2-03.4: DSR 계산 + Multiple testing 평가

**작업자**: Solo + backtest-reviewer
**예상 소요**: 0.3일

- [ ] **N_trials 박제 결정 (B-1/B-2/W-2 정정 + C-1 v6 정정)**:
  - **본 박제: N_trials = 6 (Primary만)** — Tier 2 exploratory는 Go 기여 X (사용자 #4 결정)이므로 multiple testing 분모에서 제외
  - **W-2 alarm 박제 + C-1 v6 정정 (Go 기준 V 선택 명시화)**: V[SR_n]을 6셀 Sharpe sample variance로 산출 시 N=6 협소성으로 분산 추정 신뢰도 낮음. **두 버전 둘 다 산출**: (a) `V_empirical = np.var(primary_sharpes, ddof=1)`, (b) `V_normalized = 1.0` (보수적). **Go 기준 DSR 계산에는 `V_reported = max(V_empirical, 1.0)` 적용** (Bailey 2014 conservative 취지: multiple testing family-wise 오류 방어). **V_empirical 기준 DSR 결과도 리포트에 투명 병기** (사용자 결정 참고용이지만 Go 판정에는 V_reported만 사용). 사후에 V_empirical 채택으로 변경 = cherry-pick = cycle 3 강제 (cycle 1 학습 #7 + #10 재발 차단)
  - **Stage 2 게이트 시 재산정 의무**: ensemble 후보 마킹도 selection bias 기여. Stage 2 진입 시 N_trials 재계산 (별도 박제 사이클)

- [ ] **DSR 정확 공식 박제 (B-1/B-2 정정, Bailey & López de Prado 2014 원문 인용)**:

  **출처**: Bailey & López de Prado (2014) "The Deflated Sharpe Ratio: Correcting for Selection Bias, Backtest Overfitting, and Non-Normality" (SSRN 2460551, davidhbailey.com PDF, Wikipedia "Deflated Sharpe ratio")

  **단계 1 — SR_0 (Expected maximum Sharpe under H_0, B-1 정정)**:
  ```
  SR_0 = sqrt(V[SR_n]) × ((1-γ) × Φ⁻¹(1 - 1/N) + γ × Φ⁻¹(1 - 1/(N·e)))
  ```
  - γ = Euler-Mascheroni constant ≈ 0.5772156649
  - N = N_trials = 6
  - Φ⁻¹ = inverse standard normal CDF (`scipy.stats.norm.ppf`)
  - e ≈ 2.71828 (Euler's number)
  - V[SR_n] = 6 primary 셀 Sharpe sample variance (보수적). 비교용으로 1.0 정규화 결과도 동시 산출
  - **v1 박제 `sqrt(2 × ln(N_trials))`는 거친 근사 (N=6에서 약 38% 과대평가) → 본 v2에서 폐기**

  **단계 2 — DSR (z-score form, B-2 정정)**:
  ```
  DSR_z = (SR_hat - SR_0) × sqrt((T - 1) / (1 - γ_3 × SR_0 + ((γ_4 - 1) / 4) × SR_0²))
  ```
  - SR_hat = 측정 annualized Sharpe (W-1 정정: `sqrt(365) × daily_SR`, W1-06 패턴 채택)
  - T = 일봉 returns 개수 (페어별 max-span: BTC/ETH/XRP/TRX = 1927, SOL = 1640, DOGE = 1873)
  - γ_3 = skewness of daily returns (`scipy.stats.skew`)
  - γ_4 = kurtosis of daily returns (`scipy.stats.kurtosis`, Fisher form +3 또는 raw 명시)
  - 분모 SR은 **SR_0** (B-2 정정: v1은 SR_hat vs SR_0 모호)

  **단계 3 — Go 기준 명확화 (B-2 추가 정정, decisions-final.md L518 박제 의미 확정)**:
  - **"DSR > 0" = "DSR_z > 0" = "SR_hat > SR_0"** (z-score form, 본 박제 v2 채택)
  - Bailey 2014 원문 Φ wrapper 형태 "DSR_prob = Φ(DSR_z) > 0.5" 동치
  - 본 박제 v2는 **z-score form** 채택 (사용자 박제 "DSR > 0" 일치 + 단순)
  - 비교용으로 `DSR_prob = Φ(DSR_z)` 동시 산출 (사용자 보고용)

- [ ] 6 primary 셀 각각 DSR_z + DSR_prob 산출
- [ ] DSR_z > 0 셀 식별 (Go 기준 통과 후보)
- [ ] **Multiple testing 한계 박제 인용** (decisions-final.md L521): 6 primary 셀도 family-wise 오류 여지. DSR로 부분 완화. 최종 검증은 Week 3 walk-forward
- [ ] **단위 unit test 박제** (재현성 + 외부 감사 검증 가능성):
  - synthetic data로 SR_0/DSR_z 산출 + Bailey 2014 Table 1 (있으면) 또는 Wikipedia 예시와 비교
  - 결과 `research/outputs/w2_03_dsr_unit_test.json` 저장
- [ ] 결과 저장: `research/outputs/w2_03_dsr.json`

### SubTask W2-03.5: Go/No-Go 평가

**작업자**: Solo
**예상 소요**: 0.2일

- [ ] **사전 지정 Go 기준 적용** (decisions-final.md L518 박제):
  - Primary 6셀 중 **적어도 1개 전략이 BTC 또는 ETH에서 `Sharpe > 0.8 AND DSR > 0`** → Go
  - 미달 → No-Go (Stage 1 킬 카운터 +1, Week 3 재탐색)
- [ ] **Secondary 마킹** (decisions-final.md L519 박제, Go 기여 X):
  - 동일 전략이 Tier 1+2 3+ 페어에서 `Sharpe > 0.5` → ensemble 후보 마킹
- [ ] **Strategy A/C/D 모두 동일 재평가 의무 (B-4 정정)**:
  - **Strategy A 재등장 처리** (candidate-pool.md L69-80 Recall mechanism): Go 통과 시 Active 재전이 + DSR-adjusted + Week 3 walk-forward 재검증 의무
  - **Strategy C/D Active 평가 처리**: Go 통과 시 동일하게 DSR-adjusted + Week 3 walk-forward 재검증 의무 (Strategy A와 대칭). cherry-pick 차단 (특정 전략 우대 X)
  - 본 박제 v2: A/C/D 어느 전략이 Go 통과해도 Week 3 walk-forward 의무 강제. handover #14 cherry-pick 패턴 재발 차단
- [ ] **결과 사전 박제**:
  - Go 시: Week 3 walk-forward 진입
  - No-Go 시: Stage 1 킬 카운터 +1 → Week 3 재탐색 또는 Stage 1 종료 사용자 결정
- [ ] **인간 개입 금지**: Go 기준 변경 절대 금지 (cycle 1 학습 #5 임계값 완화 함정)

### SubTask W2-03.6: Week 2 리포트 + backtest-reviewer + 사용자 Go/No-Go 결정

**작업자**: Solo + backtest-reviewer + 사용자
**예상 소요**: 0.5일

- [ ] `research/outputs/week2_report.md` 작성:
  - W2-01 cycle 1 → cycle 2 흐름 (Fallback (ii) 발동 → 박제 정정)
  - W2-02 v5 Candidate C/D 사전 등록
  - W2-03 grid 결과 (6 primary + 12 exploratory)
  - **DSR 결과 (W-N1 명시 책무)**: DSR_z form (`SR_hat - SR_0` 단위) **+** `DSR_prob = Φ(DSR_z)` 동시 보고. 사용자 보고 시 두 표현 병기 (Bailey 2014 학계 표준 + 사용자 박제 "DSR > 0" 일치)
  - Multiple testing 한계 (decisions-final.md L521 인용)
  - Go/No-Go 자동 평가 (사전 지정 기준 적용)
  - Recall mechanism 적용 결과 (Strategy A 재전이 여부)
  - Soft contamination 인정 + Week 3 walk-forward 책무
  - **Stage 1 킬 카운터 박제 (NIT-2 정정)**: decisions-final.md L482 정의 인용 + 현재 값 박제. W1 No-Go 후 카운터 +1 여부는 본 W2-03.5/.6 사용자 결정 시점 박제 (Go 시 카운터 0 유지 + W3 진입 / No-Go 시 +1 + Week 3 재탐색 vs Stage 1 종료)
  - Stage 1 진행 상황 + 다음 단계 옵션
- [ ] **synthetic data 한계 인정 박제 (자가 검증 라운드 10 신규)**: W2-03.1 W-1 미니 테스트는 synthetic data로 방법 A vs B 차이 발견 (방향성 검증 적합). 실제 BTC/ETH 일봉 데이터에서 차이 magnitude는 다를 수 있음. **본 W2-03 grid 결과에서 방법 B 채택 결과의 실제 데이터 동작 검증 추가 보고 책무**
- [ ] **6단 evidence 작성 (NIT-3 정정)**: `.evidence/w2-03-insample-grid.txt` (또는 `.md`):
  - 1. **데이터**: 6 페어 SHA256 + freeze 종료일 + actual 범위
  - 2. **파라미터**: A/C/D 박제 상수 + ta API 호출 + sqrt(365) annualization
  - 3. **결과**: 18셀 grid 산출 (Sharpe, MDD, Win rate, # trades, PF, 연도별)
  - 4. **자동 검증**: 무결성 assert + DSR 단위 unit test + Common-window vs max-span 비대칭 보고
  - 5. **룰 준수**: 사전 지정 파라미터 변경 X + cherry-pick 차단 + Tier 2 Go 기여 X + Recall mechanism 강제
  - 6. **리뷰**: backtest-reviewer trace 인용
- [ ] backtest-reviewer 호출 (W1-06 패턴, 6단 evidence 구조)
- [ ] APPROVED with follow-up 받기
- [ ] **사용자에게 Go/No-Go 결정 보고**:
  - Go 시: W3 walk-forward 진입 컨펌
  - No-Go 시: Stage 1 킬 카운터 +1 + Week 3 재탐색 vs Stage 1 종료 옵션 제시
  - **사용자 명시적 결정 (자동 진행 X)**
- [ ] 사용자 결정 박제 (handover + decisions-final.md)
- [ ] 커밋: `feat(plan): BT-005 W2-03 grid + Week 2 리포트 + 사용자 Go/No-Go 결정`

## 인수 완료 조건 (Acceptance Criteria)

- [ ] `make_notebook_08.py` + `08_insample_grid.ipynb` 신설
- [ ] W-1 미니 테스트 결과 박제 + 방법 A/B 채택 결정
- [ ] Primary 6셀 grid 실행 + max-span/common-window 이원 metric
- [ ] Exploratory 12셀 grid 실행 + Secondary 마킹 식별
- [ ] DSR 계산 (N_trials 박제) + 6 primary 셀 각각 DSR 산출
- [ ] Go/No-Go 사전 지정 기준 적용 + Strategy A Recall mechanism 적용
- [ ] Week 2 리포트 작성 + backtest-reviewer APPROVED
- [ ] **사용자 명시 Go/No-Go 결정**
- [ ] 박제 갱신 (handover + sub-plan 체크박스 + execution-plan)

## 의존성 매트릭스

| From | To | 관계 |
|------|-----|------|
| W2-01 cycle 2 완료 | W2-03 | 페어 + Common-window + 데이터 freeze |
| W2-02 v5 완료 | W2-03 | Candidate C/D 사전 등록 + 변경 금지 |
| candidate-pool.md v2 | W2-03 | Strategy A Recall mechanism 강제 |
| W2-03 | W3-* | Go 시 walk-forward 진입. No-Go 시 Week 3 재탐색 또는 Stage 1 종료 |

## 리스크 및 완화 전략

| 리스크 | 영향 | 완화 |
|--------|------|------|
| W-1 ATR trailing 방법 A 부정확 | High | W2-03.1 미니 테스트 강제. 부정확 시 방법 B 채택 |
| DSR N_trials 박제 결정 (6 vs 18) | High | 외부 감사 검증 포커스. v1 추천 = 6 (Primary만). 외부 감사 권고 따름 |
| Multiple testing family-wise 오류 | High | DSR 부분 완화 + Week 3 walk-forward 최종 검증. 본 단계는 In-sample 예비 |
| Strategy A 재등장 + DSR 평가 누락 | Medium | candidate-pool.md L69-80 Recall mechanism 강제. backtest-reviewer 책무 |
| 알트 grid 결과 편향 → cherry-pick 유혹 | High | Tier 2 = Go 기여 X 박제. 사용자 결정 시 alarm |
| Common-window 누락 (max-span만 사용) | Medium | cycle 2 v5 박제 = 두 metric 동시. backtest-reviewer 검증 |
| ta KeltnerChannel API 호출 누락 (default 적용) | High | W2-02 v5 W3-1 박제 = `original_version=False` 명시 강제 |
| Go 기준 사후 변경 유혹 | **CRITICAL** | cycle 1 학습 #5 + #14 박제 강제. 변경 = cycle 3 강제 |
| Stage 1 킬 카운터 +1 후 Week 3 재탐색 vs 종료 결정 모호 | Medium | 사전 박제 X. **사용자 명시 결정 시점**에 옵션 제시 (자동 진행 금지) |

## 산출물 (Artifacts)

### 코드
- `research/_tools/make_notebook_08.py`
- `research/notebooks/08_insample_grid.ipynb`

### 데이터/결과 (gitignored)
- `research/outputs/w2_03_primary_grid.json` (6셀)
- `research/outputs/w2_03_exploratory_grid.json` (12셀)
- `research/outputs/w2_03_dsr.json`
- `research/outputs/week2_report.md`

### 검증
- `.evidence/w2-03-insample-grid-2026-04-XX.md` (6단 구조, 실행 시점 날짜 박제, NIT-4 정정)
- `.evidence/agent-reviews/w2-03-insample-grid-review-2026-04-19.md` (sub-plan 1차/2차 외부 감사 trace, 작성 완료) + `.evidence/agent-reviews/w2-03-insample-grid-result-review-2026-04-XX.md` (W2-03.7 결과 외부 감사, 실행 시점 작성)

### 박제 갱신
- `docs/stage1-subplans/w2-03-insample-grid.md` (이 파일, 체크박스 완료)
- `docs/stage1-execution-plan.md` (W2-03 상태)
- `.claude/handover-2026-04-17.md` (vN+1)
- `docs/decisions-final.md` (Go/No-Go 결정 박제)
- `docs/candidate-pool.md` (Strategy A 재전이 여부)

### 테스트 시나리오
- **Happy (Go)**: Primary 6셀 중 1+ 전략이 BTC 또는 ETH에서 Sharpe>0.8 AND DSR>0 → Week 3 진입
- **Denial 1 (No-Go)**: 모든 셀 미달 → Stage 1 킬 카운터 +1 → 사용자 결정 (Week 3 재탐색 vs Stage 1 종료)
- **Denial 2 (Strategy A 재등장)**: Strategy A가 Go 기준 통과 → Recall mechanism 강제 적용 (DSR + Week 3)
- **Edge (Secondary 후보)**: 동일 전략이 Tier 1+2 3+ 페어에서 Sharpe>0.5 → ensemble 후보 마킹 (Go 기여 X)
- **Edge (W-1 부정확)**: ATR trailing 방법 A 부정확 → 방법 B 채택 + Strategy C 구현 변경

## Commit (예상)

```
feat(plan): BT-005 W2-03 In-sample grid + Week 2 리포트 + 사용자 Go/No-Go 결정

- make_notebook_08.py + 08_insample_grid.ipynb 신설
- W-1 미니 테스트 (ATR trailing stop): 방법 A/B 채택 결정 박제
- Primary grid 6셀 (Tier 1 × {A,C,D}) + max-span/common-window 이원 metric
- Exploratory grid 12셀 (Tier 2 × {A,C,D}) + Secondary 마킹 (Go 기여 X)
- DSR 계산 (N_trials=?, 외부 감사 박제 결정) + 6 primary 셀 각각
- Go/No-Go 사전 지정 기준 (Sharpe>0.8 AND DSR>0) 적용
- Strategy A Recall mechanism 적용 결과 박제
- Week 2 리포트 + backtest-reviewer APPROVED with follow-up
- 사용자 명시 Go/No-Go 결정 (자동 진행 X)
- 다음 단계: Go → W3 walk-forward / No-Go → 사용자 결정 (재탐색 vs 종료)
```

---

**이전 Task**: [W2-02 v5 Candidate C/D 사전 등록](./w2-02-strategy-candidates.md) (2026-04-19 사용자 승인)
**다음 Task**: W3-* (Go 결과에 따라) 또는 Stage 1 진행 결정 (No-Go 시)
