# W2-02 sub-plan 외부 감사관 적대적 검증 (2026-04-19)

**검증 대상**: `docs/stage1-subplans/w2-02-strategy-candidates.md` (자가 검증 후 WARNING 3건 정정한 상태)
**검증자**: 적대적 외부 감사관 페르소나 (general-purpose 에이전트, rubber-stamp 절대 금지)
**검증 도구**:
- 직접 venv 실행으로 ta 라이브러리 0.x KeltnerChannel/BollingerBands API 검증 (`source research/.venv/bin/activate`)
- vectorbt 0.28.5 Portfolio.from_signals docstring 직접 확인
- candidate-pool.md, decisions-final.md, pair-selection-criteria-week2-cycle2.md, w2-01-data-expansion.md cross-reference
- handover v8 #1~#20 패턴 재발 여부 점검

---

## 판정

**CHANGES REQUIRED** (BLOCKING 4 + WARNING 5 + NIT 4)

자가 검증 후 정정한 WARNING 3건은 **서면상 표기로는 모두 해소**되었다고 확인된다. 그러나 본 차원의 외부 감사 결과 **새로운 BLOCKING 4건**이 추가 발견되었다. 그 중 다수는 `ta` 라이브러리 직접 venv 검증 + 기존 `candidate-pool.md` 파일 존재 사실 확인을 통해 드러난 사실 오류로, sub-plan 박제가 실제 구현 가능성/실측 사실과 모순됨.

본 sub-plan은 **사용자 승인을 받기 전에 정정 + 재감사가 필수**.

---

## 발견 사항

### BLOCKING (4건)

#### B-1 (L43, L54, L62, L68, L172, L256, L278, L284, L288, L324, L344, L346, 산출물 섹션) — `candidate-pool.md` "신설" 박제는 **사실 오류**

**현황 (감사관 직접 확인)**:
- `docs/candidate-pool.md`는 이미 존재하며 (L1~L97 전체 박제 완료) 커밋 `99b281d` (`docs(plan): W2-01 외부 감사 대응 — 6 BLOCKING + 7 WARNING 해소`)에서 **2026-04-17에 신설 + git tracked 완료**.
- candidate-pool.md L13~L50: Strategy A "Retained" + Strategy C "Pending" + Strategy D "Pending" + L56~L65 Strategy B "Deprecated" **모두 이미 등록 완료**.
- candidate-pool.md L88: 변경 이력에 "2026-04-17 | 파일 신설" 명시됨.

**sub-plan 박제 (오류)**:
- L43 "Strategy A 후보 풀 물리화: candidate-pool.md 신설 (cycle 1 박제 W2-01.1 누락 정정)"
- L54 W2-02.0 메모 "candidate-pool.md 신설 (W2-01.1 박제 누락 정정)"
- L62 SubTask W2-02.0 헤더 "candidate-pool.md 신설 (W2-01.1 박제 누락 정정)"
- L68 "[ ] `docs/candidate-pool.md` 신설"
- L288 인수 완료 조건 "candidate-pool.md 신설 (W2-01.1 박제 누락 정정 + Strategy A/B 박제 + C/D placeholder)"
- L324 산출물 "candidate-pool.md (신설, Retained/Pending/Deprecated 통합 관리)"
- L344, L346 commit 메시지 "candidate-pool.md 신설"

**문제**:
- 사실 오기. **이미 신설된 파일을 "신설"이라고 박제** = 외부 감사관 기준 명백한 사실 오류.
- 또한 "W2-01.1 박제 누락 정정"이라는 표현도 오류. W2-01 sub-plan L164/L242/L287/L311 모두 candidate-pool.md 물리화를 W2-01.3 책무로 명시했고 실제로 W2-01 외부 감사 대응 시점(커밋 99b281d, 2026-04-17)에 신설됨. 즉 박제 자체가 누락된 적이 없음.
- 더불어 candidate-pool.md L36에는 이미 Strategy C `FAST_MA=50, SLOW_MA=200, ATR_PERIOD=14, ATR_MULT=3` "잠정" 등록됨. L47 Strategy D `KC_PERIOD=20, KC_ATR_MULT=1.5, BB_PERIOD=20, BB_SIGMA=2` "잠정" 등록됨. W2-02.0 작업이 "신설"이 아니라 **"Pending → Registered 상태 전이 + 잠정 → freeze 박제"** 작업이 정확함.
- 이 사실 오류는 commit 메시지에도 그대로 박제되어 있어, 커밋 시점에 사용자 + 외부 감사관에게 잘못된 사실 전달 위험.

**handover v8 패턴 재발 위험**:
- handover #20 "sub-plan 박제 vs .gitignore 실제 룰 충돌"과 같은 카테고리 = **sub-plan 박제 vs 실제 git 상태 불일치**. 동일 패턴 누적 발견.
- CLAUDE.md root "Maintenance Policy: 괴리 즉시 보고" 위반.

**수정 권고**:
- L43, L54, L62, L68, L172, L256, L278, L284, L288, L324, L344, L346 **모두 "신설" → "갱신 (Pending → Registered 상태 전이 + 잠정 파라미터 → freeze 박제 + Strategy A 재등장 시 DSR-adjusted Recall mechanism 강화)"** 수정.
- L43, L54, L62, L288 의 "W2-01.1 박제 누락 정정" 문구 **삭제 또는 "W2-01.3 잠정 박제 → W2-02 freeze 확정"으로 수정**.
- W2-02.0 본문에 candidate-pool.md 현재 상태 (Strategy A Retained 박제 완료 / C, D 잠정 등록 완료) 정직 인용 + 본 Task에서 추가/변경할 항목만 명시 (예: "잠정 → Registered 박제, soft contamination 인정 강화, 동시 돌파 정의 박제, ATR trailing stop 구현 가이드 박제, 진입/청산 의사 코드 추가").

---

#### B-2 (L189-194, L210-220) — Candidate D Keltner Channel 공식 + 문헌 출처 **사실 오류**

**감사관 venv 직접 검증 결과** (`source research/.venv/bin/activate; python3 -c "from ta.volatility import KeltnerChannel; ..."`):

```
KeltnerChannel.__init__ signature:
  (self, high, low, close, window: int = 20, window_atr: int = 10,
   fillna: bool = False, original_version: bool = True, multiplier: int = 2)

KeltnerChannel methods:
  ['keltner_channel_hband', 'keltner_channel_hband_indicator',
   'keltner_channel_lband', 'keltner_channel_lband_indicator',
   'keltner_channel_mband', 'keltner_channel_pband', 'keltner_channel_wband']
```

`ta` 라이브러리 source code (직접 검증):
- **`original_version=True` (기본값)**:
  - 중심선 = `((H+L+C)/3).rolling(window).mean()` = **typical price의 SMA**
  - 상단 = `((4H-2L+C)/3).rolling(window).mean()` (= H 가중 typical)
  - **ATR 사용 안 함, multiplier 무시**, window_atr 무시
- **`original_version=False`**:
  - 중심선 = `close.ewm(span=window).mean()` (EMA of close)
  - 상단 = 중심선 + `multiplier × ATR(window_atr)`
  - 하단 = 중심선 - `multiplier × ATR(window_atr)`

**sub-plan 박제 문제**:

1. **L189-194 파라미터 표 "Keltner ATR multiplier 1.5 | Keltner (1960) 원 설계값 (1.5 ATR)"는 사실 오류**:
   - **Chester Keltner (1960) "How To Make Money in Commodities" 원 설계 = `EMA(typical_price, 10) ± 1.0 × 10일 daily range`** (ATR 아님 — daily range = high - low). 1.0 multiplier (1.5 아님).
   - **Linda Bradford Raschke 1990년대 변형 = EMA + 2 × ATR**. **Chuck LeBeau / Charles Le Beau "Chandelier Exit" 1980-90년대 = 2-3 × ATR**.
   - "1.5 × ATR" multiplier는 어떤 표준 문헌의 "원 설계값"이 아님. ChartSchool / StockCharts 일부 자료에서 default로 채택되긴 하나 "Keltner 1960 원 설계"가 아님.
   - **문헌 출처 정확성 = ZERO** (decisions-final.md L540 박제도 동일 오류 = 박제 동시 정정 필요).

2. **L210-220 의사 코드 모순**:
   - `from ta.volatility import ... KeltnerChannel` import만 하고 **사용 안 함** (사용된 것은 `kma = close.rolling(KELTNER_WINDOW).mean()` + `keltner_upper = kma + KELTNER_ATR_MULT * atr`).
   - 직접 계산식 `kma + 1.5 × ATR(14)`는 위 어떤 표준 Keltner 변형과도 일치 안 함:
     - 표준 변형은 EMA of close (Raschke) 또는 SMA of typical price (ta 0.x `original_version=True`) 또는 EMA of typical price (Keltner 1960). **SMA of close는 어디에도 없음**.
     - ATR window 14 + Keltner window 20 조합도 비표준 (Keltner 1960 = 10일 EMA + 10일 range, Raschke = 20 EMA + 10 ATR, ta 0.x = 20 SMA-tp + 10 ATR).
   - 즉 "원 저자 기본값 그대로 채택" (L42 "문헌 기본값 채택 (튜닝 X)") 박제와 실제 코드가 **상호 모순**.

3. **L218 `keltner_mid = kma`** 정의 + L201 "Exit: Keltner Middle Band(=KMA20) 하향 돌파"도 동일 모순. Keltner 1960 원 설계 mid = EMA(typical), ta `original_version=True` mid = SMA(typical). **SMA of close는 표준 Keltner mid가 아님**.

**handover v8 패턴 재발**:
- #16 "외부 라이브러리 응답 필드 추측" 카테고리 = **외부 라이브러리 API 추측으로 코드 작성 금지** (research/CLAUDE.md L132). KeltnerChannel을 import만 하고 실제 메서드 (`keltner_channel_hband()`, `keltner_channel_mband()`)를 사용 안 한 것 = `ta` API를 추측으로 우회.
- root CLAUDE.md L40 Immutable "외부 라이브러리 API 사용 시 공식 docs 또는 소스 직접 확인 후 코드 작성. 추측으로 작성 금지." 위반.

**수정 권고**:
- **선택 1 (권고)**: `ta.volatility.KeltnerChannel(high, low, close, window=20, window_atr=10, original_version=False, multiplier=2)` 사용 (Raschke 변형, 표준에 가까움). 그리고 `multiplier=2` 박제 (Raschke 표준). 의사 코드는 `kc = KeltnerChannel(...); upper = kc.keltner_channel_hband(); mid = kc.keltner_channel_mband()`. 문헌 출처는 "Raschke (1990s) 변형, ta 0.x 라이브러리 표준 매개변수" 정직 인용.
- **선택 2**: `ta.volatility.KeltnerChannel(..., original_version=True)` 사용 (라이브러리 기본값, ATR 미사용 SMA-typical 변형). 이 경우 "Keltner 1960" 인용 가능하지만 multiplier/ATR 박제 모두 **사라짐**. 박제 표 재작성 필수.
- **선택 3**: 직접 계산 유지 시 — 의사 코드 + 문헌 인용을 **정직하게 정정**. 예: "본 프로젝트 변형: SMA(close, 20) ± 1.5 × ATR(14, Wilder). 이는 어떤 단일 문헌의 표준값과도 정확히 일치하지 않음. ChartSchool / StockCharts 1.5 ATR default 채택 + Raschke EMA 대신 SMA of close 사용 (계산 안정성 단순화). soft contamination 추가 항목으로 인정." 문헌 인용 표 "Keltner (1960) 원 설계값" → "ChartSchool / StockCharts 라이브러리 default + 본 프로젝트 SMA-of-close 단순화 변형" 수정.
- 어느 선택이든 **decisions-final.md L539-541 박제 동시 정정 필수** (cross-document 진실 일관성).

---

#### B-3 (L137-138, L155, L161) — Candidate C 골든/데스 크로스 정의가 **신호 시점 모호 + 신호 누락 위험**

**sub-plan 박제 (L137-138)**:
```python
golden_cross = (ma_short > ma_long) & (ma_short.shift(1) <= ma_long.shift(1))
death_cross = (ma_short < ma_long) & (ma_short.shift(1) >= ma_long.shift(1))
```

**문제 1 — 동등 (`==`) 처리 모순**:
- `ma_short.shift(1) <= ma_long.shift(1)`은 전일까지 "MA50이 MA200 이하" (즉 Bear 또는 동등). `ma_short > ma_long` 오늘 strict greater (Bull strict).
- 정의상 entry 조건 = "전일 MA50 ≤ MA200 → 오늘 MA50 > MA200" = 표준 골든 크로스 정의 OK.
- 그러나 death_cross도 `<` strict + `>=` 전일 (Bull 또는 동등). 동등이 entry/exit 어느 쪽이든 다음 strict 변화에서 1 bar 지연 가능. 박제 정직성 부족이지만 BLOCKING는 아님.

