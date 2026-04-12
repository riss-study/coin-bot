# 자동매매 알고리즘 심층 검증 리포트

> 이 문서는 `research-report.md`의 초기 추천안을 학술 논문과 실전 벤치마크로 검증한 결과입니다.
> **중요**: 일부 초기 권고안은 이 검증 결과에 따라 수정됩니다.

---

## 핵심 결론 (먼저 읽기)

초기 리포트는 "EMA 9/21 + RSI + 거래량"이라는 대중적인 조합을 추천했습니다. 심층 검증 결과:

1. **EMA 9/21 단독 전략은 "YouTube 민속학"에 가깝다** — 피어리뷰 논문에서 검증된 적이 없으며, 9/21이라는 특정 파라미터는 과적합 냄새가 강함.
2. **가장 강력한 학술적 근거를 가진 전략은 "추세 + 평균회귀 앙상블"** — Quantpedia (Padysak & Vojtko, 2022; Beluská & Vojtko, 2024)의 BTC 백테스트에서 **Sharpe 1.71, 연 56% CAGR, T-stat 4.07** 달성. 두 전략의 상관관계가 낮아 앙상블 효과 발생.
3. **AI/LLM이 직접 매매 결정을 내리는 것은 실패** — Agent Market Arena (2025년 8~10월 라이브 벤치마크)에서 **GPT-5, Claude Sonnet 4 포함 대부분의 LLM이 BTC/ETH 바이앤홀드를 이기지 못함**.
4. **AI가 가치를 제공하는 곳은 2군데** — (a) LightGBM을 사용한 **시장 레짐 분류 필터**, (b) Haiku급 저가 LLM의 **Reddit 소셜 감성 압축**. 이 외의 AI 활용(LSTM, Transformer, 강화학습, 직접 LLM 결정)은 소자본 봇에 부적합.
5. **소자본($75~$750)에서는 AI 인프라 비용이 치명적** — Sonnet 4를 4시간마다 호출 시 월 $20 → $75 계좌의 27% 드래그. Haiku/Gemini Flash만이 경제적으로 가능.

---

## 1. 전통적 전략 검증

### 1-1. EMA 9/21 조합의 진실

**발견:**
- "EMA 9/21 + RSI" 조합을 검증한 피어리뷰 논문은 찾지 못함. YouTube와 블로그에 반복되는 조합.
- 9/21 파라미터는 **전형적인 곡선 맞춤(curve-fitting) 신호**. 왜 9와 21인가? 이론적 근거 없음.
- 2022~2023 크립토 횡보장에서 대부분의 MA-Cross 시스템은 큰 손실을 기록.

**그럼에도 완전히 버리지는 않는 이유:**
- 단순 추세 추종(Donchian/MA 채널 브레이크아웃)은 BTC에서 **가장 긴 역사의 "뭔가 작동하는" 전략**.
- 단, 일반적인 최대 낙폭(drawdown) **30~50%가 정상**.

### 1-2. 학술적 근거가 있는 전략들

| 전략 | 문서화된 성과 | 출처 |
|------|--------------|------|
| **추세+평균회귀 50/50 앙상블 (BTC)** | Sharpe 1.71, CAGR 56%, T-stat 4.07 | Padysak & Vojtko (2022), Beluská & Vojtko (2024) |
| **횡단면 모멘텀 (Cross-sectional)** | 주식 모멘텀 연구와 유사한 수준의 학술 지지 | — |
| **변동성 조정 포지션 사이징 (ATR)** | 거의 모든 학술 연구에서 리스크 조정 수익 향상 | López de Prado (2018) |
| **200일 MA 추세 필터** | 단순하지만 견고. 하락 추세 필터로 드로다운 대폭 감소 | QuantifiedStrategies 백테스트 |

### 1-3. 수정된 권고 — 앙상블 중심 접근

**새로운 기본 전략 구조:**

```
Layer 1: 추세 추종 전략 (Trend-Following)
  - 진입: 가격 > 200일 MA (대추세 상승) AND Donchian(20) 상단 돌파
  - 청산: Donchian(10) 하단 터치 OR ATR 트레일링 스톱
  - 포지션: ATR 기반 변동성 조정 사이징

Layer 2: 평균회귀 전략 (Mean Reversion)
  - 진입: 가격 > 200일 MA (상승 추세에서만) AND RSI(4) < 25
  - 청산: RSI(4) > 50 OR 5일 경과
  - 포지션: 고정 비율 (2% 리스크)

Layer 3: 앙상블 결합
  - 기본 가중치: 50/50
  - 레짐 조건부 조정 (다음 섹션)
  - 두 전략의 신호가 반대면 → 해당 코인 매매 건너뜀
```

