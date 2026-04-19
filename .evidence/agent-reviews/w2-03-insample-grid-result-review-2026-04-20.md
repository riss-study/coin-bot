# W2-03.7 외부 감사 (적대적 감사관 페르소나) — 2026-04-20

- **검증 대상 (신규)**:
  - `research/outputs/week2_report.md`
  - `.evidence/w2-03-insample-grid-2026-04-20.md`
  - `research/outputs/w2_03_primary_grid.json`
  - `research/outputs/w2_03_exploratory_grid.json`
  - `research/outputs/w2_03_dsr.json`
  - `research/outputs/w2_03_dsr_unit_test.json`
  - `research/notebooks/08_insample_grid.ipynb`
  - `research/_tools/make_notebook_08.py`
- **교차 참조**: `docs/stage1-subplans/w2-03-insample-grid.md` v6, `docs/decisions-final.md` L482/L513-521, `docs/candidate-pool.md`, `.evidence/agent-reviews/w2-03-insample-grid-review-2026-04-20.md` (backtest-reviewer), `.evidence/agent-reviews/w2-03-insample-grid-review-2026-04-19.md` (sub-plan v1 1차 감사).
- **페르소나**: 적대적 외부 감사관 (ChatGPT가 작성했다고 가정, 자기-확증 편향/사실 오류/cherry-pick 통로 집중 검증).
- **감사관 태도 요약**: 결과 수치 자체는 독립 재계산으로 완벽히 일치하며, 공식/룰 준수 수준 역시 sub-plan v6 사이클에서 이미 꽤 tight 하게 정리됐다. 감사관으로서 **BLOCKING은 찾지 못했다**. 다만 "변경 금지 서약"이라는 강한 프레이밍이 **"V_reported=1.0 선택은 논의 대상이 아니다"**는 인상을 역-cherry-pick 방향으로 고정시키는 효과를 가지므로, 그 부분만큼은 WARNING 선에서 짚어 둔다. 그 외 NIT는 감사 추적성 개선 수준.

---

## 1. 적대적 감사 7개 focus 질문에 대한 직답

### Q1. Bailey & López de Prado 2014 DSR 공식 정확성

- **SR_0 공식**: sub-plan v6 + 노트북 cell 12 `compute_sr_0()` 구현 모두 Bailey 2014 eq. 9 원문대로:
  `SR_0 = sqrt(V[SR_n]) × ((1-γ)·Φ⁻¹(1-1/N) + γ·Φ⁻¹(1-1/(N·e)))`.
  `γ = 0.5772156649015329` (Euler-Mascheroni), Φ⁻¹은 `scipy.stats.norm.ppf`. 1차 감사 B-1 (v1 `sqrt(2 ln N)` 거친 근사) 완전 제거 확인. **정확**.
- **DSR_z form**: 노트북 cell 12 `compute_dsr()` = `(SR_hat - SR_0) × sqrt((T-1)/(1 - γ_3·SR_0 + ((γ_4-1)/4)·SR_0²))`. Bailey 2014 eq. 10의 z-score form. 분모 안의 SR 변수는 모두 **SR_0** (v1 B-2 분자/분모 모호 정정 완료). 정확.
- **γ_4 kurtosis 정의 일관성**:
  - 노트북 `compute_dsr()` 내부에서 `gamma_4 = scs.kurtosis(returns, fisher=True) + 3` 으로 Fisher→raw 변환. Bailey 2014 공식은 raw kurtosis (정규분포=3) 전제라서 이 변환이 **정확**.
  - 그러나 JSON 출력 필드명 `returns_kurtosis`와 evidence §3.3 표 `γ_4 (kurtosis Fisher)` 는 모두 **Fisher form 값**을 박제. 독자가 표 값 그대로 Bailey 공식에 대입하면 잘못 계산하게 된다 (공식의 γ_4는 Fisher+3). backtest-reviewer NIT-2로 이미 지적. → **로직은 정확, 문서 표기만 혼동 소지 (NIT 수준)**.
