# 전략 후보 풀 (Candidate Pool)

**목적**: 프로젝트 수명 동안 평가된 전략들의 **사전 지정 파라미터 + 상태 + 재평가 규정**을 물리적으로 저장하는 단일 파일. 외부 감사관 리뷰(2026-04-17) WARNING-5 대응으로 신설.

**원칙**:
- 모든 전략은 **사전 지정된 파라미터 freeze 상태**로만 등록
- 상태 전이는 **Active / Retained / Deprecated** 3단계
- 재등장 시 **DSR-adjusted 평가 필수** (재튜닝 금지)
- 완전 폐기된 전략은 **Deprecated log**에 기록 (재도입 방지)

---

## Active (현재 평가 중)

> Week 2 시작 시점에서 W2-03 grid 평가 대상.

### Strategy A — Trend Following (MA200 + Donchian + Volume)

| 항목 | 값 |
|------|-----|
| **상태** | **Retained (v6 역방향 복귀, 2026-04-22 W3-01 No-Go + 사용자 옵션 C 채택)** |
| **최초 등록** | Week 1 W1-02 (2026-04-15) |
| **파라미터** | MA_PERIOD=200, DONCHIAN_HIGH=20, DONCHIAN_LOW=10, VOL_AVG_PERIOD=20, VOL_MULT=1.5, SL_PCT=0.08 |
| **출처** | Padysak/Vojtko 영감 (Padysak 2020 스타일 복제 아닌 변형) |
| **W1 성적** | BTC 일봉 Sharpe 1.0353, 총수익 +171.76%, MDD -22.45%, 14 trades |
| **W1 경고** | 2024년 단년 집중 (68.3% 기여), 2024-12-17 이후 481일 Sharpe -1.14 (2승 3패) |
| **W2-03 v8 성적 (Recall 발동 근거)** | BTC 일봉 Sharpe 1.0353, DSR_z +23.22 / ETH 일봉 Sharpe 1.1445, DSR_z +29.37 (V_empirical=0.1023 기준). Tier 1 양 페어 `Sharpe>0.8 AND DSR>0` 모두 충족 → 재진입 조건 충족 |
| **재진입 조건 (원본)** | W2-03 grid에서 Tier 1 (BTC+ETH) 중 하나 이상 `Sharpe > 0.8 AND DSR > 0` → **2026-04-20 충족 (BTC_A + ETH_A 둘 다)** |
| **Recall 시 의무** | DSR > 0 필수 평가 (본 W2-03 완료). **Week 3 walk-forward 재검증 필수** (V_empirical 일관 + floor 재도입 금지 + 임계값 변경 금지) |
| **Week 3 실패 시 소급** | Stage 1 킬 카운터 +2 가산 + 외부 감사 재수행 + 사용자 명시 결정 (decisions-final.md "W2-03 Go 결정" 참조) |
| **W3-01 결과 (2026-04-22)** | No-Go 확정. BTC_A 2/5 fold pass / ETH_A 1/5 (N/A 4). 옵션 A 5/5 미충족. 사용자 옵션 C 채택 → Retained 복귀 + Stage 1 학습 모드 전환. Recall mechanism 자동 해제 |

### Strategy C — Slow Momentum (MA50/200 crossover + ATR trail)

| 항목 | 값 |
|------|-----|
| **상태** | **Retained (학습 가치 보존, 2026-04-22 W3-01 No-Go + 사용자 옵션 C 채택)** |
| **최초 등록** | Week 2 (2026-04-17 결정, W2-02 v4 사전 등록 사용자 승인 2026-04-19 "ㄱㄱ") |
| **파라미터 (확정)** | FAST_MA=50, SLOW_MA=200, ATR_PERIOD=14, ATR_MULT=3 (trailing stop) |
| **진입/청산 (W2-02 v4 박제 + W2-03.1 W-1 검증 후 방법 B 채택)** | Long entry: strict golden cross `(MA50>MA200) AND (MA50.shift(1)<=MA200.shift(1))`. Hard exit: strict death cross OR **manual trailing_high - ATR_MULT × ATR(14)(t) exit_mask** (방법 B, **매 bar 동적 ATR 적용**, 2026-04-19 W-1 미니 테스트 검증 결과 채택). Long-only. 청산 후 동일 추세 내 재진입 X |
| **출처** | Faber 2007 "A Quantitative Approach to Tactical Asset Allocation" (MA crossover 타이밍) + Wilder 1978 (ATR) |
| **독립성 한계** | W1에서 BTC 5년 데이터를 이미 본 이후 선택. 문헌 **기본값** 사용이나 완전 OOS 독립 주장 불가 (soft contamination). `decisions-final.md` "Week 2 한계 및 독립성 서약" 참조 |
| **평가 조건** | W2-03 grid에서 Tier 1 평가. Primary `Sharpe>0.8 AND DSR>0`. Secondary 마킹: 동일 전략이 Tier 1+2 3+ 페어에서 `Sharpe>0.5` → ensemble 후보 |
| **Recall 시 의무 (NIT-N2 정정, B-4 cross-document)** | Go 통과 시 **DSR-adjusted 평가 + Week 3 walk-forward 재검증 의무 강제** (Strategy A Recall mechanism과 대칭, W2-03 v2 박제 인용) |
| **W2-03 책무 (W-1, 2026-04-19 완료)** | W-1 미니 테스트 결과: 방법 A (vectorbt sl_stop+sl_trail) vs 방법 B (manual exit_mask) → **방법 B 채택 박제** (방법 A는 entry bar 시점 비율 freeze, 박제 의도 "매 bar 동적 ATR" 위반). evidence: `.evidence/agent-reviews/w2-03-w1-test-review-2026-04-19.md` + `research/_tools/w2_03_w1_test.py` |