**변경점:**
- ~~EMA 9/21 크로스~~ → **200일 MA 추세 필터 + Donchian 브레이크아웃** (더 견고, 과적합 위험 낮음)
- ~~단일 전략~~ → **추세 + 평균회귀 앙상블** (학술적 Sharpe 1.71)
- ~~RSI(14) 필터~~ → **RSI(4) 극단값** (평균회귀 신호로만 사용, 트렌드 필터 무기화)

---

## 2. AI/ML 심층 검증 — 가장 중요한 발견

### 2-1. LLM 직접 매매: 명확한 실패

**Agent Market Arena (arXiv:2510.11695, 2025년 8~10월 실시간 벤치마크):**
- 대상 모델: GPT-4o, GPT-4.1, GPT-5, Gemini-2.0-flash, Claude-3.5-haiku, Claude Sonnet 4
- 대상 자산: TSLA, BMRN, ETH, BTC
- **결과: 대부분의 LLM 에이전트가 바이앤홀드를 이기지 못함. BTC/ETH에서 통계적 유의성 있는 초과 수익 없음.**

**StockBench (arXiv:2510.02209):**
- 결론 인용: "Excelling at static financial knowledge does not translate into successful trading strategies."

**FinMem (실제 이슈):**
- GPT-4-Turbo가 GPT-4의 누적 수익의 **8%만 달성** — 같은 전략이 LLM 버전에 따라 결과가 극단적으로 달라짐 (레드 플래그).

**결론: LLM에게 "지금 매수할까?"를 묻는 아키텍처는 증거 없음.**

### 2-2. LLM이 실제로 가치를 주는 곳

#### (A) Reddit 기반 감성 압축 (증거 존재)

**"Fact-Subjectivity Aware Reasoning" (arXiv:2410.12464):**
- Reddit 소스 LLM 감성 → **23.3% 총 수익** 달성
- **뉴스 소스 감성은 오히려 성능 저하** (의미적 잡음)
- 의미: LLM은 가격 예측기가 아니라 **비정형 텍스트 압축기**로서 가치가 있음

#### (B) LightGBM 레짐 분류 (학술 지지 강함)

- Sun et al. (2024), Springer 2025 비교 연구: **LightGBM이 XGBoost/LSTM을 기술적 특징 기반 분류에서 우위**
- 결정적으로, **가격 방향 예측이 아니라 레짐 분류(trending / ranging / high-vol)에 사용할 때** 실전 가치 있음
- 검증 방법: Purged k-fold + 임바고 (López de Prado 방법)

### 2-3. AI 사용 추천/비추천 매트릭스

| 사용 방법 | 추천 여부 | 근거 |
|-----------|----------|------|
| LLM 직접 매매 결정 | ❌ | Agent Market Arena, StockBench 라이브 테스트 실패 |
| LLM 뉴스 감성 분석 | ⚠️ | 의미적 잡음 많음, 성능 저하 가능 |
| **LLM Reddit 감성 분석 (Haiku)** | ✅ | Reddit 소스 감성은 유일하게 일관된 증거 |
| **LightGBM 레짐 필터** | ✅ | 학술 지지, 과적합 제어 가능 |
| LSTM 가격 예측 | ❌ | 출판 편향, 2020~2021 불장 구간 치중 |
| Transformer (PatchTST, Informer) | ❌ | 자산마다 최적 모델 다름 → 과적합 시그널 |
| 강화학습 (PPO, DQN, FinRL) | ❌ | 샘플 효율성 문제, 크립토 4h 바 데이터 부족 |
| 다중 에이전트 (TradingAgents) | ⚠️ | 유망한 아키텍처, 하지만 주식 불장 백테스트에 치중. 크립토 라이브 검증 없음 |

### 2-4. LLM 비용 분석 (4시간봉 기준)

| 모델 | 호출당 비용 | 월 ~900콜 | $75 계좌 드래그 | $750 계좌 드래그 |
|------|------------|----------|---------------|----------------|
| Claude Sonnet 4 | $0.022 | $20 | **27%** ❌ | 2.7% ⚠️ |
| Claude Haiku 4 | $0.0017 | $1.50 | 2% ⚠️ | 0.2% ✅ |
| Gemini Flash / GPT-4o mini | $0.001~0.003 | $1~3 | 1.3~4% ⚠️ | 0.1~0.4% ✅ |