- **V_reported = max(V_empirical, 1.0) = 1.0**: Bailey 2014 원문에서 V[SR_n]은 "실제 trial SR 샘플 분산"으로 정의되어 있다. **conservative floor 1.0 적용은 Bailey 원문 절차 자체는 아니며**, sub-plan이 self-justified "N=6 협소성 방어"로 박제한 도입 조항이다 (v6 C-1). 즉 **"Bailey 공식의 입력값 V를 프로젝트 선택으로 크게 잡은 것"** — 이는 식 자체에 위배되지 않으나 "Bailey 원문의 conservative 취지"라는 표현은 약간의 포장이다. 원문에 명시된 건 "N이 매우 작으면 V 추정이 부정확" 정도이고, "floor = 1.0"은 프로젝트 방어적 선택. **사실 오류는 없지만**, "Bailey 2014 권고"가 아니라 "프로젝트 self-imposed conservative floor" 라고 쓰는 게 더 정확하다. → WARNING-1 참조.
- **N_trials = 6 (Tier 2 제외)**: Tier 2 12셀이 "Go 결정에 전혀 영향을 주지 않는다"는 사전 박제가 있으므로 multiple-testing 분모에서 제외한 것은 내적 일관. 단, **selection bias 관점에서 엄밀히 보면** 연구자가 Tier 2 성적도 본 뒤 Secondary 마킹(ensemble 후보)에 그 결과를 사용하므로, "전혀 기여하지 않는다"는 것은 절대적이지 않다 (soft selection leak). Bailey 2014 수식 해석은 프로젝트 박제대로 해도 허용 범위지만, 이 가정의 한계는 리포트 §8.1에 **명시적으로** 박제되면 더 tight. 현재 리포트 §8.1은 "ensemble 후보 마킹도 selection bias 기여"를 **Stage 2 게이트 시 재산정** 책무로만 다루고, 현재 N_trials=6 선택이 이로 인해 약간 낙관적일 수 있다는 warning은 약함. → NIT-1 참조.

### Q2. Cherry-pick 통로 탐지 (종합)

- **max-span vs common-window 중 max-span 선택**: cycle 2 v5 문서(`pair-selection-criteria-week2-cycle2.md`)에서 **사전 박제** 완료. sub-plan v2 W-4 정정에서도 "Go 기준 평가는 max-span 단독, 사후 common-window 변경 = cherry-pick" 명시. 결과 JSON도 max-span/common-window 동시 저장 + 비대칭 투명 보고 (BTC_D, ETH_D가 common-window에서 Sharpe 손실). **결과 본 후 조정 흔적 없음**. 정상.
- **V_reported=1.0 사전 박제 여부**: sub-plan v6 C-1 박제 시점이 `2026-04-20` 이고, 본 grid 실행도 `2026-04-20` 이다. `w2_03_dsr.json` `generated_at = 2026-04-19T16:27:56Z` vs sub-plan v6 박제일 2026-04-20. **시간 선후가 미묘**. KST 기준으로 보면 노트북 실행이 04-20 새벽 01:27 KST, sub-plan v6 박제가 04-20 낮으로 추정되어 UTC 환산 시 **sub-plan v6 C-1 박제 직전에 실행된 결과를 본 이후 v6 C-1 조항이 박제됐을 가능성이 존재**한다. 이 점은 cherry-pick 경계에서 가장 위험한 부분이다. → WARNING-2 참조. 다만 sub-plan v5 시점에도 이미 "V_normalized=1.0 보수적 옵션이 산출"은 박제되어 있었고, v6에서는 "Go 판정에 V_reported 사용" 조항이 명시화됐을 뿐이다. **"Go 기준을 사후에 엄격화한 결과 Go 셀이 0으로 감소"는 아니다** (Empirical/Reported 모두 산출 후 Reported 채택이 v5에서도 잠재적). 그러나 C-1 조항 서술이 "이미 v5에서 묵시적 박제"였는지 "v6에서 결과를 보고 명시화"였는지 감사 trace로는 완벽히 분리 불가. **감사관의 정직한 판단**: 의도적 cherry-pick은 아니지만, **박제 trail이 시간순 명쾌하지 않다**.
- **"Go 통과 셀 0개" = 안전 장치 vs 자의적 차단**: 자의적은 아니다 (Bailey 2014 원문 V floor 적용). 다만 **overkill 가능성**은 부정 못한다 — 6셀 sample variance 0.1023 (annualized SR가 0.32~1.18 범위로 꽤 좁음)에 대해 V_floor=1.0은 **약 10배 부풀리기** 효과, SR_0을 0.416 → 1.300으로 3배 끌어올리는 효과다. "보수적"이 아니라 "극보수적"에 가깝다. 리포트 §5.1은 이 magnitude를 투명 보고하지만, "극보수적"이라는 label은 안 붙이고 "conservative"로만 표기. → WARNING-1에 포함.
- **역-cherry-pick 가능성 (V_reported로 옮겨서 Go 셀 강제 제거)**: 감사관 시각에서 "V_empirical=0.1023 → 5셀 Go 통과" 시나리오가 reporting 투명하게 병기되어 있다는 점은 **cherry-pick 역방향** 혐의를 부분 희석한다. 그러나 리포트 §10 Option C 서술 "본 리포트는 이 옵션을 권장하지 않음" + "cycle 3 강제" 경고는 **수사적 강도가 높아서** 사용자의 중립 판단을 제약하는 효과가 있다. → WARNING-3 참조.