### Strategy D — Volatility Breakout (Keltner + Bollinger)

| 항목 | 값 |
|------|-----|
| **상태** | **Retained (학습 가치 보존, 2026-04-22 W3-01 No-Go + 사용자 옵션 C 채택)** |
| **최초 등록** | Week 2 (2026-04-17 결정, W2-02 v4 사전 등록 사용자 승인 2026-04-19 "ㄱㄱ") |
| **파라미터 (확정)** | KC_PERIOD=20, KC_ATR_MULT=1.5, ATR_PERIOD=14, BB_PERIOD=20, BB_SIGMA=2, SL_HARD=0.08 |
| **ta 라이브러리 호출 (W2-02 v4 박제)** | `KeltnerChannel(window=20, window_atr=14, original_version=False, multiplier=1.5)` 모두 명시 필수 (ta default와 다름). `BollingerBands(window=20, window_dev=2.0)` |
| **진입/청산 (W2-02 v4 박제)** | Long entry: strict 동시 상단 돌파 `(close>kc_upper) AND (close.shift(1)<=kc_upper.shift(1)) AND (close>bb_upper) AND (close.shift(1)<=bb_upper.shift(1))`. Exit: strict Keltner mid 하향 돌파 OR Hard SL 8%. Keltner mid = `EMA(close, 20)` (SMA 아님). Long-only |
| **출처** | **Bollinger 1983 (BB 기본값 20, 2σ)** + **ChartSchool/StockCharts 표준 변형 + Raschke 1990s 후속 (Keltner KC_PERIOD=20, KC_ATR_MULT=1.5)**. Chester Keltner (1960) 원 설계는 EMA(typical, 10) ± 1.0 × 10일 daily range로 다름 (ta venv 직접 검증, 2026-04-19, B-2 정정) |
| **독립성 한계** | Strategy C와 동일 (soft contamination) |
| **평가 조건** | W2-03 grid에서 Tier 1 평가. Primary `Sharpe>0.8 AND DSR>0`. Secondary 마킹 (Strategy C와 동일) |
| **Recall 시 의무 (NIT-N2 정정, B-4 cross-document)** | Go 통과 시 **DSR-adjusted 평가 + Week 3 walk-forward 재검증 의무 강제** (Strategy A Recall mechanism과 대칭, W2-03 v2 박제 인용) |
| **W3-1 책무** | ta 향후 버전 업데이트 시 KeltnerChannel signature 재검증 필수 (사이클 진입 시점 venv inspect) |

---

## Deprecated (폐기 로그, 재도입 방지)

### Strategy B — Mean Reversion (MA200 + RSI(4)<25, time stop 5d)

| 항목 | 값 |
|------|-----|
| **상태** | **Deprecated (2026-04-17, W1-06 No-Go 결정 후)** |
| **최초 등록** | Week 1 W1-03 (2026-04-16) |
| **파라미터** | MA_PERIOD=200, RSI_PERIOD=4, RSI_BUY=25, RSI_SELL=50, TIME_STOP_DAYS=5, SL_PCT=0.08 |
| **폐기 사유** |  BTC 일봉 Sharpe 0.14 (Go 기준 0.5 미달), 총수익 +4.94% (5년), PF 1.09 (번 돈 ≈ 잃은 돈), 2021년 -13.16% 손실이 전체 잠식, 민감도 그리드 전체에서도 유사 결과 → **구조적 엣지 부재**. 4h 포팅 시 Sharpe -0.61로 더 악화 |
| **재도입 금지 사유** | 같은 철학(4일 RSI 평균회귀)은 BTC 시장에서 작동하지 않음이 입증됨. 재도입 시 **완전히 다른 평균회귀 로직**으로 재설계 + 새 사전 등록 사이클 필수 |
| **재도입 정책** | 동일 파라미터 조합(MA200+RSI<25+RSI>50+5d)은 **영구 금지**. 유사 로직 재도입 시 외부 감사관 리뷰 의무 |

---

## Recall Mechanism (Retained → Active 재전이 규정)