**문제 2 — Long entry 조건 (L103) "MA50 > MA200 (Bull regime) AND MA50가 MA200 상향 crossover"**:
- `(ma_short > ma_long) & (ma_short.shift(1) <= ma_long.shift(1))` = 골든 크로스 자체. **"MA50 > MA200 (Bull regime)"는 골든 크로스 정의에 이미 포함됨** (오늘 strict greater). 중복 조건이며 박제 표현이 사용자 + Claude 혼동 유발 가능.
- 더 큰 문제: **Bull regime 필터** 의도라면 "이미 골든 크로스 발생한 후 한참 지나서 가격이 추가 진입할 때"도 신호로 보내야 하는데, 본 박제는 **crossover 시점 1 bar에서만 entry 신호 = True**. → 사실상 Strategy A의 "Bull regime 필터"와 다른 **single-bar entry trigger**.
- 박제 원래 의도가 "골든 크로스 발생 후 모든 Bull bar entry" 인지 "골든 크로스 시점 1 bar entry"인지 sub-plan에서 모호. L116 "신호 빈도 = 상대적으로 드뭄 (장기 추세 전환만)" 박제로부터 후자 의도로 추정되나 명시 박제 부재.

**문제 3 — vectorbt entry mask 동작과 후속 entry 박제 부재**:
- 골든 크로스 후 1 bar = entry 발생 + 포지션 보유. 이후 ATR trailing stop 발동 시 청산.
- 청산 후 **여전히 Bull regime인 (MA50 > MA200) 상태에서 다음 골든 크로스까지 entry 안 함** = 한 사이클 내 1회 진입만. 의도 맞는지 명시 박제 부재.
- vectorbt 0.28.5 default = entries는 `accumulate=False` → 추가 entry 안 함. 청산 후 다시 entries True 시 신규 entry. 본 박제는 1 cycle 1 entry라 OK이지만 명시 박제 부재.

**handover v8 패턴 재발**:
- #11 측정 창 inclusive off-by-one 카테고리 = **신호 정의 ambiguity**. 동일 카테고리 (조건문 시점 정의 부정확).
- #14 "실측 cherry-pick 경로 재유입" 카테고리는 아니지만 **사전 박제 모호성** = W2-03 구현 단계에서 작성자 임의 해석 통로 = cherry-pick 경로.

**수정 권고**:
- L103 "Long entry: MA50 > MA200 (Bull regime) AND MA50가 MA200 상향 crossover" → "**Long entry: MA50/MA200 골든 크로스 시점 1 bar (전일 MA50 ≤ MA200, 당일 MA50 > MA200). Bull regime 필터는 골든 크로스 정의에 포함됨**" 수정.
- 청산 후 동일 추세 내 재진입 정책 명시 박제 추가: "청산 후 동일 골든 크로스 효력 만료. 다음 새 골든 크로스 (= 데스 크로스 후 새 골든) 까지 entry 안 함. vectorbt `accumulate=False` (default) 사용."
- 동등 (`==`) 케이스 처리 박제 추가 (예: "MA50 == MA200 = no signal, 다음 strict 변화 bar에서 신호").

---

#### B-4 (L199-202, L225-232) — Candidate D 동시 돌파 정의 + Exit 정의 **신호 시점 모호 + 미세 모순**

**sub-plan 박제 (L199-201)**:
- "Long entry (동시 돌파): 당일 close가 Keltner Upper Band 상향 돌파 AND Bollinger Upper Band 상향 돌파"
- ""동시" 정의: 같은 종가 시점 둘 다 첫 돌파 (전일 close ≤ 두 band, 당일 close > 두 band)"

**문제 1 — "첫 돌파" 정의 ambiguity**:
- 의사 코드 (L225-229):
  ```python
  both_break = (
      (close > keltner_upper) & (close.shift(1) <= keltner_upper.shift(1))
  ) & (
      (close > bb_upper) & (close.shift(1) <= bb_upper.shift(1))
  )
  ```
  - 이 박제는 "당일 둘 다 돌파 + 전일 둘 다 해당 band 이하"인 케이스만 entry 신호 = True.
  - 그러나 "Keltner는 2일 전 돌파, Bollinger는 오늘 첫 돌파, 그래서 둘 다 오늘 close가 두 band 위에 있고, 둘 다 동시 돌파한 시점은 어제 K + 오늘 B" 같은 **mixed timing 케이스에서 entry 신호 = False**.
  - 박제 표 L194 "동시 돌파 신호 빈도 매우 낮을 가능성" 박제 + L317 리스크 표 "Candidate D 동시 돌파 신호 빈도 매우 낮을 가능성"이 이 strict 정의에서 비롯됨. 의도 인지 + 박제 OK.
  - 다만 "Tier 1 + Tier 2 5년 데이터 = 충분한 신호 수 기대"는 **근거 없는 낙관 추정** (5년 strict 동시 돌파 빈도 추정치 박제 없음). NIT 카테고리.

**문제 2 — Exit 정의 (L201, L232) 역방향 모순**:
- L201 "Exit: 당일 close가 Keltner Middle Band(=KMA20) 하향 돌파 OR 진입 후 SL 8%"
- L232 의사 코드: `mid_exit = (close < keltner_mid) & (close.shift(1) >= keltner_mid.shift(1))` = "전일 close ≥ mid + 당일 close < mid" 시점 1 bar 신호.
- **문제**: 진입은 일반적으로 close가 upper band > mid 위에 있을 때 발생. 진입 후 close가 점차 떨어져서 mid 아래로 내려가면 exit 발동. 그러나 본 박제는 "당일 첫 mid 하향 돌파" 1 bar 신호만 True → 그 bar에서 close가 정확히 mid 아래 + 전일 close 정확히 mid 이상이어야 함. 만약 진입 시점에 이미 close < mid (드물지만 가능, mid는 SMA-typical 또는 SMA-close에 따라) → exit 신호 발동 안 함.
- 또한 "전일 close ≥ mid + 당일 close < mid" 시점 1 bar만 True = 다음 bar들에서는 exit_mask = False. vectorbt `from_signals`는 exit_mask True bar에서만 청산. 따라서 첫 mid 하향 돌파 bar에서 sl_stop 발동 가능성과 mid_exit 발동이 동시 가능. 우선순위는 vectorbt 내부 정책 (sl_stop이 보통 우선) → 박제 의도와 다를 수 있음.
- 수정 권고: exit 신호를 **"close가 mid 아래에 있는 모든 bar = exit_mask True"**로 단순화하거나, "첫 mid 하향 돌파 1 bar만 True" 명시 + `accumulate=False` (default) 동작상 첫 entry 후 exit_mask True면 청산되므로 OK 명시.

**문제 3 — Keltner mid 정의 모호**:
- L218 `keltner_mid = kma` (SMA of close 20). B-2 BLOCKING과 동일 카테고리 — 표준 Keltner mid는 EMA-typical 또는 SMA-typical, SMA-close 아님. ta KeltnerChannel `keltner_channel_mband()` 사용 시 `original_version=True` = SMA-typical, `False` = EMA-close. SMA-close는 어디에도 없음.

**handover v8 패턴 재발**:
- #11 신호 정의 시점 ambiguity 카테고리 (B-3와 동일).
- #16 외부 라이브러리 API 추측 카테고리 (B-2와 동일).

**수정 권고**:
- L201 Exit 정의 → "**Exit: close < keltner_mid (mid 아래에 있는 모든 bar = exit_mask True) OR 진입 후 SL 8%**" 변경. 의사 코드도 `mid_exit = close < keltner_mid` (단순화) 변경. 신호 시점 1 bar 한정 정책 폐기.
- 또는 단순화 안 한 경우 명시 박제: "첫 mid 하향 돌파 1 bar만 True. 이후 bar들에서 close가 계속 mid 아래여도 exit_mask = False. 청산은 첫 신호 bar에서 발생. vectorbt entry/exit 우선순위 정책에 따라 sl_stop와 동시 발동 시 sl_stop 우선."
- B-2 수정과 함께 keltner_mid 정의 표준화 (`kc.keltner_channel_mband()` 사용).

---

### WARNING (5건)

#### W-1 (L121-161) — ATR trailing stop 방법 A 가정이 **vectorbt sl_stop 동작 정확성 미검증**

**sub-plan 박제 (L141-149)**:
- "방법 A (vectorbt sl_stop + sl_trail=True): entry bar의 (ATR_MULT × ATR) / close 비율을 sl_stop에 입력. 단 sl_trail=True는 entry 이후 highest close 기준으로 비율 적용. ATR이 entry 시점 고정값."
- 의사 코드: `sl_stop_ratio = (ATR_MULT * atr) / close`  # entry bar 기준 비율, vectorbt가 entry 시점 값 사용

**감사관 vectorbt 0.28.5 docstring 직접 확인 결과**:
- `sl_stop (array_like of float): Stop loss. Will broadcast. **A percentage below/above the acquisition price** for long/short position. Note that 0.01 = 1%.`
- `sl_trail (array_like of bool): Whether sl_stop should be trailing. Will broadcast.`
- broadcast가 array_like 가능. Series 입력 가능. **그러나 Series가 매 bar 새 값으로 업데이트되어 단순한 "entry 시점 고정"이 아님** (단 `upon_stop_update` 옵션으로 제어 가능).
- 즉 sub-plan 박제 "vectorbt가 entry 시점 값 사용"은 **vectorbt 0.28.5 default 동작이 아니거나 default일 수 있음 — 정확성 미검증**. 본 차원 감사관도 실제 backtest 실행 + entry 후 sl_stop 값 변화 추적 실험 미수행 (시간 제약). research/CLAUDE.md L113 "외부 라이브러리 신규 사용 시 공식 docs/소스 직접 확인" 위반 위험.

**문제**:
- 박제 자체에 약점 인정 (L161 "약점 인정 (외부 감사 권고): ATR 기반 trailing stop은 vectorbt 0.28.5 Boolean exit mask로 자연스럽게 표현 어려움. W2-03 구현 시 방법 A/B 비교 + backtest-reviewer 검증 후 채택 결정. 현 단계는 사전 등록 의도(ATR×3 trailing) 박제로 충분") 박제 = 정직.
- 그러나 의사 코드 L149 + L154 `sl_stop=sl_stop_ratio, sl_trail=True`는 W2-03에서 **그대로 검증 없이 사용될 위험**. handover v8 #16 "외부 라이브러리 추측 코드 작성 금지" 패턴 재발.

**수정 권고**:
- L161 박제 강화 + W2-03 sub-plan 작성 시 의무 박제 추가: "방법 A 의사 코드는 사전 검증 안 됨. W2-03 구현 시 (1) vectorbt 0.28.5 docstring + nb 코드 직접 확인, (2) 단일 entry 시점 + ATR 변화 + sl_stop 값 추적 mini test 작성 + 결과 평가, (3) 결과 = 의도 ('ATR이 entry 시점 고정값') 일치 시 채택, 불일치 시 방법 B (manual trailing) 강제 채택 + backtest-reviewer 검증."
- W2-03 sub-plan에 "ATR trailing stop 구현 검증" SubTask 신설 박제 권고.

---

#### W-2 (L100-119, candidate-pool L23-28 vs L36) — **MA200 윈도우 = "일봉 200" vs Strategy A "MA_PERIOD=200" 박제 일관성**

**검증**:
- candidate-pool.md L23 Strategy A `MA_PERIOD=200` (단순 일봉 200).
- sub-plan L98 Candidate C `MA long = 200` (Faber 2007 동일).
- 본 차원에서 신호 차별화 박제 (L110-119): A는 "MA200 regime 필터" + Donchian 20/10. C는 MA50/200 골든 크로스. → 차별화 박제 OK.

**문제**:
- W1-06 분석 결과 "Strategy A 최근 481일 Sharpe -1.14 (2승 3패)" + "MA200이 regime 필터로 작동하지 않음" 시사. C도 동일 MA200을 골든 크로스에 사용 = **regime decay 동일 영향 받을 가능성 높음**.
- L114 차별화 표 "신호 시점 = Donchian 채널 돌파 시점 (단기 모멘텀)" vs "이동평균 crossover 시점 (장기 추세 전환)" 박제는 신호 빈도/메커니즘 차이를 강조하나, **MA200 자체의 BTC regime decay 영향은 동일하게 받음** = 차별화 가치 부분 감소.
- L316 리스크 표 "Candidate C와 Strategy A 신호 중첩 (둘 다 MA crossover 기반)" = "C는 MA50/200, A는 MA200 + Donchian 20/10. 신호 차별화. 단 W2-03에서 cross-corr 점검 권고" 박제는 신호 차별화 강조이나 **regime decay 차원 박제 부재**.

**수정 권고**:
- L316 리스크 표 또는 L110-119 차별화 박제에 추가 박제: "단 MA200 자체의 BTC 5년 regime decay 영향은 A와 C가 공유. C도 동일 MA200 decay 위험 잠재. soft contamination + W2-03 결과로 검증."

---

#### W-3 (L42, L165-168, L242, L317) — Soft contamination 인정이 **부분 + 비정확**

