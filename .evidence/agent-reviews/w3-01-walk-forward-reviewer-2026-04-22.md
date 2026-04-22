# W3-01 backtest-reviewer — 2026-04-22

## 호출 정보

- 에이전트: backtest-reviewer (`.claude/agents/backtest-reviewer.md`)
- 대상 Task: W3-01 Walk-forward Analysis (Feature BT-004)
- 대상 문서/코드:
  - `research/notebooks/09_walk_forward.ipynb`
  - `research/_tools/make_notebook_09.py`
  - `research/outputs/w3_01_walk_forward.json`
  - `research/outputs/week3_report.md`
  - `.evidence/w3-01-walk-forward-2026-04-22.md`
  - `docs/stage1-subplans/w3-01-walk-forward.md` v2
- Cross-check 문서: w2-03-insample-grid.md v9, candidate-pool.md v5, decisions-final.md (W2-03 Go), research/CLAUDE.md

## 체크리스트 적용 결과 (A~H)

### A. Data Integrity — PASS

- [x] 데이터 해시 검증 코드 첫 실행 cell (cell 3)에 존재. `data_hashes.txt` 파싱 후 `actual == expected` assert.
- [x] `df.index.tz is not None and str(df.index.tz) == 'UTC'` assert (cell 3). pyupbit 타임존 처리는 freeze 시점(W1-01/W2-01.4)에 이미 완료된 파일을 읽음. re-localize 불필요.
- [x] 갭 이슈: data_hashes.txt 메타에 `gap_pct=0.0000%` (BTC/ETH 일봉 둘 다). N/A 가능성 없음.
- [x] 파일명 `KRW-BTC_1d_frozen_20260412.parquet`, `KRW-ETH_1d_frozen_20260412.parquet` — freeze 날짜 포함.
- [x] data_hashes.txt 실측 해시 `da5b5a5bd74c...`, `2dfbb4970bc8...` 노트북 출력과 일치 (12 char prefix `da5b5a5bd74c`, `2dfbb4970bc8`).

### B. Pre-registered Parameters — PASS

- [x] 사전 지정 파라미터가 cell 4에 상수로 명시 (`STRATEGY_A_PARAMS`, `STRATEGY_C_PARAMS`, `STRATEGY_D_PARAMS`, `N_TRIALS=5`, `GO_SHARPE_THRESHOLD=0.8`, `GO_DSR_Z_THRESHOLD=0.0`, `GO_STABILITY_REQUIRED=5`, `MIN_TRADE_COUNT=2`).
- [x] JSON `parameters` 필드에 3 전략 + portfolio + go_criteria 모두 기록됨.
- [x] 본 Task는 grid 아닌 walk-forward. 민감도 그리드 아님. 25 cell×fold 조합 모두 사전 지정.
- [x] DSR N_trials=5 (W2-03 Go cells 양방향 freeze에 해당) 정확.
- [x] Strategy 파라미터는 candidate-pool.md v5와 일치 (MA=200, FAST/SLOW_MA=50/200, ATR=14, ATR_MULT=3.0, KC=20+ATR14+1.5, BB=20+2.0, SL=8%).

### C. vectorbt 0.28.5 API — PASS

- [x] `sl_stop=STRATEGY_A_PARAMS['SL_PCT']=0.08` (fraction) — cell 7.
- [x] `sl_trail=False` boolean — cell 7.
- [x] `ts_stop`, `td_stop`, `max_duration`, `time_stop`, `dt_stop` 미사용.
- [x] `pf.sharpe_ratio(year_freq='365 days')` 괄호 호출, 명시적 year_freq — cell 7. ✓ W2-03 v9 SR annualization 박제 + PT-04 선행 적용 준수.
- [x] `freq='1D'` 명시 — cell 7.
- [x] Strategy C `exit_mask`는 manual 계산된 pandas Series (trailing_high - ATR_MULT × ATR), 미정의 변수(`entry_price`, `bars_held`) 참조 없음. 방법 B 정확 구현.
- [x] Walk-forward이므로 앙상블 `cash_sharing` N/A.