### Q3. Strategy A/C/D 대칭성 + Recall

- Strategy A: BTC_A Sharpe 1.0353 > 0.8, ETH_A 1.1445 > 0.8 — Sharpe 관문은 통과, DSR_z는 -3.43/-2.47로 미달. candidate-pool.md L27 "Tier 1 중 하나 이상 `Sharpe > 0.8 AND DSR > 0`"이 **AND 결합**이므로 Recall 발동 조건 미충족은 **기계적 적용 정확**. 사후 해석 아님.
- Strategy C/D 우대 없음: 동일 Go 기준 AND 결합 적용, 박제 대칭성 준수.
- 저 trade 수 경고: BTC_C 5 trade, ETH_C 5 trade. 리포트 §3.2/§8.4 low-N caveat 박제. Sharpe 신뢰 구간은 **제시되지 않음** (block bootstrap or CI). decisions-final L521 "Week 3 walk-forward 최종 검증"으로 deferred. → NIT-2 참조.

### Q4. 다중 검정 정직성

- 6 primary 셀 family-wise 오류 여지 인정 (§8.1). "Stage 2 게이트 시 N_trials 재산정 의무" 박제.
- "최종 검증은 Week 3 walk-forward" 문구 (§5.2, §8.6, §6.1)는 빈번. 감사관 관점에서 **이 문구가 과도한 안도감을 유발할 위험**이 있다. 엄밀히 Week 3 walk-forward도 **in-sample expansion (anchored walk-forward 여부에 따라)**에 가깝고, 진정한 out-of-sample은 Week 6+ 페이퍼 트레이딩부터다. 리포트 §8.6 "In-sample 예비 검증 성격" 한 줄만으로 이 구분이 충분하지 않다. "Week 3도 여전히 in-sample family (과거 데이터 기반)이며 진정한 OOS는 paper trading"을 더 명시하면 tight. → NIT-3 참조.

### Q5. 사용자 옵션 제시 중립성

- Option A/B/C/D 4개 옵션 제시. 리포트 §10 각 옵션 장단점 병기, 수치 근거 있음. 중립성 절반은 유지.
- **편향 소지 (가중)**:
  1. §11 "권장 (리포트 작성자): Option A (사전 지정 No-Go 수용)" — 작성자 권고 명시로 사용자 결정을 Option A 쪽으로 편향시킨다. 박제 룰 엄격 준수 관점에서 정합이긴 하나, **"박제 = A가 옳다"** 프레임은 사용자가 V_empirical 관점의 상식적 의문(5셀이 Sharpe > SR_0 인데 왜 No-Go인가?)을 제기하기 어렵게 만든다.
  2. Option C "본 리포트는 이 옵션을 권장하지 않음" + "cycle 3 강제 (cherry-pick 감시 트리거)" 문구는 **부당하게 억압적**이다. 사용자가 "V 선택 방법론은 프로젝트 self-imposed floor이고 Bailey 원문은 V=sample variance 사용이 원칙"이라는 Q1 관찰을 근거로 V_empirical 채택을 정당화할 여지가 있음에도, 리포트 수사는 그 여지를 "cycle 3 = 감사 +1" 페널티로 차단한다.
  3. Option B (Stage 1 조기 종료)는 충분한 근거가 있는가? — 본 grid 한 번의 결과만으로 "2개월 매몰 + 라이브 포기 + 학습 모드" 옵션을 제시하는 것은 **과도한 스케일링**. Stage 1 킬 카운터 규정(decisions-final L520 "미달 → +1, Week 3 재탐색")은 "Week 3 재탐색"을 default로 가정하며, "조기 종료" 옵션은 별도 절차가 정의된 바 없다. 리포트가 Option B를 제시한 것은 사용자 선택지를 넓히려는 선의로 보이지만, **근거 없이 제시됨**. → WARNING-4 참조.
- → WARNING-3 / WARNING-4 에 통합.

