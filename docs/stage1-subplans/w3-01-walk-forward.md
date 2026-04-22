# Task W3-01 — Walk-forward Analysis

**상태**: **v3** (2026-04-22, W3-01.7 **사용자 옵션 C 명시 채택 "3" = 프레임 C 학습 모드 전환**. Stage 1 킬 카운터 +2 소급 가산. Stage 1 실질적 조기 종료 (학습 모드 전환)).

## 변경 이력

| 버전 | 날짜 | 변경 | 트리거 |
|------|------|------|--------|
| v1 | 2026-04-21 | 첫 작성. Anchored walk-forward + 5 folds × 6개월 + V_empirical per fold + Go 이중 조건 (4+/5 fold pass AND 평균 pass). W2-03 Go cells (5 cell) 고정. W2-03 v8 WARNING-3/-4 강제 박제 | 사용자 설계 추천 채택 |
| **v3** | **2026-04-22** | **W3-01 실행 결과 No-Go 확정 + 사용자 옵션 C 명시 채택 "3" = 프레임 C 학습 모드 전환 + 외부 감사 2차 APPROVED with follow-up (WARNING 3 + NIT 2 반영) + Stage 1 킬 카운터 +2 소급**. **자동 결과**: is_go=False, go_cells=[] (0/5). 14/25 fold N/A (56%). Cell별: BTC_A 2/5, BTC_C 0/5 (전멸), BTC_D 3/5 (최고 근접), ETH_A 1/5, ETH_D 2/5. **외부 감사 2차 bit-level 재계산 일치 확인**. **감사관 신규 발견 (사용자 재고려 자료)**: (a) N=5 per fold V 변동성 실측 **3-10배** (v2 박제 "2배" 과소평가), (b) non-NA 1개 fold (fold 2/5)에서 V 산출 불가 = 구조적 한계, (c) V_empirical per fold 역설 = 엣지 강한 fold일수록 SR_0 임계 높아져 pass 어려움, (d) DSR_z 극단 fold 의존성 (γ_4=9-26). **5번째 cherry-pick 통로 신규 발견**: "BTC_D 3/5 = Pardo 60% → 단독 Go" 유혹 — 옵션 C 채택으로 자동 차단. **프레임 판단 (감사관 정직 판정)**: A 60% / B 40% 둘 다 부분 성립. **사용자 옵션 C 선택 = 둘 다 공식 인정** + Stage 1 학습 모드 전환 + **v3 박제 재탐색은 Stage 1 재시작 시점 전제** (지금은 미진행). **Strategy 처리**: A Active → Retained 복귀 (candidate-pool.md v6), C/D 학습 가치 보존 상태로 재분류. **Stage 1 킬 카운터 +2 소급** (W2-03 v8 WARNING-4 박제 발동 = 현재 총 +3 이상으로 Stage 1 킬 조건 충족). **v2 L277 정정**: "V 2배 변동" → **"실측 3-10배 변동"** (외부 감사 WARNING-A). **NIT-2 JSON native bool 재저장은 재실행 시점**으로 이월. **backtest-reviewer 1차 APPROVED with follow-up** (BLOCKING 0 / WARNING 1 fold train bar count 정정 완료 / NIT 2) — trace `.evidence/agent-reviews/w3-01-walk-forward-reviewer-2026-04-22.md`. **외부 감사 2차 APPROVED with follow-up** — trace `.evidence/agent-reviews/w3-01-walk-forward-result-review-2026-04-22.md`. **감사관 bias 선언 박제**: "sub-plan v2 '2배 변동' 과소평가 정보가 사용자 옵션 A 선택 시점(2026-04-21)에 없었음, 2026-04-22 재고려 권리 있음" → 사용자가 이 정보 반영하여 옵션 C (감사관 추천) 채택 | W3-01 결과 + 외부 감사 2차 + 사용자 옵션 C 직접 선택 |
| **v2** | **2026-04-21** | **외부 감사 1차 CHANGES REQUIRED (BLOCKING 0 / WARNING 8 / NIT 7) 반영 + 사용자 Go 기준 옵션 A 직접 선택 "2"**. **WARNING 8건**: W-1 fold 분할점 freeze 시점 명시 (v2 사용자 승인 시점 = freeze), W-2 Anchored/5-fold/6개월 설계 trade-off 논증 박제, W-3 Go cells 양방향 freeze (확장 X + 축소 X) 박제, W-4 W3-02 pooled V deferred가 Go 판정 번복 근거 X 명시 (cycle 1 #7 우회 차단), W-5 Go 기준 학술 근거 (Pardo 2008) + 대안 비교 표 + **옵션 A (5/5 모두 통과 + 평균) 사용자 직접 선택** 박제, W-6 25 trial family-wise 오류 완화 부족 인정 (DSR이 5 cell 변동만 반영, fold 변동 미포함) + W3-02 Bonferroni 재검증 책무, W-7 Strategy C low-N 완화 (`min_trade_count >= 2` 룰 박제, fold당 0 trade 시 FAIL 처리), W-8 Week 3 No-Go 시 W2-03 retrospective 해석 프레임 (A "cycle 1 #5 재발 확정" / B "극단 조건 + V_empirical 불안정 원인") 사전 박제. **NIT 7건**: NIT-1 Strategy C 방법 B 구현 명시 (manual exit_mask), NIT-2 Strategy C 단독 페어 N=5 통계 의미 (Strategy × Pair 변동성 혼재 인정), NIT-3 mean 사용 명시 (median 대체 금지), NIT-4 Active → Retained 역방향 복귀 (No-Go 시 candidate-pool.md v6 전이), NIT-5 PT-04 선행 적용 범위 "신규 노트북만" 명확화, NIT-6 Evidence 6단 "Go cells 고정 X" 오타 정정 → "양방향 freeze", NIT-7 "+2" 근거 설명 (W2-03 Go + W3-01 No-Go 이중 실패 = +1 + +1). **옵션 A 채택 근거**: N=5 per fold sample variance 불안정 (감사 독립 재계산: outlier 1개로 V 2배 변동) → 옵션 B (4+/5) 대비 옵션 A (5/5) 가 cherry-pick 통로 최대 차단. 학술적으로 Pardo 2008 70-80% stability 권고 초과하지만 retrospective 재판정 맥락 (W2-03 v8 "cycle 1 #5 본질 구분 어려움" 인정) 감안 시 정당화 | 외부 감사 1차 + 사용자 옵션 A 직접 선택 |

## 메인 Task 메타데이터

| 항목 | 값 |
|------|-----|
| **메인 Task ID** | W3-01 |
| **Feature ID** | BT-004 |
| **주차** | Week 3 (Day 1-3) |
| **기간** | 2.5-3.5일 (SubTask 순효용 + buffer) |
| **스토리 포인트** | 10 |
| **작업자** | Solo + backtest-reviewer + 외부 감사관 + 사용자 Go/No-Go 결정 |
| **우선순위** | P0 (Stage 1 Week 8 킬 게이트 직접 입력, W2-03 retrospective 재판정) |
| **상태** | v1 초안 (외부 감사 대기) |
| **Can Parallel** | NO (W3-01.0 → .1 → .2 → .3 → .4 → .5 → .6 순차) |
| **Blocks** | W3-02 (DSR + Bootstrap), W3-03 (전략 채택 결정), W4-01 (Freqtrade 이식) |
| **Blocked By** | W2-03 Go 결정 (2026-04-20 완료, `docs/decisions-final.md` "W2-03 In-sample grid Go 결정") |

## 배경

### Week 3 진입 근거

- **W2-03 Go 결정 (2026-04-20)**: Option C (V_empirical 채택) 사용자 명시 승인 "ㄱㄱ". 5/6 Go cells (BTC_A/C/D, ETH_A/D / ETH_C FAIL). Strategy A Recall 발동 (Retained → Active).
- **2차 감사관 박제**: "v8과 cycle 1 #5 본질 구분 어려움" 인정 → **Week 3 결과가 W2-03 Go 결정의 retrospective 재판정** 역할.
- **Stage 1 킬 카운터**: +1 유지 (W1 종료 시점). Week 3 실패 시 **+2 소급 가산** (W2-03 v8 2차 감사 WARNING-4).

### 박제 출처

- `docs/decisions-final.md` L518 "Week 2 게이트" + L522 "V 선택 최종 박제" + L690+ "W2-03 Go 결정"
- `docs/stage1-subplans/w2-03-insample-grid.md` v9 "SR annualization 박제" (vectorbt default year_freq='365 days' 실측 확인)
- `docs/candidate-pool.md` v5 (Strategy A Active 전이 + Recall 시 의무)
- `docs/stage1-weekly/week2.md` (Go cells 목록 + Secondary 마킹)

### 핵심 원칙 (v8 박제 강제 준수)

1. **V_empirical 일관 적용 (WARNING-3)**: 각 fold에서 V=sample variance 계산, floor 재도입 금지
2. **임계값 변경 금지 (WARNING-3)**: Sharpe > 0.8 AND DSR_z > 0 고정
3. **Fold별 DSR 재산정 의무 (WARNING-3)**
4. **실패 시 Stage 1 킬 카운터 +2 소급 (WARNING-4)** — **"+2" 근거 (NIT-7)**: W2-03 Go 결정(+1) + Week 3 No-Go(+1) 이중 실패로 가산. decisions-final.md L669 박제 + 외부 감사 재수행 + 사용자 명시 결정
5. **W2-03 Go cells 집합 양방향 freeze (NIT-6 / W-3)**: {BTC_A, BTC_C, BTC_D, ETH_A, ETH_D} 5 cell. **확장 X (ETH_C 재포함 / Secondary 마킹 포함 금지) + 축소 X (weak fold 기반 cell 제외 금지)**. 양방향 = cherry-pick 통로 전면 차단 = cycle 3 강제
6. **사전 지정 파라미터 변경 X (NIT-1)**: Strategy A/C/D W2-02 v5 박제값 + **Strategy C는 W2-03.1 방법 B 구현 (manual trailing_high - ATR_MULT × ATR(t) exit_mask)** 유지 (재튜닝 금지)
7. **Go 기준 사전 지정 (W-5)**: 본 sub-plan v2 승인 시점에 박제. 결과 본 후 완화 = cycle 3 강제 (cycle 1 학습 #5)
8. **W3-02 pooled V deferred Go 판정 번복 근거 X (W-4)**: W3-02 Bootstrap/Monte Carlo/pooled V는 **참고 metric만**. W3-01 Go 판정 번복 근거 X. 위반 시 cycle 3 강제 (WARNING-3 우회 통로 차단)
9. **Fold 분할점 freeze (W-1)**: 2023-10-15 / 2024-04-15 / 2024-10-15 / 2025-04-15 / 2025-10-15 UTC. **v2 사용자 승인 시점 = freeze 시점**. 결과 본 후 분할점 조정 = cherry-pick

## 개요

**5 cell (W2-03 Go cells) × 5 folds (Anchored walk-forward, 6개월 test) = 25 (cell, fold) 조합** 백테스트 실행. Fold별 Sharpe + DSR_z 산출. 사전 지정 Go 기준 적용. 사용자 명시 Go/No-Go 결정.

### 설계 trade-off 논증 (W-2 정정)

| 선택 | 채택 | 근거 |
|------|------|------|
| Anchored vs Rolling | **Anchored** | 암호화폐 regime 변화 (2022 하락/2024 상승) 고려 시 train 데이터 축적 유리. Rolling은 train window 축소로 sample size 저하. 단 구조적 regime shift 시 stale bias 가능 (완화: W3-02 bootstrap으로 검증) |
| 5 folds vs 3/10 | **5** | N=6 primary (W2-03)와 인접 일관성 + test 180일 확보. 3 folds = test 300일 과도 (regime 평균화), 10 folds = test 90일 과소 (거래 수 희소). Pardo 2008 "4-6 folds" 표준 일관 |
| Test 6개월 vs 3/12 | **6개월** | 암호화폐 평균 regime 지속 3-12개월 감안 중간값. Strategy C low-N 완화 + 분기별 cycle 반영 |

### Go 기준 대안 비교 + 옵션 A 채택 (W-5 정정)

**사전 지정 Go 기준 박제 (v2 사용자 직접 선택, 결과 보기 전 2026-04-21)**:

| 옵션 | Stability | Magnitude | Pardo 2008 70-80% 대응 | 채택 |
|------|-----------|-----------|------------------------|:----:|
| A | **5/5 (100%)** | 평균 Sharpe>0.8 AND 평균 DSR_z>0 | 초과 (보수) | **✓** |
| B | 4+/5 (80%) | 평균 pass | 일관 (표준) | — |
| C | 3+/5 (60%) | 평균 pass | 약간 느슨 | — |
| D | fold 수 무관 | 평균 pass | 미흡 | — |
| E | median pass (3/5) | 평균 pass | 애매 | — |

**옵션 A 채택 근거 (사용자 "2" 선택, 2026-04-21)**:
- N=5 per fold sample variance 불안정 (감사 1차 독립 재계산: outlier 1개로 V 2배 변동)
- 옵션 B (4+/5) 는 1 fold 예외 허용 → "outlier 핑계"로 cycle 1 #5 재발 통로
- 옵션 A (5/5) 는 **cherry-pick 통로 최대 차단**
- Pardo 2008 권고 초과 (80% → 100%) 하지만 **retrospective 재판정 맥락** (W2-03 v8 "cycle 1 #5 본질 구분 어려움") 감안 시 정당화
- Strategy A Recall mechanism의 "재평가 엄격 의무" 일관

## 현재 진행 상태

| SubTask | 상태 | 메모 |
|---------|------|------|
| W3-01.0 | Pending | `make_notebook_09.py` + `09_walk_forward.ipynb` 생성 |
| W3-01.1 | Pending | Fold 분할 sanity check (synthetic data 최소 검증) + 경계 bar count 확인 |
| W3-01.2 | Pending | 5 cell × 5 fold 백테스트 실행 (25 조합) |
| W3-01.3 | Pending | Fold별 Sharpe + DSR_z + aggregation (평균 + fold-pass count) |
| W3-01.4 | Pending | Go/No-Go 자동 평가 (사전 지정 이중 조건) |
| W3-01.5 | Pending | Week 3 리포트 + evidence + backtest-reviewer 호출 |
| W3-01.6 | Pending | 외부 감사 (적대적 페르소나, cherry-pick 통로 + V 일관성 + Go 기준 준수) |
| W3-01.7 | Pending | 사용자 명시 Go/No-Go 결정 (자동 진행 X) |

## SubTask 상세

### SubTask W3-01.0: 노트북 09 생성기 작성

**작업자**: Solo
**예상 소요**: 0.3일

- [ ] `research/_tools/make_notebook_09.py` 작성 (nbformat 패턴 재사용, make_notebook_08 스타일)
- [ ] `research/notebooks/09_walk_forward.ipynb` 빌드
- [ ] 박제 상수:
  - `CELLS = [("KRW-BTC", "A"), ("KRW-BTC", "C"), ("KRW-BTC", "D"), ("KRW-ETH", "A"), ("KRW-ETH", "D")]` (W2-03 Go cells 고정)
  - `FOLD_SPLIT_POINTS = ["2023-10-15", "2024-04-15", "2024-10-15", "2025-04-15", "2025-10-15"]` (UTC, 각 6개월 간격)
  - `TEST_WINDOW_DAYS = 180` (약 6개월)
  - `TRAIN_START = "2021-10-15"` (Common-window, W2-03 박제)
  - `YEAR_FREQ = "365 days"` (pf.sharpe_ratio(year_freq='365 days') 명시 — PT-04 선행 적용, cycle 1 #16 재발 방지)
  - Strategy A/C/D 파라미터 (candidate-pool.md v5 인용)
- [ ] 데이터 로드 + SHA256 재검증 (W1-01 BTC + W2-01.4 ETH, 2 페어만)
- [ ] vectorbt 0.28.5 API `pf.sharpe_ratio(year_freq='365 days')` 명시 호출 (default 의존 제거, **PT-04 신규 노트북 범위만 선행 적용**, NIT-5 정정. 기존 W1-02/03/04/06 + W2-03 노트북 갱신은 W4-01 Freqtrade 이식 시점 유지)

### SubTask W3-01.1: Fold 분할 sanity check

**작업자**: Solo
**예상 소요**: 0.2일

- [ ] 각 fold의 train/test bar count 계산 + 박제
  - Fold 1: train 2021-10-15 ~ 2023-10-15 (≈730d) / test 2023-10-15 ~ 2024-04-12 (≈180d)
  - Fold 2: train 2021-10-15 ~ 2024-04-15 / test 2024-04-15 ~ 2024-10-12
  - ... 등
- [ ] 각 fold의 test 기간 bar count가 ≈180 ±5% 확인 (weekend 등 없음, 일봉 기준 연속)
- [ ] Train 기간에 warmup (200 bar MA) 포함 확인
- [ ] 각 fold의 최소 거래 수 예상 (Strategy C는 진입 희소 → fold당 1-2 trade 가능성, low-N caveat 사전 인정)

### SubTask W3-01.2: Walk-forward 백테스트 실행

**작업자**: Solo
**예상 소요**: 0.8일

- [ ] 각 cell (BTC_A, BTC_C, BTC_D, ETH_A, ETH_D) × 각 fold (1~5)에 대해 vectorbt Portfolio 생성
  - Portfolio = 각 fold의 **test 기간만** 적용 (train 기간은 signal warmup 용도)
  - Strategy A/C/D 진입/청산 로직: candidate-pool.md v5 박제 그대로 (재튜닝 X)
  - Strategy C: 방법 B 트레일링 (manual trailing_high - ATR_MULT × ATR(t) exit_mask)
  - Strategy D: Keltner + Bollinger + SL 8% (W2-02 v5 박제)
- [ ] Fold별 metric:
  - Sharpe (max-span of test period, year_freq='365 days' 명시)
  - Total return, MDD, # trades, Win rate, PF
  - Daily returns 저장 (DSR 재산정 입력)
- [ ] 결과 저장: `research/outputs/w3_01_walk_forward.json` (25 entries + metadata)

### SubTask W3-01.3: Fold별 DSR + Aggregation

**작업자**: Solo + backtest-reviewer
**예상 소요**: 0.5일

- [ ] **Fold별 DSR_z 산출 (V_empirical 일관, v8 WARNING-3 강제)**:
  - 각 fold에서 **해당 fold의 5 cell Sharpe**의 sample variance = V_empirical_fold
  - SR_0_fold = `sqrt(V_empirical_fold) × ((1-γ)·Φ⁻¹(1-1/5) + γ·Φ⁻¹(1-1/(5·e)))`
  - N_trials = 5 (W2-03 Go cells 집합, 양방향 freeze)
  - DSR_z = Bailey 2014 eq. 10 (W2-03 v8 공식 동일)
  - **Floor 재도입 금지**: V_reported=max(V_emp, X) 같은 추가 조치 X
  - **N=5 통계 의미 주석 (NIT-2)**: Strategy C는 BTC_C 단독 cell. N=5 sample variance에 Strategy 변동성과 Pair 변동성이 혼재됨. Strategy 순수 변동성 = Week 3 이후 multiple strategy backtest에서 별도 검증 필요 (본 W3-01 범위 외)
- [ ] **Aggregation (NIT-3 mean 명시)**:
  - Cell별: 5 fold 중 Sharpe>0.8 AND DSR_z>0 통과 fold 수 (`fold_pass_count`)
  - Cell별: 5 fold **`np.mean` 평균 Sharpe, 평균 DSR_z (median 대체 금지)**. 이유: fold 변동성 높을 때 mean이 misleading할 수 있으나 stability 조건 5/5가 별도 담당
- [ ] **Strategy C low-N 처리 (W-7 정정)**:
  - BTC_C fold당 trade 수 < 2 인 fold: 해당 fold의 Sharpe/DSR_z = **`N/A` (FAIL 처리)**
  - `min_trade_count = 2` 사전 지정 (사후 완화 금지)
  - N/A fold는 `fold_pass_count` 에 미포함 (= fail 간주, 5/5 기준 자동 불통)
- [ ] **Multiple testing 한계 인정 (W-6 정정)**:
  - 25 trial (5 cell × 5 fold) family-wise 오류 여지
  - **DSR는 5 cell 변동만 반영, fold 변동 미포함** (부분 완화 한계 명시)
  - W3-02 Bootstrap + Bonferroni 조정 DSR_z cutoff (5% / 25 = 0.2% → cutoff ≈2.88) 재검증 책무
  - **W3-02는 참고 metric만, W3-01 Go 판정 번복 근거 X (핵심 원칙 #8)**

### SubTask W3-01.4: Go/No-Go 자동 평가

**작업자**: Solo
**예상 소요**: 0.2일

- [ ] **사전 지정 Go 기준 (v2 박제, 옵션 A 채택, 임계값 변경 금지)**:
  - 5 cell 중 **적어도 1개 cell**이 다음을 **모두** 충족:
    - **Stability 기준 (옵션 A, 5/5)**: 5 fold **모두**에서 Sharpe > 0.8 AND DSR_z > 0
    - **Magnitude 기준**: 5 fold `np.mean` 평균 Sharpe > 0.8 AND 평균 DSR_z > 0
  - 미달 → **No-Go**: Stage 1 킬 카운터 **+2 소급** + 외부 감사 재수행 + 사용자 명시 결정
- [ ] **No-Go 시 W2-03 retrospective 해석 프레임 사전 박제 (W-8 정정)**:
  - **프레임 A — "cycle 1 #5 재발 확정"**: W2-03 Go 결정이 사후 실패 확인. V_empirical 채택 자체가 Go 기준 완화 효과였음을 공식 인정. Stage 1 학습 모드 전환 강력 권고
  - **프레임 B — "극단 조건 + V_empirical 불안정 원인"**: 5/5 Go 기준이 과도 + per-fold V_empirical 불안정이 원인. W2-03 Go 결정 자체는 정당, Week 3 설계 문제. 재탐색 or 설계 재조정 옵션
  - **사용자가 No-Go 시점에 A vs B 선택**. A/B 모두 Stage 1 킬 카운터 +2 소급 유효 (차이는 후속 조치)
- [ ] **결과 박제**:
  - Go: Stage 1 킬 카운터 +1 유지 + W3-02 진입
  - No-Go: +2 소급 가산 + 프레임 A/B 선택 + 사용자 결정 옵션 제시
  - **Recall mechanism 역방향 (NIT-4)**: No-Go 시 Strategy A Active → Retained 복귀 + candidate-pool.md v6 상태 전이 + Recall mechanism 자동 해제
- [ ] **인간 개입 금지**: Go 기준 변경 절대 금지 (cycle 1 #5 재발 = cycle 3 강제)

### SubTask W3-01.5: Week 3 리포트 + Evidence + backtest-reviewer

**작업자**: Solo + backtest-reviewer
**예상 소요**: 0.4일

- [ ] `research/outputs/week3_report.md` 작성:
  - Walk-forward 설계 (Anchored / 5 folds / 6개월 test)
  - 25 조합 결과 (cell × fold 표)
  - Fold별 V_empirical + SR_0 + DSR_z 박제
  - Aggregation 결과 (cell별 fold_pass_count + 평균 Sharpe/DSR_z)
  - Go/No-Go 자동 평가
  - Multiple testing 한계 + Week 3 retrospective 재판정 맥락 (W2-03 v8 박제 인용)
- [ ] **6단 evidence** `.evidence/w3-01-walk-forward-2026-04-XX.md`:
  - 1. 데이터: BTC + ETH SHA256 + fold 분할점
  - 2. 파라미터: A/C/D 박제값 + fold 구조 + YEAR_FREQ='365 days'
  - 3. 결과: 25 조합 metric + fold별 DSR
  - 4. 자동 검증: fold 분할 sanity + V_empirical 일관 assert + DSR unit test
  - 5. 룰 준수: V_empirical 일관 + floor 재도입 X + 임계값 변경 X + W2-03 Go cells 양방향 freeze (확장 X + 축소 X) + min_trade_count ≥ 2 + mean aggregation (median 대체 X)
  - 6. 리뷰: backtest-reviewer trace 인용
- [ ] backtest-reviewer 호출 → APPROVED with follow-up 받기

### SubTask W3-01.6: 외부 감사 (적대적 페르소나)

**작업자**: 외부 감사관 페르소나 (general-purpose Agent)
**예상 소요**: 0.3일

- [ ] 감사 focus:
  - Cherry-pick 통로 (Go cells 집합 사후 확장 유혹, fold 정의 사후 조정, V 선택 floor 재도입 유혹)
  - V_empirical per fold 산출 정확성 (bit-level 재현)
  - Go 기준 "4+ fold + 평균" 이중 조건이 과도/과소 여부
  - Secondary 마킹 페어 (SOL/DOGE 등) 미포함의 정당성
  - Fold 수 5 + test 180일 설계의 trade-off
  - W2-03 v8 WARNING-3/-4 박제 준수 여부
- [ ] Trace 저장: `.evidence/agent-reviews/w3-01-walk-forward-review-2026-04-XX.md`
- [ ] APPROVED / APPROVED with follow-up / CHANGES REQUIRED / REJECTED 판정

### SubTask W3-01.7: 사용자 명시 Go/No-Go 결정

**작업자**: 사용자
**예상 소요**: 0.1일

- [ ] 자동 평가 + 외부 감사 결과 보고
- [ ] Go 시: W3-02 진입 컨펌
- [ ] No-Go 시: +2 소급 + 옵션 제시 (Week 3 재탐색 vs Stage 1 종료 vs V_empirical 해석 재검토)
- [ ] **사용자 명시 결정 (자동 진행 X)**
- [ ] 결정 박제 (handover + decisions-final.md + candidate-pool.md 갱신)

## 인수 완료 조건 (Acceptance Criteria)

- [ ] `make_notebook_09.py` + `09_walk_forward.ipynb` 신설 + dry-run 검증
- [ ] 5 cell × 5 fold = 25 조합 백테스트 완료
- [ ] Fold별 Sharpe + DSR_z + V_empirical 산출 (표준 Bailey 2014 공식)
- [ ] Aggregation (fold_pass_count + 평균) 완료
- [ ] Go/No-Go 사전 지정 기준 자동 평가
- [ ] Week 3 리포트 + 6단 evidence 작성
- [ ] backtest-reviewer APPROVED
- [ ] 외부 감사 APPROVED (또는 with follow-up, BLOCKING 0)
- [ ] **사용자 명시 Go/No-Go 결정**
- [ ] 박제 갱신 (handover + sub-plan + execution-plan + candidate-pool + decisions-final)

## 의존성 매트릭스

| From | To | 관계 |
|------|-----|------|
| W2-03 Go 결정 | W3-01 | Go cells 5개 집합 + V_empirical 채택 전제 |
| candidate-pool.md v5 | W3-01 | Strategy A/C/D 파라미터 + Recall 의무 |
| W2-03 v8 WARNING-3 | W3-01 | V_empirical 일관 + floor 금지 + 임계값 금지 의무 |
| W2-03 v8 WARNING-4 | W3-01 | 실패 시 +2 소급 절차 |
| W3-01 Go | W3-02 | DSR + Bootstrap + Monte Carlo 진입 |
| W3-01 No-Go | Stage 1 결정 | 학습 모드 vs 재탐색 사용자 결정 |

## 리스크 및 완화 전략

| 리스크 | 영향 | 완화 |
|--------|------|------|
| Fold별 거래 수 low-N (Strategy C 특히) | High | sub-plan v1에서 caveat 사전 박제. 필요 시 bootstrap으로 신뢰구간 산출 (W3-02 책무) |
| V_empirical per fold 불안정 (N=5, 각 fold 독립 산출) | High | 2차 감사 focus. 단위 unit test + 재현성 검증. W3-02에서 pooled V 대안 검토 |
| Anchored vs Rolling 선택 논쟁 재부상 | Medium | v1 Anchored 박제 강제. 변경 = cherry-pick = cycle 3 강제 |
| Fold 분할점 사후 조정 유혹 | High | v1 박제 5개 날짜 freeze (2023-10-15 / 2024-04-15 / 2024-10-15 / 2025-04-15 / 2025-10-15). 결과 본 후 조정 금지 |
| Go 이중 조건 옵션 A (5/5) 과도 — 모든 cell fail 가능성 | **HIGH** | **채택됨 (v2 사용자 직접 선택 "2")**. Pardo 2008 초과하지만 retrospective 재판정 맥락 정당화. 완화 조건 추가 유혹 = cycle 1 #5 재발 = cycle 3 강제 |
| Go 이중 조건 과소 (false positive) | Low | 5/5 stability + 평균 magnitude 이중 AND + min_trade_count ≥ 2 다중 필터 |
| W2-03 Go cells 집합 **양방향** freeze 위반 | **CRITICAL** | 확장 (ETH_C/Secondary 재포함) + 축소 (weak cell 제외) 모두 cherry-pick = cycle 3 강제. v2 핵심 원칙 #5 박제 |
| W3-02 pooled V로 W3-01 Go 판정 번복 유혹 | **CRITICAL** | v2 핵심 원칙 #8 박제: W3-02는 참고 metric만. Go 판정 번복 근거 X. 위반 = cycle 3 강제 |
| Strategy C fold당 0 trade 가능성 | Medium | `min_trade_count ≥ 2` 룰 박제. N/A fold = FAIL 처리 (fold_pass_count 미포함) |
| Fold 분할점 사후 조정 유혹 | **CRITICAL** | v2 핵심 원칙 #9 박제: 2026-04-21 사용자 승인 시점 = freeze 시점. 결과 본 후 조정 = cherry-pick |
| N=5 per fold sample variance 불안정 (실측 V **3-10배 변동**, v3 정정) | **CRITICAL** | 외부 감사 2차 독립 재계산 확인. V_empirical 일관 적용 강제 + floor 재도입 금지. W3-02 pooled V 재검증은 참고만. **v2 "2배" 과소평가였음 v3 정정 박제** |

## 산출물 (Artifacts)

### 코드
- `research/_tools/make_notebook_09.py`
- `research/notebooks/09_walk_forward.ipynb`

### 데이터/결과 (gitignored)
- `research/outputs/w3_01_walk_forward.json` (25 조합 + aggregation)
- `research/outputs/week3_report.md`

### 검증
- `.evidence/w3-01-walk-forward-2026-04-XX.md` (6단 구조, 실행 시점 날짜)
- `.evidence/agent-reviews/w3-01-walk-forward-review-2026-04-XX.md` (외부 감사 trace)
- `.evidence/agent-reviews/w3-01-walk-forward-reviewer-2026-04-XX.md` (backtest-reviewer trace)

### 박제 갱신
- `docs/stage1-subplans/w3-01-walk-forward.md` (이 파일, 체크박스 완료)
- `docs/stage1-execution-plan.md` (W3-01 상태)
- `docs/stage1-weekly/week3.md` (신설)
- `docs/decisions-final.md` (Go/No-Go 결정 박제)
- `docs/candidate-pool.md` (Strategy 상태 재평가)
- `.claude/handover-2026-04-17.md` (현재 위치 갱신)

### 테스트 시나리오
- **Happy (Go)**: 1+ cell이 (4+/5 fold pass AND 평균 pass) → W3-02 진입
- **Denial 1 (No-Go, 전체 실패)**: 모든 cell 미달 → +2 소급 + 사용자 결정
- **Denial 2 (No-Go, 부분 실패)**: 일부 fold만 pass (3/5 이하) → +2 소급
- **Edge (cell 1개만 통과)**: Go. 단일 cell 의존 리스크 사용자 보고
- **Edge (Strategy A만 통과)**: Recall mechanism 유지 + W3-02 DSR-adjusted 재검증

## Commit (예상)

```
feat(plan): BT-004 W3-01 walk-forward + Week 3 리포트 + 사용자 Go/No-Go 결정

- make_notebook_09.py + 09_walk_forward.ipynb 신설
- Anchored walk-forward 5 folds × 6개월 test
- 5 cell (W2-03 Go cells) × 5 fold = 25 조합 실행
- Fold별 V_empirical + SR_0 + DSR_z 산출 (Bailey 2014, W2-03 v8 박제 일관)
- Go 기준 (4+/5 fold pass AND 평균 pass) 자동 평가
- Week 3 리포트 + backtest-reviewer + 외부 감사 APPROVED
- 사용자 명시 Go/No-Go 결정 (자동 진행 X)
- 다음: Go → W3-02 (DSR + Bootstrap) / No-Go → +2 소급 + 사용자 결정
```

---

**이전 Task**: [W2-03 v9](./w2-03-insample-grid.md) (Go 결정, 2026-04-20 사용자 승인)
**다음 Task**: W3-02 (DSR + Bootstrap + Monte Carlo, Go 시) 또는 Stage 1 결정 (No-Go 시)
