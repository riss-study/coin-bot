# W2-03 In-sample grid + W2-03.6 Week 2 report/evidence — backtest-reviewer trace

- **Date**: 2026-04-20 (UTC)
- **Task**: W2-03 (Feature BT-005), SubTask W2-03.6 (report + evidence), pre-W2-03.7
- **Reviewer**: backtest-reviewer (general-purpose subagent, opus-4-7[1m])
- **Scope**: 새로 작성된 `week2_report.md` + `.evidence/w2-03-insample-grid-2026-04-20.md` 검증. 노트북/그리드 JSON은 2026-04-20 실행 시점 코드 수준 승인 기반으로 수치 정합성만 재확인.

---

## 1. Prompt (사용자/상위 에이전트 호출)

> 호출자: `/Users/riss/project/coin-bot/CLAUDE.md` + sub-plan v6 W2-03.6 체크박스 "backtest-reviewer 호출".
>
> Artifacts:
> 1. `research/notebooks/08_insample_grid.ipynb`
> 2. `research/_tools/make_notebook_08.py`
> 3. `research/outputs/w2_03_primary_grid.json`
> 4. `research/outputs/w2_03_exploratory_grid.json`
> 5. `research/outputs/w2_03_dsr.json`
> 6. `research/outputs/w2_03_dsr_unit_test.json`
> 7. `research/outputs/week2_report.md` (NEW)
> 8. `.evidence/w2-03-insample-grid-2026-04-20.md` (NEW)
> 9. `docs/stage1-subplans/w2-03-insample-grid.md` v6
>
> Cross-check: `docs/decisions-final.md` L482/L513-521 + `docs/candidate-pool.md` Strategy A Recall + `research/CLAUDE.md` vectorbt/pyupbit 룰 + 기존 agent-review traces.
>
> Focus: 새 W2-03.6 산출물 (7, 8). 리포트 수치 정합성 (Sharpe/DSR/MDD/Trades), 6단 evidence 구조, Go/No-Go 로직 (V_reported=1.0 conservative → SR_0=1.3001 → 0/6 Go cell), cherry-pick 차단 reasoning, Strategy A Recall 평가, Stage 1 킬 카운터 stance, W2-03.7 진행 가능 여부.

---

## 2. Checklist applied (A-H)

- **A. Data Integrity**: 6 pairs, SHA256 assert in notebook cell 3 + reported in report §1 + evidence §1.1. Freeze date `2026-04-12` consistent. Tz assertion present (`df.index.tz == 'UTC'`). Gaps check inherited from W1-01/W2-01.4 (reported).
- **B. Pre-registered Parameters**: Strategy A/C/D 파라미터 상수 선언 (notebook cell 5) + JSON `parameters` 필드 박제. Tier 2 = Go 기여 X 명시 (exploratory JSON `go_contribution=false`). DSR `n_trials=6` + V_reported=1.0 사전 박제 (C-1 v6).
- **C. vectorbt 0.28.5 API**: `sl_stop` fraction (0.08), `sl_trail` boolean, `freq='1D'` 명시, `pf.sharpe_ratio(year_freq='365 days')` 메서드 호출 (괄호). `from_signals`에 `year_freq` 미전달 (B-1 v6 정정 실측 기반). Strategy C `sl_stop=None` 경로는 manual trailing exit_mask에 trailing 로직 내장 (방법 B). No `ts_stop/td_stop/max_duration`. No undefined vars in exit masks.
- **D. pyupbit API**: 본 Task는 데이터 재사용만 (W1-01 + W2-01.4 freeze 재사용). pyupbit 호출 없음 → N/A.
- **E. Wilder Smoothing**: `AverageTrueRange`, `KeltnerChannel`, `BollingerBands`, `RSIIndicator` 모두 `ta` 라이브러리. 직접 구현 없음.
- **F. Strategy Logic**: MA200=200 ✓, Donchian shift(1) ✓, vol_avg shift(1) ✓, 4h×6 = N/A (일봉), warmup assert (strategy_a/c/d 모두). Strategy C 방법 B manual trailing (`trailing_high − ATR_MULT × ATR(t)` 매 bar 동적). 청산 후 동일 추세 재진입 차단 assert. Strategy D strict crossover (kc_upper + bb_upper 동시, shift(1)).
- **G. Output / Evidence**: 4개 JSON 저장, `data_hashes`, `parameters`, `sharpe`, `total_return`, `max_drawdown`, `win_rate`, `profit_factor`, `total_trades` 모두 포함 ✓. Evidence 6단 구조 준수. `generated_at` 박제 (단, JSON은 UTC, 리포트 header는 날짜만).
- **H. Cross-document Consistency**: Primary grid `data_hashes`가 W1-01 + W2-01.4 evidence 박제값과 일치. N_trials=6 = sub-plan v6 C-1 박제. Go 기준 = decisions-final.md L518 일치. Strategy A Recall trigger = candidate-pool.md L27 일치.