### D. pyupbit API — N/A

- W3-01 신규 다운로드 없음, 기존 freeze 파일만 read. pyupbit 호출 경로 없음.

### E. Wilder Smoothing — PASS

- [x] Strategy C: `AverageTrueRange(high, low, close, window=14).average_true_range()` — cell 6.
- [x] Strategy D: `KeltnerChannel(..., window_atr=14, original_version=False, multiplier=1.5)` + `BollingerBands(..., window=20, window_dev=2.0)` — ta 라이브러리 사용.
- [x] 직접 SMA/EMA로 ATR/RSI 구현 없음.

### F. Strategy Logic Correctness — PASS (minor NIT)

- [x] Strategy A: `MA_PERIOD=200` rolling mean, Donchian 20/10 `.shift(1)`, Vol avg 20 `.shift(1)`. Look-ahead 차단. 일봉 기준 200 윈도우 정확.
- [x] Strategy C: 방법 B manual trailing ATR exit_mask 구현 — W2-03.1 W-1 테스트에서 "방법 B = 매 bar 동적 ATR" 확정. cell 6의 루프에서 `atr_values[i]` 매 bar 참조, `trailing_high` 지속 갱신. 박제 의도 준수.
- [x] Strategy D: KC + BB 동시 break, Keltner `original_version=False` + `window_atr=14` + `multiplier=1.5` 명시. BB `window=20, window_dev=2.0`. candidate-pool.md v5 일치. `.shift(1)`로 breakout strict 처리.
- [x] 각 fold 200-bar MA warmup 확보 (fold 1 train=730 bars >> 200).
- [x] 신호는 전체 데이터로 계산 후 test window 만 slice — walk-forward 표준 패턴, look-ahead 차단 유지 (train 기간 신호만 warmup, test에서 거래).
- [x] 시간 스톱 `entries.shift(N)` 패턴 미사용 (본 Task에서 시간 스톱 없음).

### G. Output / Evidence — PASS (bit-level 불일치 1건 발견)

- [x] 결과 JSON `research/outputs/w3_01_walk_forward.json` 저장 (cell 10).
- [x] JSON 필드: `feature_id=BT-004`, `task_id=W3-01`, `sub_plan_version=v2`, `cells`, `folds`, `parameters`, `fold_dsr`, `fold_results`, `cell_summary`, `is_go`, `go_cells`, `multiple_testing_note` 모두 포함.
- [x] `data_hash`는 data_hashes.txt 내부 검증 assert 경로. JSON 자체에 hash 필드는 별도 없으나 evidence 1.1에서 SHA256 12 char prefix 인용 (`da5b5a5bd74c`, `2dfbb4970bc8`).
- [x] `freq='1D'` + 일봉 parquet 일치.
- [x] Evidence `.evidence/w3-01-walk-forward-2026-04-22.md` 6단 구조 (§1 데이터 / §2 파라미터 / §3 결과 / §4 자동 검증 / §5 룰 준수 / §6 리뷰 + §7 킬 카운터 + §8 커밋 프리뷰) 준수.
- [x] Evidence §5 한계/가정 (Strategy C W-7 박제, N=5 혼재, multiple testing 한계) 명시.
- [x] 커밋 메시지 프리뷰에 `Evidence: .evidence/w3-01-walk-forward-2026-04-22.md` 줄 포함.