### Q6. 박제 룰 위반 탐지

- **미승인 결정 사실화 여부**:
  - §9 "W2-03 사용자 결정에 따라: No-Go 시 +1 → 총 +2" — "사용자 결정에 따라"로 조건부로 서술됐으며, 카운터 업데이트가 **실제로 commit되지 않음** (sub-plan `current status` 표 "W2-03.6 Pending"). 정확.
  - sub-plan v6 §Current Progress 표 "W2-03.5 결과 생성 (2026-04-20, v6 자동 실행)" → 자동 `is_go=False` 결과 생성됨은 사실. 사용자 결정 전에 이를 박제한 것은 **결과 자체가 팩트이므로 허용 범위**.
- **변경 금지 서약 위반 여부**: W2-02 v5 사용자 승인 (2026-04-19)로 발효된 파라미터 (Strategy A/C/D + portfolio) 변경은 확인되지 않음. STRATEGY_*_PARAMS 상수 박제값은 candidate-pool 일치. 정상.
- **synthetic data 한계 인정**: 리포트 §8.5에서 "W-1 방법 A vs B 차이 검증은 synthetic … 실제 BTC/ETH에서 magnitude 다를 수 있음 → 방법 B 채택 결과의 실제 데이터 동작은 본 grid 결과가 경험적 증거"라는 주장. 감사관 관점에서 **이 자기 검증은 약하다** — 실제 데이터 기반 방법 A vs B 직접 비교는 수행되지 않았고, grid는 방법 B 단일 트랙. "경험적 증거"라는 표현은 과하다. → NIT-4 참조.

### Q7. 숫자 정합성 재계산 (독립)

독립 재계산 (scipy.stats + math), SR_0 + 6셀 DSR_z 전량:

```
SR_0 (V=1.0)    = 1.3001407878455840  (JSON: 1.3001407878455840)  OK
phi_inv(1-1/N)  = 0.9674215661017012  (JSON 일치)                   OK
phi_inv(1-1/Ne) = 1.5438425504501445  (JSON 일치)                   OK

BTC_A: z=-3.4317668413  JSON=-3.4317668413  diff=0.00e+00  denom=11.4716
BTC_C: z=-3.9455910951  JSON=-3.9455910951  diff=0.00e+00  denom=16.2260
BTC_D: z=-1.6408893527  JSON=-1.6408893527  diff=0.00e+00  denom=10.0126
ETH_A: z=-2.4686106788  JSON=-2.4686106788  diff=0.00e+00  denom=7.6589
ETH_C: z=-10.2263186548 JSON=-10.2263186548 diff=0.00e+00  denom=17.5610
ETH_D: z=-2.5133046502  JSON=-2.5133046502  diff=0.00e+00  denom=13.1024

SR_0 (V_emp=0.1023)     = 0.415904  (JSON: 0.4159035852)  OK

V_empirical 시나리오 (만약 V=0.1023 채택):
  BTC_A: SR=1.0353 > 0.4159? PASS, DSR_z=+23.22
  BTC_C: SR=0.9380 > 0.4159? PASS, DSR_z=+18.12
  BTC_D: SR=1.1818 > 0.4159? PASS, DSR_z=+27.27
  ETH_A: SR=1.1445 > 0.4159? PASS, DSR_z=+29.37
  ETH_C: SR=0.3237 > 0.4159? FAIL, DSR_z= -2.77
  ETH_D: SR=1.0928 > 0.4159? PASS, DSR_z=+22.71
```

**결과**: 6셀 전량 bit-level 수치 일치. **SR_0, γ_3, γ_4(Fisher+3), T, 수치 chain 전부 무결**. V_empirical 시나리오 5셀 통과 주장도 독립 재현 확인.

---

## 2. BLOCKING (수정 필수 또는 사용자 재결정 필수)

**없음.**

수치 정합성, 공식 구현, 박제 룰 준수, cross-document 정합성 모두 문제 없음. 1~3차 sub-plan 감사 사이클에서 이미 대부분 정리됨.

---

## 3. WARNING (강력 권장 정정)

### WARNING-1: "V_reported = max(V_empirical, 1.0)" 의 Bailey 2014 원문 준거 서술이 부정확 (v_reported = "프로젝트 self-imposed conservative floor"가 더 정확)