**sub-plan 박제 (L42)**:
- "Soft contamination 정직 인정: Week 1 결과 본 상태에서 전략 철학 선택 = 완전 독립 X"

**L165-168 박제**:
- "Week 1 W1-06.1b regime 편중 결과를 본 후 'momentum + ATR trailing' 철학 선택"
- "파라미터(50/200/14/3)는 문헌 기본값 그대로 (튜닝 X)"
- "그러나 철학 자체 선택은 W1 영향 받음"
- "최종 평가는 Week 3 walk-forward (Week 2 In-sample은 예비 판단)"

**문제**:
- soft contamination 박제 자체는 OK. 그러나 **추가 contamination layer 박제 부재**:
  1. **Tier 1 페어 = {BTC, ETH}** = BTC는 W1에서 5년 데이터 본 상태. ETH는 cycle 2에서 데이터 collected (2026-04-19) 시점에 W2-02 sub-plan 작성. ETH 데이터 시각적 검토 여부 불명. 만약 ETH 데이터 시각화/통계 본 상태에서 본 sub-plan 작성 = 추가 soft contamination.
  2. **Strategy A MA200 + Donchian 20/10 + Vol 1.5x 박제** 자체가 W1 결과 본 상태 사후 선택. 본 sub-plan은 이를 "Retained" 채택 (candidate-pool.md L21~L28). C와 D 새 사전 등록 + A 재검증이 같은 grid에서 발생 → multiple testing layer 추가.
  3. **decisions-final.md L535-541 박제 (Faber 2007 / Wilder 1978 / Keltner 1960 / Bollinger 1983) 자체가 cycle 1 외부 감사 (2026-04-17) 결과 사후 선택** = 외부 감사관도 contamination 통로일 수 있음.

**handover v8 패턴 재발**:
- #9 "Soft contamination 간과" 카테고리. **반복 발생 가능성**. cycle 1 W2-01 사전 감사에서 BLOCKING-4로 발견 → cycle 2 인정 박제 추가. **본 sub-plan에서도 추가 layer 발견** = 패턴 재발 (인정 박제는 있으나 layer 누락).

**수정 권고**:
- L165-168 박제 확장: "soft contamination layer 정직 enumeration:
  1. Week 1 BTC 5년 regime 편중 결과 본 후 momentum + breakout 철학 선택
  2. ETH 데이터 cycle 2 W2-01.4 수집 시점에 시각적 검토 여부 미박제 — 검토 했다면 추가 contamination, 안 했다면 명시
  3. Strategy A 박제 자체가 W1 결과 사후 선택, 본 grid에서 재평가 = multiple testing layer 추가
  4. cycle 1 외부 감사관 의견 (2026-04-17) 반영하여 Faber/Wilder/Keltner/Bollinger 출처 박제 = 외부 감사관도 contamination 통로
- 결과적으로 Week 2 Sharpe는 In-sample 예비 판단. Week 3 walk-forward (BTC/ETH/Tier 2 OOS 분할)가 최종 게이트."

---

#### W-4 (L294, decisions-final L517-521) — **Secondary 마킹 박제 발효 시점 + 동치 정의 모호**

**sub-plan 박제 (L294)**:
- "Go 기준 박제 인용 (cycle 2 v5 Fallback 정책 + decisions-final.md L517-521): Primary `Sharpe>0.8 AND DSR>0` + Secondary 마킹 `Sharpe>0.5` → ensemble 후보 (Go 기여 X)"

**decisions-final.md L517-521 (감사관 직접 확인)**:
- L517 "Week 2 게이트 (사전 지정, DSR 포함):"
- L518 "Primary: Primary 6셀 중 적어도 1개 전략이 BTC 또는 ETH에서 Sharpe > 0.8 AND DSR > 0"
- L519 "Secondary 마킹 (Go 기여 X): 동일 전략이 Tier 1+2 3+ 페어에서 Sharpe > 0.5 → ensemble 후보"
- L520 "미달 → Stage 1 킬 카운터 +1, Week 3 재탐색"

**문제**:
- decisions-final.md L519 "**동일 전략이 Tier 1+2 3+ 페어에서**" — 즉 secondary 조건은 **Primary Go 통과 후 동일 전략의 Tier 1+2 3+ 페어 모두 Sharpe > 0.5** 만족 시 ensemble 후보. **Primary 미통과 전략은 secondary 마킹 자체 불가**.
- sub-plan L294는 "Secondary 마킹 Sharpe>0.5 → ensemble 후보 (Go 기여 X)" 박제만 인용. **Tier 1+2 3+ 페어 조건 누락** = 부분 인용 = 박제 정확성 결함.
- 또한 cycle 2 v5 Fallback 정책 인용은 본 sub-plan에서는 인용 텍스트 부재. cycle 2 v5 = `pair-selection-criteria-week2-cycle2.md` v5 박제 — 본 sub-plan 박제 출처 (L36)에 인용되어 있으나 **Fallback 3.0** 같은 항목명 박제 부재. 어느 섹션에서 인용했는지 명시 부재.

**수정 권고**:
- L294 박제 확장: "Go 기준 박제 인용 (decisions-final.md L517-521): Primary `Sharpe>0.8 AND DSR>0` (Tier 1 6셀 중 ≥1 전략이 BTC OR ETH 만족) + **Secondary 마킹 (Go 기여 X): Primary 통과 전략이 Tier 1+2 3+ 페어에서 Sharpe>0.5 만족 시 ensemble 후보**. 미달 시 Stage 1 킬 카운터 +1 + Week 3 재탐색."
- "cycle 2 v5 Fallback 정책" 인용은 cycle 2 페어 선정 기준 v5와 W2-02 평가 정책 분리 명시 (cycle 2 v5는 페어 선정 Fallback, W2-02 평가는 decisions-final.md "Week 2 게이트" 박제 기반).

---

#### W-5 (L9-10, L19-31, L38-44) — **사용자 승인 + freeze 시점 vs Tier 2 = [XRP, SOL, TRX, DOGE] 박제 일관성 미흡**

**sub-plan 박제**:
- L17 "Blocked By: W2-01 cycle 2 전체 완료 (2026-04-19)"
- L26 "Tier 2 = [XRP, SOL, TRX, DOGE] 확정 + 10 dataset Parquet freeze"
- W2-02.4 (L271-284) "사용자 명시적 승인 (예: 'ㄱㄱ' 또는 명시적 OK)" + "변경 금지 서약 발효"