**[WARNING-1] bit-level 불일치**: Evidence §1.3 fold 분할 표의 train bar count가 JSON 및 notebook 실측과 어긋남.
- Evidence: Fold 2 train bars **912** / Fold 3 train bars **1095**.
- JSON (`fold_results`의 `folds`): Fold 2 train bars **913** / Fold 3 train bars **1096**.
- Notebook 출력: Fold 2 "913 bars" / Fold 3 "1096 bars" (cell 5 실행 결과).
- 원인: train 구간 계산식은 `df.index[(df.index >= TRAIN_START) & (df.index < train_end)]`로 train_end (split point) 는 exclusive. 2023-10-15 ~ 2024-04-15 사이 BTC 일봉 개수 = 913 (notebook 재현 가능). Evidence 수작업 오기로 추정.
- Focus-체크의 "Report/evidence의 수치가 JSON 값과 bit-level 일치?" 항목 위반.
- Fix: Evidence 표 **Fold 2 train bars 912 → 913**, **Fold 3 train bars 1095 → 1096** 정정. Go/No-Go 판정에는 영향 없으나 "외부 감사 2차 bit-level 재계산"에 앞서 선제 정정 필요.

### H. Cross-document Consistency — PASS

- [x] Cells `[(BTC,A),(BTC,C),(BTC,D),(ETH,A),(ETH,D)]` = W2-03 Go cells 5개 (ETH_C FAIL 재포함 X, Secondary X). Sub-plan v2 메타 + decisions-final.md "W2-03 Go 결정" 일치.
- [x] Fold 분할점 5개 (2023-10-15 / 2024-04-15 / 2024-10-15 / 2025-04-15 / 2025-10-15 UTC) = sub-plan v2 W-1 박제 일치.
- [x] `TRAIN_START=2021-10-15` Common-window (cycle 2 v5) = W2-03 박제 일치.
- [x] Strategy 파라미터 candidate-pool.md v5 일치. Strategy C 방법 B (manual trailing) W2-03.1 채택 사실 반영.
- [x] Sub-plan v2 Acceptance Criteria 모든 항목이 evidence 또는 notebook에서 평가됨 (make_notebook_09.py + dry-run + 25 조합 실행 + fold DSR + aggregation + Go/No-Go 자동 + 리포트 + evidence 6단 + reviewer 호출 대기).
- [x] Stage 1 execution-plan 업데이트 재료 준비됨 (week3_report §11 + evidence §7).
- [x] year_freq='365 days' + YEAR_FREQ 상수 — W2-03 v9 SR annualization 박제 일관.

## Focus 체크 (추가 항목)

- **수치 bit-level 일치**: JSON ↔ week3_report ↔ evidence 대조
  - week3_report.md §2 fold 표는 test 구간만 기재, train bar count 미기재 → 불일치 원인 없음.
  - week3_report.md §3 fold V_empirical/SR_0/non-NA 3 값 모두 JSON과 일치 (0.3657/0.7212/4, N/A/N/A/1, 0.2101/0.5467/2, 0.1643/0.4834/3, N/A/N/A/1).
  - week3_report.md §4.1 Sharpe/DSR_z/Trades/Return 11 non-NA row 모두 JSON과 소수점 3자리 일치.
  - week3_report.md §5 cell summary fold_pass/Mean Sharpe/Mean DSR_z/N/A 값 모두 JSON `cell_summary`와 일치.
  - evidence §3.2 cell summary, §3.3 fold V_empirical 모두 일치.
  - **단 evidence §1.3 train bar count 2건(fold 2, 3)만 JSON과 불일치** → 위 WARNING-1.