- **위치**: `week2_report.md` §5.1, `.evidence/w2-03-insample-grid-2026-04-20.md` §3.3, sub-plan v6 C-1 박제.
- **문제**:
  - 리포트 수사: "V_reported = 1.0 (conservative, C-1 v6 박제)" + "Bailey 2014 conservative 취지".
  - Bailey 2014 원문에 "V floor 1.0"은 없다. 원문은 V[SR_n] = "trial들의 SR 표본분산"으로 정의하고, N이 작을 때 추정 불확실성을 인정하지만 구체적 floor 값은 제시 안 한다. "V=1.0 floor"는 프로젝트 자체의 방어적 선택이다.
  - V_empirical=0.1023 → V_reported=1.0 으로의 승격은 약 10배 입력 부풀림이며, SR_0을 0.416 → 1.300으로 **3배 이상 끌어올린다**. 이는 "conservative" 수준이 아니라 "극보수적" 수준에 가깝다 (SR 관문이 약 3배 엄격해짐).
- **권고**:
  1. 리포트 §5.1 SR_0 섹션 + evidence §3.3 DSR 섹션에 "V_reported=1.0은 **프로젝트 self-imposed conservative floor** (Bailey 2014 원문 절차 아님, N=6 협소성에 대한 방어 목적)"라는 명시적 각주 추가.
  2. "conservative" 수식을 수량화: "V_empirical 대비 약 10배 부풀림, 이로 인해 SR_0이 약 3배 엄격화" 박제.
  3. (선택) "V_reported 선택은 감사 trace 상 프로젝트 판단임을 명확히 하여 사용자가 Option C 평가 시 Bailey 원문 절차 vs 프로젝트 선택을 구분해서 판단할 수 있도록" 함.
- **근거**: 외부 감사관으로서 본 리포트를 읽는 독자가 "Bailey 2014가 이 floor를 권고한 것처럼" 해석할 소지. 실제로는 프로젝트가 자기 방어 목적으로 설정한 값이다.

### WARNING-2: sub-plan v6 C-1 박제 시점과 grid 실행 시점의 시간 선후 trace 불완전

- **위치**: `w2_03_dsr.json` `generated_at = 2026-04-19T16:27:56+00:00` vs sub-plan v6 변경 이력 `2026-04-20`.
- **문제**:
  - sub-plan v5 박제 시점(2026-04-19 완료)에도 V_empirical/V_normalized 이원 산출은 박제되어 있었음.
  - 그러나 "Go 판정에 V_reported=max(V_empirical,1.0) 사용"의 **명시적 박제 조항**은 v6 (2026-04-20)에서 C-1 정정으로 추가.
  - 노트북 실행은 UTC 2026-04-19 16:27 (KST 2026-04-20 01:27). v6 변경 이력의 날짜 표기만 봐서는 "노트북이 v6 박제 조항보다 먼저 실행됐는지" 추적하기 어렵다.
  - 만약 실제 순서가 "grid 실행 → 결과 확인 → sub-plan v6 C-1 조항 추가 → grid 결과 재해석"이었다면, C-1은 **사후 박제**로 볼 여지.
- **권고**:
  1. sub-plan v6 변경 이력 행에 **시간 + 트리거 순서**를 분·시 단위로 박제:
     예: "2026-04-20 00:00-01:00 KST v6 C-1 초안 작성 (감사 재검증) → 01:20 sub-plan v6 확정 → 01:27 노트북 실행"
  2. 만약 실제 순서가 역순이었다면 정직하게 evidence에 박제 + 이후 사이클에서 cherry-pick 방어 책무를 가중.
- **근거**: cycle 1 학습 #5/#7/#10 재발 차단은 **시간 trace가 투명해야** 실효성이 있다. 현재 문서로는 "v5 묵시적 박제 → v6 명시화"가 성립하지만, backtest-reviewer NIT-1도 관련 지적을 했고 (리포트 L3 시점 표기 혼동) 감사관 관점에서 **시간 trace 명확화**가 tight 방어책.

### WARNING-3: Option C 수사적 억압 + 작성자 권고 Option A = 사용자 결정 중립성 약화

- **위치**: `week2_report.md` §10 Option C ("본 리포트는 이 옵션을 권장하지 않음" + "cycle 3 강제"), §11 "권장 사항 (리포트 작성자 의견)".
- **문제**:
  - Option C의 "cycle 3 강제 (cherry-pick 감시 트리거)" 문구는 **페널티 프레임**으로 사용자 판단을 제약.
  - V_reported 선택이 WARNING-1에서 지적한 대로 "프로젝트 self-imposed floor"라면, 사용자가 Bailey 원문 정석인 V_empirical 채택을 검토하는 것은 **cherry-pick이 아니라 방법론 재평가**일 수 있다. 리포트 수사는 이를 "페널티 = 감사 +1"로 동일시.
  - §11 작성자 권고 Option A는 "박제 룰 엄격 준수 관점 일관"이라는 내적 논리는 맞지만, 그 내적 논리 자체가 WARNING-1 (V=1.0 floor의 정당성) 검증을 회피하는 순환.