---

## 3. Findings

### 3.1 BLOCKING (수정 필수)

**없음.**

### 3.2 WARNING (강력 권장)

**없음.** (기존 v5→v6 감사에서 BLOCKING/WARNING 0건 달성, 본 검증에서 신규 발견 없음.)

### 3.3 NIT (개선 제안)

**NIT-1**: `research/outputs/week2_report.md` L3 "생성일시: 2026-04-20 (UTC)" vs 그리드 JSON `generated_at=2026-04-19T16:27:56+00:00`.
- 실제로 2026-04-19 UTC 16:27 = 2026-04-20 KST 01:27. 노트북 실행은 2026-04-20 (sub-plan v6 박제 당일 KST 새벽).
- **개선 제안**: 리포트 header에 "(UTC)" 표기는 실제 UTC 기준 2026-04-19이므로 혼동 소지. "작성: 2026-04-20 KST / 노트북 실행: 2026-04-19 16:27 UTC" 정도로 명시하면 감사 추적성↑. (Go/No-Go 결정에는 영향 없음.)
- **Fix**: `week2_report.md` L3 → "생성일시: 노트북 실행 2026-04-19 16:27 UTC / 리포트 작성 2026-04-20 KST".

**NIT-2**: `.evidence/w2-03-insample-grid-2026-04-20.md` §3.3 DSR 표의 `γ_4 (kurtosis Fisher)` 열 헤더.
- JSON `returns_kurtosis`는 `scipy.stats.kurtosis(..., fisher=True)` 결과 (Fisher form, 정규분포=0). 그러나 Bailey 2014 공식의 γ_4는 **raw kurtosis (정규분포=3)** 사용. 노트북 `compute_dsr()`은 `gamma_4 = scs.kurtosis(returns, fisher=True) + 3` 으로 올바르게 변환 → 최종 DSR_z 계산은 정확.
- Evidence 표에 "Fisher" 표기는 원시 JSON 값 (Fisher)을 그대로 보여주는 것이고, 공식의 γ_4로 쓰이는 값은 Fisher+3이므로 **독자가 수식과 표를 대조할 때 혼선 가능**. 사용된 DSR 계산 로직은 정확하므로 결과 자체는 올바름.
- **Fix**: evidence §3.3 열 헤더 "γ_4 (kurtosis Fisher)" → "returns_kurtosis (Fisher)" 로 명명 변경하고, "Bailey 공식 γ_4에는 Fisher+3 자동 적용됨 (노트북 `compute_dsr()` 참조)" 각주 추가 권장.

**NIT-3**: `week2_report.md` §5.1 "Euler-Mascheroni γ = 0.5772156649". 실제 노트북/JSON은 `0.5772156649015329` (15자리) 사용. 리포트 표시값은 10자리 절삭인데, 정확도 손실은 없으나 "박제값을 그대로 표기" 원칙 관점에서 JSON 값과 문자 1:1 매치가 바람직.
- **Fix**: "γ = 0.5772156649015329 (노트북/JSON 박제 문자열)" 또는 "~0.5772" 로 통일.