- **`pf.sharpe_ratio(year_freq='365 days')` 명시 호출**: cell 7 `sharpe = float(pf.sharpe_ratio(year_freq=YEAR_FREQ))` 확인 PASS.
- **Strategy C 방법 B**: make_notebook_09.py cell 6 `strategy_c_signals` 함수에 매 bar 루프 + `trailing_high` 갱신 + `stop_level = trailing_high - atr_mult * atr_values[i]` 확인 PASS.
- **min_trade_count=2 사전 박제**: cell 4 `MIN_TRADE_COUNT=2` + cell 7 `if trade_count < MIN_TRADE_COUNT: return {na: True, ...}` N/A=FAIL 처리 PASS.
- **V_empirical per fold non-NA<2 처리**: cell 8 `if len(sharpes) < 2: fold_dsr[fid]={V_empirical: None, SR_0: None, note: ...}` 해당 fold DSR_z=None + note="fold V 산출 불가" 정확. Fold 2/5에서 BTC_D만 non-NA라 V 산출 불가 + BTC_D fold 2/5의 DSR_z만 None 처리 — JSON 검증 일치.
- **Fold 분할점 freeze**: 5개 날짜 sub-plan v2 W-1과 bit-level 일치.
- **W2-03 Go cells 양방향 freeze**: 5 cell (BTC_A/C/D, ETH_A/D), ETH_C 제외 + Secondary 미포함 일치.
- **Bailey 2014 DSR 공식**: cell 8 `compute_sr_0` eq.9 (γ·Φ⁻¹ 항) + `compute_dsr_z` eq.10 (skew Fisher + kurtosis Fisher→raw 변환 `kurt_raw = kurt_fisher + 3`) 공식 구현 W2-03 v9와 동일 코드 구조. PASS.
- **Evidence 6단 구조**: §1~§6 모든 섹션 존재. 추가 §7 킬 카운터 + §8 커밋 프리뷰는 informational. PASS.
- **리포트 §11 다음 단계**: W3-01.5 완료 / W3-01.6 외부 감사 2차 / W3-01.7 사용자 공식 결정 3단계 명시. 프레임 A/B 서술은 "둘 다 Stage 1 킬 카운터 +2 소급 공통" 박제 유지 + §7 리포트에서 "프레임 B 부분적으로만 성립" 정직 해석 포함. 중립성 PASS.

## 발견 사항 (BLOCKING / WARNING / NIT)

### BLOCKING: 0건

### WARNING: 1건

```
[WARNING-1] .evidence/w3-01-walk-forward-2026-04-22.md §1.3 fold 표 train bar count 2건 불일치
Description:
  - Fold 2 train bars: Evidence 912 vs JSON/notebook 913 (+1 차이)
  - Fold 3 train bars: Evidence 1095 vs JSON/notebook 1096 (+1 차이)
  - Fold 1/4/5는 JSON과 일치 (730 / 1278 / 1461)
Fix:
  - Evidence §1.3 표 본문 편집:
    | 2 | 2021-10-15 ~ 2024-04-15 | 912 → 913  | ...
    | 3 | 2021-10-15 ~ 2024-10-15 | 1095 → 1096 | ...
Reference:
  - research/outputs/w3_01_walk_forward.json (folds[1].train_bar_count, folds[2].train_bar_count)
  - research/notebooks/09_walk_forward.ipynb cell 5 실행 출력
Impact:
  - Go/No-Go 판정에 영향 없음 (train은 signal warmup 용도)
  - 외부 감사 2차 bit-level 재계산 시 지적 확실시 → 선제 정정 권고
  - "Report/evidence의 수치 bit-level 일치" Focus 체크 위반
```

### NIT: 2건

```
[NIT-1] research/outputs/w3_01_walk_forward.json `profit_factor` 필드가 Infinity 문자열로 저장
Location:
  - fold_results[0] (BTC_A fold 1): "profit_factor": Infinity
  - fold_results[10] (BTC_D fold 1): "profit_factor": Infinity
  - fold_results[12] (BTC_D fold 3): "profit_factor": Infinity
  - fold_results[15] (ETH_A fold 1): "profit_factor": Infinity
Suggestion:
  - JSON 표준에서 Infinity는 invalid 값. `default=str` 로 직렬화되어 "Infinity" 리터럴이 찍힘.
  - 일부 JSON 파서는 이를 거부. 다운스트림(W3-02+)에서 `json.load` 시 `allow_nan=True` 기본값으로 통과되지만 엄격한 파서에는 문제.
  - Fix 옵션 1: Infinity → null 대체 (loss=0 전부승 의미).
  - Fix 옵션 2: Infinity → 문자열 `"inf"` 대체 + 다운스트림에서 sentinel 처리.
  - W3-02에서 이 JSON을 참고 metric으로 read할 때 명시 처리 필요.
Improves: 다운스트림 호환성 / JSON 표준 준수
Priority: low — 자동 평가에는 profit_factor 미사용 (Sharpe + DSR_z + trade count만). JSON 파싱 실패 없이 지속 가능하나 정책적 마이너 이슈.
```