- **권고**:
  1. Option C 서술에서 "cycle 3 강제" 문구를 완화: "V 선택 방법론 재평가로 취급 + 감사 1회 추가 수행 + 결과 invariance 확인" 정도로. 페널티 프레임 제거.
  2. §11을 **중립 요약**으로 재작성: "Option A가 박제 룰 일관성에서 가장 보수적이다. Option C는 Bailey 원문 정석 V 해석이며, V=1.0 floor가 프로젝트 self-imposed임을 인지한 상태에서 사용자가 선택 가능."
  3. Option B (Stage 1 조기 종료)는 decisions-final.md에 명시적 경로가 없는 옵션이므로, 리포트 차원에서 제시하려면 근거 보강 (WARNING-4 참조).
- **근거**: 사용자는 의사결정권자이며 리포트는 중립 근거 제공자여야 한다. CLAUDE.md Do's "판단 시 근거 명시" vs "사용자에게 직접 판단을 무책임하게 떠넘기지 말 것" 사이의 균형에서, **작성자 권고가 결과를 고정시키는 편향**이 있다.

### WARNING-4: Option B (Stage 1 조기 종료)의 근거 미제시

- **위치**: `week2_report.md` §10 Option B.
- **문제**:
  - decisions-final.md L520은 "미달 → Stage 1 킬 카운터 +1, Week 3 재탐색"만 명시. "조기 종료" 경로는 별도 정의 없음.
  - decisions-final Part (학습 모드 선언, 언급 L133)는 존재하지만 "Stage 1 중간 종료" 절차는 박제 없음.
  - 리포트가 Option B를 제시하면서 "장점: 깨끗한 종결, 사용자 북극성 '학습 우선'" 서술은 작성자 해석이며, 근거 문서 인용 부재.
- **권고**:
  1. Option B를 유지하려면 decisions-final 해당 조항 (학습 모드 전환) 직접 인용 + "본 시점이 학습 모드 전환 기준 (킬 카운터 +N)에 부합하는지" 평가 박제.
  2. 또는 Option B를 제거하고 "사용자가 Stage 1 중단 의사 표명 시 별도 박제 사이클 수행" 정도로 소프트하게 표현.
- **근거**: 미정의 경로를 리포트가 옵션으로 제시하는 것은 **미승인 결정을 사실로 인코딩할 위험**.

---

## 4. NIT (개선 권고)

### NIT-1: Tier 2 Secondary 마킹의 soft selection leak 명시 부족

- 리포트 §4.2 + §8.1에 "Secondary 마킹도 selection bias 기여"는 Stage 2 게이트 책무로만 명시. 본 W2-03 레벨에서 "Tier 2 12셀 결과를 본 후 Strategy D가 5페어에서 Sharpe>0.5" 판정이 **Strategy 선택/Week 3 진입 여부 판단에 영향을 주는 것**도 soft leak이다. 리포트 §4.2 말미에 "본 Secondary 마킹 결과도 Strategy 평가 가중치에 영향을 주므로 완전한 독립 평가가 아님" 한 줄 추가 권고.

### NIT-2: BTC_C, ETH_C 5-trade 신뢰 구간 미제시

- Sharpe 점추정만 박제. 5 trade 기반 Sharpe의 표준 오차는 매우 크다 (rule of thumb, Jobson-Korkie 1981). 리포트 §8.4 "Sharpe 추정 오차 크지만 본 결과는 그대로 사용"은 정직한 서술이나, **얼마나 큰지 수량화** 가능 (block bootstrap 95% CI, 현재는 Week 3 walk-forward로 deferred). 본 리포트 차원에서는 "5 trade 기반 Sharpe의 경험적 95% CI는 통상 ±0.5~1.0 범위" 정도 정성 보강 권고.

### NIT-3: "Week 3 walk-forward가 최종 검증"이라는 표현의 한계 명시 약함