**결론:** 소자본 봇에 LLM을 쓰려면 **Haiku / Gemini Flash급만 경제적으로 가능**. Sonnet은 $500 이상 계좌에서만 고려.

---

## 3. 시장 레짐 탐지

### 3-1. 학술적 근거

**가장 강한 증거:**
- Giudici & Abu Hashish (2020, Wiley QREI) — HMM으로 크립토 레짐 변화 탐지
- Koki et al. (2022) — **4-상태 비동질 HMM이 BTC/ETH/XRP에서 최고의 예측 성능**
  - 상태: 베어 (고변동성, 음수 수익), 불 1 (저변동성, 양수 수익, 낮은 첨도), 불 2 (높은 첨도), 중립/고요
- Padysak & Vojtko (2022), Beluská & Vojtko (2024) — **50/50 추세+평균회귀 앙상블**이 BTC에서 Sharpe 1.71

### 3-2. 핵심 인사이트

> **"단순한 정적 50/50 앙상블이 복잡한 레짐 탐지의 혜택 70~80%를 이미 달성한다."**
> — Quantpedia 실증 연구의 함의

즉, HMM으로 레짐을 탐지해서 전략을 스위칭하는 것보다, **두 전략을 항상 동시에 돌리는 것**이 대부분의 이익을 주고 덜 복잡함.

### 3-3. 권장 구현 (단순화)

**Phase A — 단순 레짐 필터 (먼저 구축):**
```
Feature 1: 가격 vs 일봉 200 MA → 추세 방향 (up/down/neutral)
Feature 2: ADX(14) 4시간봉 → 추세 강도 (강한 추세 > 25, 횡보 < 20)
Feature 3: ATR% 30일 백분위 → 변동성 레짐 (상위 10% 도달 시 비상)

레짐 분류:
  - Trending Up: 가격 > 200MA AND ADX > 25 → 추세 추종 가중치 70%
  - Trending Down: 가격 < 200MA AND ADX > 25 → 매매 중단 (현물 봇)
  - Ranging: ADX < 20 → 평균회귀 가중치 70%
  - High Volatility: ATR% 상위 10% → 노출 50% 축소
```

**Phase B — LightGBM 레짐 분류기 (Phase A 검증 후):**
- 이진 분류: "내 룰이 작동하는 레짐" vs "작동 안 하는 레짐"
- 특징: ATR 정규화 수익률 (5/10/20 바), 실현 변동성, 거래량 Z-score, BTC 도미넌스 델타
- 학습: Walk-forward, Purged k-fold with 1-week embargo
- 재학습: 매주

**Phase C — HMM (선택, Phase B가 불충분할 때만):**
- 3~4 상태 HMM, 월 단위 walk-forward 재학습
- Phase B와 out-of-sample 비교 후 승자 채택

### 3-4. 휩쏘 방지 (중요)

레짐 분류기가 자주 뒤집히면 스위칭 비용이 이득을 초과함. 3가지 방어책:

1. **히스테리시스 밴드**: 진입과 이탈 임계값을 다르게 (예: ADX > 25 진입, ADX < 18 이탈)
2. **최소 지속 필터**: N개 연속 바에서 동일 레짐 확인 후 전환 (3~7바)
3. **신호 스무딩**: EMA 처리 후 임계값 적용

---

## 4. 백테스팅 엄밀성

### 4-1. 가장 자주 일어나는 실수 (치명적)

| 실수 | 영향 | 방지 |
|------|------|------|
| Look-ahead bias | Sharpe 50~100% 과장 | 시그널 바 close → 다음 바 open 체결 |
| 생존 편향 (delisted coins 제외) | 크립토에서 특히 심각 (LUNA, Terra 등) | Point-in-time 유니버스 재구성 |
| 과적합 (curve fitting) | 최고 Sharpe가 랜덤 결과 | Walk-forward + Deflated Sharpe Ratio |
| 수수료/슬리피지 과소추정 | 고빈도 전략 치명적 | 업비트 0.05%/0.05% + 슬리피지 모델 |
| 지정가 주문 체결 과대 낙관 | 백테스트와 라이브 괴리 | 가격이 지정가를 "뚫을 때만" 체결 가정 |

### 4-2. 통계적 검증 도구

