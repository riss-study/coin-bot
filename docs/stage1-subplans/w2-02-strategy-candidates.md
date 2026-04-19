# Task W2-02 — 새 전략 후보 사전 등록 (Candidate C, D Pending → Active 전이)

**상태**: **v6** (NIT 7번 cross-document 정정, W-1 결과 박제 추가, 2026-04-19). **변경 금지 서약 발효 유지** (의미 변경 X, cross-reference 강화만). Candidate C/D 파라미터 + 진입/청산 + 출처 박제 변경 금지. 변경 시 새 사전 등록 사이클 + 새 외부 감사 + 새 승인 강제.

## 변경 이력

| 버전 | 날짜 | 변경 | 트리거 |
|------|------|------|--------|
| v1 | 2026-04-19 | 첫 작성 + 자가 검증 WARNING 3건 정정 (ATR trailing 가이드 / Secondary 마킹 / A vs C 차별화) | sub-plan 신설 |
| v2 | 2026-04-19 | 1차 외부 감사 BLOCKING 4건 정정 (B-1 candidate-pool.md 사실 오류 / B-2 KeltnerChannel 출처 / B-3 Candidate C entry / B-4 Candidate D Exit) | 1차 외부 감사 |
| v3 | 2026-04-19 | 2차 외부 감사 NEW BLOCKING 2건 정정 (NEW-B-1 "신설" 10개 위치 잔존 / NEW-B-2 vectorbt 코드 블록 ta KeltnerChannel 미사용) | 2차 외부 감사 |
| **v4** | 2026-04-19 | 3차 외부 감사 APPROVED with follow-up + **옵션 C 정정 5건** (W-1 ATR trailing 미니 테스트 박제 / W-4 Secondary 정확 인용 / W3-1 ta 버전 재검증 / N3-1 Pending → Active 통일 / N3-2 변수명 박제) | 3차 외부 감사 + 사용자 결정 |
| **v5** | **2026-04-19** | **사용자 최종 승인 발효** ("ㄱㄱ"). 변경 금지 서약 발효 + Strategy C/D candidate-pool.md Pending → Active 전이 동시 적용 (W2-02.0~.4 모두 완료) | **사용자 명시 승인** |
| **v6** | **2026-04-19** | **NIT 7번 cross-document 정정** (handover #15 + #20 패턴 차단). L163 W-1 추가 박제에 W-1 미니 테스트 결과 (방법 B 채택) 박제 추가. cross-reference 강화 (candidate-pool.md v4 L37 + W2-03 sub-plan v5 W2-03.1). 의미 변경 X = 변경 금지 서약 위반 X | W2-03.1 결과 cross-document 정정 |

## 메인 Task 메타데이터

| 항목 | 값 |
|------|-----|
| **메인 Task ID** | W2-02 |
| **Feature ID** | STR-NEW-001 |
| **주차** | Week 2 (Day 3-4) |
| **기간** | 2일 (SubTask 순효용 ~1.7일 + 외부 감사 + 사용자 승인 ~0.3일 buffer) |
| **스토리 포인트** | 5 |
| **작업자** | Solo + 외부 감사관 + 사용자 승인 |
| **우선순위** | P0 (W2-03 차단) |
| **상태** | Pending |
| **Can Parallel** | NO (W2-03 의존) |
| **Blocks** | W2-03, W3-* |
| **Blocked By** | W2-01 cycle 2 전체 완료 (2026-04-19) |

## 배경

### Week 1 → Week 2 흐름

- Week 1: Strategy A (Conditional Pass, Sharpe 1.04 2024 집중) / Strategy B (No-Go, Sharpe 0.14 Deprecated). 최근 481일 Strategy A Sharpe -1.14 (2승 3패)
- Week 1 W1-06 No-Go 결정 → Week 2 재범위 (전략 후보 재탐색 + 메이저 알트 확장)
- Week 2 W2-01 cycle 1 → cycle 2 (Tier 2 리스트 박제 빗나감, Fallback (ii) 발동)
- W2-01 cycle 2 완료 (2026-04-19): Tier 2 = [XRP, SOL, TRX, DOGE] 확정 + 10 dataset Parquet freeze
- **본 Task W2-02**: Week 2 두 번째 단계, 새 전략 후보 (Candidate C, D) 사전 등록 + Strategy A 후보 풀 물리화

### 박제 출처

- `docs/decisions-final.md` "Week 2 한계 및 독립성 서약" (W2-01 외부 감사 후 추가, 2026-04-17)
  - **Strategy C/D 파라미터 출처 명시** (L535-541)
  - **독립성 한계 서약 (Soft Contamination 인정)** (L543-547)
  - **Strategy A 후보 풀 물리적 정의** (L549-551)
- `docs/decisions-final.md` "Week 2 재범위 결정" (L495-528)
- `docs/pair-selection-criteria-week2-cycle2.md` v5 (Tier 2 확정 + Common-window 박제)

### 핵심 원칙

- **사전 지정 파라미터 (pre-registration)**: Candidate C, D 파라미터 + 진입/청산 조건 데이터 적용 전 박제. 결과 보고 튜닝 금지
- **문헌 기본값 채택 (튜닝 X)**: 파라미터는 원 저자 기본값. BTC-specific 튜닝 X
- **Soft contamination 정직 인정**: Week 1 결과 본 상태에서 전략 철학 선택 = 완전 독립 X
- **Strategy A 후보 풀 물리화 = 이미 박제됨** (`candidate-pool.md` 2026-04-17 신설, 커밋 `99b281d`). W2-02는 Strategy C/D Pending → Active 전이 책무
- **Multiple testing 한계 명시**: 6 primary 셀 family-wise 오류 여지 → DSR + Week 3 walk-forward 최종 검증

## 개요

새 전략 후보 2개 (C: Slow Momentum, D: Volatility Breakout) 사전 등록 + Strategy A 후보 풀 물리화. Candidate C/D는 문헌 기본값 그대로 채택. soft contamination 인정. 외부 감사 + 사용자 승인 후 freeze. W2-03 grid 입력 (Tier 1 × {A,C,D} = 6 primary 셀).

## 현재 진행 상태

| SubTask | 상태 | 메모 |
|---------|------|------|
| W2-02.0 | Pending | candidate-pool.md Strategy C/D Pending → Active 전이 (B-1 정정) |
| W2-02.1 | Pending | Candidate C (Slow Momentum) 사전 등록 |
| W2-02.2 | Pending | Candidate D (Volatility Breakout) 사전 등록 |
| W2-02.3 | Pending | 외부 감사 (적대적, 사전 등록 정합성) |
| W2-02.4 | Pending | 사용자 승인 + freeze |

## SubTask 목록

### SubTask W2-02.0: candidate-pool.md Strategy C/D Pending → Active 전이 (B-1 정정)

**작업자**: Solo
**예상 소요**: 0.2일
**박제 출처**: `docs/decisions-final.md` L549-551 ("Strategy A 후보 풀 물리적 정의")

**B-1 외부 감사 사실 오류 정정 (2026-04-19)**: 본 sub-plan v1은 "candidate-pool.md 신설"이라 박제했으나 **사실 오류** — `docs/candidate-pool.md`는 이미 신설 완료 (L88 "2026-04-17 파일 신설", 커밋 `99b281d`, W2-01 외부 감사 대응 시점). Strategy A Retained / Strategy B Deprecated / Strategy C/D Pending 모두 등록 + Recall Mechanism (L69-80) 박제 완료.

본 W2-02.0 책무는 **"Pending → Active 전이"**:

- [ ] **candidate-pool.md 본문 직접 확인** (사실 검증, 추가 누락 없는지)
- [ ] **Strategy C** (현재 L30-39 Pending) → **Active/Registered 전이**:
  - W2-02.1 결과 박제 (entry/exit 신호 시점 명시 + ATR trailing stop 구현 가이드)
  - 출처/파라미터/평가 조건 그대로 (이미 박제됨)
- [ ] **Strategy D** (현재 L41-50 Pending) → **Active/Registered 전이**:
  - W2-02.2 결과 박제 (Keltner 출처 정정 + 신호 시점 명시 + ta API 정확 인용)
  - **B-2 정정 cross-document 전파**: L48 "Keltner 1960 (Keltner Channel 원 설계값)" → "Chester Keltner (1960) 원 설계 = EMA(typical price, 10) ± 1.0 × 10일 daily range. 본 사이클 KC_ATR_MULT=1.5는 ChartSchool/StockCharts 표준 변형 + Raschke 1990s 후속"
- [ ] **Recall Mechanism (L69-80) 박제 강화**: 변경 안 함 (이미 박제됨), 단 W2-03 grid에서 강제 적용 명시 책임 추가
- [ ] **변경 이력에 v2 행 추가** (2026-04-19, "Strategy C/D Pending → Active 전이 + B-2 Keltner 출처 정정")

### SubTask W2-02.1: Candidate C — Slow Momentum 사전 등록

**작업자**: Solo
**예상 소요**: 0.5일
**박제 출처**: `docs/decisions-final.md` L535-538

#### 전략 철학

장기 추세 추종 + 변동성 기반 trailing stop. Bull regime 편중 가능성 (Week 1 A regime 편중 학습 → soft contamination 인정).

#### 파라미터 사전 박제 (튜닝 X)

| 파라미터 | 값 | 문헌 출처 |
|---------|-----|----------|
| MA short | 50 | Faber (2007) "A Quantitative Approach to Tactical Asset Allocation" |
| MA long | 200 | Faber (2007) 동일. Strategy A와 동일 윈도우이지만 50/200 crossover 신호 차별화 |
| ATR window | 14 | Wilder (1978) "New Concepts in Technical Trading Systems" 창시자 기본값 |
| ATR multiplier | 3.0 | Wilder 원 제안 + Chandelier Exit 후속 표준 (2-3 범위) |

#### 진입/청산 조건

- **Long entry (B-3 명시 박제)**: 골든 크로스 발생한 **그 1 bar에만** entry 신호 = `(MA50 > MA200) AND (MA50.shift(1) <= MA200.shift(1))`. 동등 (`==`) 케이스는 false → 명확한 strict crossover만 trigger. 청산 후 동일 추세 내 재진입 X (다음 골든 크로스까지 대기)
- **Trailing stop**: 진입 후 close - ATR(14) × 3 (long-side trailing high 기준, vectorbt sl_stop=ATR_MULT*ATR/close + sl_trail=True)
- **Hard exit (B-3 명시 박제)**: 데스 크로스 발생한 **그 1 bar에만** exit 신호 = `(MA50 < MA200) AND (MA50.shift(1) >= MA200.shift(1))`. ATR trailing stop과 OR 결합 (둘 중 하나 발동 시 exit)
- **포지션 사이즈**: 100% (cash_sharing 단일 진입, Strategy A와 동일 패턴), **long-only (NIT-2 해소)**
- **수수료**: 0.1% 왕복 (W1-01 박제)
- **슬리피지**: 0.05% (W1-01 박제)

#### Strategy A vs Candidate C 신호 차별화 (WARNING-C 해소)

| 항목 | Strategy A | Candidate C |
|------|-----------|-------------|
| 진입 신호 | 가격 > MA200 (Bull regime 필터) AND Donchian 20 상향 돌파 + Vol > 1.5x | MA50 > MA200 AND MA50/MA200 골든 크로스 |
| 청산 신호 | Donchian 10 하향 돌파 OR SL 8% | 데스 크로스 OR ATR(14)×3 trailing stop |
| 신호 시점 | Donchian 채널 돌파 시점 (단기 모멘텀) | 이동평균 crossover 시점 (장기 추세 전환) |
| 신호 빈도 | 상대적으로 잦음 | 상대적으로 드뭄 (장기 추세 전환만) |

→ A는 MA200을 **regime 필터**로만 사용 (가격이 MA200 위에 있는지). C는 MA50/MA200의 **상대적 위치 변화** 자체를 trigger. 신호 발생 시점과 메커니즘 다름. W2-03 grid에서 cross-correlation 점검 권고.

#### vectorbt 0.28.5 구현 가이드 (WARNING-A 해소)

```python
# 사전 박제, 튜닝 금지
MA_SHORT = 50
MA_LONG = 200
ATR_WINDOW = 14
ATR_MULT = 3.0

from ta.volatility import AverageTrueRange

ma_short = close.rolling(MA_SHORT).mean()
ma_long = close.rolling(MA_LONG).mean()
atr = AverageTrueRange(high, low, close, window=ATR_WINDOW).average_true_range()

# Crossover entry (전일까지 ma_short ≤ ma_long, 오늘 ma_short > ma_long)
golden_cross = (ma_short > ma_long) & (ma_short.shift(1) <= ma_long.shift(1))
death_cross = (ma_short < ma_long) & (ma_short.shift(1) >= ma_long.shift(1))

# ATR trailing stop 구현 (vectorbt sl_stop은 fraction 비율만 받음 → ATR 기반은 entry 시점 비율로 변환)
# 방법 A (vectorbt sl_stop + sl_trail=True): entry bar의 (ATR_MULT × ATR) / close 비율을 sl_stop에 입력
#         단 sl_trail=True는 entry 이후 highest close 기준으로 비율 적용. ATR이 entry 시점 고정값.
# 방법 B (manual trailing 계산): 매 bar마다 highest_close - ATR_MULT × ATR(14) 계산, exit_mask에 반영.
#         더 정확하지만 vectorbt boolean exit과 결합 필요.

# W2-03에서 방법 A vs B 정확 구현 + 외부 감사관 검증 (cycle 2 W2-01.2 NIT2-3 패턴 적용)

# 예시 (방법 A):
sl_stop_ratio = (ATR_MULT * atr) / close  # entry bar 기준 비율, vectorbt가 entry 시점 값 사용

pf = vbt.Portfolio.from_signals(
    close=close,
    entries=golden_cross,
    exits=death_cross,
    sl_stop=sl_stop_ratio,  # Series 입력 가능 (entry bar 시점 값 채택)
    sl_trail=True,           # trailing high 기준 적용
    init_cash=1_000_000, fees=0.0005, slippage=0.0005, freq='1D',
)
```

**약점 인정 (외부 감사 권고)**: ATR 기반 trailing stop은 vectorbt 0.28.5 Boolean exit mask로 자연스럽게 표현 어려움. W2-03 구현 시 방법 A/B 비교 + backtest-reviewer 검증 후 채택 결정. 현 단계는 사전 등록 의도(ATR×3 trailing) 박제로 충분.

**W-1 추가 박제 (W2-03 책무, 2026-04-19 완료)**: vectorbt sl_stop Series 입력 + `sl_trail=True` 결합 동작은 미니 테스트로 동작 정확성 검증 필수 (synthetic trend data → entry → trailing high 추적 → exit 시점 비교). backtest-reviewer 호출 시점에 강제. 만약 동작 부정확 발견 시 방법 B (manual trailing high - ATR_MULT × ATR(14) exit_mask) 채택.

**W-1 결과 박제 (2026-04-19 W2-03.1 완료, NIT 7번 cross-document 정정)**: 미니 테스트 결과 방법 A return 23.51% vs 방법 B 26.52% (차이 3.01%p > 임계값 0.5%p). vectorbt `sl_trail=True` 동작 분석 결과 **entry bar 시점 비율 freeze**로 박제 의도 ("매 bar 동적 ATR trailing") 위반 확정 → **방법 B 사용자 명시 채택 박제** (2026-04-19 "ㄱㄱ"). evidence: `.evidence/agent-reviews/w2-03-w1-test-review-2026-04-19.md` + `research/_tools/w2_03_w1_test.py` + `research/outputs/w2_03_w1_test.json`. cross-reference: `docs/candidate-pool.md` v4 L37 + `docs/stage1-subplans/w2-03-insample-grid.md` v5 W2-03.1.

#### Soft contamination 인정 박제

- Week 1 W1-06.1b regime 편중 결과를 본 후 "momentum + ATR trailing" 철학 선택
- 파라미터(50/200/14/3)는 문헌 기본값 그대로 (튜닝 X)
- 그러나 철학 자체 선택은 W1 영향 받음
- 최종 평가는 Week 3 walk-forward (Week 2 In-sample은 예비 판단)

#### Acceptance Criteria

- [ ] Candidate C 진입/청산 조건 + 파라미터 박제 (`candidate-pool.md` Pending → Active 전이)
- [ ] 문헌 출처 정확 인용 (Faber 2007, Wilder 1978)
- [ ] Soft contamination 인정 명시
- [ ] vectorbt 0.28.5 구현 가이드 박제

### SubTask W2-02.2: Candidate D — Volatility Breakout 사전 등록

**작업자**: Solo
**예상 소요**: 0.5일
**박제 출처**: `docs/decisions-final.md` L539-541

#### 전략 철학

변동성 채널 동시 돌파 → 추세 가속 진입. Bull/Bear 양방 가능 (단 본 사이클은 long-only). Week 1 변동성 가속 결과 영향.

#### 파라미터 사전 박제 (B-2 사실 오류 정정, ta venv 직접 검증)

| 파라미터 | 값 | 정확한 출처 |
|---------|-----|------------|
| Keltner window (mid 계산) | 20 | **표준 변형 (ChartSchool/StockCharts)**. Chester Keltner (1960) 원 설계는 EMA(typical, 10) ± 1.0 × 10일 daily range로 다름 |
| Keltner ATR multiplier | 1.5 | **ChartSchool/StockCharts 표준 변형 + Raschke 1990s 후속**. Keltner 1960 원 설계 multiplier 1.0과 다름 |
| ATR window (Keltner 내부) | 14 | Wilder (1978) ATR 창시자 기본값 |
| Bollinger window | 20 | Bollinger (1983) |
| Bollinger σ multiplier | 2.0 | Bollinger (1983) 기본값 |

**ta 라이브러리 직접 사용 (B-2 정확 호출, 추측 금지)**:

```python
from ta.volatility import KeltnerChannel, BollingerBands

kc = KeltnerChannel(
    high=high, low=low, close=close,
    window=20,           # 박제 KC_PERIOD
    window_atr=14,       # 박제 ATR window (ta default 10과 다름, 명시 필수)
    original_version=False,  # multiplier × ATR 사용 (ta default True는 multiplier 무시)
    multiplier=1.5,      # 박제 KC_ATR_MULT (ta default 2와 다름, 명시 필수)
)
keltner_upper = kc.keltner_channel_hband()
keltner_mid = kc.keltner_channel_mband()  # original_version=False 시 EMA(close, 20)

bb = BollingerBands(close=close, window=20, window_dev=2.0)
bb_upper = bb.bollinger_hband()
```

**ta API 검증** (감사관 venv 직접 확인 + 본 sub-plan 검증):
- `KeltnerChannel(window=20, window_atr=10, original_version=True, multiplier=2)` = ta default
- `original_version=True` 시 multiplier 무시 + mid + range 사용 (Keltner 1960 변형)
- `original_version=False` 시 multiplier × ATR(window_atr) 적용 + EMA(close, window) mid

**박제 충돌 위험 alarm**: `window_atr` + `multiplier` + `original_version` 모두 명시 안 하면 ta default 적용 → 박제값과 다른 결과. W2-03 구현 시 강제 명시 필수.

**W3-1 추가 박제 (ta 버전 재검증 책무)**: 본 박제는 ta 라이브러리 0.x 버전 기준 검증. ta 향후 버전 업데이트 시 KeltnerChannel signature/default/내부 계산 방식 변경 가능. **사이클 진입 시점에 venv ta 버전 재확인 + signature 직접 검증 필수** (`source research/.venv/bin/activate && python -c "from ta.volatility import KeltnerChannel; import inspect; print(inspect.signature(KeltnerChannel.__init__))"`). 변경 발견 시 본 박제 정정 + 새 외부 감사 사이클.

#### 진입/청산 조건

- **Long entry (B-4 명시 박제)**: 당일 close가 Keltner Upper Band AND Bollinger Upper Band를 **둘 다 strict crossover**:
  - `(close > kc_upper) AND (close.shift(1) <= kc_upper.shift(1)) AND (close > bb_upper) AND (close.shift(1) <= bb_upper.shift(1))`
  - 두 band 동시 첫 돌파한 1 bar에만 entry 신호. 동등 (`==`) 케이스는 false
- **Exit (B-4 명시 박제)**: **두 조건 OR**:
  - (a) Keltner Middle Band 하향 strict crossover: `(close < kc_mid) AND (close.shift(1) >= kc_mid.shift(1))`
  - (b) Hard SL 8% (vectorbt sl_stop=0.08, sl_trail=False, BTC 변동성 안전판)
- vectorbt entry/exit 우선순위: 같은 bar에 entry + sl_stop 발동 시 exit 우선 (vectorbt 기본 동작), entry + exit_mask 동시 발동 시 entry 우선 (single bar trip 차단)
- **포지션 사이즈**: 100% **long-only (NIT-2 해소)**
- **수수료/슬리피지**: 동일 (0.1% 왕복 + 0.05%)
- **Keltner mid 정의 명확화 (B-4)**: `keltner_mid = EMA(close, 20)` (ta `original_version=False` 기준). SMA 아님

#### vectorbt 0.28.5 구현 가이드

**변수명 박제 (N3-2 명시)**: `KELTNER_WINDOW`, `KELTNER_ATR_MULT`, `BOLLINGER_WINDOW`, `BOLLINGER_SIGMA`, `ATR_WINDOW`, `SL_HARD` — 모두 사전 박제 상수. W2-03 구현 시 동일 변수명 강제 사용.

```python
KELTNER_WINDOW = 20
KELTNER_ATR_MULT = 1.5
BOLLINGER_WINDOW = 20
BOLLINGER_SIGMA = 2.0
ATR_WINDOW = 14
SL_HARD = 0.08

from ta.volatility import BollingerBands, KeltnerChannel

# NEW-B-2 정정: ta KeltnerChannel 직접 사용 (SMA + 직접 계산 X)
# original_version=False + window_atr=14 + multiplier=1.5 모두 명시 필수 (ta default와 다름)
kc = KeltnerChannel(
    high=high, low=low, close=close,
    window=KELTNER_WINDOW,           # 박제 20
    window_atr=ATR_WINDOW,           # 박제 14 (ta default 10)
    original_version=False,          # multiplier × ATR 사용 (ta default True 시 multiplier 무시)
    multiplier=KELTNER_ATR_MULT,     # 박제 1.5 (ta default 2)
)
keltner_upper = kc.keltner_channel_hband()
keltner_mid = kc.keltner_channel_mband()  # original_version=False 시 EMA(close, 20)

bb = BollingerBands(close=close, window=BOLLINGER_WINDOW, window_dev=BOLLINGER_SIGMA)
bb_upper = bb.bollinger_hband()

# 동시 돌파
both_break = (
    (close > keltner_upper) & (close.shift(1) <= keltner_upper.shift(1))
) & (
    (close > bb_upper) & (close.shift(1) <= bb_upper.shift(1))
)

# Exit: Keltner mid 하향
mid_exit = (close < keltner_mid) & (close.shift(1) >= keltner_mid.shift(1))

pf = vbt.Portfolio.from_signals(
    close=close,
    entries=both_break,
    exits=mid_exit,
    sl_stop=SL_HARD, sl_trail=False,
    init_cash=1_000_000, fees=0.0005, slippage=0.0005, freq='1D',
)
```

#### Soft contamination 인정 박제 (C와 동일 패턴)

#### Acceptance Criteria

- [ ] Candidate D 진입/청산 조건 + 파라미터 박제 (`candidate-pool.md`)
- [ ] 문헌 출처 정확 인용 (Keltner 1960, Bollinger 1983, Wilder 1978)
- [ ] Soft contamination 인정 명시
- [ ] vectorbt 0.28.5 구현 가이드 박제 (`ta` 라이브러리 사용)

### SubTask W2-02.3: 외부 감사 (적대적, 사전 등록 정합성)

**작업자**: 외부 감사관 (`general-purpose` 에이전트)
**예상 소요**: 0.3일

- [ ] `general-purpose` 에이전트에 적대적 외부 감사관 페르소나 위임
- [ ] 검증 대상: 본 sub-plan W2-02.0~.2 박제 (Candidate C, D 사전 등록 + candidate-pool.md)
- [ ] 검증 기준:
  - 사전 지정 파라미터 명시성 (튜닝 여지 없는지)
  - 문헌 출처 정확성 (Faber/Wilder/Keltner/Bollinger)
  - Soft contamination 인정 정직성
  - Multiple testing 한계 박제
  - vectorbt 0.28.5 API 정확성 (research/CLAUDE.md 검증 패턴)
  - cycle 1 학습 패턴 재발 X (리스트 박제 추정 빗나감, snapshot 모호 등)
  - 평가 정책 (DSR-adjusted) 박제
- [ ] 결과: APPROVED / APPROVED with follow-up / CHANGES REQUIRED
- [ ] CHANGES REQUIRED 시 정정 → 재감사 (cycle 1 사례 = 3회 권장, BLOCKING 0 + WARNING/NIT만 잔존 시 follow-up 트래킹으로 진행 가능)
- [ ] evidence: `.evidence/agent-reviews/w2-02-strategy-candidates-review.md`

### SubTask W2-02.4: 사용자 승인 + freeze

**작업자**: Solo + 사용자
**예상 소요**: 0.2일

- [ ] 외부 감사 APPROVED 후 사용자에게 종합 보고
  - Candidate C, D 파라미터 + 문헌 출처 + soft contamination 인정
  - candidate-pool.md Strategy C/D Pending → Active 전이 + Strategy A Recall 강화
  - 외부 감사 trace + 자가 검증 결과
- [ ] 사용자 명시적 승인 (예: "ㄱㄱ" 또는 명시적 OK)
- [ ] **변경 금지 서약 발효**: 사용자 승인 시점부터 W2 실행 종료까지 Candidate C, D 파라미터 변경 금지
  - 변경 시: 새 사전 등록 사이클 + 새 외부 감사 + 새 승인 강제
- [ ] sub-plan + execution-plan + handover 박제 갱신
- [ ] 커밋: `feat(plan): STR-NEW-001 W2-02 Candidate C, D Pending → Active 전이 + Keltner 출처 정정`

## 인수 완료 조건 (Acceptance Criteria)

- [ ] `docs/candidate-pool.md` Strategy C/D Pending → Active 전이 (B-1 정정, candidate-pool.md 자체는 2026-04-17 신설 완료)
- [ ] Candidate C (Slow Momentum) 파라미터 + 진입/청산 + 출처 + soft contamination 박제
- [ ] Candidate D (Volatility Breakout) 파라미터 + 진입/청산 + 출처 + soft contamination 박제
- [ ] **Strategy A vs Candidate C 신호 차별화 명시 박제** (WARNING-C 해소)
- [ ] vectorbt 0.28.5 구현 가이드 박제 (검증된 API만 사용)
- [ ] **ATR trailing stop 구현 가이드 (방법 A/B 비교 + W2-03 정확 구현 권고) 박제** (WARNING-A 해소)
- [ ] **Go 기준 박제 인용 (cycle 2 v5 Fallback 정책 + decisions-final.md L517-521)**: Primary `Sharpe > 0.8 AND DSR > 0` + **Secondary 마킹 (Go 기여 X)**: 동일 전략이 Tier 1+2 3+ 페어에서 `Sharpe > 0.5` → ensemble 후보 (W-4 정확 인용)
- [ ] DSR-adjusted 평가 정책 박제 (Strategy A 재등장 + Candidate C/D 동시 적용)
- [ ] Multiple testing 한계 명시 (6 primary 셀 family-wise 오류 + DSR 부분 완화 + Week 3 walk-forward 최종)
- [ ] 외부 감사 APPROVED (또는 APPROVED with follow-up + 사용자 결정)
- [ ] 사용자 명시적 승인 → 변경 금지 서약 발효
- [ ] candidate-pool.md + sub-plan + handover 갱신 + 커밋

## 의존성 매트릭스

| From | To | 관계 |
|------|-----|------|
| W2-01 cycle 2 완료 | W2-02 | 페어 + Common-window 확정 후 전략 사전 등록 |
| W2-02 | W2-03 | Candidate {A, C, D} 사전 등록 결과가 W2-03 grid 입력 |
| W2-02 | W3-* | walk-forward 평가 시 동일 파라미터 사용 |

## 리스크 및 완화 전략

| 리스크 | 영향 | 완화 |
|--------|------|------|
| Candidate C/D 파라미터 BTC-specific 튜닝 유혹 | **High** | 문헌 기본값 그대로 채택 명시 + 외부 감사 검증 + 변경 금지 서약 |
| Soft contamination (Week 1 결과 본 상태에서 전략 선택) | **High** | 정직 인정 + Week 3 walk-forward 최종 평가 + 결과는 예비 판단으로만 해석 |
| Multiple testing 6 primary 셀 family-wise 오류 | **High** | DSR로 부분 완화 + Week 3 walk-forward 최종 검증. Tier 2 12셀은 exploratory 격리 |
| Candidate C와 Strategy A 신호 중첩 (둘 다 MA crossover 기반) | Medium | C는 MA50/200, A는 MA200 + Donchian 20/10. 신호 차별화. 단 W2-03에서 cross-corr 점검 권고 |
| Candidate D 동시 돌파 신호 빈도 매우 낮을 가능성 | Medium | Tier 1 + Tier 2 5년 데이터 = 충분한 신호 수 기대. W2-03 결과로 검증 |
| `ta` 라이브러리 KeltnerChannel API 검증 안 됨 | Medium | W2-02.3 외부 감사에서 `ta.volatility.KeltnerChannel` API 직접 검증 + research/CLAUDE.md 갱신 |
| Strategy A 재등장 시 DSR-adjusted 평가 누락 | Medium | candidate-pool.md "Recall mechanism" 박제. W2-03 grid에서 명시적 적용 |

## 산출물 (Artifacts)

### 문서
- `docs/candidate-pool.md` (기존 파일 갱신, Strategy C/D Pending → Active 전이 + L48 Keltner 출처 정정)
- `docs/stage1-subplans/w2-02-strategy-candidates.md` (이 sub-plan)

### 검증
- `.evidence/agent-reviews/w2-02-strategy-candidates-review.md` (외부 감사 trace)

### 박제 갱신
- `docs/decisions-final.md` (필요 시 Candidate C/D 박제 추가 또는 인용 강화)
- `docs/stage1-execution-plan.md` (W2-02 상태)
- `.claude/handover-2026-04-17.md` (vN+1)

### 테스트 시나리오
- **Happy**: Candidate C, D 사전 등록 + 외부 감사 APPROVED + 사용자 승인 → W2-03 진입
- **Denial 1**: 외부 감사 CHANGES REQUIRED (BLOCKING 발견) → 정정 + 재감사 (cycle 1 패턴 3회 권장)
- **Denial 2**: 사용자가 파라미터 변경 요구 → 사용자 의사 인정 + 새 사전 등록 사이클로만 가능 명시 (cycle 2 학습 = 변경 금지 서약 강조)
- **Edge**: Candidate D 동시 돌파 신호 0건 (Tier 1 + Tier 2 5년) → W2-03 grid에서 신호 빈도 보고 + Fallback 없음 (사전 지정 결과 그대로)

## Commit (예상)

```
feat(plan): STR-NEW-001 W2-02 Candidate C, D Pending → Active 전이 + Keltner 출처 정정

- candidate-pool.md 갱신 (B-1 정정, 파일 자체는 2026-04-17 99b281d 신설 완료):
  - Retained: Strategy A (MA200/Donchian 20/10/Vol>1.5x/SL 8%) + W1 결과
  - Deprecated: Strategy B 폐기 로그 (Sharpe 0.14, 재등장 금지)
  - Pending → Active 전이: Candidate C, D
  - Recall mechanism: DSR-adjusted 평가 + 새 사전 등록 강제
- Candidate C (Slow Momentum) 사전 등록:
  - MA50/200 crossover (Faber 2007) + ATR(14) × 3 trailing (Wilder 1978)
  - 문헌 기본값 그대로 (튜닝 X)
  - Soft contamination 인정
- Candidate D (Volatility Breakout) 사전 등록:
  - Keltner(20, 1.5 ATR) + Bollinger(20, 2σ) 동시 돌파 (Keltner 1960, Bollinger 1983)
  - Exit: Keltner Mid 하향 OR SL 8%
  - 문헌 기본값 그대로
- 외부 감사 APPROVED + 사용자 승인 → 변경 금지 서약 발효
- evidence: .evidence/agent-reviews/w2-02-strategy-candidates-review.md
- 다음 단계: W2-03 In-sample grid (Tier 1 × {A,C,D} = 6 primary + Tier 2 12 exploratory)
```

---

**이전 Task**: [W2-01 cycle 2 완료](./w2-01-data-expansion.md) (2026-04-19)
**다음 Task**: W2-03 In-sample 백테스트 grid (W2-02 완료 후 sub-plan 작성)