**NIT-4**: `week2_report.md` §4.1 SOL_A Sharpe "**0.718**" 강조 (볼드). SOL는 Tier 2 = Go 기여 X이며, 임계값 0.5 대비 Secondary 마킹 충족분만 볼드 처리하는 게 cherry-pick 소지 최소화에 맞다. 현재 표기는 max-span 0.7 이상을 볼드한 것으로 보이는데, 기준 명시가 없음. (§4.2 Secondary 마킹 임계값 0.5와 따로 노는 볼드 기준.)
- **Fix**: §4.1 볼드 기준을 명시하거나 (예: "Sharpe > 0.7 페어 볼드 = 주목할 만한 상대 강도") 제거. Go 결정과 무관.

**NIT-5**: `make_notebook_08.py` L10 sub-plan 참조 버전이 "v5"로 하드코딩 (실제 실행 시점 sub-plan은 이미 v6). 노트북 첫 셀 마크다운도 "v5 (2026-04-19 사용자 승인 + W2-03.1 방법 B 채택)" 표기.
- 노트북 빌드 시점 (2026-04-20)에는 sub-plan v6 박제 완료. 재빌드 시 "v6" 표기 권장.
- **Fix**: `make_notebook_08.py` 주석 + cell 1 마크다운을 "v6 (B-1 API 정정 + C-1 DSR V 박제 + W2-03.0 실행 검증)"로 업데이트.

### 3.4 PASS 항목 (주요 검증 포인트)

- **Go/No-Go 로직 정합성**: V_reported=1.0 → SR_0=1.3001 → 0/6 Go cell 계산 **수치 재현 확인**. `python3` scipy 실측: `math.sqrt(1.0) × ((1-γ)×Φ⁻¹(5/6) + γ×Φ⁻¹(1 - 1/6e)) = 1.300140787845584`. 리포트/evidence/JSON 세 곳 모두 일치.
- **Cherry-pick 차단 reasoning**: max-span Primary 단독 평가 (W-4 박제), V_reported=max(V_emp, 1.0) 사전 박제 (C-1 v6), V_empirical 병기는 투명 보고 목적 + Go 판정 미사용 명시. Option C에 "본 리포트는 권장하지 않음 + cycle 3 강제" 명시. **논리 정합**.
- **Strategy A Recall 평가**: BTC_A Sharpe 1.035 > 0.8, ETH_A Sharpe 1.144 > 0.8 (Sharpe 조건 만족), but DSR_z < 0 → Recall trigger 미충족 → Retained 유지. candidate-pool.md L27 "Tier 1 중 하나 이상 `Sharpe > 0.8 AND DSR > 0`" 기준과 일치. **정확**.
- **Stage 1 킬 카운터 stance**: decisions-final.md L482 "+1 (Week 1 종료 시점)" 정확 인용. 현재 값 +1 + W2-03 No-Go 채택 시 +1 추가 → 총 +2. 사용자 결정 전이므로 "+1 추가 보류" 명시. **decisions-final L520 "미달 → Stage 1 킬 카운터 +1, Week 3 재탐색"**와 일치.
- **6단 Evidence 구조**: 1.데이터 / 2.파라미터 / 3.결과 / 4.자동검증 / 5.룰준수 / 6.리뷰 — 모두 존재. docs/CLAUDE.md + sub-plan v6 NIT-3 요구 충족.
- **vectorbt 0.28.5 API 실측**: reviewer venv에서 `inspect.signature` 재확인. `Portfolio.from_signals`에 `year_freq` 파라미터 **부재**, `Portfolio.sharpe_ratio`에 `year_freq` **존재** — sub-plan v6 B-1 정정 정확. 노트북은 sharpe_ratio 메서드 경로로 올바르게 라우팅.
- **Secondary 마킹**: A [BTC, ETH, SOL, DOGE] = 4, C [BTC, XRP, SOL] = 3, D [BTC, ETH, SOL, TRX, DOGE] = 5 — JSON 값 수동 재산출(`sharpe_max_span > 0.5`) 결과 일치. 리포트/evidence/JSON 3소스 정합.
- **DSR unit test 재현성**: synthetic SR_hat=0.408, SR_0=1.300, T=1000 → DSR_z=-20.258, DSR_prob≈1.5e-91 — JSON 일치, 공식 단위 테스트 (V=1, N=6 → SR_0=1.3001) PASS.
- **Freeze date 일관**: 6 페어 모두 `frozen_20260412`. W1-01 (BTC) + W2-01.4 (5 페어) 박제 일치.