| 방법 | 용도 | 출처 |
|------|------|------|
| **Walk-Forward Analysis** | OOS 검증 | Pardo (2008) |
| **Deflated Sharpe Ratio (DSR)** | 다중 시행 편향 보정 | Bailey & López de Prado (2014) |
| **Combinatorial Purged Cross-Validation** | ML 기반 전략 검증 표준 | López de Prado (2018) |
| **Monte Carlo 트레이드 셔플링** | 최대 낙폭 신뢰구간 | — |
| **Politis-Romano 고정 부트스트랩** | Sharpe 신뢰구간 (자기상관 보존) | Politis & Romano (1994) |

### 4-3. 핵심 지표 (Sharpe 이상)

Sharpe는 크립토(두꺼운 꼬리, 왜도)에 부적합. 대시보드로 추적할 지표:

- **Sortino Ratio** — 하방 편차만 사용 (크립토 적합)
- **Calmar Ratio** — CAGR / 최대 낙폭 (고통 대비 수익)
- **최대 낙폭 + 회복 시간** — 둘 다 보고 (2주 회복과 14개월 회복은 다름)
- **Profit Factor** — <1.3 마진 없음, 1.3~1.8 양호, >3 과적합 의심
- **승률 vs R-multiple** — 35% 승률에 3:1 R:R이 70% 승률에 1:3 R:R보다 나음
- **Ulcer Index** — MDD의 지속 시간 반영
- **CVaR (Expected Shortfall)** — 꼬리 위험
- **Turnover + Capacity** — 슬리피지가 수익을 죽이는 AUM 한계

### 4-4. 최소 데이터 요건

- **트레이드 수 기준** (시간 아님):
  - 100~200 트레이드: 거친 Sharpe 추정
  - 500+ 트레이드: 실제 돈 신뢰 가능
  - 1,000+ 트레이드: 파라미터 튜닝 후에도 신뢰 가능
- **4시간봉 스윙 전략**: 페어당 연 50~250 트레이드
- **필요 기간**: **최소 3년, 권장 5~7년**, 여러 시장 레짐 교차 필수
- **업비트 데이터**: 2017년 10월부터 사용 가능 → 약 8년 사용 가능

### 4-5. 라이브 성능 저하 예상

> **실전 Sharpe는 인샘플 Sharpe의 30~60% 수준이 정상.**
> — 실무 경험칙 (Harvey, Liu, Zhu 2016 기반)

- 인샘플 Sharpe < 1.5 → 실전에서 의미 있는 성과 기대 어려움
- 인샘플 Sharpe 2.0 → 실전 0.6~1.2 예상

### 4-6. 프레임워크 선택

| 프레임워크 | 추천도 | 이유 |
|-----------|--------|------|
| **nautilus_trader** | ⭐⭐⭐⭐⭐ | Rust 코어, 백테스트/페이퍼/라이브 같은 코드, 실전 체결 시뮬레이션 우수 |
| **Freqtrade** | ⭐⭐⭐⭐ | 업비트 네이티브(ccxt), 빠른 MVP, 대규모 커뮤니티 (체결 현실성은 보강 필요) |
| **vectorbt** | ⭐⭐⭐ | 파라미터 스윕 / 리서치용 (최종 검증 아님) |
| **Backtrader** | ⭐⭐ | 성숙하지만 2021부터 원저자 비활성 |
| Backtesting.py | ⭐ | 단일 자산 한계 |
| Zipline | ❌ | 크립토 지원 부족, Quantopian 폐쇄 후 포기 |

**최종 추천:**
- **옵션 A (최고 품질)**: `nautilus_trader` — 학습 곡선 2~3주, 실전 준비 최고
- **옵션 B (최단 MVP)**: `Freqtrade` — 2주 내 작동, 커스텀 슬리피지 모델 추가 필요
- 리서치 단계에서는 `vectorbt`로 파라미터 스크리닝 후 최종 검증은 A/B로

---

## 5. 최종 알고리즘 아키텍처 (수정판)

### 5-1. 전체 구조

