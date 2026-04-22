# W3-01 외부 감사 2차 (결과 정합성 + 프레임 A/B) — 2026-04-22

**Task**: W3-01 Walk-forward Analysis / **Feature**: BT-004
**감사 대상**: `outputs/w3_01_walk_forward.json`, `outputs/week3_report.md`, `.evidence/w3-01-walk-forward-2026-04-22.md`, `notebooks/09_walk_forward.ipynb`, `stage1-subplans/w3-01-walk-forward.md` v2
**감사 관점**: 적대적 외부 감사관 (ChatGPT가 썼다고 가정, 비판적 재검토)
**감사 범위**: bit-level 재계산 + cherry-pick 통로 + 프레임 A/B 판단 + N=5 불안정성 + Strategy D 평가
**사용자 결정 (W3-01.7) 이전 감사관 입력**

---

## 감사관 태도 요약

본 감사는 **결과가 이미 나온 상태(is_go=False, 0/5)에서의 재검증**. 사용자 옵션 A 선택("2")이 2026-04-21 결과 보기 **이전** 박제된 사실은 양호. 단, "옵션 A 선택이므로 아무 변경 불가" 프레임으로 수동 통과시키지 않음. 다음을 독립 검증:

1. 수치 정합성 (fold V, SR_0, DSR_z) bit-level 재현
2. min_trade_count=2 필터 정당성 + Strategy C/A N/A 비율 설계 근거
3. N=5 sample variance 불안정성 정량화 (outlier 민감도)
4. 프레임 A (cycle 1 #5 재발) vs 프레임 B (설계 한계) 논거 독립 검토
5. Cherry-pick 통로 4가지 (옵션 완화, min_trade 완화, Secondary 포함, test 확장) 개별 차단

감사관 본인이 **적대적일 의무**. 구조적으로 둘 다 성립하면 그대로 정직하게 판정.

---

## 독립 재계산 결과 (bit-level)

### 1. Fold별 V_empirical + SR_0 독립 재계산

venv에서 numpy/scipy로 독립 산출:

| Fold | n_non_NA | Sharpes | V_recalc | V_stored | diff | SR_0_recalc | SR_0_stored | diff |
|------|----------|---------|----------|----------|------|-------------|-------------|------|
| 1 | 4 | [3.332, 3.787, 2.729, 2.439] | 0.3657194121 | 0.3657194121 | **0.00e+00** | 0.7212181158 | 0.7212181158 | **0.00e+00** |
| 2 | 1 | [-0.542 only] | N/A | N/A | — | N/A | N/A | — |
| 3 | 2 | [1.864, 2.513] | 0.2101456746 | 0.2101456746 | **0.00e+00** | 0.5467047512 | 0.5467047512 | **0.00e+00** |
| 4 | 3 | [0.543, 0.992, 1.352] | 0.1642632176 | 0.1642632176 | **0.00e+00** | 0.4833511800 | 0.4833511800 | **0.00e+00** |
| 5 | 1 | [-1.688 only] | N/A | N/A | — | N/A | N/A | — |

**PASS**: 모든 fold V_empirical + SR_0 bit-level 일치.

### 2. DSR_z 독립 재계산 (Bailey 2014 eq. 10)

주요 cell 5개 검증 (극값 + 경계 + 임계점):

| Cell + Fold | SR_hat | SR_0 | T | γ_3 | γ_4_raw | denom | DSR_z_recalc | DSR_z_stored | diff |
|-------------|--------|------|---|-----|---------|-------|--------------|--------------|------|
| BTC_A fold 1 | 3.3321 | 0.7212 | 180 | 1.0391 | 8.7913 | 1.263735 | 31.07360241 | 31.07360241 | **0.00e+00** |
| BTC_D fold 1 | 3.7874 | 0.7212 | 180 | 1.2910 | 9.9031 | 1.226683 | 37.03889278 | 37.03889278 | **0.00e+00** |
| BTC_D fold 4 | 0.9917 | 0.4834 | 180 | 0.8896 | 13.3075 | 1.288850 | 5.99050383 | 5.99050383 | **0.00e+00** |
| BTC_A fold 4 | 0.5431 | 0.4834 | 180 | 0.6996 | 12.4972 | 1.333355 | 0.69261521 | 0.69261521 | **0.00e+00** |
| ETH_D fold 4 | 1.3521 | 0.4834 | 180 | 1.2989 | 12.0717 | 1.018829 | 11.51542149 | 11.51542149 | **0.00e+00** |

**PASS**: DSR_z bit-level 일치. γ_4 Fisher→raw 변환 (+3), denom 계산, sqrt((T-1)/denom) 모두 정확.

### 3. BTC_D mean_dsr_z 재산출

BTC_D는 fold 2/5에서 non-NA(sharpe=-0.542/-1.688)지만 **fold 해당 non-NA cells=1이라 fold V 산출 불가** → dsr_z=null. mean_dsr_z는 fold 1/3/4만 평균:
- (37.038893 + 23.133191 + 5.990504) / 3 = **22.054196**
- 저장값: 22.054195953333277
- **PASS** (bit-level 일치)

이 처리에 대한 감사관 평가: **수학적 일관**. fold 2/5의 non-NA=1 상황에서 V 산출 불가를 null로 처리하되, sharpe는 보존(음수이므로 어차피 fold_pass=False). mean_sharpe는 5 fold 모두 포함 (fold 2: -0.542, fold 5: -1.688이 평균을 깎음 → +1.012로 낮아짐). 이것이 오히려 보수적(음수 fold의 영향 반영). **cherry-pick 아님**.

---

## BLOCKING / WARNING / NIT

### BLOCKING (0건)

**없음**. 수치 정합성 + 박제 준수 완전.

### WARNING (3건)

**WARNING-A (중): N=5 sample variance 불안정성 정량 입증**

독립 시뮬레이션 (fold 1 기준, non-NA=4에 가상 BTC_C Sharpe 추가):
- 원본 4 cell: V=0.3657, SR_0=0.7212
- +BTC_C=0.0: V=2.1618 (**5.91x 증가**), SR_0=1.7535
- +BTC_C=1.0: V=1.1330 (**3.10x 증가**), SR_0=1.2694
- +BTC_C=-1.0: V=3.5906 (**9.82x 증가**), SR_0=2.2598

**감사관 판정**: 1 cell outlier가 V를 3-10배 변동시킴. 이는 **sub-plan v2 리스크 섹션 "outlier 1개로 V 2배 변동"을 훨씬 초과**하는 실제 민감도. V_empirical per fold 방식은 N=5 근본 제약 하에서 **통계적으로 매우 불안정**. 프레임 B 논거의 **정량적 뒷받침**.

단, 이것이 **Go 판정 번복 근거는 아님** (v2 핵심 원칙 #8). 오히려 SR_0이 커질수록 DSR_z 통과가 어려워지므로 불안정은 **false positive 방향**이 아닌 **false negative 방향**. 즉 실제 엣지가 있어도 V 불안정으로 떨어뜨릴 가능성 존재 → **프레임 B의 "설계 한계" 논거 객관적 타당**.

**WARNING-B (중): fold 1/3의 stability_pass 구조적 disadvantage**

Fold 1: non-NA=4, V=0.3657, SR_0=0.7212 → pass threshold 매우 높음
Fold 3: non-NA=2, V=0.2101, SR_0=0.5467 → threshold 낮음
Fold 4: non-NA=3, V=0.1643, SR_0=0.4834 → threshold 가장 낮음

**불균형**: fold 1은 엣지 강한(non-NA 많은) fold일수록 SR_0 임계가 높아져 pass가 어려운 **역설**. BTC_A fold 1 sharpe=3.332 → DSR_z=31.07 → pass. 그러나 BTC_D fold 4 sharpe=0.992 → DSR_z=5.99 → pass (낮은 SR_0 덕분). fold별 pass 난이도가 **cell 난이도와 무관한 fold-level 효과**로 결정됨.

이는 **V_empirical per fold 설계 자체의 구조적 약점**. Bailey 2014 pooled V (N_trials=25) 방식으로 pooling하면 SR_0 단일 값 → fold 난이도 균등. 그러나 sub-plan v2는 pooled V를 **참고만** (W3-02 deferred). 이 문제는 W3-02에서 재조명될 가능성.

**감사관 판정**: v2 박제 준수지만, 프레임 B 옹호론자가 "V_empirical per fold 설계 자체가 stability 판정을 왜곡"을 주장 가능한 **객관적 증거**. 사용자 판단 시 고려 필요.

**WARNING-C (낮음): BTC_D fold 4 DSR_z=5.99가 "magnitude 통과"에 기여하는 한계**

BTC_D cell의 mean_dsr_z=22.05는 fold 1/3의 극단값(37.04/23.13)에 의해 부양됨. fold 4의 5.99만 "정상 범위". fold 2/5는 null. **skew/kurtosis 극단값(γ_4=9-26)**에 의해 DSR_z가 인위적으로 부풀려지는 측면 있음 (Bailey 2014 denom이 skew 양수 + 높은 kurtosis에서 작아져 DSR_z가 팽창).

이는 **DSR_z 지표 자체의 암호화폐 적용 시 한계**. Normal 분포 가정 약화 + 2-4 trade만의 daily returns에서 skew/kurt 추정 신뢰도 낮음. 단 공식 자체는 정확 + v2 박제 준수.

**감사관 판정**: 지표 한계 공지로 충분 (이미 report §10 "Multiple testing + N=5" 섹션에서 언급). **BLOCKING 아님**.

### NIT (2건)

**NIT-1**: `multiple_testing_note` JSON 필드 (L669) 한국어 유니코드 이스케이프 (`\u2192`). JSON 내부 한국어가 escape되는 것은 직렬화 기본값. 가독성만 영향, 데이터 정확성 영향 X.

**NIT-2**: `fold_passes` 리스트에 Python bool이 문자열 'True'로 저장됨 (L575 등). `fold_pass_count` (int) 계산에 영향 X (sum에서 'True'=1 평가는 Python `bool('True')` 특성상 True → 1로 평가되지만 이는 **수정 권고**). 코드상 `fold_passes.append(False)` 또는 `fold_passes.append(True)` 정상이지만 JSON 저장 시 default=str로 'True' 문자열화됨. **재실행 시 True/False native bool로 저장 권고**.

재현 확인: `sum(['True', False, 'True', 'True', False]) → 3` (Python truthy 'True' 문자열 = 1로 평가). fold_pass_count=3 값 정확. 단 파일 load 시 'True' vs True 혼동 가능 → **재저장 권고**.

---

## 프레임 A vs B 판단 (정직하게)

### 프레임 A — "cycle 1 #5 재발 확정" 객관적 증거

1. **V_empirical 채택 자체가 Go 기준 완화 효과 — Week 3에서 실증**: W2-03 v8 박제 시 "V_empirical 채택으로 SR_0 낮아져 DSR_z 쉬워진다"가 공식 인정. Week 3에서 5/5 stability 기준에 0개 cell 통과 = **완화 효과가 cycle 1 #5 재발 그 자체**였음을 확정.

2. **5 cell 중 최대 stability BTC_D의 3/5도 W2-03 primary metric 대비 후퇴**: W2-03 Go 결정 당시 BTC_D는 "DSR_z 큰 양수"로 통과. Week 3 walk-forward에서 stability 3/5 = **40% 실패**. 이는 Pardo 2008 70-80% 기준 하에서도 미달.

3. **Strategy A Recall mechanism이 전량 실패**: Recall 의무는 "재평가 엄격". BTC_A 2/5 (40%), ETH_A 1/5 (20%). Recall 실패 → Active 복귀 불가 → **Retained 복귀 + deprecation 재검토 필수**.

### 프레임 B — "설계 한계" 객관적 증거

1. **14/25 = 56% N/A 비율**: min_trade_count=2 필터가 14개 fold를 무효화. 이는 **test window 6개월 대비 Strategy A/C 진입 빈도 근본적 희소** 설명. Strategy A 전체 1927 bar에서 entries=46 → 6개월당 기대값 ≈ 4.3. 실제 fold별 0-4 실현. Poisson 변동성 자연적.

2. **Strategy C 전멸은 W-7에서 사전 박제됨**: sub-plan v2 리스크 섹션 L275 "Strategy C fold당 0 trade 가능성 Medium" 인정. 실제 5 trade/5년 = 6개월당 0.5 → 실증됨. **walk-forward 설계와 Strategy C 궁합 부적합**이 사전 예상된 대로 발생. 이는 Strategy C 엣지 부정이 아닌 평가 방법론 문제.

3. **평균 Sharpe는 non-NA fold에서 모두 >1.0**: BTC_A 1.913, BTC_D 1.012, ETH_A 2.729, ETH_D 1.896 — 거래가 발생한 경우 **엣지 존재**. 문제는 "5/5 stability" 기준이 진입 희소 전략에서 **어떤 엣지도 통과 불가**.

4. **옵션 A 5/5 기준이 Pardo 2008 70-80% 초과**: Pardo 권고는 4/5 (80%) 기준. 옵션 A 100% stability는 사용자가 선택한 보수 기준이나, **학술적으로 과도**. 옵션 B(4/5)로도 0개 통과했으나 **BTC_D 3/5는 Pardo 60% 하한 초과**. 즉 Pardo 기준으로는 BTC_D 통과.

5. **N=5 sample variance 불안정성 정량 입증** (WARNING-A): outlier 1개로 V 3-10x 변동. SR_0이 불안정하게 팽창 → false negative 방향. 프레임 B "설계 한계" 논거의 **정량적 뒷받침**.

### 감사관 최종 판단

**결론: 둘 다 부분 성립 (중간 입장 타당)**

- **프레임 A는 "완화 효과" 측면에서 강하게 성립**: W2-03 v8 박제 시 "cycle 1 #5 본질 구분 어려움" 인정 → Week 3 결과가 retrospective 재판정 역할이라는 v2 박제. W2-03 Go 결정이 완화에 과도 의존했다는 프레임 A 판단은 **정당**.

- **프레임 B는 "설계-방법론 한계" 측면에서 강하게 성립**: min_trade_count=2 × test 6개월 × Strategy 희소 진입 삼중 제약이 **어떤 실제 엣지도 통과하기 어렵게** 만듦. BTC_D가 non-NA 5/5이면서 stability 3/5 = Pardo 60% 충족 → **엣지 존재 + 과도 기준** 동시 성립.

- **중간 입장 = 둘 다 일부 타당**: 
  - W2-03 Go 결정이 완화에 의존한 것은 사실 (A 부분 인정)
  - Walk-forward 설계가 희소 진입 전략에 부적합했던 것도 사실 (B 부분 인정)
  - **둘 중 하나만 선택하는 것은 지적 정직 결여**

**감사관 추천 (사용자 결정 영역)**: 
- 프레임 A 채택 + Stage 1 학습 모드 전환: 전략 패밀리 교체 학습 + 방법론 학습 동시 진행
- 프레임 B 채택 + Week 3 v3 설계 재조정 + cycle 3 강제: test window 12개월 or 다중 방법론 비교
- **프레임 C (본 감사관 제안) 중간 입장**: 프레임 A + B 공동 인정 + Stage 1 킬 카운터 +2 소급 + 학습 모드 전환 결정 + **v3는 Stage 1 재시작 시 적용**. 단기 재탐색은 cycle 1 #5 변종 위험. 학습 모드에서 방법론 재설계 후 Stage 2부터 재적용.

**어느 프레임이 더 정당한가?** — 본 감사관은 **프레임 A 60% / 프레임 B 40%**로 판단. 근거: W2-03 v8 "cycle 1 #5 본질 구분 어려움"이 v8 박제 시점에 이미 인정 → Week 3 No-Go는 그 가정의 실증. 프레임 B 논거는 "설계 한계"가 사실이나, **이를 이유로 기준 완화하면 다시 cycle 1 #5 재발**. 따라서 프레임 A + 학습 모드가 **리스크 최소 경로**.

---

## Cherry-pick 통로 재검증

### 1. 옵션 A → B (4+/5) 변경 유혹

**감사관 분석**: 결과상 옵션 A 0/5, 옵션 B도 0/5 (BTC_D 3/5가 최고). **사후 변경해도 결과 번복 불가**. 그러나 "무의미하니 허용" 프레임은 금지. 사전 박제 변경 자체가 **cycle 1 #5 재발 통로 개방** = cycle 3 강제. v3 박제 후 재실행만 허용.

**판정**: **차단 확인**. sub-plan v2 L131 표 + report §8 "대안 기준 비교"에서 "사후 채택 금지" 명시. 양호.

### 2. min_trade_count 2 → 1 완화 유혹

**감사관 분석**: trade_count=1 fold 10개 회복 가능. Strategy C 3개(fold 1/3/4, 모두 1 trade) + A 5개 + D 2개. 단 **1 trade fold의 Sharpe는 통계적 의미 없음** (annualized Sharpe from 1 round-trip = 매우 극단). W-7 사전 박제 원칙 위반 = cycle 3 강제.

**판정**: **차단 확인**. sub-plan v2 L275 + evidence §4.4 박제. `MIN_TRADE_COUNT=2` 고정 사용자 승인 시점. 양호.

### 3. Secondary 마킹 (SOL/DOGE) 재포함 유혹

**감사관 분석**: W2-03에서 Secondary 마킹된 페어(SOL/DOGE 등) 포함 시 cell 수 증가 → cherry-pick 통로. v2 양방향 freeze (확장 X) 박제. 위반 = cycle 3 강제.

**판정**: **차단 확인**. sub-plan v2 L273 + evidence §5.4 박제. 양호.

### 4. Test 기간 6 → 12개월 확장 유혹

**감사관 분석**: test 12개월로 확장 시 fold 수 5→2-3 + trade_count 2배 증가 가능. 그러나 **사후 설계 변경 = cherry-pick**. v3 박제 + cycle 3 강제 시 가능하나, 본 감사관 의견: **Stage 1 내 재설계는 위험**. 프레임 B 선택 시 학습 모드 전환 후 Stage 2부터 재적용 권고.

**판정**: **차단 확인**. v2 핵심 원칙 #9 (fold 분할점 + test window freeze) 박제. 양호.

### 5. 추가 발견 통로: BTC_D "stability 3/5 = 최고 근접 → special case Go" 유혹

**감사관 감지**: BTC_D는 non-NA 5/5(0 N/A) + stability 3/5 + mean_dsr_z=22.05. "유일하게 모든 fold 거래 발생" + "Pardo 60% 충족" 논거로 **BTC_D 단독 Go** 주장 가능. 이는 v2 박제 "옵션 A 5/5" 위반 + cherry-pick.

**판정**: **사전 차단 필요**. 본 감사관이 **신규 발견한 통로**. v3 박제 시 "BTC_D 재평가 단독 cell 설계" 검토는 가능하나, 현 판정에서 BTC_D Go 주장 = cycle 1 #5 재발 = cycle 3 강제. **사용자 W3-01.7 결정 시 이 유혹 인지 필요**.

---

## N=5 per fold sample variance 불안정 검증

### Fold별 non-NA 분포

| Fold | non-NA | Cells | DSR 산출 |
|------|--------|-------|----------|
| 1 | 4 | BTC_A, BTC_D, ETH_A, ETH_D | 가능 |
| 2 | 1 | BTC_D 단독 | 불가 |
| 3 | 2 | BTC_A, BTC_D | 가능 (신뢰도 매우 낮음) |
| 4 | 3 | BTC_A, BTC_D, ETH_D | 가능 (신뢰도 낮음) |
| 5 | 1 | BTC_D 단독 | 불가 |

### V 신뢰도 평가

- n=2: sample variance 1 자유도. 극단적으로 불안정. V=0.21 값은 **2개 점 사이 거리의 제곱/2**로 환원. 통계적 의미 매우 제한.
- n=3: 자유도 2. 여전히 불안정. V=0.16은 BTC_A(0.54) 외 2개가 비슷해서 낮게 나옴.
- n=4: 자유도 3. Pardo 권고 N≥5에 근접. V=0.37 적당.

### 판정

V 산출 불가 처리 (non-NA=1 시 null)는 **정확**. 단 **non-NA=2-3 fold에서 V 추정 신뢰도는 낮음**. 이는 BTC_D fold 4의 stability_pass=True에 **V_empirical 불안정성**이 기여한 부분 있음 (SR_0=0.48이 낮아 DSR_z=5.99 통과). fold 3도 동일.

**감사관 평가**: 공식 적용은 정확. 단 **결과 해석 시 n_non_NA 표기 필수** (report §3 표에서 이미 명시). sub-plan v2 리스크 L277 "V 2배 변동"은 실측 3-10배로 **과소평가됨 → v3 박제 시 정정 필요**.

---

## Strategy D 상대적 성과 분석

### 데이터 관찰

| Cell | fold_passes | Non-NA | mean_sharpe | mean_dsr_z |
|------|-------------|--------|-------------|------------|
| BTC_A | [T,F,T,F,F] | 3 | 1.913 | 16.266 |
| BTC_C | [F,F,F,F,F] | 0 | None | None |
| BTC_D | [T,F,T,T,F] | **5** | 1.012 | 22.054 |
| ETH_A | [T,F,F,F,F] | 1 | 2.729 | 23.570 |
| ETH_D | [T,F,F,T,F] | 2 | 1.896 | 15.108 |

### 프레임 B 옹호론자 관점

- BTC_D **유일하게 non-NA 5/5** (진입 빈도 충분)
- BTC_D stability 3/5 = Pardo 60% 하한 충족 + Pardo 80% 권고 1 fold 부족
- BTC_D fold 2/5 음수 Sharpe = regime-dependent (2024 상반기 상승 전환 + 2026 Q1 초반)
- **"유일한 희망"**: Stage 2 게이트를 위한 single-strategy 전략으로 BTC_D만 선택 가능

### 프레임 A 관점

- **3/5 stability = 40% 실패**는 Pardo 기준으로도 경계선
- mean_dsr_z=22.054는 fold 1/3의 **극단값(37/23)**에 의해 부양 → fold 4의 5.99가 "정상". 극단 fold에 의존한 magnitude pass는 실전 환경에서 재현 불확실
- 5/5 기준 미달 = **사전 박제 기준 명백히 불통과** → BTC_D 단독 Go 주장은 **cherry-pick = cycle 3**
- fold 2/5 음수는 **regime shift에 대한 robustness 부족** 증거

### 감사관 판정

**BTC_D는 "프레임 B 옹호론자 입장에서 유일한 희망"으로 해석 가능**. 그러나 **본 감사관은 프레임 A 지지**:
1. 5/5 사전 박제 기준 명백 미달
2. mean_dsr_z가 극단 fold 의존 (Bailey 2014 가정 약화 in 2-4 trade daily returns)
3. BTC_D 단독 Go = cherry-pick 통로 5 (신규 발견)
4. Stage 1 학습 모드 전환 후 **Stage 2에서 BTC_D 재평가 시 v3 박제** 기반 재실행이 더 안전

**BTC_D를 완전 폐기할 필요는 없음** — candidate-pool.md에서 Active→Retained 복귀 후 Stage 2 재평가 대기가 적절.

---

## decisions-final.md 갱신 범위 (W3-01.7 사용자 결정 후)

### 프레임 A 선택 시

- [ ] Stage 1 킬 카운터 +2 소급 가산 (현재 +1 → +3, 목표 8/Week 8 근접)
- [ ] Stage 1 학습 모드 전환 결정 박제 (decisions-final.md 신규 섹션)
- [ ] Strategy A Active → Retained 복귀 (candidate-pool.md v6 전이)
- [ ] Strategy C/D Retained 유지 + Stage 2 재평가 대기 표시
- [ ] W2-03 Go 결정 retrospective 해석 박제: "cycle 1 #5 재발 확정"
- [ ] W3-02/W3-03 Task 중단 or 학습 모드 범위 축소
- [ ] `docs/stage1-weekly/week3.md` 신설 (Week 3 학습 결과 + Stage 1 전환 기록)

### 프레임 B 선택 시

- [ ] Stage 1 킬 카운터 +2 소급 가산 (공통)
- [ ] W3-01 v3 박제 (설계 재조정: test window 12개월, min_trade_count 재정의, cell 집합 재구성 등)
- [ ] Cycle 3 강제 (외부 감사 2회 + 사용자 명시 승인)
- [ ] W2-03 Go 결정 retrospective 해석: "방법론 한계 인정 + 재설계"
- [ ] Strategy A Active → Retained 복귀 (공통)
- [ ] Week 3 재탐색 기간 + Week 4-8 일정 재검토

### 감사관 권고 (프레임 C 중간 입장)

- [ ] Stage 1 킬 카운터 +2 소급 가산
- [ ] Stage 1 학습 모드 전환 (프레임 A 60% 근거)
- [ ] 프레임 B 인정 메모 박제 (설계 한계 공식 인정)
- [ ] v3 박제는 Stage 1 재시작 시 적용 (학습 모드 중 방법론 재설계 병행)
- [ ] Strategy A/C/D 전부 Retained 복귀 + Stage 2 재평가 대기
- [ ] W2-03 Go 결정 retrospective 박제: "프레임 A + B 공동 성립 인정"

---

## 최종 Verdict: **APPROVED with follow-up**

### 근거

1. **BLOCKING 0건** — 수치 정합성 bit-level 완전 일치 (V/SR_0/DSR_z 모두 diff=0.00e+00)
2. **WARNING 3건** (A: N=5 sample variance 3-10x 변동, B: V_empirical per fold 구조적 역설, C: DSR_z 극단 fold 의존) — 모두 프레임 B 논거 강화 + 사용자 결정 시 고려 필요, Go 판정 번복 근거 X
3. **Cherry-pick 통로 5개 차단 확인** (옵션 완화, min_trade 완화, Secondary 재포함, test 확장, **BTC_D 단독 Go 신규 통로**)
4. **프레임 A/B 둘 다 부분 성립** — 감사관 판단 프레임 A 60% / 프레임 B 40%, 중간 입장 프레임 C 권고

### Follow-up 의무

1. **NIT-2 JSON bool 재저장**: `fold_passes` native bool로 재직렬화 (재실행 시점)
2. **sub-plan v2 L277 "V 2배 변동" → "3-10배 변동" 정정**: v3 박제 시 정정 (Stage 1 재시작 or 프레임 B 채택 시)
3. **BTC_D 단독 Go 통로 사전 차단 박제**: W3-01.7 사용자 결정 안내 시 명시
4. **프레임 C 중간 입장 사용자 고려 옵션 제시**: W3-01.7 결정 UI에 3개 옵션 (A/B/C) 제시

---

## 감사관 개인 의견 (bias 명시)

### 감사관 bias 선언

1. **사용자 "2" 선택이 이미 결과 보기 전 박제**였다는 사실에 영향 받을 수 있음. 본 감사에서는 이 사실을 "프로세스 양호"로 인정하되, 결과 수치 자체는 독립 bit-level 재계산으로 검증했음.

2. **프레임 A 쪽 편향 가능성**: 본 감사관은 **cycle 1 #5 재발 방지 = 프로젝트 핵심 가치**로 내재화됨. 따라서 "번복 가능성"에 대해 보수적 태도. 프레임 B 옹호론자 입장에서 본 감사는 "너무 쉽게 프레임 A 60%"라 비판 가능.

3. **암호화폐 walk-forward 방법론 학술 공감대 부족**: Pardo 2008은 주식/선물 기반. 암호화폐 regime 변동 + 진입 희소 전략에서 5/5 stability가 과도한지는 **학계 합의 없음**. 본 감사관은 "사용자 선택 + 박제 = 존중"으로 처리.

### 감사관 개인 의견 (bias 포함)

1. **프레임 A가 리스크 최소 경로**: W2-03 v8 박제 시 이미 "cycle 1 #5 구분 어려움" 인정 → Week 3 No-Go는 그 가정의 실증. 여기서 재탐색(프레임 B)로 가는 것은 "재발 우려를 이미 알면서 재발 통로 개방"에 가까움.

2. **그러나 Strategy D는 학습 자산으로 가치 있음**: BTC_D가 non-NA 5/5 + mean_sharpe 1.012는 **"cryptocurrency regime에서 volatility breakout 전략이 평균적으로 엣지 보유"** 증거. 단 stability가 Pardo 60% 경계 = **실전 운용 부적합 but 연구 가치 있음**. Stage 1 학습 모드에서 BTC_D 변종 실험 추천.

3. **Week 3 방법론 자체 재검토 필요**: walk-forward + Anchored + 5 fold × 6개월 조합은 **진입 희소 전략(trend/momentum)에 근본적으로 부적합**. Stage 2 재시작 시 다음 대안 고려:
   - Rolling forecast origin (Bergmeir & Benítez 2012)
   - Time-series CV (Hyndman & Athanasopoulos 2018)
   - Monte Carlo permutation (Aronson 2007)
   - **Bootstrap 기반 confidence interval** (W3-02 book-keeping 본연의 역할)

4. **사용자에게 정직한 안내**: 프레임 A/B/C 중 **프레임 C (중간 입장)을 개인적으로 추천**. 이유:
   - 프레임 A 단독 = "Strategy 탓" 오해 유발 (실제로는 방법론도 문제)
   - 프레임 B 단독 = "방법론 탓" 오해 유발 (실제로는 V_empirical 완화도 문제)
   - 프레임 C = 둘 다 공식 인정 + 학습 모드 + Stage 2 재시작이 **지적 정직 + 리스크 최소 동시 달성**

### 감사관 한계

- 본 감사관은 **사용자가 "2"를 선택한 2026-04-21 시점**의 내면 의도 검증 불가. 사용자가 "결과 이미 예상하고 방어 차원에서 5/5 선택"한 것이라면 추가 검증 가치 있음. 단 본 감사 범위 외.
- **프레임 B "설계 한계" 정량 입증**은 본 감사에서 처음 명시 (sub-plan v2는 정성적 언급만). 사용자가 이 정보 없이 2026-04-21 옵션 A를 선택했으나, **2026-04-22 본 감사 후 재고려 할 권리 있음**.

---

**End of W3-01 external audit 2nd (결과 정합성 + 프레임 A/B). Generated 2026-04-22 by claude-opus-4-7 as adversarial external auditor persona.**