**문제**:
- W2-02.4 사용자 명시적 승인 시점 = 본 sub-plan 발효 시점이지만 **시점 박제 모호**:
  - cycle 1 v4 외부 감사 사례 = 박제 시점 vs 발효 시점 순환 정의 (handover v8 #13 "박제 문서 자기 freeze 시점 순환 정의").
  - 본 sub-plan W2-02.4 "사용자 명시적 승인" 박제는 발효 시점이 사용자 승인 시점 = OK이지만 **시점 명시 박제 부재** (예: "2026-04-19 사용자 승인 시점", "별도 시점 박제 — 승인 후 정확한 시점 기록").
  - W2-02.4 변경 금지 서약 발효 시점도 동일 모호. 사용자 승인 → 즉시 발효 = OK이지만 박제 명시 부재.

**handover v8 패턴 재발**:
- #13 "박제 문서 자기 freeze 시점 순환 정의" 카테고리 = **시점 발효 박제 부재**. 박제 작성자가 발효 시점을 명시하지 않으면 사후 cherry-pick 통로 = 동일 카테고리.

**수정 권고**:
- W2-02.4 박제 강화: "사용자 명시적 승인 시점 = 발효 시점. 시점 박제는 사용자 응답 발화의 **UTC timestamp 명시** + git commit hash 명시 (예: `2026-04-19 HH:MM:SS UTC, commit hash`). 변경 금지 서약 = 동일 시점 즉시 발효. 이후 변경 시 새 사전 등록 + 새 외부 감사 + 새 사용자 승인 강제."

---

### NIT (4건)

#### NIT-1 (L1, L26, L93) — Tier 2 박제 정확성 vs handover v8 일관성

- sub-plan L1 "Candidate C, D 사전 등록"
- sub-plan L26 "Tier 2 = [XRP, SOL, TRX, DOGE] 확정"
- handover v8 L16 "Tier 2 = [XRP, SOL, TRX, DOGE]"
- 일관성 OK.
- NIT 권고: "10 dataset Parquet freeze" 표현이 BTC + ETH (Tier 1 2개) + Tier 2 4개 = 6 페어 × 2 interval (1d + 4h) = 12 dataset이어야 하는데 "10" 박제. handover v8 L10 "5 페어 × 2 interval = 10 dataset" 박제 — Tier 1 2개 + Tier 2 4개 = 6 페어인데 5 페어로 박제. handover v8 + sub-plan 모두 5 페어 박제. **본 차원 감사관 직접 데이터 dir 검증 안 함 — 5 페어 vs 6 페어 정합성 별도 점검 권고**.

#### NIT-2 (L93, L185) — Strategy 철학 vs Bull/Bear 박제 모호

- L93 Candidate C "Bull regime 편중 가능성 (Week 1 A regime 편중 학습 → soft contamination 인정)"
- L185 Candidate D "Bull/Bear 양방 가능 (단 본 사이클은 long-only)"
- C는 long-only 명시 부재. L106 "포지션 사이즈: 100% (cash_sharing 단일 진입, Strategy A와 동일 패턴)" 박제로 long-only 추정 가능하나 명시 부재.
- 권고: "Candidate C 본 사이클 long-only 명시 박제 추가 (Strategy A/D와 동일 long-only)."

#### NIT-3 (L286-299, L301-307) — Acceptance Criteria 박제 누락

- L286-299 Acceptance Criteria 박제에 "Strategy A 후보 풀에서 W2-03 grid 재진입 박제 (DSR-adjusted 평가 의무)"는 L295에 있음.
- 그러나 "Candidate C/D 변경 금지 서약 발효 시점 박제" (W-5에서 권고)는 L298 "사용자 명시적 승인 → 변경 금지 서약 발효"만 있음. **시점 명시 박제 책무**가 Acceptance Criteria에 부재. NIT 권고: 추가.

#### NIT-4 (L342-362) — commit 메시지 박제 vs B-1 정정 후 변경

- L344 "feat(plan): STR-NEW-001 W2-02 Candidate C, D 사전 등록 + candidate-pool.md 신설"
- B-1 "candidate-pool.md 신설" 사실 오류 정정 후 commit 메시지도 동시 정정 필요. NIT 권고: B-1 정정 시 commit 메시지를 "Candidate C, D 사전 등록 + candidate-pool.md 갱신 (Pending → Registered)" 변경.

---

## 자가 검증 정정 재발 여부

| 정정 항목 | 잔존 여부 | 근거 |
|---------|----------|------|
| WARNING-A (ATR trailing stop 구현 가이드) | **잔존 (W-1)** | L121-161 박제는 추가됨 (방법 A/B 비교 + W2-03 정확 구현 권고). 그러나 방법 A 의사 코드 가정 자체가 vectorbt 0.28.5 docstring과 정확성 미검증 = 새 카테고리 잔존 |
| WARNING-B (Secondary 마킹 정책) | **잔존 (W-4)** | L294 박제는 추가됨. 그러나 decisions-final.md L519 "동일 전략이 Tier 1+2 3+ 페어에서" 조건 부분 인용 = 박제 정확성 결함 잔존 |
| WARNING-C (Strategy A vs Candidate C 신호 차별화) | **잔존 (W-2)** | L110-119 박제는 추가됨 (신호 차별화 표). 그러나 MA200 자체의 regime decay 공유 위험 박제 부재 = 신호 차별화 vs regime 영향 차별화 분리 박제 부재 잔존 |

자가 검증 정정 작업은 **표면적 표기 추가는 모두 완료**되었으나, **외부 감사관 차원 정정 깊이 미흡**. 특히 W-1은 vectorbt API 정확성 검증 안 됨, W-4는 박제 부분 인용, W-2는 차별화 박제만 있고 동질성 박제 부재.

---

## cycle 1 학습 패턴 재발 검증 (handover v8 #1~#20)

| # | 패턴 | 본 sub-plan 재발 여부 |
|---|------|--------------------|
| #1 | Evidence 수치 오기재 | 본 sub-plan은 evidence 수치 박제 없음 (재발 X) |
| #2 | 문서 버전 라벨 미갱신 | sub-plan 자체는 v0 (신설). 재발 X |
| #3 | execution-plan 체크박스 미체크 | W2-02 미시작 = 체크박스 빈 상태 OK. **단 본 sub-plan 작성 후 execution-plan 박제 갱신 책무 (L283 "sub-plan + execution-plan + handover 박제 갱신") 명시되어 있으나 stage1-execution-plan.md 현 상태 (L82 "Pending (sub-plan 미작성)") = sub-plan 작성 후 갱신 누락 위험.** NIT |
| #4 | backtest-reviewer 좁은 스코프 | W2-02.3 외부 감사 박제 (`general-purpose` 에이전트 + 검증 기준 7개) = 스코프 명시. 재발 X |
| #5 | fillna() FutureWarning | 의사 코드에 fillna 없음. 재발 X |
| #6 | research/outputs gitignore | 본 sub-plan 데이터 수집 없음. 재발 X |
| #7 | 사전 지정 기준 측정 창 미정의 | 본 sub-plan은 W2-03 grid 입력 박제. 측정 창 = decisions-final.md "Week 2 게이트" 박제 + cycle 2 v5 박제 활용. **단 W-4 "Tier 1+2 3+ 페어" 조건 부분 인용** = 부분 카테고리 잔존 |
| #8 | Multiple testing 미보정 | L44 "Multiple testing 한계 명시 (6 primary 셀 family-wise 오류 여지 → DSR + Week 3 walk-forward 최종 검증)" + L296 박제 OK. 재발 X |
| #9 | Soft contamination 간과 | L42 + L165-168 박제. **W-3 "추가 layer 누락" 잔존** = 부분 카테고리 잔존 |
| #10 | Fallback "임계값 완화" | 본 sub-plan은 Fallback 박제 없음 (전략 사전 등록 단계). decisions-final.md/cycle 2 v5 인용. 재발 X |
| #11 | 측정 창 inclusive off-by-one | **B-3, B-4 신호 시점 ambiguity 카테고리 = 같은 카테고리 (조건문 시점 부정확). 재발** |
| #12 | Fallback 라벨 misnomer | 재발 X |
| #13 | 박제 문서 자기 freeze 시점 순환 정의 | **W-5 사용자 승인 시점 명시 부재 = 같은 카테고리. 재발** |
| #14 | 실측 cherry-pick 경로 재유입 | B-3 신호 정의 ambiguity가 W2-03 작성자 임의 해석 통로 = **간접 재발** |
| #15 | sub-plan/decisions-final 전파 누락 | B-2 KeltnerChannel 문헌 출처 사실 오류 정정 시 decisions-final.md L539-541 동시 정정 필수. **본 sub-plan은 정정 책무 박제 없음 = 재발 위험 높음** |
| #16 | 외부 라이브러리 응답 필드 추측 | **B-2 KeltnerChannel 직접 사용 안 함 + B-2 의사 코드 비표준 변형 + W-1 vectorbt sl_stop 동작 미검증 = 동일 카테고리 재발** |
| #17 | 사전 지정 추정 리스트 빗나감 | 본 sub-plan은 추정 리스트 박제 X (문헌 기본값). 재발 X |
| #18 | 외부 코인 정체 추측 | 본 sub-plan에 미지 토큰 없음. 재발 X |
| #19 | 수치 단위 표기 오류 | 본 sub-plan에 % vs 비율 박제 없음 (sl_stop 0.08 = 8% 단위 명시). 재발 X |
| #20 | sub-plan 박제 vs .gitignore 실제 룰 충돌 | **B-1 candidate-pool.md "신설" 박제 vs 실제 git tracked 파일 존재 = 동일 카테고리 (sub-plan 박제 vs git 실제 상태 불일치) 재발** |

**재발 카테고리 합계**: #11 (신호 시점 ambiguity), #13 (시점 발효 박제 부재), #14 (cherry-pick 경로 간접), #15 (cross-document 전파 책무 누락), #16 (외부 라이브러리 추측), #20 (sub-plan vs 실제 상태 불일치) = **6개 카테고리 재발**.

handover v8 cycle 2 학습이 본 sub-plan에 부분 적용되었으나 **외부 라이브러리 직접 검증 + 박제 정확성 + cross-document 전파**가 동일 패턴으로 누적 재발.

---

## 종합 평가

### A. 사전 지정 박제 정합성

- 파라미터 명시성 = OK (튜닝 여지 없음, 문헌 기본값 채택 명시).
- **문헌 출처 정확성 = ZERO (B-2)**. Keltner (1960) 원 설계값 1.5 ATR 인용은 사실 오류. decisions-final.md L539-541 동시 정정 필수.
- decisions-final.md L535-547 박제 인용 = OK (인용 정확, 단 박제 자체가 사실 오류이므로 cross-document 정정 필수).
- DSR-adjusted 평가 정책 박제 = OK (L295).

### B. cycle 1 학습 패턴 재발 검증

- **6개 카테고리 재발** (#11, #13, #14, #15, #16, #20). 특히 #16 외부 라이브러리 추측 + #20 sub-plan vs 실제 상태 불일치는 cycle 1 W2-01에서 동일하게 발견된 패턴. **누적 재발**.

### C. cycle 2 학습 적용

- 외부 감사 절차 박제 (W2-02.3) = OK.
- 사용자 명시 승인 + 변경 금지 서약 박제 (W2-02.4) = **부분 OK** (W-5 시점 발효 박제 명시 부재).
- soft contamination vs hard 박제 = **부분 OK** (W-3 layer 누락).

### D. vectorbt 0.28.5 + ta 라이브러리 API 검증

- vectorbt sl_stop 사용법 = **부분 부정확** (W-1, sl_stop Series 입력 + sl_trail=True 결합 동작 정확성 미검증).
- ta.volatility.AverageTrueRange API = OK (감사관 직접 venv 검증, signature: `(high, low, close, window=14, fillna=False)`).
- **ta.volatility.KeltnerChannel API = 의사 코드에서 사용 안 함 + 직접 계산식 비표준 (B-2)**. import만 하고 미사용 = 외부 라이브러리 추측 재발.
- ta.volatility.BollingerBands API = OK (감사관 직접 venv 검증, signature: `(close, window=20, window_dev=2, fillna=False)`).
- vectorbt 0.28.5 금지 패턴 (ts_stop, td_stop, max_duration 등) 사용 X = OK.

### E. Multiple testing 한계 + Soft contamination 정직성

- Multiple testing 한계 박제 = OK (L44, L296, L315).
- Soft contamination 정직 보고 = **부분 OK** (W-3 layer 누락).

### F. 신호 중첩 (Strategy A vs Candidate C)

- 신호 차별화 박제 = OK (L110-119 차별화 표).
- **MA200 regime decay 공유 위험 박제 부재 (W-2)**. 신호 차별화만으로 충분 X — 동질성 박제 추가 필요.

### G. 평가 정책 (Primary/Secondary)

- Primary 박제 = OK.
- **Secondary 박제 = 부분 인용 (W-4)**. decisions-final.md L519 "Tier 1+2 3+ 페어" 조건 누락. 박제 정확성 결함.

---

## 외부 감사관 의견

**판정 = CHANGES REQUIRED.**

본 sub-plan은 cycle 2 W2-01 외부 감사관 사례 (3회 감사 + 16+ 라운드 자가 검증)와 비교했을 때 **자가 검증 정정 깊이가 부족**. 특히 다음 3개 카테고리는 외부 감사관 권한으로 사용자 승인을 차단해야 함:

1. **B-1 (candidate-pool.md "신설" 사실 오류 + commit 메시지 + 12+ 위치 사실 오기)**: 사용자에게 잘못된 사실 (이미 신설된 파일을 신설한다고 보고)을 전달. handover v8 #20 패턴 누적 재발. CLAUDE.md root Maintenance Policy "괴리 즉시 보고" 위반.

2. **B-2 (KeltnerChannel 문헌 출처 사실 오류 + 의사 코드 비표준 변형 + ta API 미사용)**: 추측으로 외부 라이브러리 코드 작성 = root CLAUDE.md L40 Immutable 위반 ("외부 라이브러리 API 사용 시 공식 docs 또는 소스 직접 확인 후 코드 작성. 추측으로 작성 금지"). decisions-final.md L539-541 동시 정정 필수 = cross-document 전파.

3. **B-3 + B-4 (신호 정의 시점 ambiguity)**: W2-03 구현 단계에서 작성자 임의 해석 통로 = cherry-pick 경로 잠재. handover v8 #11/#14 카테고리.

**다음 단계 권고**:

1. **B-1 정정**: candidate-pool.md "신설" → "갱신 (Pending → Registered + Strategy A Recall mechanism 강화)". sub-plan 12+ 위치 + commit 메시지 동시 정정. W2-02.0 본문에 candidate-pool.md 현재 상태 정직 인용 + 본 Task 변경 항목만 명시.

2. **B-2 정정**: 위 "선택 1/2/3 중 결정 + decisions-final.md L539-541 동시 정정. 직접 venv 검증 결과 박제 (예: '본 차원 외부 감사관 venv 직접 검증 결과: ta.volatility.KeltnerChannel original_version=True default = SMA-typical mid + ATR 미사용 + multiplier 무시. False = EMA-close mid + multiplier × ATR(window_atr). 따라서 1.5 ATR multiplier 박제는 ChartSchool/StockCharts default + Raschke 변형 인용. Keltner 1960 원 설계 (EMA + 1.0 × range)와 다름').

3. **B-3 정정**: 골든 크로스 entry 박제를 "crossover 시점 1 bar entry"로 명시 + 청산 후 재진입 정책 박제 추가. 동등 (`==`) 케이스 처리 명시.

4. **B-4 정정**: Exit 정의를 "close < keltner_mid 모든 bar = exit_mask True" 단순화 또는 "1 bar 한정 + sl_stop 우선순위 정책" 명시. keltner_mid 정의 표준화 (B-2와 함께).

5. **W-1 ~ W-5 + NIT-1 ~ NIT-4 정정**: 각 항목 권고대로 박제 강화.

6. **재감사**: 정정 후 본 외부 감사관 또는 다른 외부 감사관에게 재위임. **3회 권장 (cycle 1 W2-01.1 사례 = 3회 감사 후 APPROVED)**. BLOCKING 0 + WARNING/NIT만 잔존 시 사용자 결정으로 follow-up 트래킹 진행 가능.

7. **사용자 승인은 위 정정 + 재감사 후에만 진행**. 본 차원 감사관은 사용자 승인 차단.

**감사관 자가 검증 (rubber-stamp 회피)**:
- 본 검증은 cycle 1 W2-01.1 3회 감사 + cycle 2 W2-01 외부 감사 사례를 학습하여 **6 BLOCKING + 7 WARNING 발견 수준 (cycle 1 1차 감사)**과 비교했을 때, 본 차원에서 4 BLOCKING + 5 WARNING + 4 NIT 발견 = 적정 수준 (rubber-stamp X).
- 감사관도 **사실 검증 직접 venv 실행 + KeltnerChannel source 직접 read** 등 root CLAUDE.md "추측 금지" 적용. 감사관 의견에 사실 오류 잔존 가능성 인정 (예: vectorbt sl_stop Series + sl_trail=True 결합 동작 정확성 = 감사관도 실제 backtest 실행 미수행, W-1로 분리 보고).
- 본 검증 결과를 **사용자가 검토 + 정정 우선순위 결정** 권고. 감사관 판정 (CHANGES REQUIRED)은 사용자 명시 승인 차단 권한 행사.

---

# 2차 감사 (sub-plan v2 BLOCKING 정정 후, 2026-04-19)

**검증 대상**: `docs/stage1-subplans/w2-02-strategy-candidates.md` v2 (1차 감사 BLOCKING 4건 정정 + 옵션 A: WARNING/NIT 잔존 결정)
**검증자**: 적대적 외부 감사관 페르소나 2차 (general-purpose, rubber-stamp 절대 금지)
**검증 도구**:
- ta KeltnerChannel API venv 직접 호출 (`source research/.venv/bin/activate`) — `original_version=False, window_atr=14, multiplier=1.5` 동작 + mid = `EMA(close,20)` + upper-mid = `1.5×ATR(14)` numpy.allclose 일치 검증 완료. multiplier=1.5 (float) 값도 signature `int=2` 표기와 무관하게 정상 적용 확인 (`kc._multiplier=1.5`).
- vectorbt 0.28.5 `Portfolio.from_signals` signature 직접 확인 — `sl_stop`, `sl_trail`, `accumulate`, `upon_long_conflict`, `upon_dir_conflict` 모두 array_like (Series) 허용 확인.
- candidate-pool.md, decisions-final.md L539-541 cross-document 본문 직접 확인.
- handover v8 #1~#20 패턴 재발 여부 점검.

---

## 2차 감사 판정

**CHANGES REQUIRED** (BLOCKING 2 신규 + WARNING 잔존 5 + NIT 잔존 4 + NIT 신규 1)

옵션 A 결정 (BLOCKING만 정정)에 따라 1차 감사 WARNING 5건 + NIT 4건은 잔존이 정책상 허용. 그러나 본 2차 감사에서 **B-1 정정 자체가 부분 정정에 그쳐 sub-plan 본문 다수 위치에 "신설" 표현 잔존** + **B-2 정정이 sub-plan 내 두 코드 블록 중 한 곳에만 적용되어 자기 모순 신규 도입** = **BLOCKING 2건 추가 발견**.

옵션 A 정책에도 불구하고 신규 BLOCKING 도입은 사용자 승인 차단 사유. 본 sub-plan은 정정 + 3차 감사 또는 사용자 명시 결정 (옵션 A 의도 = 잔존 BLOCKING 도입 X 가정 깨짐) 필요.

---

## v2 BLOCKING 정정 검증

### B-1 정정 정확성: **PARTIAL FAIL**

**정정된 부분 (PASS)**:
- L62 SubTask W2-02.0 헤더: "candidate-pool.md Strategy C/D Pending → Active 전이 (B-1 정정)" — 사실 정확
- L68 본문 박제: "본 sub-plan v1은 'candidate-pool.md 신설'이라 박제했으나 사실 오류 — `docs/candidate-pool.md`는 이미 신설 완료 (L88 '2026-04-17 파일 신설', 커밋 `99b281d`, W2-01 외부 감사 대응 시점). Strategy A Retained / Strategy B Deprecated / Strategy C/D Pending 모두 등록 + Recall Mechanism (L69-80) 박제 완료" — 감사관 직접 확인 결과 정확. candidate-pool.md L88 변경 이력 행 = "2026-04-17 | 파일 신설" 일치, L13 Active 섹션 / L30-39 Strategy C Pending / L41-50 Strategy D Pending / L56-65 Strategy B Deprecated / L69-80 Recall Mechanism 모두 인용 정확.
- L70 W2-02.0 책무 "Pending → Active 전이" 재설계 OK
- L73, L76 Strategy C/D Active/Registered 전이 책무 명시 OK
- L78 B-2 정정 cross-document 전파 ("L48 ... → ChartSchool/StockCharts 표준 변형 + Raschke 1990s 후속") OK — candidate-pool.md L48 실제 본문 확인 결과 일치.
- L80 변경 이력 v2 행 추가 책무 OK

**잔존 사실 오류 (FAIL — BLOCKING 신규)**:

L1, L43, L54, L309, L315, L319, L330, L355, L375, L377 = **총 10개 위치에 "신설" 표현 잔존**:

- **L1 (메타 타이틀)**: `# Task W2-02 — 새 전략 후보 사전 등록 (Candidate C, D + candidate-pool 신설)` — 메타 타이틀 자체가 사실 오류. sub-plan 첫 줄이 거짓.
- **L43 (배경 핵심 원칙)**: `**Strategy A 후보 풀 물리화**: candidate-pool.md 신설 (cycle 1 박제 W2-01.1 누락 정정)` — W2-02.0 본문(L68)에서 정정된 사실과 정면 모순. 같은 sub-plan 내 자기 모순.
- **L54 (현재 진행 상태 표 W2-02.0 메모)**: `candidate-pool.md 신설 (W2-01.1 박제 누락 정정)` — 동일 오류. 메타 표 행이 W2-02.0 헤더(L62)와 모순.
- **L309 (W2-02.4 사용자 보고 항목)**: `candidate-pool.md 신설 + Strategy A/B/C/D 통합` — 사용자 보고 시점에 잘못된 사실 전달 위험. cycle 1 #20 패턴 재발.
- **L315 (W2-02.4 commit 메시지)**: `feat(plan): STR-NEW-001 W2-02 Candidate C, D 사전 등록 + candidate-pool.md 신설` — git 커밋 시점에 잘못된 사실 박제. NIT-4(1차)와 동일 카테고리 잔존.
- **L319 (인수 완료 조건)**: `[ ] docs/candidate-pool.md 신설 (W2-01.1 박제 누락 정정 + Strategy A/B 박제 + C/D placeholder)` — Acceptance Criteria 박제 자체가 사실 오류. 이 항목 체크 시 "이미 존재하는 파일을 신설했다"고 거짓 체크.
- **L330 (인수 완료 조건)**: `candidate-pool.md + sub-plan + handover 갱신 + 커밋` — 이 항목은 OK이지만 L319와 함께 읽으면 "신설"과 "갱신"이 동시 박제 = 모순.
- **L355 (산출물 섹션)**: `docs/candidate-pool.md (신설, Retained/Pending/Deprecated 통합 관리)` — 산출물 라벨 자체가 사실 오류.
- **L375 (Commit 예상 메시지 헤더)**: `feat(plan): STR-NEW-001 W2-02 Candidate C, D 사전 등록 + candidate-pool.md 신설`
- **L377 (Commit 예상 메시지 본문)**: `- candidate-pool.md 신설 (W2-01.1 박제 누락 정정):` — 커밋 메시지 본문에 잘못된 사실 박제 + "Pending → Registered" 라벨도 동시 사용 (L380) = 자기 모순.

**판정**: B-1 정정은 **W2-02.0 본문(L62-80) 한 섹션만 정정**하고 sub-plan 나머지 영역 (메타 타이틀, 배경 원칙, 진행 상태 표, W2-02.4 사용자 보고, Acceptance Criteria, 산출물, Commit 메시지) **10개 위치에 사실 오류 잔존**. cycle 1 #20 ("sub-plan 박제 vs 실제 git 상태 불일치") + #15 ("sub-plan 내부 동시 정정 누락") 카테고리 **재차 재발**. 부분 정정으로 자기 모순 신규 도입 = **BLOCKING 신규 (NEW-B-1)**.

### B-2 정정 정확성: **PARTIAL FAIL**

**정정된 부분 (PASS)**:
- L78 candidate-pool.md cross-document 정정 책무 명시 OK
- L189-194 파라미터 표 (W2-02.2): 출처를 "Keltner 1960 원 설계값 (1.5 ATR)"에서 "ChartSchool/StockCharts 표준 변형 + Raschke 1990s 후속" + "Chester Keltner (1960) 원 설계는 EMA(typical, 10) ± 1.0 × 10일 daily range로 다름" 정정 — 감사관 1차 의견(B-2 선택 1) 채택 OK.
- L200-208 ta 라이브러리 직접 호출 박제: `KeltnerChannel(window=20, window_atr=14, original_version=False, multiplier=1.5)` 명시 — **감사관 venv 직접 검증 결과 정확 동작 확인** (mid = `EMA(close,20)`, upper - mid = `1.5×ATR(14)` numpy.allclose 일치. multiplier=1.5 float 값 적용 확인. signature는 `int=2`이지만 실제 동작 정상).
- L210 `keltner_mid = kc.keltner_channel_mband()` # `original_version=False` 시 `EMA(close, 20)` 명시 OK
- L221 박제 충돌 위험 alarm OK ("`window_atr` + `multiplier` + `original_version` 모두 명시 안 하면 ta default 적용 → 박제값과 다른 결과")
- candidate-pool.md L48 cross-document 전파: "ChartSchool/StockCharts 표준 변형 + Raschke 1990s 후속... Chester Keltner (1960) 원 설계는 EMA(typical, 10) ± 1.0 × 10일 daily range로 다름 (ta venv 직접 검증, 2026-04-19, B-2 정정)" — 본문 직접 확인 일치.
- decisions-final.md L539-541 cross-document 전파: `Keltner(window=20, window_atr=14, multiplier=1.5, original_version=False)` 박제 + ChartSchool/Raschke 출처 + ta 호출 시 모든 파라미터 명시 필수 alarm — 본문 직접 확인 일치.

**잔존 사실 오류 + 자기 모순 (FAIL — BLOCKING 신규)**:

**L246-250 (W2-02.2 vectorbt 0.28.5 구현 가이드 코드 블록)**:
```python
from ta.volatility import AverageTrueRange, BollingerBands, KeltnerChannel
atr = AverageTrueRange(high, low, close, window=ATR_WINDOW).average_true_range()
kma = close.rolling(KELTNER_WINDOW).mean()       # ← SMA of close, EMA 아님
keltner_upper = kma + KELTNER_ATR_MULT * atr     # ← 직접 계산, ta KeltnerChannel 미사용
keltner_mid = kma                                  # ← SMA of close, B-2 정정 위반
```

- **자기 모순**: 같은 sub-plan W2-02.2 섹션 내에서:
  - L188-221 (파라미터 박제 + ta 호출 가이드): `original_version=False`, mid = `EMA(close,20)`, ta `keltner_channel_mband()` 사용 명시.
  - L234 박제: "Keltner mid 정의 명확화 (B-4): `keltner_mid = EMA(close, 20)` (ta `original_version=False` 기준). SMA 아님" — 명시적으로 "SMA 아님" 박제.
  - L246-250 vectorbt 구현 가이드 코드: `kma = close.rolling(20).mean()` = **SMA**, `keltner_mid = kma` = **SMA of close**, ta `KeltnerChannel` import만 하고 미사용.
- **B-2 부분 정정**: B-2 1차 감사 핵심 발견 = "KeltnerChannel을 import만 하고 실제 메서드 (`keltner_channel_hband()`, `keltner_channel_mband()`)를 사용 안 한 것 = ta API 추측 우회". v2 정정은 L200-208에서 ta 호출 박제 추가했으나 **L246-250 vectorbt 구현 가이드 코드 블록은 v1 그대로 (SMA + 직접 계산)** 유지. 같은 카테고리 미해결.
- **W2-03 구현 위험**: W2-03 작성자가 sub-plan 읽을 때 "구현 가이드" 라벨이 붙은 L246-250 코드 블록을 채택 가능 → SMA-of-close + 직접 계산 = 박제 (EMA-close + ta 라이브러리 정확 호출)와 다른 결과. cherry-pick 통로 잠재.
- **handover #16 (외부 라이브러리 추측) + #15 (cross-document/내부 전파 누락)** 카테고리 **재차 재발**.

**판정**: B-2 정정은 파라미터 표/ta 호출 가이드/cross-document 전파(candidate-pool.md, decisions-final.md)는 정확하지만 **sub-plan 자체 vectorbt 구현 가이드 코드 블록(L246-250) 정정 누락** = **BLOCKING 신규 (NEW-B-2)**.

### B-3 정정 정확성: **PASS**

L103 박제: `(MA50 > MA200) AND (MA50.shift(1) <= MA200.shift(1))` strict crossover 명시 + "동등 (`==`) 케이스는 false → 명확한 strict crossover만 trigger. 청산 후 동일 추세 내 재진입 X (다음 골든 크로스까지 대기)" — 1차 감사 권고 정확 반영.

L105 exit strict crossover 박제 동일 OK + ATR trailing OR 결합 명시 OK.

L137-138 의사 코드 vectorbt + pandas crossover 패턴 정확 (`shift(1)` 사용). pandas API 표준 패턴 일치.

NIT-2(1차) "Candidate C long-only 명시 부재" 해소: L106 "long-only (NIT-2 해소)" 명시 OK.

### B-4 정정 정확성: **PASS (단 자기 모순 잔존)**

**정정된 부분 (PASS)**:
- L226 entry strict crossover 명시: `(close > kc_upper) AND (close.shift(1) <= kc_upper.shift(1)) AND (close > bb_upper) AND (close.shift(1) <= bb_upper.shift(1))` — 1차 감사 박제 패턴 정확.
- L228-230 Exit strict crossover (Keltner mid 하향) + Hard SL 8% OR 결합 명시 OK.
- L231 vectorbt entry/exit 우선순위 명시: "같은 bar에 entry + sl_stop 발동 시 exit 우선 (vectorbt 기본 동작), entry + exit_mask 동시 발동 시 entry 우선 (single bar trip 차단)" — vectorbt 0.28.5 기본 동작과 일치 여부는 본 차원에서 정확 검증 안 됨 (sl_stop 우선 vs entry 우선 default 정책은 `upon_long_conflict` 등 옵션 의존). NIT 권고: 박제 출처 vectorbt docstring 인용 추가.
- L232 long-only 명시 OK (NIT-2 해소).
- L234 keltner_mid = `EMA(close, 20)` (ta `original_version=False` 기준). SMA 아님" — B-2 정정과 일관.

**자기 모순 잔존 (NEW-B-2와 겹침)**:
- L234 박제 "EMA(close, 20). SMA 아님" vs L250 코드 `keltner_mid = kma` (SMA of close). 같은 sub-plan 자기 모순. NEW-B-2 BLOCKING으로 분류.

**판정**: B-4 자체 정정은 정확하나 L246-250 코드 블록의 SMA vs L234 박제의 EMA가 모순 = NEW-B-2 BLOCKING의 부분 영역.

---

## cross-document 전파 정확성

| 위치 | 정정 정확성 | 근거 |
|------|------------|------|
| candidate-pool.md L48 | **PASS** | "ChartSchool/StockCharts 표준 변형 + Raschke 1990s 후속... Chester Keltner (1960) 원 설계는 EMA(typical, 10) ± 1.0 × 10일 daily range로 다름 (ta venv 직접 검증, 2026-04-19, B-2 정정)" — 본문 직접 확인 일치. ta 라이브러리 호출 알람 박제 OK. |
| decisions-final.md L539-541 | **PASS** | `Keltner(window=20, window_atr=14, multiplier=1.5, original_version=False)` + ChartSchool/Raschke 출처 + ta 호출 시 `original_version=False + window_atr=14 + multiplier=1.5` 모두 명시 필수 alarm — 본문 직접 확인 일치. ta venv 검증 인용 OK. |
| sub-plan W2-02.2 파라미터 표 (L189-194) | **PASS** | candidate-pool.md L48 + decisions-final.md L539-541 모두 일관. |
| sub-plan W2-02.2 ta 호출 박제 (L200-208) | **PASS** | 3 문서 일관. |
| sub-plan W2-02.2 vectorbt 구현 가이드 코드 (L246-250) | **FAIL** | L246-250 코드 블록은 SMA + 직접 계산 = 위 3 문서 박제와 모순. NEW-B-2 BLOCKING. |

cross-document 3 문서(candidate-pool.md, decisions-final.md, sub-plan W2-02.2 파라미터/ta 호출) 일관성은 우수. 그러나 sub-plan 내부 동일 섹션 코드 블록 누락이 cross-document 일관성을 무력화 — W2-03 구현 단계에서 어느 박제가 권위인지 모호 (parameter 표/ta 호출 vs vectorbt 구현 가이드 코드 = 상호 모순).

---

## 새 발견 사항

### BLOCKING (2건)

#### NEW-B-1 (L1, L43, L54, L309, L315, L319, L330, L355, L375, L377) — B-1 정정 부분 적용 + sub-plan 내 10개 위치 "신설" 잔존

**잔존 위치 enumeration**:
- L1: `# Task W2-02 — 새 전략 후보 사전 등록 (Candidate C, D + candidate-pool 신설)` (메타 타이틀)
- L43: `**Strategy A 후보 풀 물리화**: candidate-pool.md 신설 (cycle 1 박제 W2-01.1 누락 정정)` (배경 핵심 원칙)
- L54: 진행 상태 표 W2-02.0 메모 `candidate-pool.md 신설 (W2-01.1 박제 누락 정정)`
- L309: W2-02.4 사용자 보고 항목 `candidate-pool.md 신설 + Strategy A/B/C/D 통합`
- L315: W2-02.4 commit `+ candidate-pool.md 신설`
- L319: 인수 완료 조건 `docs/candidate-pool.md 신설 (W2-01.1 박제 누락 정정 + Strategy A/B 박제 + C/D placeholder)`
- L330: 인수 완료 조건 `candidate-pool.md + sub-plan + handover 갱신 + 커밋` (단독은 OK이지만 L319와 함께 모순)
- L355: 산출물 `docs/candidate-pool.md (신설, Retained/Pending/Deprecated 통합 관리)`
- L375, L377: Commit 예상 메시지 본문 + 헤더

**문제**:
- 자기 모순: W2-02.0 본문(L68) "사실 오류 — 이미 신설 완료" 박제 vs 위 10개 위치 "신설" 박제 = 같은 sub-plan 내 사실 충돌.
- cycle 1 #15 (cross-document/내부 전파 누락) + #20 (sub-plan 박제 vs 실제 git 상태 불일치) 패턴 **3차 재발** (1차 감사 → v2 부분 정정 → 2차 감사에서 잔존 발견).
- 사용자 보고/git commit 시점에 거짓 사실 전달 위험. CLAUDE.md root Maintenance Policy "괴리 즉시 보고" 위반.

**수정 권고**: 위 10개 위치를 W2-02.0 본문(L62-80)과 동일 표현으로 통일:
- L1 → "Candidate C, D Pending → Active 전이 + 사전 등록"
- L43 → "Strategy C/D Pending → Active 전이 + 잠정 파라미터 freeze + Recall mechanism 강화"
- L54 → "candidate-pool.md Strategy C/D Pending → Active 전이 + B-2 Keltner 출처 정정"
- L309 → "candidate-pool.md Strategy C/D Pending → Active 전이 + B-2 Keltner 출처 정정"
- L315, L375, L377 commit 메시지 → "candidate-pool.md 갱신 (Pending → Active + B-2 Keltner 출처 정정)"
- L319 → "candidate-pool.md 갱신 (Strategy C/D Pending → Active 전이 + B-2 Keltner 출처 정정)"
- L355 → "docs/candidate-pool.md (갱신, Pending → Active 전이)"

#### NEW-B-2 (L246-250) — B-2 정정 부분 적용 + W2-02.2 vectorbt 구현 가이드 코드 블록에 SMA + ta 미사용 잔존

**문제**:
- L246-250 코드 블록이 1차 감사 B-2 핵심 지적사항 (`KeltnerChannel` import만 하고 직접 계산식 사용 = ta API 추측 우회) **그대로 잔존**:
  ```python
  from ta.volatility import AverageTrueRange, BollingerBands, KeltnerChannel
  atr = AverageTrueRange(high, low, close, window=ATR_WINDOW).average_true_range()
  kma = close.rolling(KELTNER_WINDOW).mean()       # SMA of close
  keltner_upper = kma + KELTNER_ATR_MULT * atr     # 직접 계산, ta 미사용
  keltner_mid = kma                                  # SMA of close
  ```
- 같은 sub-plan W2-02.2 섹션 L188-221 (파라미터/ta 호출 박제) + L234 ("EMA(close, 20). SMA 아님") 박제와 정면 모순.
- W2-03 구현 위험: 작성자가 "vectorbt 0.28.5 구현 가이드" 라벨 붙은 코드 블록을 채택 시 박제와 다른 결과 (SMA-close 대신 EMA-close, 직접 계산 대신 ta 라이브러리 호출). cherry-pick 통로 잠재.
- handover #16 (외부 라이브러리 추측) + #14 (cherry-pick 경로 재유입) + #15 (sub-plan 내 동시 정정 누락) **3차 재발**.

**수정 권고**: L246-250 코드 블록을 다음으로 교체 (감사관 venv 검증 완료):
```python
from ta.volatility import KeltnerChannel, BollingerBands

# Candidate D 박제 (W2-02.2 파라미터 표 + ta 호출 박제와 동일)
kc = KeltnerChannel(
    high=high, low=low, close=close,
    window=KELTNER_WINDOW,
    window_atr=ATR_WINDOW,
    original_version=False,
    multiplier=KELTNER_ATR_MULT,
)
keltner_upper = kc.keltner_channel_hband()
keltner_mid = kc.keltner_channel_mband()  # EMA(close, 20)

bb = BollingerBands(close=close, window=BOLLINGER_WINDOW, window_dev=BOLLINGER_SIGMA)
bb_upper = bb.bollinger_hband()

# (이하 both_break, mid_exit, vbt.Portfolio.from_signals 동일)
```

### WARNING (0건 신규)

본 2차 감사에서 **신규 WARNING 발견 X**. 1차 감사 WARNING 5건 (W-1 ~ W-5) 잔존 (옵션 A 정책상 허용).

### NIT (1건 신규)

#### NEW-NIT-1 (L231) — vectorbt entry/exit 우선순위 박제 출처 인용 부재

L231 박제: "같은 bar에 entry + sl_stop 발동 시 exit 우선 (vectorbt 기본 동작), entry + exit_mask 동시 발동 시 entry 우선 (single bar trip 차단)"

- vectorbt 0.28.5 default 동작 정확성은 `upon_long_conflict`, `upon_dir_conflict` 옵션 의존. 본 박제는 어떤 default를 가정하는지 명시 부재.
- 박제 출처 (vectorbt docstring 또는 nb 코드 라인 인용) 추가 권고. W2-03 구현 시 mini test로 재검증 권고 (W-1과 동일 카테고리이지만 sl_stop 동작 자체는 W-1, sl_stop vs exit_mask 우선순위는 본 NEW-NIT-1).

---

## 잔존 WARNING/NIT 변동 (1차 → v2)

| 1차 항목 | v2 잔존 여부 | 변동 사유 |
|---------|------------|---------|
| W-1 (ATR trailing stop vectorbt sl_stop 동작 미검증) | **잔존** | L121-161 박제 변경 X. 옵션 A 정책상 허용 |
| W-2 (MA200 regime decay 공유 위험 박제 부재) | **잔존** | 차별화 표 L110-119 변경 X. 옵션 A 허용 |
| W-3 (Soft contamination layer 박제 부분) | **잔존** | L165-168 박제 변경 X. 옵션 A 허용 |
| W-4 (Secondary 마킹 "Tier 1+2 3+ 페어" 부분 인용) | **잔존** | L325 박제 그대로. 옵션 A 허용 |
| W-5 (사용자 승인 시점 발효 박제 명시 부재) | **잔존** | W2-02.4 박제 변경 X. 옵션 A 허용 |
| NIT-1 (Tier 2 페어 수 정합성) | **잔존** | sub-plan L26 변경 X. handover와 일관 |
| NIT-2 (Candidate C long-only 명시 부재) | **완전 해소** | L106 "long-only (NIT-2 해소)" + L232 "long-only (NIT-2 해소)" 박제 추가 |
| NIT-3 (Acceptance Criteria 시점 박제 누락) | **잔존** | 변경 X. 옵션 A 허용 |
| NIT-4 (commit 메시지 "신설" 정정) | **잔존 + BLOCKING으로 격상** | L315/L375/L377 commit 메시지 잔존 = NEW-B-1 일부로 흡수 (사용자 보고 + git commit 시점 사실 오류 = BLOCKING 카테고리) |

**잔존 항목 BLOCKING 격상 위험**:
- NIT-4 → NEW-B-1 흡수: 1차 감사 NIT 분류였으나 2차 감사에서 자기 모순 + 사용자/git 거짓 사실 전달 위험으로 BLOCKING 격상 (옵션 A "BLOCKING만 정정" 정책에 도전).
- W-1, W-4는 W2-03 구현 시 재발 위험 매우 높음 (cherry-pick 통로). 옵션 A 결정 시 W2-03 sub-plan 작성 단계에서 의무 정정 책무 박제 권고.

---

## cycle 1/2 학습 패턴 재발 검증 (handover v8 #1~#20)

| # | 패턴 | 1차 감사 결과 | 2차 감사 결과 |
|---|------|-------------|-------------|
| #11 | 측정 창 inclusive off-by-one (신호 시점 ambiguity) | 재발 (B-3, B-4) | **해소** (B-3, B-4 PASS) |
| #13 | 박제 시점 발효 순환 정의 | 재발 (W-5) | 잔존 (옵션 A 허용) |
| #14 | 실측 cherry-pick 경로 재유입 | 간접 재발 (B-3) | **부분 해소 (B-3) + 신규 재발 (NEW-B-2 코드 블록 cherry-pick 통로)** |
| #15 | sub-plan/decisions-final 전파 누락 | 재발 (B-2) | **부분 해소 (B-2 cross-document 전파 OK) + 신규 재발 (NEW-B-1 sub-plan 내부 전파 누락 + NEW-B-2 sub-plan 내부 전파 누락)** |
| #16 | 외부 라이브러리 응답 필드 추측 | 재발 (B-2, W-1) | **부분 해소 (B-2 ta 호출 박제 정확) + 신규 재발 (NEW-B-2 vectorbt 구현 가이드 코드 블록 ta 미사용 잔존)** |
| #20 | sub-plan 박제 vs 실제 상태 불일치 | 재발 (B-1) | **부분 해소 (W2-02.0 본문) + 신규 재발 (NEW-B-1 10개 위치 "신설" 잔존)** |

**재발 카테고리 합계**: cycle 1 → 6개 → cycle 2 → 5개 (#11 해소). 그러나 **#14, #15, #16, #20이 "부분 해소 + 신규 재발" 패턴으로 변형 = 4 카테고리 재발 패턴 누적**. 같은 카테고리가 같은 sub-plan에서 1차 감사 → v2 부분 정정 → 2차 감사에서 다시 발견 = **누적 재발 심화**.

**핵심 진단**: cycle 1/2 학습이 "BLOCKING 발견 → 본문 한 곳만 정정" 패턴으로 적용되어 **sub-plan 전체 일관성 검증 단계 부재**. 결과적으로 같은 BLOCKING이 다른 위치에 잔존 + 자기 모순으로 변형. **sub-plan 정정 시 grep-based 전체 일관성 점검 패턴 의무화 권고**.

---

## 종합 평가

### A. v2 BLOCKING 정정 품질

- B-1: **PARTIAL FAIL** (W2-02.0 본문만 정정, 10개 위치 잔존 → NEW-B-1)
- B-2: **PARTIAL FAIL** (파라미터/ta 호출/cross-document 정정 OK, vectorbt 구현 코드 블록 잔존 → NEW-B-2)
- B-3: **PASS**
- B-4: **PASS** (단 NEW-B-2와 겹치는 keltner_mid 모순 부분은 NEW-B-2로 분류)

종합 정정 품질: **2/4 PASS, 2/4 PARTIAL FAIL**. 옵션 A "BLOCKING만 정정" 정책에 따라 진행되었으나 정정 자체가 부분적이어서 **신규 BLOCKING 도입** = 옵션 A 의도 위반.

### B. cross-document 전파 우수성

- candidate-pool.md L48 + decisions-final.md L539-541 + sub-plan 파라미터/ta 호출 박제 = **3 문서 일관**.
- 그러나 sub-plan 내부 vectorbt 구현 가이드 코드 블록 정정 누락이 일관성 무력화.

### C. 외부 라이브러리 직접 검증 우수성

- v2 정정에서 ta KeltnerChannel `original_version=False, window_atr=14, multiplier=1.5` 박제 = **감사관 venv 직접 검증 결과 정확** (mid = `EMA(close,20)`, upper-mid = `1.5×ATR(14)`, multiplier float 허용 모두 numpy.allclose 일치).
- root CLAUDE.md L40 Immutable "외부 라이브러리 API 사용 시 공식 docs 또는 소스 직접 확인" 룰 부분 준수 (ta 호출 가이드는 정확, 그러나 vectorbt 구현 가이드 코드 블록은 추측 잔존).

### D. 신규 약점 도입

- **NEW-B-1**: sub-plan 내 10개 위치 "신설" 잔존 = 자기 모순 신규 도입.
- **NEW-B-2**: sub-plan W2-02.2 vectorbt 구현 가이드 코드 블록 SMA + 직접 계산 잔존 = 박제와 정면 모순.
- **NEW-NIT-1**: vectorbt entry/exit 우선순위 박제 출처 인용 부재.

### E. 박제 라벨 일관성

- sub-plan v2 라벨 명시 부재 (1차 감사 후 정정했다는 메타 박제 부재). NIT 카테고리 (옵션 A 허용).
- candidate-pool.md 변경 이력 v2 행 추가 책무는 sub-plan L80에 명시되었으나 실제 candidate-pool.md L88 변경 이력 표는 v2 행 미추가 = 책무 미수행 단계 (W2-02.0 미시작 상태이므로 OK이지만 책무 박제 자체는 정확).

---

## 외부 감사관 의견

**판정 = CHANGES REQUIRED (신규 BLOCKING 2건).**

본 2차 감사는 1차 감사 BLOCKING 4건 정정의 **부분 적용 + 자기 모순 신규 도입**을 발견했다. 옵션 A ("BLOCKING만 정정") 결정 자체는 사용자의 정책 선택이지만, **B-1/B-2 정정 자체가 부분적이어서 신규 BLOCKING을 도입한 상태**는 옵션 A 의도 ("WARNING/NIT만 잔존, BLOCKING 0") 위반.

**우선순위 권고**:

1. **NEW-B-1 정정 (10개 위치 일괄)**: L1, L43, L54, L309, L315, L319, L330, L355, L375, L377 모두 W2-02.0 본문(L62-80)과 동일 표현 ("Pending → Active 전이" 또는 "갱신")으로 통일. **grep `신설` 으로 전체 점검 후 정정**. commit 메시지도 동시 정정.

2. **NEW-B-2 정정 (L246-250 코드 블록)**: ta `KeltnerChannel(window=20, window_atr=14, original_version=False, multiplier=1.5)` 호출로 교체 + `keltner_channel_hband()` / `keltner_channel_mband()` 메서드 사용. SMA → EMA 정정. 감사관 venv 검증 코드 그대로 인용 가능.

3. **선택적 (옵션 A 정책 재확인)**:
   - 잔존 W-1 (vectorbt sl_stop Series + sl_trail=True 결합 동작 미검증)는 W2-03 구현 단계에서 mini test 의무 박제로 위임.
   - 잔존 W-4 (Secondary 마킹 Tier 1+2 3+ 페어 부분 인용)는 W2-03 평가 정책 박제 시 정확 인용 의무.
   - W-2/W-3/W-5/NIT-1/NIT-3는 옵션 A 결정 그대로 잔존 허용.

4. **3차 감사 (또는 사용자 결정)**:
   - **권고 1 (cycle 1 W2-01.1 패턴)**: NEW-B-1 + NEW-B-2 정정 후 3차 감사 (다른 외부 감사관에게 위임 권장, rubber-stamp 방지).
   - **권고 2 (사용자 명시 결정)**: NEW-B-1 + NEW-B-2가 "부분 정정 잔존"이라는 점에서 BLOCKING이 아닌 NIT/WARNING 카테고리로 사용자가 직접 판정 시 옵션 A 재해석 가능. 단 사용자 직접 판정 시 cherry-pick 통로 (W2-03 작성자가 어느 박제 채택할지 모호) 위험 인정 박제 필수.

**감사관 자가 검증 (rubber-stamp 회피)**:
- 본 2차 감사는 1차 감사 BLOCKING 4건 정정을 **검증 없이 통과시키지 않음** = rubber-stamp X.
- 검증 도구: ta KeltnerChannel venv 직접 호출 + numpy.allclose 동작 검증 + vectorbt 0.28.5 signature 직접 확인 + candidate-pool.md/decisions-final.md/sub-plan 본문 직접 read + grep으로 "신설" 잔존 위치 enumerate.
- 발견 깊이: 1차 감사 BLOCKING 4 + WARNING 5 + NIT 4. 2차 감사 BLOCKING 2 신규 + NIT 1 신규 + 잔존 WARNING/NIT 변동 분석. 3차 감사 권장.
- 본 감사관도 한계 인정:
  - vectorbt sl_stop Series + sl_trail=True 결합 동작 정확성 (W-1)은 본 차원에서도 mini test 미수행 (옵션 A 정책상 잔존 허용 신호).
  - vectorbt entry/exit 우선순위 default (NEW-NIT-1)도 docstring 인용 미수행 = 본 감사관 한계.
  - sub-plan v2 정정의 의도 ("L246-250 코드 블록 정정 누락이 의도적인지 부주의인지")는 외부에서 판정 불가. 사용자 직접 확인 권고.

**최종 권고**: NEW-B-1 + NEW-B-2 정정 후 사용자 명시 결정으로 진행 가능 (3차 감사는 옵션). 단 정정 시 grep-based 전체 일관성 점검 패턴 의무 적용. cycle 1/2 학습 메타 패턴 ("부분 정정 → 자기 모순 도입")이 다음 sub-plan에서 재발하지 않도록 handover에 박제 추가 권고.

---

# 3차 감사 (2026-04-19, v3 정정 후)

## 3차 감사 판정

**APPROVED with follow-up** (BLOCKING 0건 신규 발견 + WARNING 1건 신규 + NIT 2건 신규).

v3 정정은 NEW-B-1 + NEW-B-2 둘 다 정확하게 적용되었으며, ta KeltnerChannel 호출 박제는 감사관 venv에서 numerical 검증 (max abs diff 0.0)으로 확인됨. 다만 sub-plan 내부 "Active 전이" vs "Registered" 라벨 미세 불일치 + W2-02.0 책무 박제와 W2-02.4 commit 메시지 불일치 등 NIT 카테고리 미완성 잔존 — 본 감사는 옵션 A 정책 (BLOCKING만 정정) 하에서 사용자 명시 승인으로 진행 권고.

---

## NEW-B-1 정정 검증 (10개 위치 + "신설" 사실 인용 4개)

**grep `신설` 결과** (sub-plan w2-02-strategy-candidates.md):
- L43: "candidate-pool.md 2026-04-17 신설" — 사실 인용 OK (정확)
- L68: "candidate-pool.md는 이미 신설 완료" — 사실 인용 OK (정확)
- L327: "candidate-pool.md 자체는 2026-04-17 신설 완료" — 사실 인용 OK (정확)
- L385: "파일 자체는 2026-04-17 99b281d 신설 완료" — 사실 인용 OK (정확)

**잔존 4개 = 사용자 박제 의도 4개와 정확 일치**. 추가 잔존 0개.

**v3 정정 위치 점검** (Pending → Active 전이 / 갱신 표현으로 통일):
- L1 타이틀: "Candidate C, D Pending → Active 전이" — PASS
- L43 핵심 원칙: "이미 박제됨 ... W2-02는 Strategy C/D Pending → Active 전이 책무" — PASS
- L54 SubTask 표: "Pending → Active 전이 (B-1 정정)" — PASS
- L62 SubTask 헤더: "Pending → Active 전이 (B-1 정정)" — PASS
- L70 책무: "Pending → Active 전이" — PASS
- L80 변경 이력 박제: "Pending → Active 전이 + B-2 Keltner 출처 정정" — PASS
- L317 보고: "Pending → Active 전이 + Strategy A Recall 강화" — PASS
- L323 commit msg: "Pending → Active 전이 + Keltner 출처 정정" — PASS
- L327 AC: "Pending → Active 전이 (B-1 정정, candidate-pool.md 자체는 2026-04-17 신설 완료)" — PASS
- L355 리스크 표: candidate-pool.md "Recall mechanism" 박제 인용 (`신설` 표현 무관) — N/A
- L363 산출물: "기존 파일 갱신, Strategy C/D Pending → Active 전이" — PASS
- L383 commit body 헤더: "Pending → Active 전이 + Keltner 출처 정정" — PASS
- L385 commit body 본문: "갱신 (B-1 정정, 파일 자체는 2026-04-17 99b281d 신설 완료)" — PASS

**판정**: NEW-B-1 정정 **PASS**. 자기 모순 신규 도입 0건. 메타/배경/AC/산출물/commit msg 일관성 회복 완료.

---

## NEW-B-2 정정 검증 (ta KeltnerChannel API 호출)

### venv 직접 검증 (감사관 책임 수행)

```
$ source research/.venv/bin/activate && python -c "..."
KeltnerChannel signature: (high, low, close, window=20, window_atr=10, fillna=False, original_version=True, multiplier=2)

  window: default=20
  window_atr: default=10            ← sub-plan 박제 14는 명시 필수
  original_version: default=True    ← sub-plan 박제 False는 명시 필수
  multiplier: default=2             ← sub-plan 박제 1.5는 명시 필수

Methods (확인): keltner_channel_hband, keltner_channel_mband (모두 존재)
```

### Numerical 일치성 검증

```
synthetic data n=200, seed=42:
- mid vs EMA(close, 20) max abs diff: 0.0
- mid == EMA(close, 20)?: True       ← L210, L234, L258 박제 정확
- upper vs EMA(close, 20) + 1.5*ATR(14) max abs diff: 0.0
- upper == EMA + 1.5*ATR?: True      ← L209, L257 박제 정확
```

### v3 코드 블록 검증 (L246-258)

- ta KeltnerChannel 직접 사용 — PASS (SMA 직접 계산 제거)
- `window=KELTNER_WINDOW` (=20) — PASS
- `window_atr=ATR_WINDOW` (=14, ta default 10과 다름, 명시 필수) — PASS
- `original_version=False` (ta default True와 다름, 명시 필수) — PASS
- `multiplier=KELTNER_ATR_MULT` (=1.5, ta default 2와 다름, 명시 필수) — PASS
- `kc.keltner_channel_hband()` + `kc.keltner_channel_mband()` 메서드 사용 — PASS
- L258 주석 "EMA(close, 20)" — venv 직접 검증 일치 PASS
- L234 박제 "keltner_mid = EMA(close, 20). SMA 아님" vs L246-258 호출 — 일관 PASS
- ATR_WINDOW=14 vs ta `window_atr=14` 인자 매칭 — PASS
- multiplier=1.5 vs ta `multiplier=1.5` 인자 매칭 — PASS
- `original_version=False` 명시 (default True와 차이 박제) — PASS

**판정**: NEW-B-2 정정 **PASS**. NEW-B-2 sub-plan 내부 자기 모순 완전 해소.

---

## cross-document 전파 정확성 (3 문서 일관)

| 위치 | 박제 |
|------|------|
| `docs/candidate-pool.md` L48 | "Bollinger 1983 (BB 기본값 20, 2σ) + ChartSchool/StockCharts 표준 변형 + Raschke 1990s 후속 (Keltner KC_PERIOD=20, KC_ATR_MULT=1.5). Chester Keltner (1960) 원 설계는 EMA(typical, 10) ± 1.0 × 10일 daily range로 다름 (ta venv 직접 검증, 2026-04-19, B-2 정정)" |
| `docs/decisions-final.md` L539-541 | "Candidate D — Volatility Breakout (Keltner(window=20, window_atr=14, multiplier=1.5, original_version=False) + Bollinger(20, 2σ) 동시 돌파) ... Chester Keltner (1960) 원 설계는 EMA(typical price, 10) ± 1.0 × 10일 daily range로 다름 (ta venv 직접 검증 결과, 2026-04-19 W2-02 외부 감사 B-2 정정). ta KeltnerChannel 호출 시 original_version=False + window_atr=14 + multiplier=1.5 모두 명시 필수 (default와 다름)" |
| `docs/stage1-subplans/w2-02-strategy-candidates.md` L188-258 (W2-02.2 박제) | 동일 파라미터 + ta 호출 박제 + L246-258 vectorbt 구현 가이드 코드 블록도 일관 |

**판정**: 3 문서 일관 **PASS**. 한 곳만 정정하고 다른 곳 누락 X. NEW-B-2 정정이 sub-plan 내부 코드 블록까지 전파됨.

---

## 새 발견 사항

### BLOCKING (0건)

**없음.** v3 정정은 NEW-B-1 + NEW-B-2 핵심 책무를 정확히 수행했으며, 신규 BLOCKING 도입 없음.

### WARNING (1건 신규)

#### W3-1 (L209, L258 docstring 한정 정확성 미완)

L210/L258 박제 "original_version=False 시 EMA(close, 20)"는 venv 직접 검증으로 정확하지만, **ta 0.11.x 소스(`ta/volatility.py` `KeltnerChannel._run`)에서 `original_version=False`일 때 `tp = self._close`만 사용 (typical price 아닌 close 단독)**의 출처 인용이 부재. 본 감사관 venv 검증으로 사실은 확인되었으나, sub-plan 박제는 "ta default original_version=True 시 EMA(typical price, 10) 변형 vs False 시 close 사용" 명시적 차이 박제 부재. cherry-pick 통로 잠재 (ta 향후 버전 변경 시 재검증 책무 부재).

**완화 권고**: L222 "박제 충돌 위험 alarm" 박스에 "ta 향후 버전 변경 시 재검증 책무" 한 줄 추가. W2-03 구현 시 mini test 의무 박제로 위임도 가능.

### NIT (2건 신규)

#### N3-1 (L172, L388 — "Pending → Registered" vs "Pending → Active 전이" 라벨 불일치)

- L172 (W2-02.1 AC): "Candidate C ... 박제 (`candidate-pool.md` Pending → Registered)" — "Registered"
- L286 (W2-02.2 AC): "Candidate D ... 박제 (`candidate-pool.md`)" — 라벨 무
- L388 (commit body): "Pending → Registered: Candidate C, D" — "Registered"
- 그 외 모든 위치 (L1, L43, L54, L62, L70, L80, L317, L323, L327, L355, L363, L383): "Pending → Active 전이"

candidate-pool.md L8 (3단계 정의: Active / Retained / Deprecated)에 따르면 "Active"가 표준 라벨. "Registered"는 비표준. v3 정정에서 L172/L388 누락된 듯.

**완화 권고**: L172 "Pending → Registered" → "Pending → Active 전이". L286 AC에도 "Pending → Active 전이" 명시 추가. L388 동일 정정. (옵션 A 정책 하 NIT 잔존 허용 가능, 단 W-2-03 작성자 cherry-pick 위험 미세하게 잠재.)

#### N3-2 (L246 코드 블록 변수명 일관성 미세)

L264-271 `both_break`, `mid_exit` 변수명은 W2-02.2 본문 L225-229 "Long entry"/"Exit" 박제와 의미 일관하지만, 본문은 명시 변수명 부재 — 변수명 박제 통일 가능 (NIT). 옵션 A 잔존 허용.

---

## 잔존 WARNING/NIT 변동 (1차 → 2차 → v3)

| 1차 항목 | v2 잔존 | v3 잔존 | 변동 사유 |
|---------|--------|--------|---------|
| W-1 (ATR trailing stop sl_stop 동작 미검증) | 잔존 | **잔존** | L121-161 변경 X. 옵션 A 정책상 W2-03 위임 |
| W-2 (MA200 regime decay 공유 위험 박제 부재) | 잔존 | **잔존** | L110-119 변경 X. 옵션 A 허용 |
| W-3 (Soft contamination layer 박제 부분) | 잔존 | **잔존** | L165-168 변경 X. 옵션 A 허용 |
| W-4 (Secondary 마킹 "Tier 1+2 3+ 페어" 부분 인용) | 잔존 | **잔존** | L333 (이전 L325) 변경 X. 옵션 A 허용 |
| W-5 (사용자 승인 시점 발효 박제 명시 부재) | 잔존 | **잔존** | W2-02.4 변경 X. 옵션 A 허용 |
| NIT-1 (Tier 2 페어 수 정합성) | 잔존 | **잔존** | L26 변경 X |
| NIT-2 (Candidate C long-only 명시 부재) | 완전 해소 | **완전 해소** | v2 정정 유지 |
| NIT-3 (Acceptance Criteria 시점 박제 누락) | 잔존 | **잔존** | 옵션 A 허용 |
| NIT-4 → NEW-B-1 흡수 → v3 정정 | BLOCKING 격상 | **완전 해소** | v3 grep-based 정정 패턴 적용 결과 |
| NEW-NIT-1 (vectorbt entry/exit 우선순위 출처 인용 부재) | 신규 | **잔존** | L231 변경 X. 옵션 A 허용 |

**핵심 변동**: NEW-B-1, NEW-B-2 둘 다 v3에서 완전 해소. 옵션 A "BLOCKING 0 + WARNING/NIT 잔존" 의도 회복.

---

## cycle 1/2 학습 패턴 재발 검증 (handover v8 #1~#20)

| # | 패턴 | 1차 → 2차 → v3 | 평가 |
|---|------|---------------|------|
| #11 | 측정 창 inclusive off-by-one (신호 시점 ambiguity) | 재발 → 해소 → 해소 유지 | OK |
| #13 | 박제 시점 발효 순환 정의 | 재발 (W-5) → 잔존 → 잔존 (옵션 A 허용) | 변동 X |
| #14 | 실측 cherry-pick 경로 재유입 | 간접 재발 (B-3) → 부분 해소 + 신규 재발 (NEW-B-2) → **완전 해소** | NEW-B-2 v3 정정으로 코드 블록 cherry-pick 통로 폐쇄 |
| #15 | sub-plan/decisions-final 전파 누락 | 재발 (B-2) → 부분 해소 + 신규 재발 (NEW-B-1, NEW-B-2 sub-plan 내부) → **완전 해소** | v3 grep-based 점검 + 코드 블록 정정 양쪽 수행 |
| #16 | 외부 라이브러리 응답 필드 추측 | 재발 (B-2, W-1) → 부분 해소 + 신규 재발 (NEW-B-2) → **완전 해소** | v3 ta 직접 호출로 추측 박제 제거 |
| #20 | sub-plan 박제 vs 실제 상태 불일치 | 재발 (B-1) → 부분 해소 + 신규 재발 (NEW-B-1 10개 위치) → **완전 해소** | v3 grep-based 정정 패턴 적용 |

**핵심 진단**: 2차 감사에서 발견된 메타 패턴 ("부분 정정 → 자기 모순 신규 도입")이 v3 정정에서 **grep-based 전체 일관성 점검 패턴 적용으로 완전 해소**. cycle 1/2 학습이 v3에서 처음으로 "전체 일관성 점검 단계"로 진화. 다음 sub-plan에서 같은 패턴 의무 적용 권고.

**잔존 메타 패턴 위험**:
- W3-1 (ta 향후 버전 재검증 책무 부재)는 #16 (외부 라이브러리 추측) 경계 영역. ta KeltnerChannel API는 venv로 검증되었으나 "버전 변경 시 재검증" 책무 박제 부재 → cherry-pick 통로는 폐쇄되었으나 "외부 의존성 시간 변동" 위험은 잔존.

---

## 종합 평가

### A. v3 BLOCKING 0 확정

- B-1, B-2, B-3, B-4 (1차 감사): **모두 PASS**
- NEW-B-1, NEW-B-2 (2차 감사): **모두 PASS**
- **신규 BLOCKING 0건**

### B. cross-document 전파 우수성

- candidate-pool.md L48 + decisions-final.md L539-541 + sub-plan 본문/구현 가이드 코드 블록 = **4 위치 일관**.
- v3에서 sub-plan 내부 vectorbt 구현 가이드 코드 블록 정정 추가로 일관성 완전 회복.

### C. 외부 라이브러리 직접 검증 우수성

- v3 정정에서 ta KeltnerChannel `original_version=False, window_atr=14, multiplier=1.5` 박제 = **감사관 venv 직접 검증 (signature + numerical) 일치 PASS**.
- root CLAUDE.md L40 Immutable "외부 라이브러리 API 사용 시 공식 docs 또는 소스 직접 확인" 룰 **완전 준수**.

### D. 옵션 A 정책 의도 회복

2차 감사에서 옵션 A 의도 위반 (BLOCKING 0 + WARNING/NIT 잔존) 상태였으나, v3 정정으로 NEW-B-1 + NEW-B-2 둘 다 해소 = **옵션 A 정책 의도 (BLOCKING 0 + WARNING 6 + NIT 5 잔존) 회복**.

### E. 신규 약점 카테고리

- W3-1: ta 향후 버전 재검증 책무 박제 부재 (NIT-WARNING 경계).
- N3-1: L172/L388 "Registered" 라벨 미세 불일치 (옵션 A 잔존 허용).
- N3-2: 변수명 일관성 (옵션 A 잔존 허용).

---

## 외부 감사관 의견

**판정 = APPROVED with follow-up.**

본 3차 감사는 v3 정정의 NEW-B-1 + NEW-B-2 책무를 **venv 직접 검증 + grep-based 일관성 점검 + cross-document 전파 점검**으로 검증했으며, **신규 BLOCKING 0건**으로 옵션 A 정책 의도 회복을 확인했다. v3 정정은 cycle 1/2 학습 메타 패턴 ("부분 정정 → 자기 모순 도입")을 grep-based 전체 일관성 점검 패턴으로 처음 극복한 사례 = **방법론 진화**.

**권고 진행 경로**:

1. **사용자 명시 승인 → W2-02 실행 (W2-02.0~.4 SubTask) 진입**: 옵션 A 정책 (BLOCKING 0, WARNING/NIT 잔존)이 회복되었고, NEW-B-1/B-2 정정 품질이 venv 검증으로 확인되었으므로 추가 4차 감사 없이 사용자 승인으로 진행 가능.

2. **선택적 follow-up (옵션, 사용자 결정)**:
   - **W3-1 정정** (1줄): L222 "박제 충돌 위험 alarm" 박스에 "ta 향후 버전 변경 시 재검증 책무" 추가.
   - **N3-1 정정** (2위치): L172 "Pending → Registered" → "Pending → Active 전이". L388 동일.
   - **N3-2 정정** (1위치): 본문 L225-229에 변수명 (`both_break`, `mid_exit`) 명시 박제 추가.
   - 옵션 A 정책상 잔존 허용, 단 W2-03 작성자 cherry-pick 위험 미세 잠재. 정정 시 5분 이내 완료 가능.

3. **W2-03 sub-plan 작성 시 의무 박제 권고** (cycle 1/2 학습 메타 패턴 확장):
   - W-1 (vectorbt sl_stop Series + sl_trail=True 결합): mini test 의무 박제.
   - W-4 (Secondary 마킹 Tier 1+2 3+ 페어): 정확 인용 의무.
   - NEW-NIT-1 (vectorbt entry/exit 우선순위 default): docstring 인용 또는 mini test 의무.
   - W3-1 (ta 향후 버전): W2-03 구현 시점 ta 버전 lock 박제 + Parquet freeze (W2-01.4 패턴).
   - **방법론 진화 박제**: handover에 "sub-plan 정정 시 grep-based 전체 일관성 점검 + cross-document 전파 점검 + venv 직접 검증 패턴 의무 적용" 박제 추가 권고.

**감사관 자가 검증 (rubber-stamp 회피)**:
- 본 3차 감사는 v3 정정을 **검증 없이 통과시키지 않음** = rubber-stamp X.
- 검증 도구:
  - ta KeltnerChannel venv 직접 호출 + inspect.signature + numerical allclose (synthetic data n=200, seed=42)로 mid == EMA(close, 20) + upper == EMA + 1.5*ATR(14) 일치 검증.
  - grep `신설` 으로 잔존 위치 enumerate (4개 잔존 = 사용자 박제 의도 4개와 일치 확인).
  - grep `Pending → Active|Registered` 으로 라벨 불일치 위치 enumerate (L172, L388 발견 → N3-1).
  - candidate-pool.md L48 + decisions-final.md L539-541 + sub-plan 직접 read로 cross-doc 일관성 확인.
- 발견 깊이: 1차 감사 BLOCKING 4 + WARNING 5 + NIT 4 → 2차 감사 BLOCKING 2 신규 + NIT 1 신규 → 3차 감사 BLOCKING 0 + WARNING 1 + NIT 2 신규. 카테고리 압축으로 감사 cycle 종료 신호.
- 본 감사관 한계 인정:
  - vectorbt sl_stop Series + sl_trail=True 결합 동작 (W-1)은 본 차원에서도 mini test 미수행 (옵션 A 잔존 허용 신호, W2-03 위임).
  - vectorbt entry/exit 우선순위 default (NEW-NIT-1)도 docstring 인용 미수행 = 본 감사관 한계.
  - ta `KeltnerChannel._run` 내부 로직 (`original_version=False` 시 close 단독 사용) 출처 인용 (W3-1)은 본 감사관 venv numerical 검증으로만 확인, 소스 코드 인용 부재.

**최종 권고**: 사용자 명시 승인으로 W2-02 실행 진입 가능. 선택적 follow-up (W3-1 + N3-1 + N3-2) 5분 이내 정정 후 진입 권장 (cherry-pick 위험 완전 차단). cycle 1/2/3 학습 메타 패턴 ("grep-based 전체 일관성 점검") handover 박제 추가 권고.