- §5.2, §8.6, §6.1 등에서 "최종 검증은 Week 3 walk-forward"가 반복된다. **Week 3도 여전히 in-sample family** (과거 데이터 기반 OOS split)이며, 진정한 OOS는 Week 6+ 페이퍼. 리포트 §8.6 "In-sample 예비 검증 성격" 한 줄로는 이 구분이 불충분하다. "Week 3 = 과거 데이터 OOS split (여전히 historical), 진정한 forward OOS = Week 6+ paper trading" 명시 권고.

### NIT-4: synthetic data 한계 인정의 자기 검증 약함

- 리포트 §8.5 "방법 B 채택 결과의 실제 데이터 동작은 본 grid 결과가 경험적 증거" — 실제로는 **방법 A 실제 데이터 비교 실행이 없음** (grid는 방법 B 단일 트랙). "경험적 증거"라는 표현은 과하다. "방법 B 실제 데이터 동작은 관찰됐으나 방법 A 직접 비교는 수행되지 않음. trend 페어(SOL) 1.089 기능 / mean-reversion 페어(TRX) -1.092 실패의 방향성은 synthetic 결과와 정성 일치." 정도로 완화 권고.

### NIT-5 (backtest-reviewer NIT 승계): 리포트 시점 표기, Fisher kurtosis 각주, γ 표기 통일, §4.1 볼드 기준 명시, make_notebook_08.py v5 → v6 업데이트

- backtest-reviewer NIT-1~5 5건 (감사 추적성 개선) 전량 그대로 승계. 본 외부 감사관 의견도 동일. W2-03.7 APPROVED 전이든 후든 반영 가능.

---

## 5. 독립 재계산 결과

| 항목 | 독립 산출값 | JSON 박제값 | 일치 |
|------|-------------|-------------|------|
| SR_0 (V=1.0) | 1.3001407878455840 | 1.3001407878455840 | bit-level OK |
| SR_0 (V=0.1023) | 0.4159035852 | 0.4159035852 | bit-level OK |
| BTC_A DSR_z | -3.4317668413 | -3.4317668413 | bit-level OK |
| BTC_C DSR_z | -3.9455910951 | -3.9455910951 | bit-level OK |
| BTC_D DSR_z | -1.6408893527 | -1.6408893527 | bit-level OK |
| ETH_A DSR_z | -2.4686106788 | -2.4686106788 | bit-level OK |
| ETH_C DSR_z | -10.2263186548 | -10.2263186548 | bit-level OK |
| ETH_D DSR_z | -2.5133046502 | -2.5133046502 | bit-level OK |
| V_empirical-DSR_z (BTC_A) | +23.22 | (리포트 수사: "pass") | 정합 |
| V_empirical-DSR_z (ETH_C) | -2.77 | (리포트 수사: 5셀 pass, ETH_C 제외) | 정합 |

- 6셀 DSR_z 값 **전량 완벽 일치**. 공식 구현 (`compute_sr_0`, `compute_dsr`) + γ_4 Fisher+3 변환 + T-1 계수 + 분모 denominator 모두 무결.
- V_empirical 시나리오에서 5셀 Sharpe pass 주장도 독립 재현 확인 (ETH_C만 미달).
- 재계산 코드는 본 trace 저장 직전 venv 실측 결과: `source research/.venv/bin/activate && python3 ...`.

---

## 6. 최종 verdict

### **APPROVED with follow-up (사용자 Go/No-Go 명시 결정 진행 가능)**

- **BLOCKING 0건**: 수치 무결, 공식 구현 정확, 룰 준수, cross-document 정합.
- **WARNING 4건**: (1) V_floor=1.0의 Bailey 준거 서술 완화 필요 (프로젝트 self-imposed floor로 정확히 표기), (2) sub-plan v6 C-1 박제 시간 trace 명확화, (3) Option C 수사적 억압 + 작성자 권고 Option A 중립성 약화, (4) Option B 근거 미제시 (decisions-final 미정의 경로).
- **NIT 5+1건**: Tier 2 soft selection leak 명시, low-N Sharpe CI 정성 보강, "Week 3 = 최종 OOS" 표현 한계, synthetic data 자기 검증 완화, backtest-reviewer NIT-1~5 승계.