```
┌─────────────────────────────────────────────────────────┐
│                  MARKET DATA PIPELINE                    │
│  업비트 + 바이낸스 (참조) + FRED (거시) + Reddit (감성)    │
└─────────────────────────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────┐
│                  COIN UNIVERSE FILTER                    │
│  주간 갱신: 유동성 > 10억 KRW, 상장 > 6개월 등             │
└─────────────────────────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────┐
│           REGIME CLASSIFIER (Layer 1)                    │
│                                                           │
│  Phase A: 일봉 200MA + 4H ADX(14) + ATR% percentile      │
│  Phase B: LightGBM 이진 분류기 (Purged K-fold)           │
│                                                           │
│  Output: {trending_up, trending_down, ranging, high_vol} │
└─────────────────────────────────────────────────────────┘
                           │
              ┌────────────┼────────────┐
              ▼            ▼            ▼
    ┌───────────────┐ ┌──────────┐ ┌──────────────┐
    │  TREND        │ │  MEAN    │ │  NO-TRADE    │
    │  FOLLOWING    │ │ REVERSION│ │              │
    │               │ │          │ │              │
    │ 200MA +       │ │ 200MA +  │ │ High vol,    │
    │ Donchian(20)  │ │ RSI(4)<25│ │ trending     │
    │ breakout      │ │ only in  │ │ down, or     │
    │               │ │ uptrend  │ │ no regime    │
    │ ATR trailing  │ │          │ │ clarity      │
    └───────────────┘ └──────────┘ └──────────────┘
              │            │
              └─────┬──────┘
                    ▼
┌─────────────────────────────────────────────────────────┐
│           ENSEMBLE COMBINER (Layer 2)                    │
│                                                           │
│  Base weights: 50/50                                     │
│  Regime-adjusted: 70/30 or 30/70                         │
│  Hysteresis + 3-bar persistence                          │
└─────────────────────────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────┐
│          SENTIMENT VETO LAYER (Layer 3, Optional)        │
│                                                           │
│  Claude Haiku / Gemini Flash — 4시간마다                  │
│  Input: Reddit r/CryptoCurrency + Korean crypto subs     │
│  Output: {-1, 0, +1} score                               │
│                                                           │
│  역할: 거부권 또는 사이즈 배수 (신호 생성 NO)              │
│  비용: $1~3/월                                            │
└─────────────────────────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────┐
│           MACRO RISK FILTER (Layer 4)                    │
│                                                           │
│  FOMC/CPI 전후 2시간: 신규 진입 금지                      │
│  BTC 24h -10% 하락: 6시간 전체 중단                       │
│  Kimchi Premium 극단: 포지션 축소                         │
│  Fear & Greed < 10 or > 95: 신규 진입 중단                │
└─────────────────────────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────┐
│           POSITION SIZER & ORDER EXECUTOR                │
│                                                           │
│  ATR 기반 변동성 조정 사이징                              │
│  트레이드당 리스크 1%                                    │
│  단일 포지션 최대 40% of capital                          │
│  총 노출 최대 70% of capital                              │
└─────────────────────────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────┐
│           CIRCUIT BREAKERS (항상 작동)                   │
│                                                           │
│  Level 1: BTC -5%/4h → 포지션 50% 정리, 4h 중단          │
│  Level 2: BTC -10%/24h OR 일일 -2% → 전부 청산, 12h 중단 │
│  Level 3: BTC -15%/24h OR 피크 -10% → 100% 현금, 72h    │
│  Level 4: 수동 킬 스위치                                  │
└─────────────────────────────────────────────────────────┘
```

### 5-2. 개발 Phase별 로드맵

| Phase | 내용 | 기간 | 검증 기준 |
|-------|------|------|----------|
| 1 | 데이터 파이프라인 (업비트 + 보조 소스) | — | 데이터 품질 > 99.9% |
| 2 | 백테스팅 엔진 (nautilus_trader 또는 Freqtrade) | — | 거래 체결 재현 검증 |
| 3 | 베이스라인: 단순 추세 추종 (200MA + Donchian) | — | 5년 백테스트, DSR > 0.5 |
| 4 | 평균회귀 전략 단독 | — | 5년 백테스트, DSR > 0.5 |
| 5 | **50/50 앙상블** | — | **Sharpe > 1.0, Max DD < 25%** |
| 6 | Phase A 레짐 필터 추가 | — | 앙상블 대비 DSR 개선 |
| 7 | 페이퍼 트레이딩 (실시간, 2~4주) | — | 백테스트 대비 성능 70% 이상 |
| 8 | 소액 실전 (10만원) | — | 2주 페이퍼 결과 확인 |
| 9 | LightGBM 레짐 분류기 (Phase B) | — | 200+ 트레이드 축적 후 |
| 10 | Reddit 감성 LLM 레이어 (선택) | — | 앙상블 대비 개선 증명 시만 |