**Retained**에서 **Active**로 다시 불러올 때:
1. 새 사전 등록 불필요 (원 파라미터 사용)
2. 평가 시 **DSR > 0 필수** (Bailey & López de Prado 2014)
3. **Walk-forward 재검증** 필수 (Week 3+ 또는 재평가 시점 OOS 분할)
4. 재평가 결과 Sharpe 열화 시 다시 Retained로 이동

**Deprecated → Active 전이는 금지**. 재도입 원할 시:
1. 완전히 **새 파라미터 조합** 필요 (기존 대비 최소 30% 변경)
2. 새 사전 등록 문서 + backtest-reviewer + 사용자 승인
3. Deprecated 로그에 "재등장 시도 + 승인 이력" 기록

---

## 변경 이력

| 날짜 | 변경 | 트리거 |
|------|------|--------|
| 2026-04-17 | 파일 신설. Strategy A Retained, Strategy B Deprecated, Strategy C/D Pending 등록 | W1-06 No-Go + W2-01 외부 감사 WARNING-5 |
| 2026-04-19 | **v2: Strategy C/D Pending → Active 전이** (W2-02 v4 사용자 승인 발효). 진입/청산 strict crossover 박제 + ta KeltnerChannel API 호출 명시 (`original_version=False, window_atr=14, multiplier=1.5`) + L48 Keltner 출처 정정 (ChartSchool 표준 변형, Keltner 1960 원 설계 ≠ 우리 박제값). 외부 감사 1차+2차+3차 APPROVED with follow-up | W2-02 v4 사용자 승인 |
| 2026-04-19 | **v3: Strategy C/D Recall 의무 cross-document 박제** (NIT-N2 정정). L41 (Strategy C) + L55 (Strategy D)에 "Go 통과 시 DSR-adjusted + Week 3 walk-forward 의무 강제 (Strategy A Recall과 대칭, W2-03 v2 박제 인용)" 추가. cycle 1 학습 #15 (cross-document) 패턴 해소 | W2-03 sub-plan 2차 외부 감사 NIT-N2 |
| 2026-04-19 | **v4: Strategy C 진입/청산 박제 정확화** (W2-03.1 W-1 미니 테스트 + 사용자 채택 결정). L37 trailing stop 표현 → **manual 매 bar 동적 ATR(14)×3 exit_mask (방법 B)** 명시. 방법 A (vectorbt sl_trail=True) 검증 결과 entry bar 시점 비율 freeze로 박제 의도 위반 발견 → 사용자 명시 채택 결정 ("ㄱㄱ"). evidence: `.evidence/agent-reviews/w2-03-w1-test-review-2026-04-19.md` | W2-03.1 W-1 미니 테스트 결과 |
| 2026-04-20 | **v5: Strategy A Recall 발동 (Retained → Active)**. W2-03 v8 Go 결정 (Option C, V_empirical 채택) 반영: BTC_A Sharpe 1.0353 DSR_z +23.22 / ETH_A Sharpe 1.1445 DSR_z +29.37 → Tier 1 양 페어 `Sharpe>0.8 AND DSR>0` 충족 → L27 재진입 조건 충족. 상태 Retained → **Active** 전이. W2-03 v8 성적 행 추가. Recall 시 의무 (DSR 평가 완료 + Week 3 walk-forward 재검증 의무) 박제 강화. Week 3 실패 시 소급 절차 행 추가 (decisions-final.md "W2-03 Go 결정" cross-reference) | W2-03 v8 Go 결정 사용자 명시 승인 |
| 2026-04-22 | **v6: Strategy A Active → Retained 역방향 복귀 + Strategy C/D Active/Registered → Retained (학습 가치 보존)**. W3-01 No-Go 확정 + 사용자 옵션 C 명시 채택 "3" (프레임 C = A+B 둘 다 공식 인정 + Stage 1 학습 모드 전환). Strategy A Recall mechanism 자동 해제 (W2-03 Go → W3-01 No-Go로 정당성 상실). Strategy C 전멸 (BTC_C 5/5 fold N/A, 실전 운용 부적합). Strategy D 경계선 (BTC_D 3/5, ETH_D 2/5) 최고 근접이나 5/5 미달. **Deprecated 이동 X** (학습 모드이므로 전부 Retained). Deprecated 승격은 v3 Stage 1 재시작 시점 판단. Stage 1 킬 카운터 +2 소급 = 총 +3 → Stage 1 킬 조건 충족. decisions-final.md "W3-01 No-Go 결정 + 프레임 C 학습 모드 전환" 섹션 + stage1-execution-plan.md + handover 전파 | W3-01 No-Go + 사용자 옵션 C 명시 채택 |

---

**관련 문서**:
- `docs/decisions-final.md` "Stage 1 실행 기록" (Week 1 No-Go + Week 2 재범위 + 한계 서약)
- `docs/stage1-subplans/w2-01-data-expansion.md` (SubTask W2-01.3에서 이 파일 물리화)
- `docs/stage1-subplans/w1-06-week1-report.md` (Strategy A/B Week 1 평가 결과)
- `research/outputs/week1_summary.json` (수치 원본)