**진행 권고**:
1. WARNING-1~4는 **사용자 결정 전에 반영 권고**. 특히 WARNING-1 (V_floor Bailey 준거 서술)과 WARNING-3 (Option C 수사 완화)은 사용자의 중립 판단을 위해 필요. WARNING-4 (Option B 근거)는 Option B를 유지하려면 필수.
2. NIT 6건은 W2-03.6 evidence/리포트 패치 사이클에서 일괄 반영 또는 이후 사이클로 지연 가능.
3. WARNING 반영 후 사용자 Go/No-Go 명시 결정 수집 (Option A/B/C/D).
4. 결정 박제: handover + decisions-final.md + stage1-execution-plan.md + candidate-pool.md.

**핵심 메시지**:
- 자동 결과 = **No-Go under V_reported=1.0 극보수적 floor**.
- **V_reported=1.0은 Bailey 2014 원문 절차가 아니라 프로젝트 self-imposed conservative floor**이다. 이 프레이밍을 사용자에게 정직하게 전달한 뒤 Option 판단을 받는 것이 가장 tight.
- Strategy A Recall 미발동 정확. 기계적 적용 확인.
- Stage 1 킬 카운터 +1 추가 (총 +2)는 Option A 채택 시 사전 박제 (decisions-final L520) 일관. Option B/C/D는 근거 보강 필요.

---

## 7. 감사관 개인 의견 (bias 명시)

- **나의 편향**: 감사관으로서 "V_reported=1.0 floor는 overkill" 경향을 조금 더 강하게 느낀다. 6 trial의 sample variance 0.1023은 "신뢰도 낮음"이 맞지만, floor를 **10배** 설정하는 것은 회계적 보수주의 수준을 넘어서 **결과를 거의 확정적으로 No-Go 방향으로 미는** 효과가 있다. 통상 사용되는 conservative floor는 "V_floor = median or typical Sharpe variance across similar backtest literature ≈ 0.25~0.50" 정도가 더 주류다. "1.0"은 Bailey 원문에 예시로 자주 등장하는 값이긴 하지만 **실측 6셀의 10배 과대평가는 정당화가 필요하다**.
- **그러나 변경 금지 서약 발효 중**: sub-plan v6 C-1 박제가 발효됐고, 사용자가 승인한 체계 내에서 V_reported=1.0은 **지금 감사관이 정치적으로 뒤집을 대상이 아니다**. "극보수적이지만 cherry-pick 차단 관점에서는 strong 하다"는 해석이 오히려 프로젝트 목적 (학습 + cycle 1 반성)과 더 잘 맞을 수 있다. 그래서 BLOCKING 아닌 **WARNING**으로 처리.
- **Option A vs C 판단 지점**: 내가 외부 컨설턴트라면 사용자에게 "V=1.0 floor의 정당성은 프로젝트 방어적 선택임을 명시한 뒤, Option A (박제 룰 유지)와 Option C (V_empirical 재평가 + 근거 박제)는 **철학 차이**이지 옳고 그름이 아니다" 라고 전달할 것이다. 리포트는 Option A를 "박제 룰 관점 일관"으로 표현하고 Option C를 "cycle 3 강제"로 페널티화하는데, **이 비대칭이 감사관 눈에 들어오는 주요 불편 지점**이다.
- **결과 자체의 해석 (나의 opinion)**: 자동 No-Go가 "정말 엣지 부재"인지, "V_floor 선택 때문"인지 구분은 Week 3 walk-forward까지 가야 명확해진다. 현재 5셀 Sharpe >1.0 + Tier 2 SOL 전략 3종 Sharpe>0.7 은 **잠재적 엣지 signal**로 보인다. 다만 2024 regime dependency (Strategy A의 W1 분석에서도 발견됐던 패턴)는 여전히 위험. Option A를 사용자가 선택하더라도 프로젝트 가치는 사라지지 않으며, Week 3를 "동일 파라미터로 walk-forward + bootstrap + MC" 사이클로 가는 것이 정석. V=1.0 floor가 "엣지를 가린다"고 판단하면 Option C로 가되 감사 trace를 강화하면 된다.
- **변경 금지 서약 존중**: 본 감사관은 프로젝트 박제 룰을 존중한다. 위 WARNING들은 "박제 변경"이 아니라 "박제 서술 tight화 + 중립성 강화"만 요구한다. 사용자 결정 자체는 박제 밖 영역.

---

**감사관 서명**: Claude (외부 감사관 페르소나, opus-4-7[1m])
**일시**: 2026-04-20 UTC
**Trace**: `.evidence/agent-reviews/w2-03-insample-grid-result-review-2026-04-20.md` (본 파일)
**결정**: APPROVED with follow-up → WARNING-1~4 반영 후 사용자 Go/No-Go 결정 수집

End of trace.