```
[NIT-2] evidence §1.3 표 Fold 2 train "912" → sub-plan v2 원문 "913"과도 불일치 가능성
Location: sub-plan v2에는 train bars 숫자가 본문에 명시되어 있지 않음 (범위만 표기).
Suggestion:
  - NIT가 아닌 WARNING-1의 일부. Sub-plan은 train 범위만 박제하고 bar count는 notebook sanity check 결과를 evidence에 담는 구조. 정정 시 범위 유지 + bar count만 913/1096로 수정.
Improves: 일관성
```

## 최종 verdict

```
APPROVED with follow-up

검증 결과:
- A. Data Integrity:          PASS
- B. Pre-registered Params:   PASS
- C. vectorbt 0.28.5 API:     PASS (sl_stop fraction, sl_trail False, freq='1D',
                                   pf.sharpe_ratio(year_freq='365 days') 명시)
- D. pyupbit API:             N/A (데이터 다운로드 없음)
- E. Wilder Smoothing:        PASS (ta 라이브러리)
- F. Strategy Logic:          PASS (Strategy C 방법 B manual trailing ATR 정확 구현,
                                   shift(1) look-ahead 차단, MA200 윈도우 정확)
- G. Output / Evidence:       PASS with WARNING-1 (evidence train bar count 2건 불일치)
- H. Cross-document:          PASS (sub-plan v2 + W2-03 v9 + candidate-pool v5 + decisions-final 일관)

Focus 체크:
- [x] Report/evidence ↔ JSON bit-level 일치 → 11 fold non-NA + 5 cell summary + fold DSR 완전 일치.
      단 evidence §1.3 train bar count 2건만 불일치 (WARNING-1).
- [x] pf.sharpe_ratio(year_freq='365 days') 명시 호출 — cell 7
- [x] Strategy C 방법 B (manual trailing exit_mask) — make_notebook_09.py cell 6
- [x] min_trade_count=2 사전 박제 + N/A fold 처리 정확
- [x] V_empirical per fold (non-NA<2 DSR 산출 불가) 정확
- [x] Fold 분할점 freeze 정확
- [x] W2-03 Go cells 양방향 freeze 준수
- [x] Bailey 2014 DSR 공식 (skew Fisher / kurtosis Fisher+3 → raw)
- [x] Evidence 6단 구조
- [x] 리포트 §11 다음 단계 + 프레임 A/B 중립 서술

발견:
- 0 BLOCKING
- 1 WARNING (WARNING-1: evidence train bar count 2건 — Fold 2: 912→913, Fold 3: 1095→1096)
- 2 NIT (NIT-1: JSON Infinity 직렬화 / NIT-2: WARNING-1 subset)

Follow-up (다음 Task 진행 조건 아님, 사용자 보고 필요):
1. WARNING-1: evidence §1.3 표에서 Fold 2 train bars 912 → 913, Fold 3 train bars 1095 → 1096
   정정 (bit-level 정합성 복원). 선제 정정 후 W3-01.6 외부 감사 2차로 이관 권고.
2. NIT-1: W3-02 진입 시 (Go/No-Go 판정 확정 후) JSON `profit_factor` Infinity 처리 정책
   박제. W3-02 입력 참고 metric 파싱 범위에서만 영향.

다음 단계:
- W3-01.6 외부 감사 2차 진행 가능 (BLOCKING 없음)
- W3-01.7 사용자 공식 Go/No-Go 결정 대기
- is_go=False 자동 평가 정확, 프레임 A/B 사용자 선택 필요
```

---

End of backtest-reviewer trace. Generated 2026-04-22 by Opus 4.7 (1M).