### 5-3. 의도적으로 제외하는 것들

| 제외 항목 | 이유 |
|-----------|------|
| ~~EMA 9/21 크로스~~ | 학술 검증 부재, 과적합 냄새 |
| ~~LSTM / Transformer 가격 예측~~ | 출판 편향, 자산별 최적 모델 불안정 |
| ~~강화학습 (PPO/DQN/FinRL)~~ | 샘플 효율 문제, 4H 바 데이터 부족 |
| ~~직접 LLM 매매 결정~~ | Agent Market Arena 라이브 실패 증명 |
| ~~뉴스 기반 LLM 감성~~ | 의미적 잡음, Reddit보다 성능 낮음 |
| ~~다중 LLM 에이전트 (TradingAgents)~~ | 주식 불장 백테스트 치중, 크립토 라이브 없음 |
| ~~선물/레버리지~~ | 사용자 요청대로 제외 |

---

## 6. 주요 학술 출처

### LLM & AI 트레이딩
- [Agent Market Arena: Live Multi-Market LLM Benchmark (arXiv:2510.11695)](https://arxiv.org/pdf/2510.11695) — **크립토 LLM 거래 가장 냉정한 평가**
- [StockBench: Can LLM Agents Trade Profitably? (arXiv:2510.02209)](https://arxiv.org/html/2510.02209v1)
- [TradingAgents Multi-Agent Framework (arXiv:2412.20138)](https://arxiv.org/abs/2412.20138)
- [CryptoTrade Reflective LLM Agent (arXiv:2407.09546)](https://arxiv.org/abs/2407.09546)
- [Fact-Subjectivity Aware Reasoning (arXiv:2410.12464)](https://arxiv.org/html/2410.12464v3) — **Reddit vs News 감성 비교**
- [FinRL Backtest Overfitting Paper (arXiv:2209.05559)](https://arxiv.org/abs/2209.05559)

### 레짐 탐지 & 앙상블
- Padysak & Vojtko (2022), Beluská & Vojtko (2024) — **BTC 앙상블 Sharpe 1.71** (SSRN)
- [Quantpedia: Revisiting Trend-following and Mean-Reversion in Bitcoin](https://quantpedia.com/revisiting-trend-following-and-mean-reversion-strategies-in-bitcoin/)
- Giudici & Abu Hashish (2020, Wiley QREI) — HMM 크립토 레짐
- Koki et al. (2022) — 4-상태 NHHM 크립토 예측 (ScienceDirect)
- [MDPI Mathematics 12/18/2911 (2024)](https://www.mdpi.com/2227-7390/12/18/2911) — Hurst Exponent 크립토
- [MDPI Mathematics 13/10/1577 (2025)](https://www.mdpi.com/2227-7390/13/10/1577) — Bitcoin 레짐 HMM

### 백테스팅 엄밀성
- López de Prado, *Advances in Financial Machine Learning* (2018) — CPCV, Purging
- Bailey & López de Prado, "Deflated Sharpe Ratio" (*JPM*, 2014)
- Harvey, Liu, Zhu, "...and the Cross-Section of Expected Returns" (*RFS*, 2016)
- Lo, "The Statistics of Sharpe Ratios" (*FAJ*, 2002)
- Pardo, *The Evaluation and Optimization of Trading Strategies* (2008)

### ML 방법론
- Sun et al. (2024) — LightGBM vs XGBoost vs BNN 크립토
- [Springer Discover AI 2025 (doi:10.1007/s44163-025-00519-y)](https://link.springer.com/article/10.1007/s44163-025-00519-y) — ML 크립토 비교

---

## 7. 사용자 결정 필요 사항

이 수정안 진행을 위해 확인해주실 점:

1. **앙상블 전략으로 전환 OK?** (EMA 9/21 → 200MA + Donchian + RSI(4) 평균회귀 앙상블)
2. **프레임워크 선택**:
   - (A) `nautilus_trader` — 학습 2~3주, 최고 품질
   - (B) `Freqtrade` — 2주 내 MVP, 업비트 기본 지원
3. **LLM 레이어 포함 여부?**
   - (A) 완전 제외 (가장 단순)
   - (B) Phase 10에 Haiku-tier Reddit 감성만 (월 $1~3)
   - (C) 감성 + 레짐 내러티브 (월 $3~5)
4. **LightGBM 레짐 필터**: Phase 9에 반드시 포함? (Phase A 단순 필터로 충분하다고 판단되면 생략 가능)
