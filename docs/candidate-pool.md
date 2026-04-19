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
| **상태** | Retained (Week 1 Conditional Pass, 2025 regime decay) |
| **최초 등록** | Week 1 W1-02 (2026-04-15) |
| **파라미터** | MA_PERIOD=200, DONCHIAN_HIGH=20, DONCHIAN_LOW=10, VOL_AVG_PERIOD=20, VOL_MULT=1.5, SL_PCT=0.08 |
| **출처** | Padysak/Vojtko 영감 (Padysak 2020 스타일 복제 아닌 변형) |
| **W1 성적** | BTC 일봉 Sharpe 1.0353, 총수익 +171.76%, MDD -22.45%, 14 trades |
| **W1 경고** | 2024년 단년 집중 (68.3% 기여), 2024-12-17 이후 481일 Sharpe -1.14 (2승 3패) |
| **재진입 조건** | W2-03 grid에서 Tier 1 (BTC+ETH) 중 하나 이상 `Sharpe > 0.8 AND DSR > 0` |
| **Recall 시 의무** | DSR > 0 필수 평가. Week 3 walk-forward 재검증 필수 |

### Strategy C — Slow Momentum (MA50/200 crossover + ATR trail)

| 항목 | 값 |
|------|-----|
| **상태** | **Active/Registered (W2-02 v4 사용자 승인 발효, 2026-04-19)** |
| **최초 등록** | Week 2 (2026-04-17 결정, W2-02 v4 사전 등록 사용자 승인 2026-04-19 "ㄱㄱ") |
| **파라미터 (확정)** | FAST_MA=50, SLOW_MA=200, ATR_PERIOD=14, ATR_MULT=3 (trailing stop) |
| **진입/청산 (W2-02 v4 박제)** | Long entry: strict golden cross `(MA50>MA200) AND (MA50.shift(1)<=MA200.shift(1))`. Hard exit: strict death cross OR ATR(14)×3 trailing stop. Long-only. 청산 후 동일 추세 내 재진입 X |
| **출처** | Faber 2007 "A Quantitative Approach to Tactical Asset Allocation" (MA crossover 타이밍) + Wilder 1978 (ATR) |
| **독립성 한계** | W1에서 BTC 5년 데이터를 이미 본 이후 선택. 문헌 **기본값** 사용이나 완전 OOS 독립 주장 불가 (soft contamination). `decisions-final.md` "Week 2 한계 및 독립성 서약" 참조 |
| **평가 조건** | W2-03 grid에서 Tier 1 평가. Primary `Sharpe>0.8 AND DSR>0`. Secondary 마킹: 동일 전략이 Tier 1+2 3+ 페어에서 `Sharpe>0.5` → ensemble 후보 |
| **W2-03 책무 (W-1)** | vectorbt sl_stop Series + sl_trail=True 미니 테스트 동작 검증 강제 (backtest-reviewer) |

### Strategy D — Volatility Breakout (Keltner + Bollinger)

| 항목 | 값 |
|------|-----|
| **상태** | **Active/Registered (W2-02 v4 사용자 승인 발효, 2026-04-19)** |
| **최초 등록** | Week 2 (2026-04-17 결정, W2-02 v4 사전 등록 사용자 승인 2026-04-19 "ㄱㄱ") |
| **파라미터 (확정)** | KC_PERIOD=20, KC_ATR_MULT=1.5, ATR_PERIOD=14, BB_PERIOD=20, BB_SIGMA=2, SL_HARD=0.08 |
| **ta 라이브러리 호출 (W2-02 v4 박제)** | `KeltnerChannel(window=20, window_atr=14, original_version=False, multiplier=1.5)` 모두 명시 필수 (ta default와 다름). `BollingerBands(window=20, window_dev=2.0)` |
| **진입/청산 (W2-02 v4 박제)** | Long entry: strict 동시 상단 돌파 `(close>kc_upper) AND (close.shift(1)<=kc_upper.shift(1)) AND (close>bb_upper) AND (close.shift(1)<=bb_upper.shift(1))`. Exit: strict Keltner mid 하향 돌파 OR Hard SL 8%. Keltner mid = `EMA(close, 20)` (SMA 아님). Long-only |
| **출처** | **Bollinger 1983 (BB 기본값 20, 2σ)** + **ChartSchool/StockCharts 표준 변형 + Raschke 1990s 후속 (Keltner KC_PERIOD=20, KC_ATR_MULT=1.5)**. Chester Keltner (1960) 원 설계는 EMA(typical, 10) ± 1.0 × 10일 daily range로 다름 (ta venv 직접 검증, 2026-04-19, B-2 정정) |
| **독립성 한계** | Strategy C와 동일 (soft contamination) |
| **평가 조건** | W2-03 grid에서 Tier 1 평가. Primary `Sharpe>0.8 AND DSR>0`. Secondary 마킹 (Strategy C와 동일) |
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

---

**관련 문서**:
- `docs/decisions-final.md` "Stage 1 실행 기록" (Week 1 No-Go + Week 2 재범위 + 한계 서약)
- `docs/stage1-subplans/w2-01-data-expansion.md` (SubTask W2-01.3에서 이 파일 물리화)
- `docs/stage1-subplans/w1-06-week1-report.md` (Strategy A/B Week 1 평가 결과)
- `research/outputs/week1_summary.json` (수치 원본)
