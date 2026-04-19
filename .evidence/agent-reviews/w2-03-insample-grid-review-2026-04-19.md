# W2-03 sub-plan v1 외부 감사 (1차) — 적대적 외부 감사관 trace

- **검증 대상**: `docs/stage1-subplans/w2-03-insample-grid.md` v1 (2026-04-19)
- **감사관**: Claude (적대적 외부 감사관 모드, rubber-stamp 금지)
- **검증 일시**: 2026-04-19
- **참고 박제 출처**:
  - `docs/decisions-final.md` L513-521, L549-551, L595-611
  - `docs/pair-selection-criteria-week2-cycle2.md` v5
  - `docs/stage1-subplans/w2-02-strategy-candidates.md` v5 (사용자 승인 발효, 변경 금지 서약 중)
  - `docs/candidate-pool.md` v2
  - `research/CLAUDE.md` (vectorbt 0.28.5 + ta API 검증 패턴)
  - `.claude/handover-2026-04-17.md` v9 (#1~#20 패턴)
- **DSR 원문 검증 출처**:
  - Wikipedia "Deflated Sharpe ratio" (직접 fetch, Bailey-Lopez 공식 인용)
  - Bailey & López de Prado (2014) PDF (davidhbailey.com 호스팅, fetch 시 PDF 압축으로 일부 추출 한계, Wikipedia + Balaena Quant Insights blog 보완)
  - Lopez de Prado "False Strategy Theorem" SSRN 3221798

---

## 판정

**CHANGES REQUIRED** (BLOCKING 4건 + WARNING 6건 + NIT 5건)

핵심 결함 두 줄 요약:
1. **DSR 공식이 원문(Bailey-Lopez 2014)과 두 군데에서 부정확** — `SR_0 = sqrt(2 ln N)` 단순화 + 분모 SR 변수 모호 (SR_hat인지 SR_0인지). 본 문서가 W2-03 grid의 핵심 통계 입력이므로 BLOCKING.
2. **본문 L57에 산술 오류** — "5 페어"라고 박제했으나 Tier1(2) + Tier2(4) = **6 페어**. 정합성 0.

---

## 발견 사항

### BLOCKING (4건)

#### B-1 (CRITICAL): DSR 공식 원문 부정확 — `SR_0 = sqrt(2 × ln(N_trials))` 단순화는 V[SR_n] 사용 무시

**위치**: L146 "SR_0 = sqrt(2 × ln(N_trials)) (gamma + ψ approx 단순화)"

**문제**:
- Bailey & López de Prado (2014) "The Deflated Sharpe Ratio" 정확한 SR_0 공식은:
  ```
  SR_0 = sqrt(V[SR_n]) × ((1 - γ) × Φ⁻¹[1 - 1/N] + γ × Φ⁻¹[1 - 1/(N·e)])
  ```
  여기서 `γ = Euler-Mascheroni 상수 ≈ 0.5772156649`, `Φ⁻¹` = 표준정규 역CDF, `V[SR_n]` = 실제 trial들의 SR cross-sectional 분산
- v1 박제 `sqrt(2 × ln(N_trials))`는 **두 개의 가정을 암묵적으로 추가한 거친 근사**:
  1. `V[SR_n] = 1`이라고 단언 (실제로는 6 trials의 SR 분산 직접 측정 가능)
  2. Φ⁻¹의 두 항을 통합한 closed-form 제거 (Euler-Mascheroni γ + 1/(Ne) 항 누락)
- "(gamma + ψ approx 단순화)" 표기는 의미 불분명 (ψ는 digamma 함수인가? Bailey-Lopez 원문에는 ψ 등장 X). 사용자/외부 감사관에게 정확한 출처 추적 불가능
- **N_trials = 6이 작은 경우 두 공식 차이가 크다**:
  - 단순 근사: `sqrt(2 × ln(6)) ≈ 1.892`
  - 정확 공식 (V[SR_n]=1 가정 시): `(1-0.5772) × Φ⁻¹(1 - 1/6) + 0.5772 × Φ⁻¹(1 - 1/(6e))` ≈ `0.4228 × 0.967 + 0.5772 × 1.674` ≈ `0.409 + 0.966` = `1.375`
  - 즉 단순 근사는 정확값보다 **약 38% 과대평가** (보수적 방향이긴 하나 박제 신뢰도 X)

**수정 권고**:
1. 정확 공식을 박제 + Wikipedia/Bailey-Lopez 직접 인용 라인 첨부
2. V[SR_n] 산출 방식 명시 (6 primary 셀의 SR 분산 직접 측정)
3. 단순 근사를 채택하려면 그 명시적 정당성 + 보수성 명시 (감사 트레이스 차원에서 둘 다 산출 권고)
4. 외부 라이브러리 (예: `quantstats`) 또는 직접 구현 시 numpy + scipy.stats.norm.ppf 정확 호출 박제

---

#### B-2 (CRITICAL): DSR 공식 분모 SR 변수 모호 — SR_hat인지 SR_0인지 명시 X

**위치**: L147 "DSR = (SR - SR_0) × sqrt((T-1) / (1 - γ_3 × SR + (γ_4-1)/4 × SR^2))"

**문제**:
- Wikipedia + Bailey-Lopez 원문의 정확한 DSR 분모는 **SR_0**을 사용:
  ```
  DSR = Φ((SR_hat - SR_0) × sqrt(T-1) / sqrt(1 - γ_3 × SR_0 + (γ_4-1)/4 × SR_0^2))
  ```
  분모 안의 `SR`은 **SR_0** (threshold/expected max), `SR_hat`은 분자에만 등장
- v1 박제는 분자/분모 모두 `SR`이라고 적어 모호. 마지막 줄 "γ_3, γ_4 = skewness, kurtosis of returns"만 정의하고 SR 변수 정의 X
- W2-03.4 SubTask 구현 시 `SR_hat`을 분모에 넣을 가능성이 높음 (직관적 함정). 그 경우 DSR 값이 **체계적으로 다르게** 산출 → Go/No-Go 결정에 직접 영향
- 추가 누락: 외부 Φ() (표준정규 CDF wrapper) 누락. 박제 공식 그대로 계산하면 z-score 형태가 나오는데 Bailey-Lopez DSR은 Φ(z)로 [0,1] 확률 값. v1의 "DSR > 0" 기준 (L150)이 z-score 기준인지 Φ(z)>0.5 기준인지 모호

**수정 권고**:
1. 정확 공식 박제 (분자 SR_hat, 분모 SR_0)
2. 외부 Φ() wrapper 명시 + DSR 결과 단위 (확률 [0,1] 또는 z-score) 명시
3. **"DSR > 0" 기준 재해석 강제**:
   - z-score 기준이라면 (분자만 측정) → 임의 양수 (예: 0)
   - Φ(z) 기준이라면 → DSR > 0.5 또는 > 0.95 (95% 신뢰도) 등 통계적 의미 명시
4. 사용자/감사관이 결과 검증 가능하도록 W2-03.4 코드에 reference unit test 추가 권고 (Bailey-Lopez 예제 input → DSR output 일치 확인)

---

#### B-3: 본문 산술 오류 — "5 페어"는 6 페어 (Tier 1 + Tier 2 = 2 + 4)

**위치**: L57 "5 페어 (Tier 1 BTC+ETH + Tier 2 XRP+SOL+TRX+DOGE) × 3 전략 (A, C, D) = 18셀"

**문제**:
- BTC + ETH = 2 페어 (Tier 1) + XRP + SOL + TRX + DOGE = 4 페어 (Tier 2) = **6 페어**
- v1 본문은 "5 페어"라고 박제 → 산술 오류 (handover #1 "evidence 수치 오기재" 패턴 재발)
- 셀 수 18 (6 × 3) 자체는 일관 (이게 다행이지 그렇지 않으면 grid 구조 통째 흔들림)
- "5 페어" 표기는 cycle 1 격리 양성 목록 (Tier 2 = {XRP, SOL, ADA, DOGE}) 시절의 4 페어 + Tier 1 2 = 6에서 ADA → TRX 전이 시 잘못된 "5"가 들어간 것으로 추정 (cycle 1 잔존)

**수정 권고**:
1. "6 페어"로 즉시 정정
2. handover 패턴 #1 (evidence 수치 오기재) 추가 발생 사례로 박제

---

#### B-4: Strategy A "재진입 조건" 차단 약속과 Recall mechanism 적용 책무가 sub-plan에 약화

**위치**:
- L166-168 "Strategy A가 Go 기준 통과 시 Active로 재전이 + DSR-adjusted 평가 + Week 3 walk-forward 재검증 의무 박제"
- vs candidate-pool.md L27-28 (Strategy A 행) "재진입 조건: Tier 1 (BTC+ETH) 중 하나 이상 `Sharpe > 0.8 AND DSR > 0` / Recall 시 의무: DSR > 0 필수 평가. Week 3 walk-forward 재검증 필수"

**문제**:
- candidate-pool.md L27 "재진입 조건"은 W2-03 grid의 결과를 평가 후 발효되는 **사전 지정 조건**. v1 sub-plan L166의 "Strategy A가 Go 기준 통과 시"는 정확히 Strategy A이 BTC 또는 ETH에서 `Sharpe > 0.8 AND DSR > 0`인 경우와 동일해야 정합. 하지만 v1 sub-plan은 Go 기준 (L160 "적어도 1개 전략이 BTC 또는 ETH에서") 적용 시 Strategy A 셀 단독 충족만으로 재전이 발효되는 경로를 명확히 박제 X
- v1 W2-03.5 SubTask는 Recall mechanism 적용 결과 박제 단계가 모호 — Strategy A가 Active로 재전이되면 candidate-pool.md 갱신 (Retained → Active) 책무가 어디 있는지 명시 X (W2-03.6 산출물 L251에 "candidate-pool.md (Strategy A 재전이 여부)" 한 줄만 있음)
- 추가 약점: Strategy A는 Recall 시 "DSR > 0 필수 평가" + "Week 3 walk-forward 재검증 필수" 인데, v1 W2-03.5 L166-167 박제는 **Strategy A에만 추가 의무 박제**. 이는 Candidate C/D vs Strategy A 비대칭 — Candidate C/D도 Go 기준 통과 시 Week 3 walk-forward 재검증 의무는 동일 적용되는가? v1 미명시. 만약 Strategy A에만 적용 시 cherry-pick 위험 (C/D가 통과한 경우와 A가 통과한 경우 평가 강도 비대칭)

**수정 권고**:
1. W2-03.5 SubTask에 "Strategy A가 Recall mechanism 발효 → candidate-pool.md L17 행 (Retained → Active) 갱신 + 변경 이력 v3 추가" 단계 명시
2. Candidate C/D도 Go 기준 통과 시 Week 3 walk-forward 재검증 동일 의무 박제 (대칭 평가 보장)
3. Recall mechanism의 "DSR-adjusted 평가" 정확한 의미 박제 — Strategy A에 추가 패널티 적용인지, 단지 동일 DSR > 0 기준 적용인지 (candidate-pool.md L28과 일관 유지)

---

### WARNING (6건)

#### W-1: SR annualization 단위 미명시 — 프로젝트 내부 일관성 깨짐

**위치**: 본문 전체 (annualization 명시 X), L84 `RANGE = ("2021-01-01", "2026-04-12")`, L144 N_trials=6 산정 등

**문제**:
- v1 박제는 vectorbt `pf.sharpe_ratio()` 기본 호출에 위임. 그러나:
  - vectorbt 0.28.5 default `year_freq = '252 days'` (검증된 사실, 검색 결과)
  - 그러나 crypto 24/7 거래는 `year_freq = '365 days'`가 표준
  - 프로젝트 내부 W1-04 산출물은 `np.sqrt(252)` 사용 (`research/_tools/make_notebook_04.py:238`)
  - W1-06 산출물은 `np.sqrt(365)` 사용 (`research/_tools/make_notebook_06.py:543`)
  - **W1 내부에서도 일관성 깨짐** (handover 미박제 누적 사실)
- v1 W2-03 박제는 어느 쪽인지 명시 X → W1-06 결과(Strategy A Sharpe 1.04, sqrt(365) 산식)와 W2-03 결과 직접 비교 시 단위 불일치 위험
- Go 기준 `Sharpe > 0.8`은 sqrt(365) 기준인지 sqrt(252) 기준인지 명시 X — 두 기준 차이는 약 `sqrt(365/252) ≈ 1.20` 배. 즉 sqrt(365) 1.04 = sqrt(252) 약 0.86 — Go 기준 0.8 통과 여부가 결정 단위에 흔들림

**수정 권고**:
1. W2-03.0에 박제 상수 추가: `YEAR_FREQ_DAYS = 365` (crypto 24/7) + `vbt.settings.array_wrapper['freq'] = '1D'` + `vbt.settings.returns['year_freq'] = '365 days'` 또는 `pf.sharpe_ratio(year_freq='365 days')` 명시
2. W1-04 vs W1-06 단위 일관성 깨짐 → handover 신규 패턴 #21로 박제 추천
3. Go 기준 `Sharpe > 0.8`이 sqrt(365) 기준임을 W2-03.5 박제 인용 (decisions-final.md L518 박제는 단위 미명시 → 본 sub-plan에서 단위 박제 책무)

---

#### W-2: N_trials = 6 (Primary만) 박제 결정의 정당성이 부분적

**위치**: L141-144 "DSR 박제 결정: N_trials = 6 (Primary만): Tier 2 exploratory는 Go 기여 X이므로 multiple testing 분모에서 제외 / 또는 N_trials = 18 (전체 셀): 보수적 / 본 sub-plan v1 추천: N_trials = 6 (Primary만)"

**문제**:
- 사용자 #4 결정 "Tier 2 = Secondary 마킹, Go 기여 X" 박제와 일관 (Go 평가 대상 = 6셀이므로 multiple testing 분모도 6)
- 그러나 보다 엄밀한 외부 감사관 시각:
  - **Tier 2 grid 결과를 본 후 ensemble 후보 마킹 (Sharpe>0.5)** 자체가 selection bias 일종 → ensemble 후보가 Stage 2 (Week 12) 라이브 게이트 기여 시 결국 다중 검정 입력
  - "Go 기여 X"는 W2 게이트 한정. Stage 2 게이트까지 확장 시 N_trials = 18 (Tier 2도 포함)이 정직
  - 박제 시점은 **W2 게이트만** 기준이라는 명시가 필요. Stage 2 게이트 시 재계산 의무 박제 권고
- 추가 약점: V[SR_n] 산출 시 N_trials=6 셀의 SR 분산을 사용한다면, primary 6셀이 거의 동일 결과 시 V[SR_n] 작아 → SR_0도 작아져 → DSR 과대 추정. **6셀 결과 분포가 좁을 시 DSR 신뢰성 저하** alarm 박제 필요

**수정 권고**:
1. "본 박제는 W2 게이트 한정. Stage 2 게이트 평가 시 N_trials 재산정 (Tier 2 + Week 3 walk-forward 셀 포함)" 명시
2. 6셀 V[SR_n] 협소성 alarm 박제 + Week 3 walk-forward 단계에서 N_trials 확장 (예: 6 + walk-forward 6 = 12)으로 재평가 권고
3. (옵션) v1 추천 N_trials=6 + 보수 대안 N_trials=18 **둘 다 산출** 후 외부 감사관 비교 평가 권고

---

#### W-3: vectorbt multi-asset Portfolio 구현 패턴 미명시

**위치**: W2-03.2/.3 SubTask 본문 (L108-134)

**문제**:
- `research/CLAUDE.md` L75-88 "앙상블 (Week 2+, cash_sharing 패턴)"은 단일 페어 위에서 두 전략 동시 평가 패턴
- W2-03 grid는 **6 페어 × 3 전략 = 18 독립 백테스트**가 자연스럽지만, vectorbt 0.28.5의 `from_signals`는 multi-asset close DataFrame + multi-column entries/exits로 한번에 18셀 처리도 가능
- v1 박제는 어느 패턴인지 명시 X → W2-03.0 구현 시 "18번 for loop" vs "vectorbt vectorized multi-asset" 결정이 backtest-reviewer 단계에 미뤄짐
- 추가 위험: `cash_sharing=True`/`group_by` 잘못 적용 시 18셀이 단일 portfolio처럼 합쳐져 결과 왜곡 위험 (handover #4 "backtest-reviewer 좁은 스코프" 패턴 재발 위험)

**수정 권고**:
1. W2-03.0에 "각 (페어, 전략) 셀은 독립 vectorbt Portfolio 생성, cash_sharing=False 또는 단일 자산 호출 강제" 박제
2. multi-asset wide-format vs for-loop 구현 결정 + research/CLAUDE.md 패턴 인용
3. 결과 JSON 구조 박제 (예: `{"BTC_A": {sharpe_max_span: ..., sharpe_common: ..., dsr: ...}, ...}`)

---

#### W-4: Common-window vs max-span 두 metric 동시 산출의 통계적 함의 미명시

**위치**: L116-118 W2-03.2 "Primary metric: 페어별 max-span Sharpe / Secondary metric: common-window Sharpe"

**문제**:
- `pair-selection-criteria-week2-cycle2.md` L194-198 박제 "Go 기준 평가는 primary metric 기준. Secondary는 페어 간 비교 공정성 확인용"
- v1 박제는 두 metric 동시 산출 사실은 명시했으나:
  - 두 metric 결과가 **상이할 시 어떻게 처리하는가** 박제 X
  - 예: BTC max-span Sharpe = 1.2 (>0.8 통과) but BTC common-window Sharpe = 0.3 (의미적 불통과)
  - 사전 지정 정신은 **primary만 Go 기준 입력**이지만, 외부 감사관 시각은 두 metric의 비대칭 결과를 정직하게 보고하지 않으면 cherry-pick (cycle 1 패턴 #14 "실측 cherry-pick 경로 재유입") 위험
- DSR 계산 시 N_trials=6은 어느 metric 기준인지 명시 X — max-span 기준이라면 페어별 T(샘플 길이) 다름 → DSR T-1 항이 페어마다 다름. common-window 기준이라면 모든 페어 T 동일 (약 4.5년 = 1638 일)

**수정 권고**:
1. Go 기준 입력 metric 명시 (primary = max-span Sharpe + DSR using max-span returns)
2. 두 metric 비대칭 결과 발견 시 W2-03.6 리포트에 "**페어별 max-span vs common-window Sharpe 비대칭 표**" 강제 박제 (cherry-pick 차단)
3. DSR 입력 returns 길이 T 명시 (max-span 기준 시 페어마다 T 다름 박제, common-window 기준 시 단일 T)

---

#### W-5: ta KeltnerChannel API 호출 박제 인용 누락

**위치**: W2-03.0 박제 상수 L86-88 "Strategy D 파라미터 (candidate-pool.md + W2-02 v5 인용)"

**문제**:
- W2-02 v5 박제는 **`KeltnerChannel(window=20, window_atr=14, original_version=False, multiplier=1.5)` 4개 파라미터 모두 명시 강제** (handover v9 "ta KeltnerChannel API 호출 박제 (`original_version=False, window_atr=14, multiplier=1.5` 명시 필수)")
- v1 W2-03.0 박제는 "candidate-pool.md + W2-02 v5 인용"으로 한 줄 처리. 실제 노트북 작성 시 default 적용 위험 (W2-02 v5 W3-1 "ta 향후 버전 업데이트 시 KeltnerChannel signature/default/내부 계산 방식 변경 가능" 책무 적용 누락 위험)
- 본 sub-plan은 W2-03 책무 직접 박제 단계인데 ta API 호출 박제를 외부 문서 인용으로만 처리 → cycle 1 학습 #15 "sub-plan/decisions-final 전파 누락" 패턴 재발 위험

**수정 권고**:
1. W2-03.0에 ta KeltnerChannel + BollingerBands 호출 코드 박제 (W2-02 v5 L213-228 인용 + 4개 파라미터 명시)
2. W2-03.0에 W2-02 v5 W3-1 책무 인용: "사이클 진입 시점에 venv ta 버전 재확인 + signature 직접 검증 (`source research/.venv/bin/activate && python -c "from ta.volatility import KeltnerChannel; import inspect; print(inspect.signature(KeltnerChannel.__init__))"`)" 단계 박제
3. backtest-reviewer 호출 시 ta API default 미적용 검증 필수 명시

---

#### W-6: BTC 데이터 W1 재사용 vs W2-01.4 갱신 데이터 사이 중복/불일치 처리 미명시

**위치**: W2-03.0 L89 "데이터 로드 + SHA256 무결성 재검증 (W1-01 BTC + W2-01.4 5 페어)"

**문제**:
- 산술 오류: "5 페어"는 W2-01.4 신규 페어 (ETH + Tier2 4) = 5 페어로 정합 가능. 그러나 본문 L57의 "5 페어" 오류와는 별개 의미.
- W1-01 BTC vs W2-01.4 BTC 중복 가능성 — `pair-selection-criteria-week2-cycle2.md` L219 "KRW-BTC | (W1 재사용, 자동 통과)" 박제. W2-01.4가 BTC를 신규 수집했는지 W1 재사용했는지 명시 X
- handover v9 "v8 시점 작업: cycle 2 W2-01.4 데이터 수집 + W2-01.5/.6/.7 통합 완료 + backtest-reviewer APPROVED with follow-up. cycle 2 W2-01 전체 완료 시점" — W2-01.4가 정확히 어떤 페어를 수집했는지 sub-plan v1에서 추적 불가
- 추가 위험: W1-01 BTC freeze 종료일 = 2026-04-12 vs W2-01.4 freeze 종료일이 동일한지 명시 X. 다를 시 cross-strategy 비교 불공정

**수정 권고**:
1. W2-03.0에 데이터 출처 명시 박제: BTC = W1-01 frozen Parquet 재사용 (handover에서 확인) / ETH + Tier2 = W2-01.4 산출 Parquet
2. 모든 페어 freeze 종료일 = 2026-04-12 UTC 일관성 확인 단계 박제 (불일치 시 W2-03 중단)
3. data_hashes.txt에 6 페어 SHA256 모두 기록 + W2-03.0 노트북 첫 셀 무결성 검증

---

### NIT (5건)

#### NIT-1: SubTask 외부 감사 단계 누락 (W2-02.3 패턴)

**위치**: SubTask 목록 전체 (L73-194)

**관찰**: W2-02 v5는 SubTask W2-02.3에 "외부 감사 (적대적, 사전 등록 정합성)" 단계를 명시 박제. v1 W2-03은 SubTask로 외부 감사 단계 박제 X. 본 1차 감사가 그 책무 수행 중이지만, sub-plan 자체에 "W2-03.X 외부 감사" SubTask 명시 박제 권고 (재현 가능성 + 후속 cycle 학습)

**수정 권고**: SubTask "W2-03.5b 외부 감사 (적대적, 사전 지정 정합성)" 추가 + 본 1차 감사 evidence 인용

---

#### NIT-2: "Stage 1 킬 카운터" 정의 + 현재 카운터 값 명시 X

**위치**: L169 "No-Go 시 Stage 1 킬 카운터 +1 → Week 3 재탐색 또는 Stage 1 종료 사용자 결정"

**관찰**: Stage 1 킬 카운터 누적 값이 sub-plan에 명시 X. handover에 따르면 W1-06 No-Go 결정 후 카운터 +1되었는지 모호. Week 1 No-Go 카운트 +1 + W2-03 No-Go 카운트 +1 = 2 (또는 Week 1은 No-Go가 아닌 "재범위" 결정이므로 카운트 X)

**수정 권고**: decisions-final.md에서 Stage 1 킬 카운터 정의 + 현재 값 박제 인용 (없으면 신설 박제 책무 명시)

---

#### NIT-3: W2-03.6 백테스트 evidence 6단 구조 명시 X

**위치**: L186 "backtest-reviewer 호출 (W1-06 패턴, 6단 evidence 구조)"

**관찰**: "6단 evidence 구조"라고 인용했으나 본문에 6단 항목 명시 X. CLAUDE.md `Context Map` "Evidence 파일 (검증 서명) — Task 완료 시 작성. 6단 구조 (데이터/파라미터/결과/자동검증/룰준수/리뷰)" 인용 권고

**수정 권고**: 6단 항목 명시 박제 또는 CLAUDE.md L31 직접 인용

---

#### NIT-4: 산출물 evidence 파일명 placeholder

**위치**: L244 "`.evidence/agent-reviews/w2-03-insample-grid-review-202604XX.md`"

**관찰**: "202604XX" placeholder. 본 1차 감사 trace는 `.evidence/agent-reviews/w2-03-insample-grid-review-2026-04-19.md`로 작성 중 — placeholder는 확정 시 갱신 권고

**수정 권고**: 본 1차 감사 통과 후 sub-plan 갱신 시 `2026-04-19` 박제

---

#### NIT-5: 변경 이력 v1 행 + 외부 감사 결과 반영 v2 행 placeholder

**위치**: L9-10 변경 이력 표

**관찰**: 외부 감사 결과 반영 v2 행이 "TBD"로 placeholder. 본 1차 감사 결과 정정 시 v2 박제 (W2-02 패턴: v2/v3/v4/v5 단계별 행 추가)

**수정 권고**: 본 1차 감사 정정 적용 시 v2 행 추가 + 정정 내용 명시 (B-1~B-4 + W-1~W-6 + NIT-1~NIT-5 해소 항목별)

---

## DSR 공식 검증 결과 (Bailey & López de Prado 2014)

### v1 박제 vs 원문 비교

| 항목 | v1 박제 | Bailey-Lopez 2014 원문 (Wikipedia + WebSearch 확인) | 평가 |
|------|---------|-------------------------------------------------------|------|
| SR_0 (expected max SR) | `sqrt(2 × ln(N_trials))` (gamma + ψ approx 단순화) | `sqrt(V[SR_n]) × ((1-γ)·Φ⁻¹[1-1/N] + γ·Φ⁻¹[1-1/(Ne)])`, γ=0.5772 (Euler-Mascheroni), Φ⁻¹=정규 역CDF | **부정확**: V[SR_n] 무시 + Φ⁻¹ closed-form 제거 |
| DSR 분모 | `1 - γ_3 × SR + (γ_4-1)/4 × SR^2` (SR 변수 모호) | `1 - γ_3 × SR_0 + (γ_4-1)/4 × SR_0^2` (SR_0 사용) | **모호**: SR_hat인지 SR_0인지 명시 X (정답 = SR_0) |
| DSR 외부 wrapper | 누락 | `Φ((분자) / sqrt(분모))` (Φ = 정규 CDF) | **누락**: z-score인지 확률[0,1]인지 모호 |
| Go 기준 "DSR > 0" | z-score 기준 가정 시 단순 양수 | Φ(z) 기준 시 보통 0.95 (95% 신뢰) | **단위 불명**: B-2 정정 후 재해석 강제 |

### N_trials = 6 vs 18 박제 결정 정당성

- **N_trials = 6 (Primary만)** 추천 정당성:
  - 사용자 #4 결정 "Tier 2 = Secondary 마킹, Go 기여 X" 박제와 일관
  - W2 게이트 평가 대상 = primary 6셀이므로 selection bias 분모도 6
- **N_trials = 18 (전체)** 보수 대안 정당성:
  - Tier 2 grid 결과를 본 후 ensemble 후보 마킹 (Sharpe>0.5) 자체가 selection bias의 일종
  - Stage 2 게이트까지 확장 시 결국 다중 검정 입력
- **W-2 권고: 둘 다 산출 후 비교 보고**. v1 추천 6은 W2 게이트 한정 박제 명시. Stage 2 게이트 시 재산정 의무 박제

### V[SR_n] 산출 약점 (B-1 추가 alarm)

- N_trials=6일 때 6셀 SR 분산 직접 측정 가능. 그러나 6셀이 거의 동일 결과 시 V[SR_n] 작아짐 → SR_0 작아짐 → DSR 과대 추정 risk
- **사전 지정 strategy family 다양성** (A=trend-following + Donchian, C=slow momentum, D=volatility breakout)가 어느 정도 보장하지만, 모두 long-only + crypto bull 편중 가능성 → V[SR_n] 협소화 alarm 박제 권고

---

## cycle 1/2 학습 패턴 재발 검증 (handover #1~#20)

| # | 패턴 | 본 v1 재발 여부 | 비고 |
|---|------|----------------|------|
| #1 | Evidence 수치 오기재 | **재발** (B-3 "5 페어" 오류) | 산술 검증 누락 |
| #2 | 문서 버전 라벨 미갱신 | 미재발 | v1 라벨 정확 |
| #3 | execution-plan 체크박스 미체크 | 미재발 (해당 단계 X) | - |
| #4 | backtest-reviewer 좁은 스코프 | 잠재 재발 위험 (W-3) | multi-asset 패턴 미명시 |
| #5 | fillna() FutureWarning | 미재발 (해당 코드 X) | - |
| #6 | research/outputs gitignore | 미재발 (산출물 위치 명시 정확) | - |
| #7 | 사전 지정 기준 측정 창 미정의 | 미재발 (RANGE 박제) | - |
| #8 | Multiple testing 미보정 | 미재발 (DSR 박제 + L151 "Multiple testing 한계 박제 인용") | - |
| #9 | Soft contamination 간과 | 미재발 (decisions-final.md 인용) | - |
| #10 | Fallback "임계값 완화" | 잠재 재발 위험 (W-2 N_trials 결정 + W-4 두 metric 비대칭) | cherry-pick 차단 박제 미흡 |
| #11 | 측정 창 inclusive off-by-one | 해당 X (날짜 추가 박제 X) | - |
| #12 | Fallback 라벨 misnomer | 미재발 | - |
| #13 | 박제 문서 자기 freeze 시점 순환 정의 | 미재발 (v1 박제 시점 명확) | - |
| #14 | 실측 cherry-pick 경로 재유입 | **잠재 재발 위험** (W-4 두 metric 비대칭 처리 미박제) | Go 기준 변경 차단 박제 강화 필요 |
| #15 | sub-plan/decisions-final 전파 누락 | **잠재 재발 위험** (W-5 ta API 호출 외부 인용으로만 처리) | sub-plan 자체 박제 권고 |
| #16 | 외부 라이브러리 응답 필드 추측 | 미재발 (W-3에 backtest-reviewer 검증 박제) | - |
| #17 | 사전 지정 추정 리스트의 빗나감 위험 | 미재발 (페어 리스트는 cycle 2 v5 freeze 인용) | - |
| #18 | 외부 코인 정체 추측 | 미재발 (해당 X) | - |
| #19 | 수치 단위 표기 오류 | **잠재 재발 위험** (W-1 SR annualization 단위 미명시) | 단위 박제 강화 필요 |
| #20 | sub-plan 박제 vs .gitignore 실제 룰 충돌 | 미재발 (산출물 gitignore 박제 정확) | - |

**재발 사례 #1 (B-3) + 잠재 재발 위험 #4/#10/#14/#15/#19 = 6건**. 정정 시 모두 해소 가능.

---

## 종합 평가

### 사전 지정 정합성

- Primary 6셀 + Exploratory 12셀 + Tier 1+2 페어 리스트 = cycle 2 v5 박제와 일관 (B-3 산술 오류 정정 시 100%)
- W2-02 v5 Candidate C/D 변경 금지 서약 발효 중 — sub-plan v1은 인용으로만 처리 (W-5 박제 권고 적용 시 sub-plan 자체 박제 강화)

### DSR 공식 정확성

- **부정확** (B-1 + B-2). 정정 권고:
  1. SR_0 정확 공식 박제 (Bailey-Lopez 원문 + Wikipedia 인용)
  2. DSR 분모 SR_0 사용 명시 + 외부 Φ() wrapper 명시
  3. Go 기준 "DSR > 0" 단위 (z-score vs Φ(z)) 명시 + 통계적 의미 박제
  4. V[SR_n] 산출 방식 + 6셀 협소성 alarm 박제

### Multiple testing 한계 정직성

- L151 박제 인용은 정확. W-2 권고 적용 시 더 정직 (N_trials=6 박제는 W2 게이트 한정 + Stage 2 게이트 시 재산정 의무 명시)
- W-4 권고 적용 시 두 metric 비대칭 보고 강제 → cherry-pick 차단

### 사용자 결정 정직성

- L189-191 "사용자 명시 Go/No-Go 결정 (자동 진행 X)" + L227 "Go 기준 사후 변경 유혹 = CRITICAL" 박제 정확
- B-4 정정 시 Strategy A Recall mechanism + Candidate C/D 대칭 평가 강제 → 사용자에게 정확한 옵션 제시 가능

---

## 외부 감사관 의견

**판정: CHANGES REQUIRED**

다음 단계 권고:

1. **즉시 정정 (BLOCKING 4건)**:
   - B-1: DSR SR_0 정확 공식 박제 + Wikipedia/Bailey-Lopez 인용
   - B-2: DSR 분모 SR_0 명시 + 외부 Φ() wrapper + Go 기준 단위 명시
   - B-3: "5 페어" → "6 페어" 즉시 정정
   - B-4: Strategy A Recall mechanism vs Candidate C/D 대칭 평가 박제

2. **WARNING 정정 (6건)** — 사용자 승인 전 권고:
   - W-1: SR annualization sqrt(365) 박제 + W1 산출물 일관성 정정 책무
   - W-2: N_trials=6 (W2 게이트 한정) + Stage 2 게이트 재산정 의무 박제
   - W-3: vectorbt multi-asset 구현 패턴 박제
   - W-4: 두 metric 비대칭 결과 보고 강제
   - W-5: ta KeltnerChannel API 호출 sub-plan 직접 박제
   - W-6: BTC W1 재사용 vs W2-01.4 데이터 출처 명시

3. **NIT 정정 (5건)** — 정합성 향상:
   - NIT-1: SubTask "W2-03.5b 외부 감사" 명시 박제
   - NIT-2: Stage 1 킬 카운터 정의 + 현재 값 인용
   - NIT-3: 6단 evidence 구조 명시
   - NIT-4: evidence 파일명 placeholder → `2026-04-19` 확정
   - NIT-5: 변경 이력 v2 행 추가

4. **재감사 절차** (cycle 1/2 패턴):
   - 정정 v2 작성 → 본 감사관 재호출 (별도 agent call) → APPROVED with follow-up 또는 추가 정정
   - W2-02 v5 패턴은 1차/2차/3차 외부 감사 + 옵션 C 정정 5건 → 사용자 승인. W2-03도 유사 강도 권장
   - **사용자 승인 전 BLOCKING 0 + WARNING/NIT 모두 해소 또는 명시적 follow-up 트래킹** (CLAUDE.md "팀장/이사급 책임 원칙")

5. **사용자 결정 옵션 명시 (정정 후)**:
   - (a) 본 감사 결과 즉시 v2 정정 + 재감사 후 사용자 승인 (W2-02 패턴, 권장)
   - (b) BLOCKING만 정정 후 사용자 승인 + WARNING/NIT는 follow-up 트래킹 (시간 압박 시)
   - (c) 본 감사 결과 거부 + 추가 외부 감사관 (`general-purpose` agent) 호출하여 2차 의견 (BLOCKING 4건이 사실 오류이므로 거부 가능성 낮음)

**감사 결과 신뢰도**: B-1/B-2는 Bailey-Lopez 원문 + Wikipedia + WebSearch 직접 확인 (다중 출처 일관). B-3는 단순 산술 검증 (1 + 1 + 1 + 1 + 1 + 1 = 6). B-4는 candidate-pool.md L27 직접 인용 확인. WARNING/NIT는 프로젝트 내부 문서 + handover 패턴 직접 확인.

**다음 단계**: 사용자 보고 → 정정 v2 작성 → 재감사 또는 사용자 승인.

---

## 참고 출처 (외부 감사 trace 신뢰성 보강)

- Wikipedia "Deflated Sharpe ratio": https://en.wikipedia.org/wiki/Deflated_Sharpe_ratio
- Bailey & López de Prado (2014) "The Deflated Sharpe Ratio: Correcting for Selection Bias, Backtest Overfitting, and Non-Normality" SSRN 2460551
- Lopez de Prado & Bailey "The False Strategy Theorem" SSRN 3221798
- vectorbt 0.28.5 docs (year_freq='252 days' default 확인): https://vectorbt.dev/api/portfolio/base/
- Issue #294 vectorbt (crypto 24/7 ann_factor 논의): https://github.com/polakowo/vectorbt/issues/294
- Balaena Quant Insights "Deflated Sharpe Ratio (DSR)" (Wikipedia 공식과 일관 확인 보강)

---

# W2-03 sub-plan v2 외부 감사 (2차) — 적대적 외부 감사관 trace

- **검증 대상**: `docs/stage1-subplans/w2-03-insample-grid.md` v2 (2026-04-19, 1차 감사 BLOCKING 4 + WARNING 6 + NIT 5 정정 후)
- **감사관**: Claude (적대적 외부 감사관 모드, rubber-stamp 절대 금지)
- **검증 일시**: 2026-04-19 (1차 감사 직후 v2 정정본)
- **DSR 공식 cross-check 출처**: Wikipedia "Deflated Sharpe ratio" 직접 fetch (2026-04-19 본 세션). Bailey-Lopez 2014 PDF (davidhbailey.com)는 PDF 압축 인코딩으로 일부 추출 한계, Wikipedia 본문이 원문 공식 정확 인용.

---

## 2차 감사 판정

**APPROVED with follow-up** (BLOCKING 0건, WARNING 1건 신규, NIT 4건 잔존 + NIT 1건 신규)

핵심 두 줄 요약:
1. 1차 감사 BLOCKING 4 + WARNING 6은 모두 본문 정정 박제 확인. DSR 공식 Wikipedia 원문 cross-check 결과 정확. 사용자 승인 진입 적격.
2. 그러나 (a) **L94 "5 페어" 잔존 박제 1건** (B-3 정정 누락된 케이스) + (b) **decisions-final.md L515 ADA 박제와 v2 sub-plan TRX 박제 cross-reference 모순 미언급** + (c) NIT-1~4 잔존은 follow-up 트래킹 책무.

---

## v2 BLOCKING/WARNING 정정 검증

### B-1/B-2 DSR 공식 정정 정확성: PASS (조건부)

**v2 박제** (L168, L179):
```
SR_0 = sqrt(V[SR_n]) × ((1-γ) × Φ⁻¹(1 - 1/N) + γ × Φ⁻¹(1 - 1/(N·e)))
DSR_z = (SR_hat - SR_0) × sqrt((T - 1) / (1 - γ_3 × SR_0 + ((γ_4 - 1) / 4) × SR_0²))
```

**Wikipedia "Deflated Sharpe ratio" 직접 fetch 결과** (2026-04-19 본 세션):
```
SR_0 = √V[SR̂_n] × ((1−γ)Φ⁻¹[1−1/N] + γ·Φ⁻¹[1−1/(Ne)])
DSR = Φ((SR̂* − SR_0) · √(T−1) / √(1 − γ̂_3·SR_0 + ((γ̂_4−1)/4)·SR_0²))
```

**일치 판정**:
- SR_0 공식: γ Euler-Mascheroni (≈0.5772), Φ⁻¹, V[SR_n], N과 N·e 항 모두 **완전 일치 PASS**
- DSR 분모 SR 변수: v2는 명확하게 **SR_0** 사용 (B-2 정정 완료 PASS). 1차 감사 우려 해소
- DSR 형태:
  - Wikipedia/원문: `Φ(z)` wrapper 적용 = **확률 [0,1]** 형태가 표준
  - v2 박제 채택: `DSR_z` (z-score form) + 비교용으로 `DSR_prob = Φ(DSR_z)` 동시 산출 (L191)
  - L188-191에서 "DSR_z > 0 ⇔ SR_hat > SR_0 ⇔ Φ(DSR_z) > 0.5" 의미 동치 박제 명확
  - **Wikipedia 원문 표준은 Φ(z) 확률 형태**이지만 v2는 z-score form을 채택 + decisions-final.md L518 박제 "DSR > 0" 의미 동치 명확화 + 두 form 동시 산출 명시 → **수학적으로 정확하고 정직한 박제. PASS**
- v1의 거친 근사 `sqrt(2 × ln(N))` 폐기 명시 (L175) **PASS**
- V[SR_n] 산출 = 6셀 sample variance + 1.0 정규화 비교용 둘 다 산출 박제 (L174, L159) **PASS**

**조건부**: WARNING N-1 (아래) — Wikipedia/원문 표준이 Φ(z) 확률 형태이고 학계 인용 시 통상 "DSR > 0.95 (95% 신뢰)" 같은 형태로 보고된다는 점이 v2 본문에 명시되지 않음. 단 z-score form 채택 자체는 사용자 박제 "DSR > 0"과 일치하므로 사실 오류 X. **사용자 보고 시 "Wikipedia/Bailey-Lopez 원문은 Φ(z) 확률 형태가 표준이지만 본 v2는 사용자 박제 'DSR > 0'과의 동치 + 단순성을 위해 z-score form 채택" 명시 권고**.

### B-3 산술 정정 정확성: PARTIAL FAIL (잔존 1건)

**v2 박제 L57**: "**6 페어** (Tier 1 BTC+ETH = 2 + Tier 2 XRP+SOL+TRX+DOGE = 4) × 3 전략 (A, C, D) = **18셀**" → **PASS**

**그러나 L94 잔존**: `데이터 로드 + SHA256 무결성 재검증 (W1-01 BTC + W2-01.4 5 페어, W-6 정정)`
- 여기 "5 페어"는 W2-01.4가 신규로 수집한 페어 수(ETH + Tier2 4개 = 5)를 의미할 수 있어 **L57의 "5 페어" 산술 오류와는 의미가 다름**
- 그러나 1차 감사 W-6 권고 (W2-01.4가 어느 페어를 수집했는지 명시) 적용 결과 "5 페어"가 그대로 잔존 = 외부 감사관 시각에서 모호 (BTC 포함 여부 불명)
- **수정 권고**: "W1-01 BTC (1 페어) + W2-01.4 신규 수집 5 페어 (ETH + Tier2 XRP/SOL/TRX/DOGE) = 총 6 페어 SHA256 무결성 재검증" 으로 명확화

**판정**: B-3 핵심 산술 (L57)은 PASS. L94는 의미 모호 (오류는 아니지만 외부 감사관 혼동 유발) → **NIT 신규 추가 (NIT-N1)**.

### B-4 Recall 대칭 정정: PASS

**v2 L211-214 박제**:
- Strategy A 재등장 시: candidate-pool.md Recall mechanism 적용 (Active 재전이 + DSR-adjusted + Week 3 walk-forward)
- Strategy C/D 통과 시: 동일하게 DSR-adjusted + Week 3 walk-forward 의무 (대칭)
- 명시 박제: "A/C/D 어느 전략이 Go 통과해도 Week 3 walk-forward 의무 강제. handover #14 cherry-pick 패턴 재발 차단"

**candidate-pool.md cross-check**:
- Strategy A L27-28: "재진입 조건 + Recall 시 의무: DSR > 0 필수. Week 3 walk-forward 재검증 필수"
- Strategy C L40-41 / D L54: "평가 조건: Primary `Sharpe>0.8 AND DSR>0`. Secondary 마킹"
- C/D는 candidate-pool에서 Walk-forward 재검증 명시 없음 → v2 sub-plan L213이 **C/D에도 동일 의무 추가 박제** = 1차 감사 B-4 우려 해소 + candidate-pool과 비대칭 보강

**판정**: PASS. 단 **candidate-pool.md L40/L54에도 "Go 통과 시 Week 3 walk-forward 의무" 박제 추가 권고** = follow-up (NIT-N2 신규).

### W-1 SR annualization 정정: PASS + follow-up

- v2 L51, L88, L95, L127, L181 = `sqrt(365)` / `year_freq='365 days'` 일관 박제 PASS
- handover #21 신규 패턴 "W1-04 sqrt(252) vs W1-06 sqrt(365) 일관성 깨짐" 박제 권고 명시 (L51) — 단 별도 task로 W1 산출물 정정 = 본 W2-03 책무 외 위임 정직
- **잔존 약점**: handover-2026-04-17.md 본문에 "패턴 #21" 실제 박제는 1차 감사 trace 외 미실시. v2 sub-plan은 권고만 명시 → 본 잔존은 별도 task 책무로 위임 정직성 확보

### W-2 N_trials 보강: PASS

- v2 L159 "V[SR_n] 협소성 alarm 박제 + max(empirical_var, 1.0) 또는 1.0 정규화 둘 다 산출"
- v2 L160 "Stage 2 게이트 시 재산정 의무 (별도 박제 사이클)"
- 두 항목 모두 1차 감사 W-2 권고 정확 반영 PASS

### W-3 vectorbt multi-asset 정정: PASS

- v2 L124-126 = 방식 A (각 페어 독립 Portfolio) 박제 채택 명시 + 방식 B는 W3 ensemble 시 적용 명시 PASS
- L127 vectorbt API 호출 박제 (`freq='1D', year_freq='365 days'` + cash_sharing 무관) 명시 PASS

### W-4 Common-window vs max-span 비대칭 정정: PASS

- v2 L134 = "**Go 기준 평가는 max-span (Primary) 단독**. common-window는 secondary 분석용. 사후에 common-window를 Go 기준으로 변경 = cherry-pick = cycle 3 강제" 명시 PASS
- 1차 감사 W-4 cherry-pick 차단 우려 해소

### W-5 ta KeltnerChannel 정정: PASS

- v2 L91-93 = `KELTNER_WINDOW=20, KELTNER_ATR_MULT=1.5, BOLLINGER_WINDOW=20, BOLLINGER_SIGMA=2.0, ATR_WINDOW=14, SL_HARD=0.08` 본 sub-plan 직접 박제 + ta API 호출 시그니처 명시 강제 PASS
- 1차 감사 W-5 외부 인용만 처리 우려 해소

### W-6 데이터 출처 정정: PARTIAL PASS

- v2 L118-122 = BTC W1-01 + ETH/Tier2 W2-01.4 freeze + 종료일 모두 2026-04-12 UTC 일관 박제 PASS
- 그러나 L94 "5 페어" 표현 잔존 → B-3 PARTIAL FAIL과 동일 사례

---

## 새 발견 사항

### BLOCKING (0건)

- 사실 오류, 자기 모순, 통계 부정확 등 BLOCKING급 발견 X. v2 정정은 1차 감사 권고를 정직하게 반영 + Wikipedia 원문 cross-check 통과.

### WARNING (1건)

#### W-N1: DSR z-score form vs Φ(z) 확률 형태 학계 표준 차이 사용자 보고 권고

**위치**: v2 L186-191 (DSR Go 기준 명확화 섹션)

**문제**:
- Wikipedia + Bailey-Lopez 2014 원문 표준 표현은 `DSR = Φ(z)` 확률 형태 [0,1]. 학계 인용 통상 "DSR > 0.95 (95% confidence)" 형태로 보고
- v2 박제는 z-score form 채택 + decisions-final.md L518 사용자 박제 "DSR > 0"과 동치 + 비교용 Φ(DSR_z) 동시 산출 → 수학적 정확 + 단순성 확보 (PASS)
- 그러나 **외부 감사관 또는 학계 독자가 v2 결과 "DSR_z = 0.3" 같은 수치를 보면 "이게 정상인가? Wikipedia는 Φ(z) 형태인데..." 혼동 가능성**
- 사용자 보고 시 명시 권고: "Wikipedia/Bailey-Lopez 원문 표준은 Φ(z) 확률 형태이며 학계 인용 시 'DSR > 0.95' 형태로 보고됨. 본 v2는 decisions-final.md L518 사용자 박제 'DSR > 0'과의 동치 + 단순성을 위해 z-score form (DSR_z) 채택. 두 form은 수학적으로 동치 (DSR_z > 0 ⇔ Φ(DSR_z) > 0.5). 외부 감사 보고 시 DSR_prob = Φ(DSR_z) 동시 보고 책무 (L191)"

**수정 권고**:
1. v2 L188-191 박제에 "Wikipedia/Bailey-Lopez 원문 표준 = Φ(z) 확률 형태. 학계 통상 'DSR > 0.95' 보고. 본 v2는 사용자 박제 'DSR > 0'과 동치성 + 단순성으로 z-score form 채택. 외부 감사 시 두 form 동시 보고 책무" 한 줄 추가
2. 또는 본 W-N1을 사용자 보고 시 직접 명시 → v2 자체 변경 X

### NIT (1건 신규)

#### NIT-N1: L94 "5 페어" 표현 모호 (B-3 잔존)

**위치**: v2 L94

**문제**: "데이터 로드 + SHA256 무결성 재검증 (W1-01 BTC + W2-01.4 5 페어, W-6 정정)" — "5 페어"가 (a) W2-01.4 신규 수집 5 페어 (ETH + Tier2 4) 또는 (b) 본문 L57의 "5 페어" 산술 오류 잔존인지 모호. 의미는 (a)일 것으로 추정되나 외부 감사관 혼동 유발

**수정 권고**: "W1-01 BTC (1 페어) + W2-01.4 신규 수집 5 페어 (ETH + Tier2 XRP/SOL/TRX/DOGE) = 총 6 페어 SHA256 무결성 재검증" 으로 명확화

#### NIT-N2: candidate-pool.md L40/L54 Walk-forward 의무 박제 누락 (B-4 follow-up)

**위치**: candidate-pool.md L40 (Strategy C 평가 조건) + L54 (Strategy D 평가 조건)

**문제**: v2 sub-plan L213이 C/D에도 Week 3 walk-forward 의무를 박제했으나 candidate-pool.md L40/L54 본문은 "Primary Sharpe>0.8 AND DSR>0. Secondary 마킹"만 명시. Walk-forward 재검증 의무는 candidate-pool에 누락 = 다음 사이클 작성자가 candidate-pool만 보면 비대칭 위험

**수정 권고**: candidate-pool.md L40 (Strategy C) + L54 (Strategy D) 행에 "Recall 시 의무 (대칭)" 항목 추가 = "DSR > 0 필수. Week 3 walk-forward 재검증 필수 (Strategy A와 대칭, W2-03 v2 L213 박제)"

#### NIT-N3 (cross-reference 모순): decisions-final.md L515 ADA 박제 잔존 vs v2 sub-plan TRX 박제

**위치**: decisions-final.md L515 vs v2 sub-plan L84

**문제**:
- decisions-final.md L515: `Tier 2 {XRP, SOL, ADA, DOGE} × {A, C, D}` 박제 (cycle 1 잔존)
- v2 sub-plan L84: `PAIRS_TIER2 = ["KRW-XRP", "KRW-SOL", "KRW-TRX", "KRW-DOGE"]` (cycle 2 v5 박제, ADA → TRX)
- W2-01 cycle 1 → cycle 2 전이 시 decisions-final.md L515 박제는 미갱신 잔존 (handover #15 "sub-plan/decisions-final 전파 누락" 패턴 재발)
- **v2 sub-plan은 cycle 2 v5 페어 리스트와 일치하므로 sub-plan 자체는 정합**. 그러나 **decisions-final.md L513-521을 박제 출처로 인용** (L40)하면서 L515의 ADA 잔존 모순을 짚지 않음 = 정직성 약점
- 본 모순은 W2-03 v2 sub-plan 책무 외이지만 외부 감사관 시각에서 cross-reference 정합성 깨짐

**수정 권고**:
1. decisions-final.md L515를 `Tier 2 {XRP, SOL, TRX, DOGE}`로 정정 + 변경 이력 박제 (cycle 2 v5 사용자 승인 시점 미갱신 누락 명시)
2. 또는 v2 sub-plan에서 "decisions-final.md L515 cycle 1 잔존 박제. 실제 적용은 cycle 2 v5 (XRP/SOL/TRX/DOGE)" 명시 cross-reference 추가
3. handover-2026-04-17.md에 패턴 #15 추가 발생 사례로 박제

---

## 잔존 NIT 평가 (NIT-1 ~ NIT-4)

### NIT-1 (외부 감사 단계 W2-03.7 신설) — 잔존, follow-up 적정

**평가**:
- v2 SubTask 목록 (L63-71) = W2-03.0~.6 6단계로 구성. SubTask "외부 감사" 단계 (예: W2-03.5b 또는 W2-03.7) 신설 박제 X
- L24 "작업자 = Solo + backtest-reviewer + 외부 감사관 + 사용자 Go/No-Go 결정"으로 외부 감사관 책무는 명시되어 있으나 SubTask 단계로 박제 X
- 본 1차+2차 감사가 그 책무를 대신 수행 중 → **잔존이 사용자 승인 진입을 막을 정도의 결함은 아님**. 단 W2-02 v5 패턴 (W2-02.3 외부 감사 SubTask 박제) 일관성 깨짐 = follow-up

**판정**: 잔존 허용. 단 사용자 승인 시점에 "본 v2는 1차+2차 외부 감사 완료 + 사용자 승인 = 사실상 NIT-1 책무 수행 완료" 명시 권고

### NIT-2 (Stage 1 킬 카운터 정의) — 잔존, follow-up 적정

**평가**:
- decisions-final.md L482 "Stage 1 킬 카운터: +1 (Week 1 종료 시점)" 박제 확인
- v2 sub-plan L208/L217 "Stage 1 킬 카운터 +1" 인용만 있고 현재 값 (=1) 명시 X
- **잔존이 사용자 승인 진입을 막을 정도의 결함은 아님**. 단 사용자 보고 시 "현재 카운터 = 1 (Week 1 종료). W2-03 No-Go 시 = 2" 명시 권고

**판정**: 잔존 허용

### NIT-3 (6단 evidence 구조) — 잔존, follow-up 적정

**평가**:
- v2 L234 "backtest-reviewer 호출 (W1-06 패턴, 6단 evidence 구조)" 인용만 있고 6단 항목 (데이터/파라미터/결과/자동검증/룰준수/리뷰) 명시 X
- CLAUDE.md Context Map L31 인용 위임 = 정합. 단 본 sub-plan에서 자기완결적 박제는 약함

**판정**: 잔존 허용

### NIT-4 (파일명 placeholder) — 잔존, follow-up 적정

**평가**:
- v2 L292 "`.evidence/agent-reviews/w2-03-insample-grid-review-202604XX.md` (외부 감사 trace)" placeholder 잔존
- 본 1차/2차 감사 trace 실제 파일명 = `w2-03-insample-grid-review-2026-04-19.md`
- v2 사용자 승인 진입 시 v3 박제 시점에 placeholder → 확정 갱신 권고

**판정**: 잔존 허용 (v3 박제 시점에 정정)

### 본 v2 사용자 승인 진입 적절성?

**판정**: **APPROVED with follow-up — 사용자 승인 진입 적격**

근거:
1. 1차 감사 BLOCKING 4건 모두 본문 정정 박제 확인 (B-1/B-2 DSR 공식 Wikipedia cross-check 통과 + B-3 핵심 산술 PASS + B-4 Recall 대칭 PASS)
2. 1차 감사 WARNING 6건 모두 정정 박제 확인 (W-1 sqrt(365) + W-2 V[SR_n] alarm + W-3 방식 A + W-4 max-span Primary + W-5 ta API + W-6 데이터 출처)
3. 2차 감사 신규 발견은 BLOCKING 0 + WARNING 1 (사용자 보고 시 명시) + NIT 3 (follow-up)
4. NIT-1~4 잔존은 사용자 승인 진입을 막을 정도의 결함 X

**사용자 승인 진입 권고 형식**:
- (a) 본 2차 감사 결과 + 사용자 보고 후 즉시 사용자 승인 진입 → v3 박제 (NIT-N1/N2/N3 + 잔존 NIT-1~4 follow-up 트래킹) → W2-03 실행 진입 (권장)
- (b) NIT-N1/N2/N3까지 정정 후 3차 감사 → 사용자 승인 (시간 비용 大, 한계효용 小)
- (c) 사용자 결정에 위임

---

## DSR 공식 v2 검증 (Bailey 2014 원문 cross-check)

### Wikipedia "Deflated Sharpe ratio" 직접 fetch 결과 (2026-04-19 본 세션)

| 항목 | v2 박제 | Wikipedia 원문 | 평가 |
|------|---------|----------------|------|
| SR_0 (expected max SR) | `sqrt(V[SR_n]) × ((1-γ)Φ⁻¹(1 - 1/N) + γΦ⁻¹(1 - 1/(N·e)))` | `√V[SR̂_n] × ((1−γ)Φ⁻¹[1−1/N] + γ·Φ⁻¹[1−1/(Ne)])` | **완전 일치 PASS** |
| γ 값 | Euler-Mascheroni ≈ 0.5772156649 | ≈ 0.5772 | PASS |
| Φ⁻¹ | scipy.stats.norm.ppf | inverse standard normal CDF | PASS |
| V[SR_n] | 6셀 sample variance + 1.0 정규화 비교 | cross-sectional variance of Sharpe Ratios across trials | PASS |
| DSR 분자 | `(SR_hat - SR_0) × sqrt((T-1)/...)` | `(SR̂* − SR_0) · √(T−1)/...` | PASS |
| DSR 분모 SR | **SR_0** (B-2 정정) | **SR_0** | **완전 일치 PASS** |
| DSR 형태 | z-score form (DSR_z) + Φ(DSR_z) 동시 산출 | Φ(z) 확률 [0,1] 표준 | **수학적 동치, 표현 형태 차이 (W-N1 권고)** |
| Go 기준 의미 | "DSR_z > 0 ⇔ SR_hat > SR_0 ⇔ Φ(DSR_z) > 0.5" | Φ(DSR) > 0.95 (95% 신뢰) 통상 | 박제 신뢰도 차이 (사용자 박제 "DSR > 0" 정직 채택) |

### N_trials 박제 결정 (W-2 정정 후 평가)

- v2 박제 N_trials = 6 (Primary만, W2 게이트 한정) + Stage 2 게이트 시 재산정 의무 명시 → **정직 + 보수적 PASS**
- V[SR_n] 협소성 alarm + 1.0 정규화 비교 둘 다 산출 → **6셀 분포 좁음 위험 alarm 박제 PASS**

### V[SR_n] 산출 약점 보강 (1차 감사 alarm 정정 확인)

- v2 L159 = "V[SR_n] = max(empirical_var, 1.0) 또는 1.0 정규화 둘 다 산출 + 비교" 박제 PASS
- 6셀 결과 좁을 시 두 산출값 차이가 명확하게 사용자에게 보고됨

---

## cycle 1/2 학습 패턴 재발 검증

| # | 패턴 | v2 재발 여부 | 비고 |
|---|------|--------------|------|
| #1 | Evidence 수치 오기재 | **부분 재발** (L94 "5 페어" 모호) | NIT-N1 신규 |
| #2 | 문서 버전 라벨 미갱신 | 미재발 (v2 라벨 + 변경 이력 정확) | - |
| #3 | execution-plan 체크박스 미체크 | 해당 X (실행 전 단계) | - |
| #4 | backtest-reviewer 좁은 스코프 | 미재발 (W-3 정정 박제) | - |
| #5 | fillna() FutureWarning | 해당 X | - |
| #6 | research/outputs gitignore | 미재발 | - |
| #7 | 사전 지정 기준 측정 창 미정의 | 미재발 | - |
| #8 | Multiple testing 미보정 | 미재발 (DSR + W-2 정정) | - |
| #9 | Soft contamination 간과 | 미재발 (decisions-final.md 인용) | - |
| #10 | Fallback "임계값 완화" | 미재발 (Go 기준 사후 변경 차단 박제 L218) | - |
| #11 | 측정 창 inclusive off-by-one | 해당 X | - |
| #12 | Fallback 라벨 misnomer | 미재발 | - |
| #13 | 박제 문서 자기 freeze 시점 순환 정의 | 미재발 (v2 박제 시점 명확) | - |
| #14 | 실측 cherry-pick 경로 재유입 | 미재발 (W-4 정정 박제 L134) | - |
| #15 | sub-plan/decisions-final 전파 누락 | **재발** (decisions-final.md L515 ADA 잔존 vs v2 TRX) | NIT-N3 신규 |
| #16 | 외부 라이브러리 응답 필드 추측 | 미재발 (W-5 정정 박제) | - |
| #17 | 사전 지정 추정 리스트의 빗나감 위험 | 미재발 | - |
| #18 | 외부 코인 정체 추측 | 해당 X | - |
| #19 | 수치 단위 표기 오류 | 미재발 (W-1 sqrt(365) 박제) | - |
| #20 | sub-plan 박제 vs .gitignore 실제 룰 충돌 | 미재발 | - |
| #21 | W1 SR annualization 일관성 깨짐 (1차 감사 신규) | **잔존 (별도 task 위임)** | v2 L51 책무 명시, follow-up |

**재발 사례**: #1 부분 재발 (NIT-N1) + #15 재발 (NIT-N3) + #21 잔존 (별도 task) = 3건. 모두 사용자 승인 진입을 막을 정도 X.

---

## 종합 평가

### 사전 지정 정합성

- v2 박제 페어/전략/셀/Go 기준 = cycle 2 v5 + W2-02 v5 + decisions-final.md L513-521과 일관 (단 L515 ADA 잔존 cross-reference 모순은 별도 정정 책무, NIT-N3)
- W2-02 v5 변경 금지 서약 발효 + ta API 호출 본 sub-plan 직접 박제 (W-5 정정) → cycle 1 학습 #15 패턴 차단

### DSR 공식 정확성

- **Wikipedia 원문 cross-check 통과 PASS**:
  - SR_0 정확 공식 박제 (γ Euler-Mascheroni + Φ⁻¹ + V[SR_n]) 완전 일치
  - DSR 분모 SR_0 사용 명시 (B-2 정정)
  - z-score form vs Φ(z) 확률 형태 두 표현 동치 박제 + 비교용 동시 산출
  - V[SR_n] 6셀 sample variance + 1.0 정규화 둘 다 산출 박제
- 단 W-N1 권고: 사용자 보고 시 "Wikipedia/Bailey-Lopez 원문 표준 = Φ(z) 확률 형태이지만 본 v2는 사용자 박제 'DSR > 0'과 동치 + 단순성으로 z-score form 채택" 명시 책무

### Multiple testing 한계 정직성

- v2 L195 박제 "6 primary 셀도 family-wise 오류 여지. DSR로 부분 완화. 최종 검증은 Week 3 walk-forward" PASS
- W-2 정정 = N_trials=6 (W2 게이트 한정) + Stage 2 게이트 시 재산정 의무 박제 = 정직 + 보수적 PASS
- V[SR_n] 협소성 alarm 박제 PASS

### 사용자 결정 정직성

- v2 L218 "Go 기준 사후 변경 절대 금지 (cycle 1 학습 #5 임계값 완화 함정)" 박제 PASS
- v2 L239 "사용자 명시적 결정 (자동 진행 X)" 박제 PASS
- B-4 정정 = Strategy A/C/D 모두 Go 통과 시 Week 3 walk-forward 의무 대칭 박제 → 사용자에게 정확한 옵션 제시 가능

---

## 외부 감사관 의견

**판정: APPROVED with follow-up**

다음 단계 권고:

1. **즉시 사용자 보고 (W-N1 명시 책무)**:
   - DSR z-score form vs Φ(z) 확률 형태 학계 표준 차이 명시
   - "본 v2는 사용자 박제 'DSR > 0' 동치 + 단순성으로 z-score form 채택. 외부 감사 보고 시 두 form 동시 보고 책무 (L191)"

2. **사용자 승인 진입 (권장 옵션 a)**:
   - 본 2차 감사 결과 보고 + 사용자 승인 진입 → v3 박제 (NIT-N1/N2/N3 정정 + NIT-1~4 follow-up 트래킹) → W2-03 실행 진입
   - W2-02 v5 패턴 (1차 + 2차 + 3차 외부 감사 + 옵션 C 정정 5건)과 일관 (W2-03도 1차 + 2차 외부 감사 + 정정 적용)

3. **v3 박제 권고 항목 (사용자 승인 후 적용)**:
   - L94 "5 페어" → "총 6 페어 (BTC + ETH + Tier2 4)" 명확화 (NIT-N1)
   - candidate-pool.md L40/L54 Walk-forward 의무 박제 추가 (NIT-N2)
   - decisions-final.md L515 ADA → TRX 정정 또는 cross-reference 명시 (NIT-N3)
   - NIT-1~4 잔존은 사용자 승인 시점에 follow-up 트래킹 박제 (handover + execution-plan)

4. **별도 task 책무 (W2-03 외부)**:
   - handover #21 "W1-04 sqrt(252) vs W1-06 sqrt(365) 일관성 깨짐" 별도 task로 W1 산출물 정정 (v2 L51 위임 박제 일관)
   - decisions-final.md L515 cycle 1 잔존 박제 정정 (NIT-N3와 통합 가능)

5. **재감사 절차 (옵션)**:
   - (a) 본 2차 감사 통과 → 사용자 승인 진입 → v3 정정 → W2-03 실행 (권장, 시간 효율)
   - (b) 3차 외부 감사 호출 (별도 agent) — NIT-N1/N2/N3 정정 후 검증. 한계효용 小 (BLOCKING 0 + WARNING 1 사용자 보고 책무로 해소 가능)
   - (c) 사용자 결정에 위임

**감사 결과 신뢰도**:
- B-1/B-2 정정 = Wikipedia "Deflated Sharpe ratio" 직접 fetch (2026-04-19 본 세션) cross-check PASS. Bailey-Lopez 2014 PDF는 압축 인코딩 한계로 직접 인용 X (Wikipedia 본문이 원문 공식 정확 인용). 외부 감사 trace 신뢰성 유지
- B-3/B-4/W-1~W-6 정정 = sub-plan 본문 + candidate-pool.md + decisions-final.md cross-check 직접 확인
- 신규 발견 (W-N1 + NIT-N1/N2/N3) = 본 세션 직접 확인, 모두 사용자 승인 진입을 막을 정도의 결함 X

**다음 단계**: 사용자 보고 → 사용자 승인 진입 (권장) → v3 박제 + W2-03 실행 진입.

---

## 참고 출처 (2차 감사 trace 신뢰성 보강)

- Wikipedia "Deflated Sharpe ratio" (2026-04-19 본 세션 직접 fetch, SR_0 + DSR 공식 verbatim 확인): https://en.wikipedia.org/wiki/Deflated_Sharpe_ratio
- Bailey & López de Prado (2014) PDF (davidhbailey.com): 압축 인코딩으로 직접 인용 한계, Wikipedia 원문 인용으로 보강
- v2 sub-plan: `docs/stage1-subplans/w2-03-insample-grid.md` (L1-329 직접 검증)
- 1차 감사 trace: `.evidence/agent-reviews/w2-03-insample-grid-review-2026-04-19.md` (본 파일 상단)
- candidate-pool.md (Strategy A/C/D Recall 의무 cross-check): `docs/candidate-pool.md` L17-86
- decisions-final.md (Stage 1 킬 카운터 + Week 2 게이트 + Tier 2 박제): `docs/decisions-final.md` L482, L513-521, L515

---

# W2-03 sub-plan v3 외부 감사 (3차) — 적대적 외부 감사관 trace

- **검증 대상**: `docs/stage1-subplans/w2-03-insample-grid.md` v3 (2026-04-19, 1차 BLOCKING 4 + WARNING 6 + NIT 5 정정 + 2차 APPROVED with follow-up + 옵션 A 정정 NIT-N1/N2/N3 + NIT-1~4 + W-N1 모두 적용)
- **감사관**: Claude (적대적 외부 감사관 모드, rubber-stamp 절대 금지, 3차 감사관)
- **검증 일시**: 2026-04-19 (2차 감사 + v3 정정 직후)
- **cross-document 검증 대상**:
  - `docs/decisions-final.md` L515 (NIT-N3 정정: ADA → TRX)
  - `docs/candidate-pool.md` L41/L55 (NIT-N2 정정: Strategy C/D Recall 의무 박제)

---

## 3차 감사 판정

**APPROVED** (BLOCKING 0건, WARNING 0건, NIT 2건 잔존 follow-up — 사용자 승인 진입 적격)

핵심 두 줄 요약:
1. v2 → v3 옵션 A 정정 8건 (NIT-N1/N2/N3 + NIT-1~4 + W-N1) **모두 정확 적용 확인**. cross-document (decisions-final.md L515 TRX 박제 + candidate-pool.md L41/L55 Recall 의무 박제) 정합성 회복. v2 잔존 NIT 모두 해소.
2. 3차 감사 grep 기반 잔존 표현 점검 결과 새 사실 오류 / 자기 모순 / 누락 X. handover #15 (cross-document) + #21 (sqrt 일관성, 별도 task 위임) 외 cycle 1/2 패턴 재발 0건. **사용자 승인 진입 권고**.

---

## v3 정정 검증 (8건)

### NIT-N1 (L94 "5 페어" 모호) — PASS

**v3 박제** (L96):
```
데이터 로드 + SHA256 무결성 재검증 (W1-01 BTC + W2-01.4 신규 5 페어 = **총 6 페어**, W-6 + NIT-N1 정정)
```

**판정**: PASS
- "신규 5 페어 = **총 6 페어**" 명확화 → BTC 1 + W2-01.4 신규 5 = 6 페어 산술 명시
- L60 본문 "**6 페어**" + L239 evidence "6 페어 SHA256" 모두 일관
- 외부 감사관 혼동 유발 표현 제거

### NIT-N2 (candidate-pool.md L41/L55 Walk-forward 의무 박제 누락) — PASS (cross-document)

**v3 박제 (candidate-pool.md L41 Strategy C)**:
```
**Recall 시 의무 (NIT-N2 정정, B-4 cross-document)** | Go 통과 시 **DSR-adjusted 평가 + Week 3 walk-forward 재검증 의무 강제** (Strategy A Recall mechanism과 대칭, W2-03 v2 박제 인용)
```

**v3 박제 (candidate-pool.md L55 Strategy D)**: 동일 박제 적용 확인

**판정**: PASS
- Strategy A L28 "DSR > 0 필수. Week 3 walk-forward 재검증 필수" 와 비대칭 해소
- "(Strategy A Recall mechanism과 대칭, W2-03 v2 박제 인용)" 인용 추적 체인 명확
- W2-03 sub-plan L213-215 "A/C/D 어느 전략이 Go 통과해도 Week 3 walk-forward 의무 강제"와 cross-document 일관

**잔존 약점 (NIT급 follow-up, 본 정정 외)**: candidate-pool.md L96 변경 이력에 "v2"가 명시되었으나 "v3 NIT-N2 정정" 행은 별도 추가 X. 단, L41/L55 본문에 "(NIT-N2 정정, B-4 cross-document)" 명시되어 있으므로 cross-reference 추적은 가능. follow-up.

### NIT-N3 (decisions-final.md L515 ADA 잔존 vs sub-plan TRX) — PASS (cross-document)

**v3 박제 (decisions-final.md L515)**:
```
**Exploratory 대상**: Tier 2 {XRP, SOL, **TRX**, DOGE} × {A, C, D} = 12셀 (참고용, Go 기여 X) — **cycle 1 박제 ADA → cycle 2 v5 TRX 정정 (2026-04-19, W2-01 cycle 2 완료 + W2-02 v5 사용자 승인 발효)**
```

**판정**: PASS
- L515 ADA → TRX 정정 + 변경 이유 + 변경 시점 + 트리거 모두 명시
- L504 (cycle 1 history "Tier 2 후보: XRP, SOL, ADA, DOGE") 그대로 유지 = 정확 (history 보존, cycle 1 시점 박제)
- L562/L565/L566/L587/L597 (cycle 1 ADA top10 밖 사례) 잔존 = 정확 (history 보존, Fallback (ii) 발동 사례)
- v3 sub-plan L86 `PAIRS_TIER2 = ["KRW-XRP", "KRW-SOL", "KRW-TRX", "KRW-DOGE"]` 와 cross-document 일관
- **handover #15 패턴 재발 차단 책무 수행**

**잔존 cross-document 약점 (NIT급 follow-up, 본 정정 외)**:
- `docs/stage1-execution-plan.md` L207 "Tier 2 후보: XRP, SOL, ADA, DOGE" + L227 "Tier 2 {XRP, SOL, ADA, DOGE} × {A, C, D} = 12셀" — cycle 2 v5 TRX 미반영 잔존
- `docs/stage1-subplans/w2-01-data-expansion.md` L72/L154/L281/L309 — cycle 1 ADA 잔존 (cycle 1 history는 일관, 단 L281 데이터 파일명도 ADA 잔존 = cycle 2 신규 freeze 데이터 ETH/XRP/SOL/TRX/DOGE와 cross-document 모순)
- 본 v3 정정 책무는 **decisions-final.md L515** 단독이므로 PASS. 단 stage1-execution-plan.md + w2-01-data-expansion.md 잔존은 별도 task로 follow-up 권고

### NIT-1 (W2-03.7 외부 감사 SubTask 신설) — PASS

**v3 박제** (L73):
```
| **W2-03.7** | **Pending** | **외부 감사 (적대적, sub-plan + 결과 정합성, NIT-1 정정)**: cycle 1/2 W2-01.1/W2-02 패턴 = 1차/2차/3차 감사 사이클. 본 sub-plan은 v1 → v2 → v3 (1차+2차 감사 + 옵션 A 정정) 거침. W2-03.6 결과 사용자 Go/No-Go 결정 직전에 **추가 외부 감사 1회** (결과 정합성 + cherry-pick 통로 검증) 호출 |
```

**판정**: PASS
- W2-02 v5 패턴 (W2-02.3 외부 감사 SubTask 박제) 일관성 회복
- "W2-03.6 결과 사용자 Go/No-Go 결정 직전" 시점 명시 + "결과 정합성 + cherry-pick 통로 검증" 스코프 명시
- L303 evidence 파일명 (`w2-03-insample-grid-result-review-2026-04-XX.md`) 산출물 매핑 명확
- 단 SubTask 본문 (산출물 형식 / backtest-reviewer 호출 여부 / 사용자 보고 형식) 상세 박제는 표 1행으로만 처리 = NIT급 follow-up

### NIT-2 (Stage 1 킬 카운터 정의 + 현재 값 박제) — PASS

**v3 박제** (L236):
```
**Stage 1 킬 카운터 박제 (NIT-2 정정)**: decisions-final.md L482 정의 인용 + 현재 값 박제. W1 No-Go 후 카운터 +1 여부는 본 W2-03.5/.6 사용자 결정 시점 박제 (Go 시 카운터 0 유지 + W3 진입 / No-Go 시 +1 + Week 3 재탐색 vs Stage 1 종료)
```

**판정**: PASS (조건부)
- decisions-final.md L482 인용 책무 명시 + 현재 값 박제 책무 명시
- Go/No-Go 시점별 카운터 처리 (Go 시 0 유지 / No-Go 시 +1) 명확
- **조건부**: decisions-final.md L482 cross-check 결과 = "Stage 1 킬 카운터: +1 (Week 1 종료 시점)" → 현재 값 = **1**. v3 sub-plan은 "현재 값" 명시 박제 책무를 W2-03.6 실행 시점에 위임 = 정직 (실행 전 sub-plan에서 현재 값을 본문에 직접 박제하면 W2-03.6 실행 시점에 다른 결정으로 변경된 경우 cross-document 모순 위험)
- 단 W2-02 v5 패턴은 "Stage 1 킬 카운터 = 1 (Week 1 종료 시점, decisions-final.md L482)" 직접 박제했음 → 본 v3는 위임 박제. 사용자 승인 진입 시 위임 정직성 OK 판단

### NIT-3 (6단 evidence 항목 명시) — PASS

**v3 박제** (L238-244):
```
**6단 evidence 작성 (NIT-3 정정)**: `.evidence/w2-03-insample-grid.txt` (또는 `.md`):
  - 1. **데이터**: 6 페어 SHA256 + freeze 종료일 + actual 범위
  - 2. **파라미터**: A/C/D 박제 상수 + ta API 호출 + sqrt(365) annualization
  - 3. **결과**: 18셀 grid 산출 (Sharpe, MDD, Win rate, # trades, PF, 연도별)
  - 4. **자동 검증**: 무결성 assert + DSR 단위 unit test + Common-window vs max-span 비대칭 보고
  - 5. **룰 준수**: 사전 지정 파라미터 변경 X + cherry-pick 차단 + Tier 2 Go 기여 X + Recall mechanism 강제
  - 6. **리뷰**: backtest-reviewer trace 인용
```

**판정**: PASS
- CLAUDE.md Context Map L31 "6단 구조 (데이터/파라미터/결과/자동검증/룰준수/리뷰)" 직접 박제 + 각 항목별 W2-03 스코프 구체 내용 명시
- 자기완결적 박제 강도 회복

### NIT-4 (evidence 파일명 placeholder 결정) — PASS (조건부)

**v3 박제** (L302):
```
`.evidence/w2-03-insample-grid-2026-04-XX.md` (6단 구조, 실행 시점 날짜 박제, NIT-4 정정)
```

**판정**: PASS
- "실행 시점 날짜 박제, NIT-4 정정" 명시 → 실행 시점에 placeholder 갱신 책무 명확화
- L303 추가 박제 `.evidence/agent-reviews/w2-03-insample-grid-result-review-2026-04-XX.md` 도 동일 패턴 (실행 시점 결정)
- 1차 감사 trace 파일명은 실제 `2026-04-19` 박제 = 정확 (sub-plan v3 L303 좌측 박제와 일치)

### W-N1 (DSR z-score vs Φ(z) 사용자 보고 책무) — PASS

**v3 박제** (L231):
```
**DSR 결과 (W-N1 명시 책무)**: DSR_z form (`SR_hat - SR_0` 단위) **+** `DSR_prob = Φ(DSR_z)` 동시 보고. 사용자 보고 시 두 표현 병기 (Bailey 2014 학계 표준 + 사용자 박제 "DSR > 0" 일치)
```

**판정**: PASS
- 2차 감사 W-N1 권고 "두 form 동시 보고 책무" 정확 반영
- "Bailey 2014 학계 표준 + 사용자 박제 'DSR > 0' 일치" 양립 명시
- L195 산출 단계 박제 "6 primary 셀 각각 DSR_z + DSR_prob 산출" + L196 식별 단계 "DSR_z > 0 셀 식별" 일관
- W2-03.6 사용자 보고 단계에서 W-N1 명시 책무 박제 = follow-up 트래킹 완료

---

## cross-document 일관성 검증

### candidate-pool.md L41/L55 (NIT-N2 정정)

- **L41 (Strategy C Recall 의무)**: PASS — Strategy A L28과 대칭 박제 + W2-03 v2 박제 인용
- **L55 (Strategy D Recall 의무)**: PASS — 동일 패턴 적용 확인
- **변경 이력 L96 (v2 행)**: "외부 감사 1차+2차+3차 APPROVED with follow-up" 명시. 단 본 v3 정정은 candidate-pool.md를 "v2"로 유지 (변경 이력 v3 행 신규 추가 X). cross-reference 추적은 L41/L55 본문 "(NIT-N2 정정, B-4 cross-document)" 박제로 가능. **잔존 NIT급 follow-up**: candidate-pool.md 변경 이력에 v3 행 추가 권고 (옵션, 한계효용 小)

### decisions-final.md L515 (NIT-N3 정정)

- **L515 본문**: PASS — `Tier 2 {XRP, SOL, **TRX**, DOGE}` 박제 + cycle 2 v5 TRX 정정 시점/트리거 명시
- **L504 (cycle 1 history)**: 그대로 유지 — 정확 (cycle 1 시점 박제 보존)
- **L562/L565/L566/L587/L597 (cycle 1 ADA Fallback (ii) 사례)**: 그대로 유지 — 정확 (history 보존)
- handover #15 패턴 재발 차단 책무 수행 PASS

### sub-plan W2-03 v3 본문 (자기 일관성)

- **L60 "6 페어"** + **L96 "총 6 페어"** + **L239 "6 페어 SHA256"** = 일관 PASS
- **L86 PAIRS_TIER2 (TRX 박제)** + decisions-final.md L515 = 일관 PASS
- **L213-215 A/C/D 대칭 의무** + candidate-pool.md L41/L55 = cross-document 일관 PASS
- **L181 DSR 분모 SR_0** (B-2 정정) + L191 DSR_prob 동시 산출 + L231 사용자 보고 두 form 병기 = 일관 PASS
- **L52/L88/L97/L129 sqrt(365) / year_freq='365 days'** = 일관 PASS

### 3차 감사 잔존 표현 grep 점검

**"5 페어" grep**:
- L10/L11 (변경 이력 v2/v3 행) = 정정 history 박제, 사실 오류 X. PASS
- L96 "신규 5 페어 = **총 6 페어**" = 명확화 박제, NIT-N1 정정 PASS
- 본문 산술 오류 잔존 0건 확인

**"ADA" grep (decisions-final.md)**:
- L504 (cycle 1 history "Tier 2 후보") = 정확
- L515 정정 박제 (TRX 채택, ADA history 박제) = 정확
- L562/L565/L566/L587/L597 (cycle 1 Fallback (ii) 사례) = 정확
- W2-03 v3 sub-plan에서 ADA 잔존 = 0건 (L11 변경 이력에 정정 trigger로만 등장)

**"ADA" grep (잔존 다른 문서)**:
- `docs/stage1-execution-plan.md` L207/L227 — cycle 2 v5 미반영 잔존 (W2-03 v3 책무 외, 별도 follow-up)
- `docs/stage1-subplans/w2-01-data-expansion.md` L72/L154/L281/L309 — cycle 1 history는 정확하나 L281 데이터 파일명 cycle 2 미반영 잔존 (W2-03 v3 책무 외, 별도 follow-up)
- `docs/pair-selection-criteria-week2.md` (cycle 1 v4 사이클 중단 격리 문서) — 정확 (cycle 1 history 보존)

**"TRX" grep (decisions-final.md)**:
- L515 (Tier 2 TRX 박제) + L565 (cycle 1 top10 실측 TRX 8위) = 정확

---

## 새 발견 사항

### BLOCKING (0건)

- 사실 오류, 통계 부정확, cross-document 모순 BLOCKING급 발견 X
- v3 옵션 A 정정 8건 모두 정확 + 새 약점 도입 0건 확인

### WARNING (0건)

- 2차 감사 W-N1 (DSR z-score vs Φ(z) 사용자 보고 책무)는 v3 L231 박제로 해소 PASS
- 새 WARNING 발견 X

### NIT (2건 잔존 follow-up, 사용자 승인 진입 무관)

#### NIT-3rd-1: cross-document 잔존 (W2-03 v3 책무 외) — stage1-execution-plan.md L207/L227 + w2-01-data-expansion.md L281 cycle 2 미반영

**위치**:
- `docs/stage1-execution-plan.md` L207 "Tier 2 후보: XRP, SOL, ADA, DOGE"
- `docs/stage1-execution-plan.md` L227 "Tier 2 {XRP, SOL, ADA, DOGE} × {A, C, D} = 12셀"
- `docs/stage1-subplans/w2-01-data-expansion.md` L281 "research/data/KRW-{ETH,XRP,SOL,ADA,DOGE}_{1d,4h}_frozen_20260412.parquet"

**문제**:
- W2-03 v3 NIT-N3 정정은 **decisions-final.md L515** 단독 책무로 한정. cross-document 잔존 (stage1-execution-plan.md + w2-01-data-expansion.md L281)은 미정정
- handover #15 "sub-plan/decisions-final 전파 누락" 패턴이 다른 문서로 확장 잔존
- W2-03 v3 사용자 승인 진입 자체에는 영향 X. 단 다음 세션 작성자가 stage1-execution-plan.md만 보면 cycle 1 ADA를 사실로 오인 위험

**수정 권고**:
1. 별도 follow-up task로 stage1-execution-plan.md L207/L227 cycle 2 v5 TRX 정정 (NIT-N3 패턴 일관 적용)
2. w2-01-data-expansion.md L281 데이터 파일명 cycle 2 v5 TRX 반영 (또는 L281이 cycle 1 history임을 명시)
3. 본 NIT는 W2-03 v3 사용자 승인 진입을 막을 정도 X = follow-up 트래킹 (handover에 패턴 #15 추가 사례 박제)

#### NIT-3rd-2: candidate-pool.md 변경 이력 v3 행 신규 추가 누락

**위치**: `docs/candidate-pool.md` L96 (변경 이력 v2 행만 존재, v3 행 X)

**문제**:
- v3 NIT-N2 정정으로 candidate-pool.md L41/L55 본문 변경 적용 = 사실
- 그러나 변경 이력 표 (L93-96)에 "v3: NIT-N2 정정 — Strategy C/D Recall 의무 박제 (W2-03 v2 박제 cross-document, 2026-04-19)" 행 신규 추가 X
- 단 L41/L55 본문에 "(NIT-N2 정정, B-4 cross-document)" 박제로 cross-reference 추적 가능 → 잔존 약점 minor

**수정 권고**:
1. candidate-pool.md L96 다음에 v3 행 추가 권고: `| 2026-04-19 | **v3 (cross-document follow-up)**: Strategy C L41 + D L55 Recall 의무 박제 추가 — Go 통과 시 DSR-adjusted + Week 3 walk-forward 재검증 의무 강제 (Strategy A Recall mechanism과 대칭). W2-03 v3 NIT-N2 정정 cross-document 적용 | W2-03 v3 옵션 A 정정 |`
2. 본 NIT는 사용자 승인 진입을 막을 정도 X = follow-up 트래킹

---

## 잔존 사항 평가 (사용자 승인 진입 적절성)

### v2 잔존 NIT-1~4 + W-N1 → v3 모두 정정 적용 확인

| 항목 | v2 잔존 → v3 정정 결과 |
|------|------------------------|
| NIT-N1 (L94 "5 페어") | PASS — "신규 5 페어 = 총 6 페어" 명확화 |
| NIT-N2 (candidate-pool.md L41/L55) | PASS — Recall 의무 박제 cross-document 적용 |
| NIT-N3 (decisions-final.md L515) | PASS — ADA → TRX 정정 + 시점/트리거 명시 |
| NIT-1 (W2-03.7 외부 감사 SubTask) | PASS — 신설 박제 |
| NIT-2 (Stage 1 킬 카운터) | PASS (조건부) — L482 인용 + 현재 값 박제 W2-03.6 실행 시점 위임 |
| NIT-3 (6단 evidence 항목) | PASS — 6단 모두 명시 박제 |
| NIT-4 (evidence 파일명) | PASS — 실행 시점 결정 명시 |
| W-N1 (DSR z-score vs Φ(z)) | PASS — 두 form 동시 보고 책무 박제 |

**v2 잔존 8건 모두 정정 PASS**. 새 BLOCKING/WARNING 0건. NIT 2건 잔존 (NIT-3rd-1: cross-document 추가 정정 follow-up + NIT-3rd-2: candidate-pool.md 변경 이력 v3 행 추가)은 사용자 승인 진입을 막을 정도 X.

### 사용자 승인 진입 권고 형식

**판정**: **APPROVED — 사용자 승인 진입 적격**

근거:
1. v3 옵션 A 정정 8건 모두 정확 + 새 사실 오류 / 자기 모순 / 누락 0건
2. cross-document 정합성 (decisions-final.md L515 + candidate-pool.md L41/L55) 회복
3. DSR 공식 + sqrt(365) annualization + Recall 대칭 + Multiple testing 한계 + Go 기준 사후 변경 차단 = 모두 박제 강도 충분
4. NIT 2건 잔존 (NIT-3rd-1/2)는 사용자 승인 진입 후 follow-up 트래킹으로 처리 가능
5. handover #15 패턴 재발 차단 책무 수행 (decisions-final.md L515 정정으로 cycle 1 잔존 vs cycle 2 v5 모순 1차 해소)

**사용자 승인 진입 후 W2-03 실행 진입 권고 단계**:
- (a) 사용자 승인 → W2-03.0 노트북 빌드 → W2-03.1 W-1 미니 테스트 → W2-03.2~.6 grid + DSR + Go/No-Go → W2-03.7 외부 감사 1회 → 사용자 Go/No-Go 결정
- (b) NIT-3rd-1 follow-up 별도 task (stage1-execution-plan.md L207/L227 + w2-01-data-expansion.md L281 cycle 2 TRX 정정)는 W2-03 실행과 병렬 또는 사후 처리

---

## cycle 1/2 학습 패턴 재발 검증

| # | 패턴 | v3 재발 여부 | 비고 |
|---|------|--------------|------|
| #1 | Evidence 수치 오기재 | 미재발 (L96 "신규 5 페어 = 총 6 페어" 명확화) | NIT-N1 정정 PASS |
| #2 | 문서 버전 라벨 미갱신 | 미재발 (v3 라벨 + 변경 이력 v3 행 정확) | - |
| #3 | execution-plan 체크박스 미체크 | 해당 X (실행 전 단계) | - |
| #4 | backtest-reviewer 좁은 스코프 | 미재발 | - |
| #5 | fillna() FutureWarning | 해당 X | - |
| #6 | research/outputs gitignore | 미재발 | - |
| #7 | 사전 지정 기준 측정 창 미정의 | 미재발 | - |
| #8 | Multiple testing 미보정 | 미재발 (DSR + W-2 정정) | - |
| #9 | Soft contamination 간과 | 미재발 (decisions-final.md 인용) | - |
| #10 | Fallback "임계값 완화" | 미재발 (Go 기준 사후 변경 차단 박제) | - |
| #11 | 측정 창 inclusive off-by-one | 해당 X | - |
| #12 | Fallback 라벨 misnomer | 미재발 | - |
| #13 | 박제 문서 자기 freeze 시점 순환 정의 | 미재발 (v3 박제 시점 명확) | - |
| #14 | 실측 cherry-pick 경로 재유입 | 미재발 (W-4 정정 박제 L136) | - |
| #15 | sub-plan/decisions-final 전파 누락 | **부분 해소 (NIT-N3 정정)** + 잔존 (stage1-execution-plan.md L207/L227 + w2-01-data-expansion.md L281) | NIT-3rd-1 신규 follow-up |
| #16 | 외부 라이브러리 응답 필드 추측 | 미재발 (W-5 정정 박제) | - |
| #17 | 사전 지정 추정 리스트의 빗나감 위험 | 미재발 | - |
| #18 | 외부 코인 정체 추측 | 해당 X | - |
| #19 | 수치 단위 표기 오류 | 미재발 (W-1 sqrt(365) 박제) | - |
| #20 | sub-plan 박제 vs .gitignore 실제 룰 충돌 | 미재발 | - |
| #21 | W1 SR annualization 일관성 깨짐 | 잔존 (별도 task 위임 일관) | follow-up |

**3차 감사 재발 사례**: #15 부분 해소 (W2-03 v3 책무 NIT-N3는 정정 / 잔존 cross-document NIT-3rd-1 follow-up) + #21 잔존 (별도 task) = 2건. 모두 사용자 승인 진입을 막을 정도 X. **새 패턴 재발 0건**.

### v3 정정 과정에서 새 약점 도입 검증 (grep-based 일관성 점검, W2-02 cycle 학습)

- "5 페어" grep = 변경 이력 history 박제 + L96 명확화 = 사실 오류 0건
- "ADA" grep (W2-03 v3 sub-plan) = 변경 이력 정정 trigger 외 0건
- "TRX" grep (decisions-final.md L515) = 정확 박제 + cross-document sub-plan L86과 일관
- "DSR_z / DSR_prob / Φ(DSR_z)" grep = L181/L191/L195/L196/L231 일관 박제
- "Stage 1 킬 카운터" grep = L210/L219/L236/L249/L287/L314 일관 박제 + decisions-final.md L482 인용 책무 명시
- **새 약점 도입 0건 확인**

---

## 종합 평가

### 사전 지정 정합성

- v3 박제 페어/전략/셀/Go 기준 = cycle 2 v5 + W2-02 v5 + decisions-final.md L513-521 (L515 TRX 정정 후) + candidate-pool.md L17-86 (L41/L55 Recall 의무 정정 후) 모두 일관 cross-document 회복

### DSR 공식 정확성

- v2 Wikipedia 원문 cross-check 통과 + v3 W-N1 정정 (사용자 보고 두 form 병기 책무) 추가 적용 = **수학적 정확 + 사용자 박제 'DSR > 0' 동치 + 학계 표준 양립 PASS**

### Multiple testing 한계 정직성

- v2 W-2 정정 (N_trials=6 W2 게이트 한정 + Stage 2 게이트 재산정 의무 + V[SR_n] 협소성 alarm) 그대로 유지 PASS

### 사용자 결정 정직성

- v2 박제 "Go 기준 사후 변경 절대 금지 (CRITICAL)" + v3 W-N1 정정 (DSR 두 form 동시 보고 책무) → 사용자에게 정확한 정보 + 옵션 제시 가능

### cross-document 일관성

- decisions-final.md L515 TRX 정정 + candidate-pool.md L41/L55 Recall 대칭 박제 = handover #15 패턴 재발 1차 차단
- 단 stage1-execution-plan.md + w2-01-data-expansion.md L281 cycle 2 TRX 미반영 잔존 = NIT-3rd-1 follow-up

---

## 외부 감사관 의견

**판정: APPROVED**

### 다음 단계 권고

1. **즉시 사용자 승인 진입** (권장):
   - v3 옵션 A 정정 8건 모두 PASS + 새 BLOCKING/WARNING 0건 + NIT 2건 follow-up
   - 사용자 보고 형식: "v3 정정 8건 모두 PASS. 3차 감사 신규 NIT 2건 (cross-document stage1-execution-plan.md/w2-01-data-expansion.md 추가 정정 + candidate-pool.md 변경 이력 v3 행) follow-up 트래킹 후 W2-03 실행 진입"

2. **W2-03 실행 진입 후 follow-up 처리** (병렬 또는 사후):
   - NIT-3rd-1: stage1-execution-plan.md L207/L227 cycle 2 v5 TRX 정정 + w2-01-data-expansion.md L281 데이터 파일명 정정 (또는 L281이 cycle 1 history임을 명시)
   - NIT-3rd-2: candidate-pool.md L96 변경 이력 v3 행 추가
   - 별도 task ("docs cross-document cycle 2 v5 일관성 정리") 또는 W2-03 실행 commit 시 함께 처리

3. **재감사 절차 (옵션, 한계효용 판단)**:
   - (a) 본 3차 감사 통과 → 사용자 승인 진입 → W2-03 실행 (권장, 시간 효율 + cycle 1/2 패턴 일관)
   - (b) 4차 외부 감사 호출 — 한계효용 小 (NIT 2건 잔존은 follow-up 처리 가능)
   - (c) 사용자 결정에 위임

### 감사 결과 신뢰도

- **v3 정정 8건**: 본 세션 직접 grep + Read cross-check (decisions-final.md L515 + candidate-pool.md L41/L55 + sub-plan v3 본문 L60/L73/L86/L94/L96/L181/L191/L195/L213/L231/L236/L238-244/L302) → 모두 정확 적용 확인
- **새 NIT 2건**: 본 세션 grep (`ADA` in `docs/`) + Read (stage1-execution-plan.md + w2-01-data-expansion.md + candidate-pool.md) → 정확 발견. 사용자 승인 진입을 막을 정도 X
- **cycle 1/2 패턴 재발**: handover #1~#21 직접 cross-check → #15 부분 해소 + #21 잔존 (별도 task) 외 재발 0건

### 사용자 승인 권고 형식

**다음 단계**: 사용자 보고 → 사용자 승인 진입 → v4 박제 (3차 감사 결과 변경 이력 v4 행 추가 + NIT-3rd-1/2 follow-up 트래킹) → W2-03 실행 진입.

---

## 참고 출처 (3차 감사 trace 신뢰성 보강)

- v3 sub-plan: `docs/stage1-subplans/w2-03-insample-grid.md` (L1-340 직접 검증)
- 1차+2차 감사 trace: `.evidence/agent-reviews/w2-03-insample-grid-review-2026-04-19.md` (본 파일 상단)
- candidate-pool.md (NIT-N2 정정 cross-check): `docs/candidate-pool.md` L41/L55 + L96 변경 이력
- decisions-final.md (NIT-N3 정정 cross-check): `docs/decisions-final.md` L515 + L482 (Stage 1 킬 카운터)
- 잔존 cross-document (NIT-3rd-1): `docs/stage1-execution-plan.md` L207/L227 + `docs/stage1-subplans/w2-01-data-expansion.md` L72/L154/L281/L309
- grep 점검 키워드: "5 페어" / "ADA" / "TRX" / "DSR_z" / "DSR_prob" / "Stage 1 킬 카운터" / "2026-04-XX"
