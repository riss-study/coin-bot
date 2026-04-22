# W3-01 sub-plan v1 외부 감사 — 2026-04-21

- **검증 대상 (v1)**:
  - `docs/stage1-subplans/w3-01-walk-forward.md` v1 (2026-04-21 초안, 사용자 설계 승인 "추천 ㄱㄱ")
  - `docs/stage1-weekly/week3.md` (신설)
  - `docs/stage1-execution-plan.md` W3-01 상태 갱신 (In Progress)
- **교차 검증 (박제 출처)**:
  - `docs/stage1-subplans/w2-03-insample-grid.md` v9 (WARNING-3/-4 박제)
  - `docs/decisions-final.md` L518 + L690+ (W2-03 Go 결정)
  - `docs/candidate-pool.md` v5 (Strategy A/C/D 파라미터 + Recall)
  - `.evidence/agent-reviews/w2-03-v8-v-empirical-adoption-review-2026-04-20.md` (2차 감사 WARNING 원천)
- **페르소나**: 적대적 외부 감사관 (W2-03 v8 박제 준수 + cherry-pick 통로 + V_empirical per fold 안정성 + Go 기준 정당성). 합의자 아님.

---

## 감사관 태도 요약 (1-2 문장)

v1 sub-plan은 W2-03 v8 WARNING-3/-4 박제를 성실히 복제하고 fold 분할점을 날짜로 freeze했으며 독립 재계산 결과 fold bar count + Bailey 2014 N=5 SR_0 계수 모두 산술적으로 정합이다. 다만 (i) "4+ fold AND 평균 pass" Go 기준의 **사전 정당성 분석 부재**, (ii) **V_empirical per fold의 통계적 불안정성** 경감 대책 부재 (N=5 fold별 독립 산출이 정말 cycle 1 #7 "사전 지정 기준 미정의" 재발을 방지하는가), (iii) **Strategy C low-N 거래 caveat**이 "인정만" 있고 fold당 1-2 trade 시 Sharpe가 사실상 noise인 상황에서의 fallback 부재, (iv) **PT-04 선행 적용 주장**의 과잉 claim — 4건이 주요 WARNING이다.

---

## 1. 감사 focus 질문 직답

### Q1. W2-03 v8 WARNING-3/-4 박제 준수 여부

v8 WARNING-3 박제 (decisions-final.md L659-665 + sub-plan v8 L16):

| v8 박제 의무 | v1 sub-plan 박제 위치 | 준수? |
|---|---|---|
| V_empirical 일관 적용 (fold별 sample variance) | L44 "V_empirical 일관 적용 (WARNING-3)", L122-124 "각 fold에서 해당 fold의 5 cell Sharpe sample variance" | OK (명시 박제) |
| Floor 재도입 금지 | L45 "floor 재도입 금지", L126 "Floor 재도입 금지: V_reported=max(V_emp, X) 같은 추가 조치 X" | OK (이중 박제) |
| 임계값 변경 금지 (Sharpe>0.8, DSR_z>0 고정) | L45 "임계값 변경 금지", L140-141 "Sharpe > 0.8 AND DSR_z > 0" 사전 박제 | OK |
| Fold별 DSR 재산정 의무 | L46 "Fold별 DSR 재산정 의무", L122-127 per-fold 계산 공식 박제 | OK |
| 실패 시 Stage 1 킬 카운터 +2 소급 | L47 "실패 시 +2 소급", L142, L191 SubTask .7 박제 | OK |
| Strategy 파라미터 재튜닝 금지 | L49 "사전 지정 파라미터 변경 X", L108 "재튜닝 X" | OK |

**v8 WARNING-4 (실패 시 소급 절차)**: SubTask W3-01.4 L142 "미달 → No-Go: Stage 1 킬 카운터 +2 소급 + 외부 감사 재수행 + 사용자 명시 결정" 충실 박제. SubTask W3-01.7 L191 사용자 결정 옵션 제시 박제.

**판정**: WARNING-3/-4 박제 준수 **완전**. v1이 박제 강제 조항 6건을 모두 이중 박제 (Background 섹션 L44-47 + SubTask 본문 L122-127/140-142)했다. 이는 v8 감사관이 "Week 3에서 V 재논쟁 = cycle 1 #7 재발"을 방지하려던 의도를 기계적으로 구현한 것으로 OK.

**그러나 1건 미묘한 문제**: v1 L49 "Strategy A/C/D W2-02 v5 박제값 그대로 사용 (재튜닝 금지)" — 하지만 Strategy C는 W2-03.1에서 **방법 B (manual trailing_high - ATR_MULT × ATR(t) exit_mask) 채택**으로 구현이 v4 박제에서 변경됨 (candidate-pool.md v4 L37/L39). v1 L109 "Strategy C: 방법 B 트레일링 (manual ...) 박제"는 OK. 단 **"W2-02 v5 박제값 그대로"** 표현은 부정확 — 실제로는 "W2-02 v5 파라미터 + W2-03.1 방법 B 구현 박제"가 정확하다. NIT-1 참조.

### Q2. Cherry-pick 통로 (구조적 검증)

**Q2.1 — Fold 분할점 freeze**:
- v1 L80 `FOLD_SPLIT_POINTS = ["2023-10-15", "2024-04-15", "2024-10-15", "2025-04-15", "2025-10-15"]`
- 독립 재계산 결과 test 기간 모두 179-183일, 평균 182일, ±1% 이내 (하단 §5 참조)
- v1 L226 "v1 박제 5개 날짜 freeze. 결과 본 후 조정 금지"
- **문제**: freeze 시점이 **"v1 박제 = 2026-04-21"**인데 v1이 사용자 승인 전 상태 (L2 "외부 감사 대기"). **사용자 명시 승인 시점이 박제 시점이어야 한다** — 현재 v1은 감사 → 사용자 승인 이후 박제이므로, **본 감사 통과 + 사용자 승인 시점이 fold freeze 시점**. v1 본문이 이를 명시 안 함. → WARNING-1 참조.
- **별도 질문**: fold 분할점 선택 근거 박제 부재. 왜 2023-10-15 시작인지 (= 2021-10-15 + 2년 warmup)? 왜 6개월 test? v1 L80-82가 상수만 박제, **설계 trade-off 논증 부재**. → WARNING-2 참조.

**Q2.2 — Go cells 집합 고정**:
- v1 L48 + L79 "5 cell 고정 {BTC_A, BTC_C, BTC_D, ETH_A, ETH_D}"
- v1 L229 "CRITICAL: W2-03 Go cells 집합 확장 유혹" (ETH_C 재포함 / Secondary 마킹 SOL/DOGE 추가)
- 확장 유혹 명시 + freeze 강제 OK
- **그러나 역방향 유혹 미박제**: **축소 유혹** (예: "Strategy C는 ETH 부적격이니 BTC_C만 대상에서 제외" — Week 3에서 low-N caveat이 심각하면 "Strategy C 제외"로 cell 수를 4로 줄이면 일부 cell이 Go 통과 가능성↑). v1 L228 "Go 이중 조건 과도 (5 cell 모두 fail)"만 언급, 축소 유혹 방지 없음. → WARNING-3 참조.

**Q2.3 — Go 기준 사후 완화 유혹**:
- v1 L50 "Go 기준 사전 지정... 결과 본 후 완화 = cycle 3 강제"
- v1 L146 "인간 개입 금지: Go 기준 변경 절대 금지"
- 박제는 충분. 단 "3+ fold로 완화" 가능성 방지 외에 **"5/5 모두 pass로 엄격화"** 반향 유혹도 주의 필요 (결과 본 후 "더 엄격하게 바꿔도 결과 동일하니 무방" 프레임). 현재 v1 박제는 "변경 X"로 양방향 커버 OK.

**Q2.4 — V_empirical per fold floor 재도입 유혹**:
- v1 L126 "Floor 재도입 금지: V_reported=max(V_emp, X) 같은 추가 조치 X"
- v1 L224 리스크 표 "V_empirical per fold 불안정 (N=5)"에서 **완화 방안**이 "단위 unit test + 재현성 검증. W3-02에서 pooled V 대안 검토"로 되어 있음
- **문제**: "W3-02에서 pooled V 대안 검토"가 **V floor 재도입 우회 경로**로 악용 가능. W3-02에서 "fold별 V 불안정하니 pooled V 채택"이 곧 "fold별 V 폐기 + 단일 V 사용"이며 이는 결과 본 후 V 선택 방법 변경 = cycle 1 #5/#7 재발. v1이 **pooled V를 W3-02로 deferred**한 것이 구조적 통로로 작동할 수 있다. → WARNING-4 참조.

### Q3. 설계 정당성 (Anchored / 5 folds × 6개월 / Strategy C single-pair)

**Q3.1 — Anchored vs Rolling 선택**:
- v1 L225 "Anchored vs Rolling 선택 논쟁 재부상... v1 Anchored 박제 강제. 변경 = cherry-pick = cycle 3 강제"
- **근거 박제 부재**: Anchored를 선택한 이유 = "암호화폐 regime 변화에 대응하려면 rolling이 낫다"가 학술 통설이다 (Lopez de Prado 2018 "Advances in Financial Machine Learning" Ch.7). Anchored는 "모든 과거 데이터 활용, 점점 최근 데이터 비중 희석"이라 regime 변화에 둔감. 사용자 설계 승인 배경 문맥이 박제 부재.
- **반대 논리**: 5년짜리 데이터에서 fold당 6개월 OOS + 2년 초기 anchor면 rolling과 차이가 미미하다 (마지막 fold train=1461d vs 첫 fold train=730d). 실질 근거는 "단순성 + 데이터 활용" 수준. 충분한 정당화 아님. → WARNING-2에 통합.

**Q3.2 — 5 folds × 6개월 trade-off**:
- 5 folds × 6개월 = 30개월 OOS 커버 (W2-03 in-sample 2021-10 ~ 2026-04 = 54개월 중 마지막 30개월)
- 암호화폐 regime 변화 속도(월~분기 단위) 감안 시 6개월 test는 regime mix 가능성 (예: fold 2 = 2024-04 ~ 2024-10 bull + correction mix)
- 대안: 3개월 test × 10 folds = 50개월 커버, fold당 30일 trade + regime 좀 더 균일. 그러나 N=5에서 N=10으로 늘면 multiple testing 악화
- v1 L213-214 "Fold별 거래 수 low-N" 완화가 "bootstrap 신뢰구간 (W3-02 책무)"으로 deferred. **설계 시점에서 fold 설계 trade-off 표 박제 부재**. → WARNING-2에 통합.

**Q3.3 — Strategy C single-pair cell**:
- W2-03 v8 2차 감사관 NIT-2 (본 감사관 1차 감사): "Strategy C의 ETH 부적격 처리 Week 3 책무 명시 필요"
- v1 L79 CELLS에 `("KRW-BTC", "C")`만 포함, ETH_C 미포함 — NIT-2 준수
- 그러나 **단일 페어 cell이 N=5 sample variance 산출에 포함되어 있음** (BTC_C 1개만 Strategy C 대표). v1 L124 "N_trials = 5" → 5 cell sample variance. Strategy C가 단일 페어이면서 전략 변동성의 대표로 쓰이는 것은 **통계적 의미 불명확** (Strategy 변동성 vs Pair 변동성 혼재). → NIT-2 참조.
- 대안 프레임: "N_trials = 5 cells"가 아니라 "N_trials = 3 strategies × 2 pairs = 6 trial"으로 재정의. 단 W2-03 v8 N=6 기준이 이미 존재하므로 재정의는 일관성 문제 유발. 현행 유지 OK, 단 ETH_C 제외의 통계적 대가 (N=5, Strategy C 단독 cell) 박제 필요.

### Q4. Go 기준 "4+ fold pass AND 평균 pass" 분석

**Q4.1 — 4/5 = 80% stability 요구**:
- "4+ fold" = 5 fold 중 최소 4 fold에서 Sharpe > 0.8 AND DSR_z > 0
- 통계적 관점: 각 fold 독립 시 p=0.5 Bernoulli → 4+ success 확률 = C(5,4)·0.5^5 + C(5,5)·0.5^5 = (5+1)/32 = 18.75% — 즉 무작위 전략이 통과할 확률 ≈ 19%
- 이는 **적당히 엄격**. 통상 "75% stability" 학술 기준(Bailey 2014 Table, Lopez de Prado 2018 Ch.7.4)과 일관
- **단점**: "AND 평균 pass" 추가 → p=0.5 → 평균 Sharpe > 0 확률 ≈ 50%, 결합 ≈ 10% → 전체 false positive rate ≈ 10%
- **실질 문제**: W2-03에서 이미 "5셀 Go" 결과 (cycle 1 #5 재발 의심)가 있는 상황에서, 5 cell 중 **1개만** 4+/5 pass + 평균 pass 조건 충족하면 전체 Go → 실질적으로 "5 cell × 평균 10% FP = 약 40%" family-wise error rate. 너무 느슨할 가능성
- v1 L141 "5 cell 중 적어도 1개 cell" = any-of-5 조건. **단일 cell survivor bias** 우려. → WARNING-5 참조.

**Q4.2 — 평균 Sharpe > 0.8 vs 평균 DSR_z > 0**:
- 평균 DSR_z > 0 = "fold별 DSR_z 평균값 > 0" — fold별 변동 큰 경우 평균이 misleading (예: [+30, +30, +30, +30, -150]이면 평균 -6 FAIL, 실제 80% stability는 만족). 평균 중앙값 대체 또는 fold별 양분 비율 제시 등 고려 필요
- 현재 v1 L141 "평균 pass"가 mean vs median 미박제. → NIT-3 참조.

**Q4.3 — 대안 비교**:
| Go 기준 | False Positive Rate (5 cell 중 1+) | False Negative Rate (진짜 엣지 있을 때) | Comment |
|---|---|---|---|
| 5/5 모두 pass | ~15% | 매우 낮음 | 너무 엄격, Strategy C 단독 cell이 ETH-like pair fail 시 전체 탈락 |
| 4+/5 + 평균 (v1 박제) | ~40% | 중간 | tight bias toward Go |
| 3+/5 + 평균 | ~60% | 낮음 | 너무 느슨 |
| 평균 Sharpe > 0.8만 | ~50% | 낮음 | stability 미검증 |
| 3+/5 AND 평균 DSR_z > 0.5 | ~30% | 중간 | 엄격도 증가 |
- v1 박제 "4+/5 + 평균" 정당화 부재. v1 L227-228 리스크 표 "과도/과소" 양방향 언급만 있음. **학술 근거 또는 W2-03 결과 기반 근거 박제 필요**. → WARNING-5에 통합.

### Q5. 다중 검정

**Q5.1 — 25 trials family-wise 오류**:
- 5 cell × 5 fold = 25 trial
- 각 cell의 DSR_z는 fold별 5 cell의 sample variance 기반 (v1 L124) → cell 내부는 DSR 조정, fold 축은 미조정
- v1 L131 "Fold×cell 25 trial family-wise 오류 여지. DSR로 부분 완화. 최종 검증은 W3-02"
- **정직 인정**. 그러나 v1은 **DSR 조정 범위가 fold내 5 cell만** — fold간 5개 독립 반복 테스트는 miss. 실제 effective trial = 25. Bonferroni 수준 보정 → α=0.05/25 = 0.002 필요. DSR_z > 0의 p-value = 0.5 (z=0 cutoff)를 대신 DSR_z > Φ⁻¹(0.999+0.002) ≈ 2.88로 해야 25 trial 보정. v1이 DSR_z > 0 임계값을 W2-03 v8 박제 유지 중이므로 **multiple testing 완화 부재**. → WARNING-6 참조.

**Q5.2 — W3-02 deferred 정당성**:
- v1 L132 "최종 검증은 W3-02 (bootstrap/DSR 재산정)"
- W3-02에서 bootstrap CI + Monte Carlo로 재검증하면 **W3-01 Go 판정을 retrospectively 번복 가능**한가? v1 박제 부재
- v1 L141 Go 판정은 **W3-02 전에 이미 Go/No-Go 확정** → W3-02가 Go 확정을 번복하는 절차 없음. W3-02는 Go 전략 "선별/ordering"용으로만 쓰이는 구조. 이는 **multiple testing 최종 검증이 아니라 W3-01 이후 잔존 선택 단계**에 불과. → WARNING-6에 통합.

### Q6. Low-N 거래 수 caveat

**Q6.1 — Strategy C의 진입 희소성**:
- W2-03에서 BTC_C 5년 = 5 trade / 54개월 = 연 1.11 trade
- fold당 6개월 → 기대 trade = 0.55 trade. 즉 **fold당 0-1 trade 빈도**
- fold당 0 trade 시 Sharpe 정의 불가능 (returns = 0 → Sharpe = NaN or 0). v1 L99 "fold당 1-2 trade 가능성, low-N caveat 사전 인정"은 underestimate
- fold당 1 trade 시 Sharpe는 단일 trade PnL 기반 noise. Bailey 2014도 T (= returns count) 최소 요구 명시 없음이지만 실질적으로 T < 30이면 Sharpe CI 매우 wide
- v1 L125 DSR 계산 T = daily returns count (180일)이므로 Sharpe 공식 자체는 성립. 단 **실제 경제적 의미는 거의 없음** (180일 중 170일은 cash position, 10일만 in-trade)
- v1 L224 리스크 표 완화 "필요 시 bootstrap으로 신뢰구간 산출 (W3-02 책무)" → 또 deferred. **W3-01 Go 판정이 low-N Sharpe에 의존하면 판정 자체가 noise-driven** 가능성. → WARNING-7 참조.

**Q6.2 — 완화 방안 부재**:
- v1은 "caveat 인정"만, 구체 대책 부재
- 대안: (a) Strategy C 대상에서 fold당 min_trade_count ≥ 2 요구 (미달 시 fold = N/A → 평균/4+ 계산 시 제외), (b) Strategy C 평가를 "BTC full span" 단독 평가로 격리 + Strategy A/D와 다른 기준 적용, (c) Strategy C를 W3-01 대상에서 제외 + Week 3 종료 후 별도 평가
- v1은 (a)(b)(c) 중 어느 것도 박제 X. 현재 상태로는 BTC_C가 fold 1-2 trade만 나와도 "Sharpe > 0.8"이 무작위로 만족될 가능성. → WARNING-7에 통합.

### Q7. Recall mechanism + retrospective 판정

**Q7.1 — Strategy A Recall**:
- candidate-pool.md v5 L27 Strategy A Active (Recall 발동 2026-04-20)
- v1 L213 의존성 매트릭스 "candidate-pool.md v5 → W3-01: Strategy A/C/D 파라미터 + Recall 의무"
- v1 L259 테스트 시나리오 "Edge (Strategy A만 통과): Recall mechanism 유지 + W3-02 DSR-adjusted 재검증"
- W3-01 실패 시 Strategy A "Active → Retained 복귀" 절차 박제 부재 — SubTask W3-01.7 L191 "No-Go 시: +2 소급 + 옵션 제시"만 있고 candidate-pool.md 상태 전이 절차 미박제. → NIT-4 참조.

**Q7.2 — W2-03 retrospective 재판정**:
- v1 L31-33 Week 3 진입 근거에 "Week 3 결과가 W2-03 Go 결정의 retrospective 재판정 역할" 명시 OK
- v1 L33 "Week 3 실패 시 +2 소급 가산" 박제 OK
- 그러나 **retrospective 재판정의 구체적 결과 해석 프레임 부재**: Week 3 No-Go 시 "W2-03 Go = cycle 1 #5 재발 확정"으로 재분류되는지, 아니면 "Week 3만 단독 fail + W2-03 Go 판정은 유지"인지 모호. 본 감사관(W2-03 2차 감사)은 **후자가 위험**하다고 판단 (W2-03 Go 자체가 retrospectively 무의미해짐 = cycle 1 #5 재발 확정). v1에 이 재해석 프레임 사전 박제 권고. → WARNING-8 참조.

### Q8. PT-04 선행 적용 주장

- v1 L83 `YEAR_FREQ = "365 days"` + L86 `pf.sharpe_ratio(year_freq='365 days')` 명시 호출 + L85 "PT-04 선행 적용, cycle 1 #16 재발 방지"
- `docs/stage1-execution-plan.md` L125 PT-04 원문: "W4-01 Freqtrade 이식 진입 시점 일괄 갱신. W1-02/03/04/06 + W2-03 + 미래 Week 3 walk-forward 노트북 모두 `pf.sharpe_ratio(year_freq='365 days')` 명시 호출로 전환"
- **실제 v1이 해결한 범위**: W3-01 신규 노트북(09)에만 명시 호출. **W1-02/03/04/06 + W2-03 기존 노트북 갱신은 미포함**
- v1 L54 week3.md 박제: "PT-04 선행 적용... 기존 노트북 (W1-*, W2-03) 일괄 갱신은 W4-01 Freqtrade 이식 시점 (기존 박제)"
- **판정**: PT-04의 "미래 W3 walk-forward 노트북" 부분만 해결 = **부분 해소**. week3.md L54가 이를 정확히 서술함. 그러나 **v1 sub-plan L85 "PT-04 선행 적용"**은 overclaim 여지 — "PT-04 신규 노트북 범위만 선행 적용"이 정확. 혼동 우려. → NIT-5 참조.

---

## 2. BLOCKING (수정 필수)

**없음.**

W2-03 v8 WARNING-3/-4 박제 준수 완전, fold 분할점 freeze + Go cells 고정, 독립 재계산 산술 정합, Recall/retrospective 기본 프레임 박제. 사용자 설계 승인("추천 ㄱㄱ") 이후 감사 대기 상태 + 승인 전 freeze 시점 명시 추가로 BLOCKING 수준은 아님. 단 WARNING 8건 중 3건은 BLOCKING 직전 수준 (WARNING-4/5/7).

---

## 3. WARNING (강력 권장)

### WARNING-1: Fold 분할점 freeze 시점의 박제 시점 명확화 부재 — cherry-pick 통로

- **위치**: v1 L80 `FOLD_SPLIT_POINTS`, L226 리스크 표
- **문제**: v1 L2 상태 "v1 초안, 외부 감사 대기"이며 fold 분할점은 v1 박제 시점 freeze. 그러나 실제 freeze 시점은 "사용자 승인 시점"이어야 cherry-pick 방어 가능. 현재 v1은 "사용자 승인 이전 감사" 단계 → 감사 결과 반영 후 사용자 최종 승인 시점에 freeze 시점 박제 필요.
- **권고**: v1 L80에 "본 분할점은 사용자 W3-01 sub-plan v1 명시 승인 시점에 freeze. 승인 시점 박제 = [날짜 placeholder → 실제 승인 시 확정]" 명시. 추가로 "감사 과정에서 분할점 수정 제안 시 재freeze + 전체 재감사 cycle" 절차 박제.
- **근거**: W2-03 cycle 1 #5 재발 방지 패턴 — 박제 시점이 결과보다 **앞서야** 한다는 원칙.

### WARNING-2: 설계 trade-off 논증 박제 부재 — Anchored/5 folds/6개월 왜 선택

- **위치**: v1 L52-54 개요, L225 리스크 표 "Anchored vs Rolling 선택 논쟁 재부상"
- **문제**: Anchored vs Rolling 선택 근거, 5 folds vs 다른 N 선택, 6개월 test window 선택 trade-off **학술 근거 박제 부재**. "사용자 설계 추천 채택"만 박제됨 (L3/L9). 외부 감사관 관점에서 "왜 이 설계인가?" 대답 불가능.
- **권고**: v1 "배경" 섹션에 다음 박제 추가:
  - "Anchored 선택 근거: Lopez de Prado 2018 Ch.7 Rolling이 regime 변화에 유리하나, 본 프로젝트는 (i) 5년 데이터 제한으로 rolling 시 첫 fold warmup 부족, (ii) 암호화폐 regime 변화가 월 단위로 너무 빨라 rolling 6개월도 mix regime. Anchored 단순성 + 데이터 활용 극대화 선택"
  - "5 folds 선택 근거: N=5는 W2-03 N=6과 일관 (sample variance 공식 호환 의도) + OOS 6개월×5 = 30개월 확보"
  - "6개월 test 선택 근거: (i) 최소 180 trading days로 Sharpe CI 수렴 (Lo 2002), (ii) 암호화폐 regime 변화 속도 고려 최소 단위"
- **근거**: W2-03 v8 WARNING-3에서 박제된 "v1 승인 시점에 박제, 결과 본 후 완화 X"의 반대편 = 사전 박제된 근거가 충분해야 사후 수정 방지 가능.

### WARNING-3: Go cells 집합 축소 유혹 방지 박제 부재

- **위치**: v1 L229 리스크 표 "CRITICAL: Go cells 집합 확장 유혹"
- **문제**: v1은 **확장 방향** (ETH_C/Secondary 추가)만 방지 박제. **축소 방향** (예: Strategy C 단독 cell BTC_C 제외 + Strategy A/D 4 cell로만 평가)은 방지 박제 부재. Strategy C가 low-N (Q6)으로 fold 평균 실패 시 "Strategy C 제외 + 재산정" 유혹 발생 가능 → cell 집합 ↓ = multiple testing 분모 ↓ = V_empirical 축소 = SR_0 완화 = Go 역행.
- **권고**: v1 L229에 "5 cell 축소 유혹 (Strategy C 제외 등) = cherry-pick = cycle 3 강제" 추가. 양방향 freeze 명시.
- **근거**: cycle 1 #5 사후 완화 통로의 대칭 (Strategy 단독 제외도 사후 기준 변경).

### WARNING-4: pooled V 검토의 W3-02 deferred가 V 선택 재논쟁 통로

- **위치**: v1 L224 리스크 표 "V_empirical per fold 불안정 (N=5, 각 fold 독립 산출) → High → 2차 감사 focus. 단위 unit test + 재현성 검증. **W3-02에서 pooled V 대안 검토**"
- **문제**: W3-01은 V_empirical per fold (fold별 5 cell sample variance) 고정 박제. 그러나 "W3-02에서 pooled V 대안 검토" 박제가 **결과 본 후 V 선택 재협상 통로**로 작동할 위험. W3-01 Go 판정이 V_empirical per fold 기준이며 이 판정은 W3-01 시점 확정되는 구조이지만, W3-02에서 pooled V로 재산정 시 Go/No-Go가 번복될 수 있음 = 실질적으로 W3-01 결과를 W3-02에서 재평가 = cycle 1 #7/#10 재발.
- **권고**: v1 리스크 표 L224 수정:
  - 제거: "W3-02에서 pooled V 대안 검토"
  - 대체: "W3-01은 V_empirical per fold 확정. pooled V는 W3-02 bootstrap CI 계산 시점 참고 metric으로만 산출 (Go/No-Go 재판정 근거로 사용 금지). W3-02가 W3-01 판정을 번복 시 cycle 3 강제"
- **근거**: W2-03 v8 WARNING-3 (Week 3 V 일관성 사전 박제 = cycle 1 #7 재발 방지)의 직접 연장.

### WARNING-5: "4+ fold + 평균" Go 기준 사전 정당성 논증 부재 — BLOCKING 직전

- **위치**: v1 L140-141 SubTask W3-01.4 Go 기준
- **문제**: "4+ fold pass AND 평균 pass" 조합이 왜 "5/5" 또는 "3+ + 평균" 대신 선택되었는지 **학술 근거 또는 W2-03 결과 기반 근거 박제 부재**. 사용자 설계 추천 채택("ㄱㄱ")만으로는 cycle 1 #5 재발 방어 어려움. 외부 감사관이 "왜 4+/5이고 3+/5 아닌가?" 질문에 답 불가능.
- **권고**: v1 SubTask W3-01.4에 다음 근거 박제 추가:
  - "4+/5 (80%) stability 선택 근거: 통상 walk-forward stability 기준은 70-80% (Pardo 2008 'Evaluation and Optimization of Trading Strategies' Ch.9). 5 fold 독립 p=0.5 Bernoulli 가정 시 4+ pass 확률 ≈ 18.75% = 무작위 전략 통과 억제. 3+/5 (60%)는 37.5%로 느슨, 5/5 (100%)는 3.1%로 single fold noise에 취약"
  - "평균 pass 추가 근거: stability + magnitude 이중 AND로 false positive 억제 (5 cell any-of-5 단일 cell survivor bias 부분 완화)"
  - "any-of-5 단일 cell 통과 = 전체 Go 조건의 single cell survivor 리스크: 5 cell 중 1 cell만 4+/5 + 평균 pass 시 Go. 이는 Strategy 선택이 아닌 Go/No-Go 판정이므로 single cell Go도 논리적 충분. 그러나 W3-02 DSR + Bootstrap에서 단일 cell 의존 전략의 robustness 검증 필수 (W3-02 책무 추가)"
- **근거**: cycle 1 #5/#7 재발 방지 = 사전 지정 기준의 정당성 논증이 사전 박제되어야 사후 변경 방지 가능.

### WARNING-6: Multiple testing 완화 부재 + W3-02 deferred 한계

- **위치**: v1 L131-132 SubTask W3-01.3 + 리스크 표
- **문제**: 25 trial (5 cell × 5 fold) family-wise 오류 완화가 "fold별 DSR로 부분 완화. 최종 검증은 W3-02 bootstrap/DSR 재산정"으로 deferred. 그러나 (i) fold별 DSR은 fold 내부 5 cell 조정만, fold 축 25 trial 전체 보정 아님. (ii) W3-02는 W3-01 Go 확정 이후 실행이며 W3-01 판정 번복 절차 부재 → multiple testing 최종 검증이 **판정 뒤에 따라오는 잔존 선택 단계**에 불과.
- **권고**: v1 SubTask W3-01.4에 "Go 판정 임계값 Sharpe > 0.8 AND DSR_z > 0은 cell×fold 25 trial family-wise 미조정 수준. 조정 시 DSR_z > Φ⁻¹(1-0.05/25) ≈ 2.88 필요. 본 박제는 Bailey 2014 DSR이 이미 selection bias 부분 완화임을 근거로 현 임계값 유지 (W2-03 v8 일관) — 단 25 trial full family-wise 방어 X. 최종 robustness 검증은 W3-02 bootstrap CI 하한 > 0.5 요구 (이미 박제)" 명시.
- **근거**: 학술적 정직성 + cycle 1 #5/#7 재발 방지의 extension.

### WARNING-7: Strategy C low-N 거래 caveat 완화 방안 부재 — BLOCKING 직전

- **위치**: v1 L99 SubTask W3-01.1 + L223 리스크 표
- **문제**: W2-03 BTC_C 5 trade / 5년 = fold당 기대 0.55 trade. fold당 0 trade 가능성 실재. fold당 1 trade 시 Sharpe가 단일 trade PnL 기반 noise. v1은 "caveat 인정"만, 구체적 완화 부재. 저-N 상황에서 Sharpe > 0.8을 무작위로 충족 가능성 매우 높음.
- **권고**: v1 SubTask W3-01.1에 다음 박제 추가:
  - "fold별 min_trade_count 룰: 각 fold에서 `# trades < 2` 시 해당 fold는 `fold_pass = N/A` 처리 (4+ fold pass 카운트 분모에서 제외, 평균에서 제외)"
  - "Strategy C 특수 처리: 전체 5 fold 중 N/A fold ≥ 3 시 Strategy C cell은 전체 FAIL (평가 불가, Go 판정 기여 X)"
  - 또는 대안: "Strategy C를 W3-01 대상에서 제외 + Week 3 별도 평가 (BTC full-span 단독)"
- **근거**: 통계적 정직성 + cycle 1 #7 "사전 지정 기준 미정의" 방지.

### WARNING-8: W2-03 retrospective 재판정의 결과 해석 프레임 사전 박제 부재

- **위치**: v1 L31-33 배경, L142 SubTask W3-01.4, L191 SubTask W3-01.7
- **문제**: Week 3 No-Go 시 W2-03 Go 판정의 사후 재분류 방향이 모호. (A) "W2-03 Go = cycle 1 #5 재발 확정, V_empirical 채택 자체가 cherry-pick" 또는 (B) "Week 3만 단독 fail, W2-03 in-sample Go 판정은 유효 + OOS fail은 별개" 중 어느 쪽인지 사전 박제 부재. 결과 본 후 해석 선택 유혹 = cycle 1 #5 재발.
- **권고**: v1 배경 L31-33에 다음 박제 추가:
  - "Week 3 No-Go 시 retrospective 해석 프레임 사전 박제: W2-03 Go 판정은 'in-sample 예비 판단'이며 Week 3 OOS 결과가 최종 판정. W2-03 v8 V_empirical 채택의 cycle 1 #5 재발 여부는 Week 3 결과로 확정 — No-Go 시 W2-03 v8 판단을 'retrospectively cherry-pick 재해석 + Stage 1 킬 카운터 +2 소급' 처리"
  - "Go 시 해석: W2-03 v8 V_empirical 채택이 OOS로 입증됨. retrospective cherry-pick 위험 dismissed"
- **근거**: W2-03 v8 2차 감사 개인 의견 (L299-316) "Week 3가 retrospective 재판정" 박제의 직접 연장.

---

## 4. NIT (개선 제안)

### NIT-1: Strategy C 구현 박제 표현 정확화

- v1 L49 "Strategy A/C/D W2-02 v5 박제값 그대로 사용 (재튜닝 금지)" → "W2-02 v5 파라미터 + W2-03.1 방법 B 구현 (manual trailing_high - ATR_MULT × ATR(t) exit_mask) 박제"로 수정 권고. candidate-pool.md v4 L37/L39 + v1 L109 일관.

### NIT-2: Strategy C 단독 페어 cell의 N=5 sample variance 통계 의미 박제

- v1 L124 "N_trials = 5 (W2-03 Go cells 집합)"에 "단 N=5 중 Strategy C는 BTC_C 단독 cell이며 Strategy 변동성과 Pair 변동성이 혼재된 sample variance임을 인정. Strategy 순수 변동성은 Week 3 이후 multiple strategy backtest에서 별도 검증 필요" 주석 추가.

### NIT-3: 평균 Sharpe/DSR_z의 mean vs median 명시

- v1 L141 "평균 Sharpe > 0.8 AND 평균 DSR_z > 0" → "`np.mean` 평균 (mean) 사용 박제. median 대체 금지 (fold 변동성이 높을 경우 평균값이 misleading할 수 있으나, stability 조건 4+/5가 별도 담당)" 명시.

### NIT-4: Recall mechanism 역방향 (W3-01 No-Go 시 Active → Retained 복귀) 박제

- v1 L191 SubTask W3-01.7 + candidate-pool.md v5 L27 Strategy A Active 상태
- 권고: v1 L191에 "No-Go 시 Strategy A Active → Retained 복귀 + candidate-pool.md v6 전이 박제 + Recall mechanism 자동 해제" 추가.

### NIT-5: PT-04 선행 적용 범위 명확화

- v1 L85 "PT-04 선행 적용" → "PT-04 신규 노트북 범위만 선행 적용. 기존 W1-02/03/04/06 + W2-03 노트북 갱신은 W4-01 Freqtrade 이식 시점 (stage1-execution-plan.md L125 기존 박제)" 명시.

### NIT-6: Evidence 6단 구조 항목 명확화

- v1 L160-166 Evidence 6단 구조에 "5. 룰 준수" 항목에 "V_empirical 일관 + floor 재도입 X + 임계값 변경 X + W2-03 Go cells 고정 X" 박제 중 **마지막 항목 "Go cells 고정 X"는 오타 (의도 "고정 O")**. → "Go cells 집합 확장 X + 축소 X (양방향 freeze)"로 수정.

### NIT-7: Week 3 실패 시 Stage 1 킬 카운터 +2의 "+2" 근거

- v1 L142 "+2 소급 가산"의 근거가 W2-03 v8 WARNING-4 박제 (decisions-final.md L669) 인용. v1이 인용만 있고 왜 "+2"인지 (W2-03 Go + Week 3 No-Go 이중 실패로 +1 + +1 = +2) 설명 부재. 가벼운 주석 추가 권고.

---

## 5. 독립 재계산 결과

### 5.1 Fold 분할점 bar count 독립 검증

```
입력:
  train_start = 2021-10-15
  split_points = [2023-10-15, 2024-04-15, 2024-10-15, 2025-04-15, 2025-10-15]
  freeze_end = 2026-04-12

Fold 1: train 2021-10-15 ~ 2023-10-15 (730d) / test 2023-10-15 ~ 2024-04-15 (183d)
Fold 2: train 2021-10-15 ~ 2024-04-15 (913d) / test 2024-04-15 ~ 2024-10-15 (183d)
Fold 3: train 2021-10-15 ~ 2024-10-15 (1096d) / test 2024-10-15 ~ 2025-04-15 (182d)
Fold 4: train 2021-10-15 ~ 2025-04-15 (1278d) / test 2025-04-15 ~ 2025-10-15 (183d)
Fold 5: train 2021-10-15 ~ 2025-10-15 (1461d) / test 2025-10-15 ~ 2026-04-12 (179d)
```

**v1 L94-96 박제값 대조**:
- v1 L95 "Fold 1 test ≈ 180d" → 실제 183d (오차 +3d). v1 "≈180 ±5%" 허용 범위 (171-189d) 내 OK.
- Fold 5 test = 179d (freeze 종료일 2026-04-12 기준). ±5% 범위 내 OK.
- 전체 fold test 기간: 평균 182.0d, 표준편차 1.58d (매우 균일).
- 일봉 + 암호화폐(24/7 연속) + weekend 없음 가정 하에 각 fold test ≈ 180 ±3d로 **연속 일봉 기준 정합**.

### 5.2 N=5 Bailey 2014 SR_0 계수 독립 재계산

```
γ (Euler-Mascheroni) = 0.5772156649015329
e = 2.718281828...
N = 5

Φ⁻¹(1 - 1/5) = Φ⁻¹(0.8) = 0.841621 (Acklam inverse normal)
Φ⁻¹(1 - 1/(5e)) = Φ⁻¹(0.926424) = 1.449666

coef_N5 = (1-γ)·Φ⁻¹(1-1/5) + γ·Φ⁻¹(1-1/(5e))
        = 0.4227843·0.841621 + 0.5772157·1.449666
        = 0.3558 + 0.8367
        = 1.1926
```

**N=6 비교 (W2-03 v8 박제 SR_0=0.4159 ÷ sqrt(0.1023) = 1.3001)**:
- coef_N5 / coef_N6 = 1.1926 / 1.3001 = 0.9173
- **N=5 → N=6 이동 시 SR_0 8.27% 완화 효과**
- W2-03 V_empirical=0.1023 동일 가정 → N=5 SR_0 = 0.3815 (N=6 0.4159 대비 -0.0344)

### 5.3 Synthetic V per fold 시뮬레이션

N=5 fold별 sample variance 불안정성 체크:

| Scenario | fold별 5 cell Sharpe | V | SR_0 (N=5) | 해석 |
|---|---|---|---|---|
| A: uniform | [1.0, 1.0, 1.0, 1.0, 1.0] | 0.0000 | 0.0000 | 극단 → SR_0=0, 모든 Sharpe > 0이면 Go |
| B: low var | [1.0, 0.8, 1.2, 0.9, 1.1] | 0.0250 | 0.1886 | 합리적, W2-03 N=6 V=0.1023 대비 1/4 수준 |
| C: high var | [1.0, 0.3, 1.5, 0.5, 1.3] | 0.2620 | 0.6104 | ETH_C 같은 outlier 1개로 V 2배 |

**관찰**: N=5 per fold는 outlier 단 1개로 V가 2배 변동. Scenario C에서 Sharpe=1.0인 cell도 SR_0=0.6104를 넘지 못해 FAIL. 즉 fold별 V_empirical가 **특정 fold의 outlier에 의해 해당 fold 전체가 conservative 해지거나 (high V), 반대로 low V fold가 과도하게 관대**. 이는 WARNING-4에서 지적한 V 불안정성의 구체적 산술 증거.

### 5.4 판정

- Fold 분할점 bar count 산술 **정합**
- Bailey 2014 N=5 SR_0 계수 독립 재계산 **OK** (1.1926)
- N=5 sample variance 불안정성 시뮬레이션 결과 → **WARNING-4/5 근거 보강**
- v1 박제값 전체 **산술 재현 완전**

---

## 6. 최종 verdict

### **CHANGES REQUIRED (WARNING-4/5/7 반영 필요)**

- **BLOCKING 0건**: W2-03 v8 WARNING-3/-4 박제 완전 준수, fold bar count 정합, Bailey 2014 수식 재현 OK, Recall/retrospective 기본 프레임 박제.
- **WARNING 8건**: (1) fold freeze 시점 명확화 (승인 시점 박제), (2) 설계 trade-off 논증 부재 (Anchored/5 folds/6개월), (3) Go cells 집합 **축소 유혹** 방지 부재, (4) **pooled V W3-02 deferred가 V 재논쟁 통로** — BLOCKING 직전, (5) **"4+/5 + 평균" Go 기준 사전 정당성 부재** — BLOCKING 직전, (6) multiple testing 25 trial 완화 부재, (7) **Strategy C low-N 완화 방안 부재** — BLOCKING 직전, (8) retrospective 재판정 해석 프레임 사전 박제 부재.
- **NIT 7건**: Strategy C 구현 표현, N=5 통계 의미, mean vs median, Recall 역방향 전이, PT-04 범위, 6단 오타, +2 근거.

### 진행 권고

1. **WARNING-4, -5, -7는 사용자 최종 승인 전 v1 → v2 수정 필수**. 이 3건은 "사전 지정 기준 미정의" (cycle 1 #7) 재발 방지 직접 관련.
2. WARNING-1, -2, -3, -6, -8은 v2에 박제 추가로 반영 가능. 학술 근거 + cherry-pick 양방향 freeze + retrospective 프레임.
3. NIT 7건은 v2 작성 시 일괄 반영.
4. v2 수정 후 사용자 최종 승인 시점에 fold 분할점 + Go cells 집합 + Go 기준 **3개 요소 동시 freeze** (박제 시점 박제).
5. v2 박제 후 커밋 전 본 감사관 재검증 권고 (외부 감사 2차 cycle).

### 핵심 메시지

- v1은 **W2-03 v8 WARNING-3/-4 박제를 기계적으로 정확히 복제**한 성실한 초안이다. 산술 정합성 bit-level 완전.
- 그러나 **cycle 1 #7 "사전 지정 기준 미정의"** 재발 위험이 3건 (WARNING-4/5/7). 특히 "4+/5 + 평균" Go 기준의 정당성 논증이 "사용자 추천 승인"만으로 끝나 있는 것은 **외부 감사관 관점에서 방어 불가능**.
- pooled V W3-02 deferred (WARNING-4)는 **실질적으로 V 재논쟁 통로를 W3-02에서 열어두는 것**과 같다. W3-01 V_empirical per fold 박제를 W3-02가 번복하지 못하도록 사전 차단해야 W2-03 v8 WARNING-3의 의도가 보존된다.
- Strategy C low-N (WARNING-7)은 **fold당 0-1 trade 시 Sharpe > 0.8 무작위 충족 가능성** = 통계적 noise-driven Go 판정 위험. 최소 trade count 룰 박제 필수.
- retrospective 재판정 프레임 (WARNING-8)은 Week 3 결과 확정 후 해석 선택 유혹 방어. 결과 본 후 "W2-03 Go 유효 vs 재분류" 선택권이 남아 있으면 cycle 1 #5 재발.
- W2-03 v8 2차 감사관(본 감사관 1차 감사)의 **"cycle 1 #5와 본질적 구분 어려움" 인정**이 Week 3 sub-plan 설계 정밀도를 평소 이상으로 요구한다 — WARNING 8건 반영이 그 수준을 맞추는 최소 기준.

---

## 7. 감사관 개인 의견 (bias 명시)

- **나의 bias**: 본 감사관은 W2-03 v8 2차 감사(`.evidence/agent-reviews/w2-03-v8-v-empirical-adoption-review-2026-04-20.md`)를 수행한 동일 페르소나이며, 거기서 WARNING-3 (Week 3 V 일관성 사전 박제 부재 = BLOCKING 직전)을 제기했다. v1이 WARNING-3/-4를 충실히 박제한 것을 보고 **"내 감사 결과가 성공적으로 반영됐다"는 긍정 편향 위험**이 있다. 본 1차 W3-01 감사에서 의식적으로 "v1이 새로운 cycle 1 #7 재발을 만들고 있는가?"를 적대적으로 검토했다.
- **솔직한 판단**: v1 박제는 **형식적으로는 W2-03 v8 WARNING 완전 반영**이지만, 실질적으로는:
  - (i) "4+/5 + 평균" Go 기준이 **사용자 추천 = '추천 ㄱㄱ'**만으로 박제 → 이는 "사용자 재량"을 "사전 박제"로 포장하는 외관. 학술 근거 논증이 없으면 cycle 1 #5 재발 방지 불가능.
  - (ii) pooled V W3-02 deferred는 **W2-03 v8 WARNING-3 "Week 3 V 일관성 사전 박제"의 정확한 우회 통로**. Week 3 "안"에서 V를 바꾸지 말라 했는데 Week 3 "종료 후" W3-02에서 V 해석 재협상은 열어둠 = 실질적으로 같은 위반.
  - (iii) Strategy C low-N은 **통계 노이즈로 Go를 얻을 수 있는 구조적 취약점**. v1이 이를 caveat만 인정 + 완화 부재 = 결과 본 후 "Strategy C low-N이라 제외" 또는 "Strategy C low-N인데 Sharpe 1.5 나왔으니 Go 인정" 둘 다 선택 가능한 구조.
- **그럼에도 BLOCKING 아닌 이유**: (a) v1이 감사 대기 단계이며 사용자 최종 승인 전, (b) WARNING 반영으로 v2 수정 가능, (c) 산술 정합성 + 기본 프레임 완전. **CHANGES REQUIRED는 "v1 자체는 수정 후 승인 가능" 수준의 중간 판정**이다.
- **Week 3 실행 이후 재평가 예고**: 본 v1이 v2로 수정되어 WARNING 8건 반영된 상태여도, **Week 3 실제 실행 결과가 Go면 retrospective로 "v1 설계가 최적"으로 재해석될 수 있고, No-Go면 "v1 설계가 불충분"으로 재해석될 수 있다**. 이는 cycle 1 #5의 메타적 재발이며, 본 감사관은 **결과에 무관한 정당성 근거를 v2에 박제해야만** 이 메타 순환에서 벗어날 수 있다고 본다.
- **메타 관찰**: W2-03 v8 감사에서 "감사 사이클 자체의 효과성이 시험대에 오른다"고 적었다. W3-01 v1 감사 결과는 **감사 사이클이 WARNING-3/-4를 Week 3 sub-plan에 정확히 전파**했지만 **새로운 위험 (pooled V deferred, Go 기준 정당성, low-N fallback 부재)**을 만들어냈음을 확인시켰다. 감사가 이전 cycle 학습은 반영하되 **새 cycle에 맞는 새로운 위험은 독자적으로 탐지**해야 한다. 본 감사관은 이 작업을 수행했고 WARNING 8건으로 보고한다. 다만 "감사에 만족하면 다음 감사의 필요성이 줄어든다"는 감사 피로 위험을 경계해야 한다.
- **사용자에게 직언**: "추천 ㄱㄱ" 승인 발화 방식은 **판단 책임을 감사 프로세스에 전가**할 수 있다. W3-01은 Stage 1 킬 게이트 직접 입력이며 Week 3 결과에 따라 ±2 카운터가 움직이는 중대 결정이다. v2 수정 후 Go 기준 "4+/5 + 평균"의 정당성 근거를 사용자가 **직접 검토하고 대안 (3+/5, 5/5, median 기반 등) 중 명시 선택**하는 절차가 cycle 1 #7 방어의 핵심이다. 현재 v1은 이 단계가 건너뛰어져 있다.

---

**감사관 서명**: Claude (외부 감사관 페르소나, opus-4-7[1m])
**일시**: 2026-04-21 UTC
**Trace**: `.evidence/agent-reviews/w3-01-walk-forward-review-2026-04-21.md` (본 파일)
**결정**: CHANGES REQUIRED → WARNING-4/-5/-7 반영 v2 수정 필수, 나머지 WARNING + NIT는 v2 박제 추가. v2 수정 후 사용자 최종 승인 시점에 fold 분할점 + Go cells + Go 기준 3요소 동시 freeze + 재감사 권고.

End of trace.