---

## 4. Final verdict

### **APPROVED with follow-up (W2-03.7 외부 감사 진행 가능)**

**판정 근거**:
- **BLOCKING 0건**: 데이터 무결성, 사전 지정 파라미터, vectorbt API, DSR 공식, Go/No-Go 로직 모두 정합.
- **WARNING 0건**: cherry-pick 차단 박제 완결, Strategy A Recall 평가 정확, Stage 1 킬 카운터 stance decisions-final 일치.
- **NIT 5건 (비블로킹)**: 시점 표기 세분화, Fisher kurtosis 각주, γ 표기 통일, §4.1 볼드 기준 명시, sub-plan 버전 표기 최신화 — 모두 감사 추적성/가독성 개선. W2-03.7 외부 감사 전에 선택적 반영 가능 (Go/No-Go 판정 자체에는 영향 없음).

**진행 권고**:
1. (선택) NIT-1 ~ NIT-5 반영 (10~15분).
2. W2-03.7 외부 감사 1회 호출 (결과 정합성 + cherry-pick 통로 검증, 적대적 감사관 페르소나).
3. W2-03.7 APPROVED 후 사용자 Go/No-Go 명시 결정 대기 (Option A/B/C/D).

**핵심 메시지**:
- 자동 결과 = **No-Go** (0/6 Go cell under V_reported=1.0).
- V_empirical=0.1023 기준이면 5셀 pass지만, **사전 박제 V_reported 적용 일관성 유지 필수** (cycle 1 학습 #7/#10 재발 차단).
- Strategy A Recall 미발동 → Retained 유지 정확.
- Stage 1 킬 카운터 +1 추가 (총 +2) 옵션이 박제 룰 엄격 준수 관점 일관.

---

## 5. Follow-up items

| # | 항목 | 우선순위 | 처리 시점 |
|---|------|----------|-----------|
| 1 | NIT-1: 리포트 L3 시점 표기 세분화 (UTC/KST 구분) | Low | W2-03.7 전 선택 |
| 2 | NIT-2: evidence §3.3 Fisher kurtosis 각주 | Low | W2-03.7 전 선택 |
| 3 | NIT-3: γ 표기 JSON 박제 문자열과 통일 | Low | W2-03.7 전 선택 |
| 4 | NIT-4: §4.1 볼드 기준 명시 또는 제거 | Low | W2-03.7 전 선택 |
| 5 | NIT-5: make_notebook_08.py 주석 + cell 1 "v5" → "v6" | Low | 재빌드 시 |
| 6 | W2-03.7 외부 감사 1회 호출 (적대적 페르소나) | High | 즉시 |
| 7 | 사용자 Go/No-Go 명시 결정 수집 (Option A/B/C/D) | High | W2-03.7 완료 후 |
| 8 | Stage 1 킬 카운터 박제 갱신 (+1 추가 여부) | High | 사용자 결정 후 즉시 |
| 9 | handover + decisions-final.md + stage1-execution-plan.md 체크박스 업데이트 | Medium | 사용자 결정 후 |
| 10 | W1 `sqrt(252)` vs W2 `sqrt(365)` 일관성 깨짐 별도 Task 처리 (handover #21) | Medium | Stage 1 킬 카운터 결정 후 별도 사이클 |

---

## 6. Reviewer 서명

- **Reviewer**: backtest-reviewer (opus-4-7[1m] subagent)
- **Date**: 2026-04-20 UTC
- **Trace path**: `.evidence/agent-reviews/w2-03-insample-grid-review-2026-04-20.md` (본 파일)
- **Referenced by**: `.evidence/w2-03-insample-grid-2026-04-20.md` §6.1 (예정)
- **Checklist reference**: `.claude/agents/backtest-reviewer.md` (A~H 항목 전체)
- **Verdict**: APPROVED with follow-up → W2-03.7 외부 감사 진행 가능

End of trace.
