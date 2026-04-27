# V2-Strategy-ML (Trend Factor + LightGBM Cross-Sectional Ranking) sub-plan

Task ID: V2-Strategy-ML
Feature: STAGE1-V2-015
Created: 2026-04-27
Status: **사용자 명시 동의 박제됨** ("A로 가되 우리의 함정 4개도 다 보완하자" 2026-04-27)

박제 출처:
- Cambridge JFQA "A Trend Factor for the Cross Section of Cryptocurrency Returns" (2024) — 79% 조합 양의 유의 alpha
- Liu et al. ScienceDirect 2022 — XGBoost cross-sectional 패널 + EW Sharpe 1.95 (단 CW 0.27 차이 큼)
- López de Prado "Advances in Financial Machine Learning" (2018) — DSR + CPCV 표준
- 사용자 발화 (2026-04-27): "추가 학습을 해. 그동안의 모든 코인들의 백테스팅 추세 보고 학습해볼 수 있나?"
- 조사 보고: 일반-purpose agent 2026-04-27 (10 사례 + 함정 5개 + 권장 모델)

---

## 0. 사용자 명시 동의 ⚠️ (handover #10/11)

> "Strategy ML 트랙은 산업 평균 90%+ 모델 OOS fail 통계 인지. Survivorship bias + lookahead 등 함정 박제 동의. 결과는 cycle 1 #5 회피 정신 그대로 (사전 박제 + cherry-pick X). OOS PASS 시 자동매매 진입 / FAIL 시 학습 가치만 박제. 50만원 라이브 시 ML 트랙 별도 한도."

사용자 동의: **"A로 가되 우리의 함정 4개도 다 보완하자"** (2026-04-27).

---

## 1. 핵심 설계 — Trend Factor + LightGBM Cross-Sectional Ranking

### 1.1 구조 (한 문단)

매일 KST 09:05 시점에 **Upbit KRW 250 코인 + 상장폐지 코인** 데이터에서 **30~100 features** 계산 → **LightGBM 모델**이 "다음 7일 cross-sectional rank" 예측 → **상위 10% (top decile) 동일가중 매수** → 7일 후 재평가 (rebalance).

### 1.2 Why Cross-Sectional Ranking

- 단일 코인 일봉 ML alpha = 거의 없음 (Sharpe 0~0.5, 룰 기반과 차이 X)
- **Cross-sectional ranking** (250 코인 비교) = Cambridge 학술 검증 alpha 있음
- "오를 코인" 절대 예측보다 "**상대적으로 더 오를 코인**" 예측이 훨씬 쉬움

### 1.3 Why LightGBM (not LSTM/Transformer)

- Kaggle G-Research 코인 예측 우승 3팀 모두 LightGBM
- 학습 빠름 (CPU 분 단위)
- feature importance + SHAP 해석 가능 (디버깅 ↑)
- LSTM/Transformer = 학습 비용 + 디버깅 비용 vs alpha 차이 미미 (조사 결과)

---

## 2. 함정 4개 회피 박제 ⭐

### 함정 1: Survivorship Bias (상장폐지 코인 데이터 부재)

**위험**: 살아남은 코인만 학습 → in-sample alpha 과대평가, 실제 라이브에서 망함.

**회피**:
- Upbit 공지사항 크롤링 (`https://upbit.com/service_center/notice`) → 상장폐지/투자유의 이력 수집
- CoinGecko historical API → 글로벌 시총 + 기간별 가격 (Upbit 미상장 시기 포함)
- 데이터셋에 **상장폐지 코인도 포함** (delisted=True flag)
- 모델 학습 시 delisted 코인의 마지막 N일 행은 "delisting" target으로 학습 (강제 매도 시그널)
- **fallback**: 상장폐지 데이터 수집 어려우면 → 측정 창 시작 시점에 상장된 코인만 (forward dataset 구성). 이건 불완전하나 baseline.

**WARNING #1 보강 (거래정지 TRADING_HALT)**:
- Upbit는 가끔 24시간 단위 거래정지 후 재개 (변동성/공지 사유)
- `is_trading_halted` flag 추가 (그 기간 OHLCV는 비정상)
- 학습/평가에서 정지 기간 행 제외 (`mask & ~is_trading_halted`)
- Upbit 공지 크롤링 시 "거래지원종료" + "거래일시정지" 둘 다 수집

### 함정 2: 김치 프리미엄 (Kimchi Premium)

**위험**: Upbit 가격 = 글로벌 가격 + 한국 프리미엄. 프리미엄 자체가 시계열 변동 → 모델이 이걸 모르면 OOS 깨짐.

**회피**:
- Feature 추가:
  - `kimchi_premium_btc` = Upbit BTC / Binance BTC × 1000 (premium ratio)
  - `kimchi_premium_change_7d` = 7일 변동률
- Binance global price 별도 fetch (CoinGecko API 또는 Binance public API)
- 학습 데이터에 김치 프리미엄 high/low 시기 모두 포함 (2017~2018, 2021 high / 2024+ low)

### 함정 3: 저유동성 김치코인 (펌프&덤프)

**위험**: Upbit 단독 상장 + 일평균 거래대금 < 10억 = 펌프&덤프. 백테스트는 fill 가정으로 좋은 결과, 라이브에서 slippage 폭발.

**회피**:
- 학습 dataset 필터: **일평균 거래대금 ≥ 10억 KRW** (측정 시점 30일 평균)
- Strategy G와 동일 필터 (Tier 3 자동 필터 §3.1 박제)
- 동시에 **slippage 박제 강화**: 저유동성 코인 (거래대금 < 50억) = slippage 0.3%, 메이저 코인 = 0.1%
- 결과 리포트에 "저유동성 코인 alpha 기여도" 별도 분리

### 함정 4: 거래비용 누락

**위험**: 백테스트 fill at close + 수수료 미반영 → Sharpe 과대평가.

**회피**:
- Upbit fee 0.05% × 왕복 = 0.10%/trade
- Slippage:
  - 메이저 (BTC/ETH/XRP/SOL): 0.05% (0.10% 왕복)
  - 중형 (거래대금 50~500억): 0.10% (0.20% 왕복)
  - 소형 (거래대금 10~50억): 0.30% (0.60% 왕복)
- 백테스트 함수에서 강제 적용
- 거래비용 후 Sharpe만 보고 (gross Sharpe 보고 X)

---

## 3. 추가 학술 표준 (cycle 1 #5 회피 강화)

### 3.1 DSR (Deflated Sharpe Ratio) 강제

- N_trials = 사전 박제 (hyperparameter grid 크기)
- 측정한 Sharpe → DSR_z 계산 → DSR_z > 0 PASS
- W2-03 시점과 동일 절차

### 3.2 CPCV (Combinatorial Purged Cross-Validation)

- 단순 walk-forward 대신 CPCV 사용 (Lopez de Prado 권장)
- skfolio.model_selection.CombinatorialPurgedCV 활용
- purge gap = 7일 (target 5d forward return의 lookahead 차단)
- embargo = 3일 (post-test 시점 보호)

### 3.3 사전 박제 (Cherry-pick 회피)

본 sub-plan에서 박제할 항목 (변경 금지):
- Universe: Upbit KRW 마켓 + 상장폐지 코인
- Filter: 일평균 거래대금 ≥ 10억 (30일 평균)
- Target: 다음 7일 cross-sectional rank → top 10% (binary 또는 percentile)
- Features: 아래 §4 50개 (변경 금지)
- Model: LightGBM (rank:pairwise objective 또는 binary classification)
- Hyperparameter grid: 사전 박제 (§5)
- Train/test split: 2020-01 ~ 2023-12 (학습) / 2024-01 ~ 2025-12 (OOS) / 2026-01~ (페이퍼 forward)
- Go 기준: OOS Sharpe > 1.0 (거래비용 후) AND DSR_z > 0 AND OOS trades ≥ 50

### 3.4 Go/No-Go 기준 (사전 박제)

```
- OOS Sharpe (거래비용 후) > 1.0
- DSR_z > 0
- OOS trades >= 50 (통계 유의)
- 김치 프리미엄 break point 별 성과 일관성 (sub-period 모두 + Sharpe)

→ 충족 시 V2-07 라이브 진입 후보 (별도 한도 10만원)
→ 미달 시 학습 가치만 박제 (Strategy E No-Go 패턴)
```

---

## 4. Feature Engineering (50개 사전 박제)

### 4.1 Momentum / Trend (15개)

```
return_1d, return_3d, return_7d, return_14d, return_30d, return_60d, return_90d
ma_5_distance, ma_20_distance, ma_50_distance, ma_200_distance
macd_histogram, macd_signal_distance
golden_cross_5_50, golden_cross_50_200
```

### 4.2 Volatility (7개, NIT 정정 — volatility_rank_cs는 §4.4로 이동)

```
realized_vol_7d, realized_vol_30d, realized_vol_90d
atr_14, parkinson_vol_14
volatility_ratio_7d_30d (단기/중기 비율)
volatility_change_7d
```

### 4.3 Liquidity (8개)

```
log_dollar_volume_avg_7d, log_dollar_volume_avg_30d
amihud_illiquidity_30d
volume_ratio_7d_30d (단기/중기)
volume_rank_cs (cross-sectional 거래량 percentile)
volume_spike (volume / 20d_avg)
turnover_ratio (volume / market_cap, 가능 시)
liquidity_change_30d
```

### 4.4 Cross-Sectional Rank (10개)

```
return_7d_rank_cs, return_14d_rank_cs, return_30d_rank_cs (percentile across all coins)
volatility_rank_cs, volume_rank_cs
ma_distance_rank_cs_5, ma_distance_rank_cs_50, ma_distance_rank_cs_200 (3 timeframes)
macd_rank_cs
return_consistency_rank_cs (양봉/음봉 비율 cross-sectional)
```

### 4.5 Reversal (3개)

```
return_1d_reversal (전일 종가 반전)
return_3d_reversal
overbought_score (RSI > 70 강도)
```

### 4.6 Macro / Cross-coin (6개)

```
btc_dominance (BTC market_cap / total_market_cap, CoinGecko)
btc_return_7d (대장 코인 트렌드 overlay)
btc_volatility_30d
kimchi_premium_btc (Upbit BTC / Binance BTC)
kimchi_premium_change_7d
total_market_cap_change_7d (전체 코인 시장 momentum)
```

### 4.7 Asset-specific (선택, 가능 시 추가)

```
days_since_listing (신규 상장 코인 식별)
exchange_count (Upbit 단독 vs 다중 거래소)
sector_label (DeFi/Layer1/Meme 등 — Coinpaprika 활용)
```

---

## 5. Hyperparameter Grid (사전 박제, N_trials=27)

LightGBM:
```
num_leaves: [31, 63, 127]
learning_rate: [0.01, 0.05]
n_estimators: [200, 500, 1000]
min_child_samples: [20, 50]
reg_alpha: [0, 0.1]
reg_lambda: [0, 0.1, 1.0]
```

총 3 × 2 × 3 × 2 × 2 × 3 = 216. **이를 27개 서브셋으로 사전 박제** (랜덤 X, regular grid 27 = 3³). 너무 많은 trial은 multiple testing fail.

또는 단순화: **단일 hyperparameter set 사전 박제** (N_trials=1, DSR 가장 보수적). 권장.

---

## 6. 작업 분해 (~3주)

| ID | 항목 | 추정 | 산출물 |
|----|------|:---:|--------|
| **ML-01a** | **외부 API 가용성 사전 검증 (WARNING #4)**: Upbit 공지 robots.txt + CoinGecko historical KRW 데이터 sample 5개 fetch + LightGBM `inspect.signature` (cycle 1 #16 회피) | 0.5d | api_availability_report.md |
| **ML-01b** | 데이터 수집 (Upbit 250 + 상장폐지 + Binance global + USD/KRW 환율 + CoinGecko historical) + **데이터 품질 검증 (rate limit / fetch fail / 수정 이력)** | 2.5d | parquet datasets |
| **ML-02** | Feature engineering (50 features, look-ahead 차단 단위 테스트) | 3d | features.parquet |
| **ML-03** | Target 정의 + 라벨링 (cross-sectional 7d forward rank, top decile binary) | 1d | targets.parquet |
| **ML-04** | LightGBM 학습 + CPCV (skfolio.CombinatorialPurgedCV) | 3d | model artifact |
| **ML-05** | Walk-forward backtest + DSR + sub-period 분석 (김치 프리미엄 break point) | 3d | backtest report |
| **ML-06** | Feature importance + SHAP + 결과 박제 | 1d | report + sub-plan 결과 박제 |
| **ML-07** | (PASS 시) engine 통합 / (FAIL 시) 학습 박제만 | 2d | candidate-pool.md v10 |

**총 ~16일 (3주)**, V2-06 페이퍼 4주 동안 병행.

---

## 7. 진입 / 종료 기준

### 진입 조건 (모두 충족 ✓)
- ✅ V2-06 페이퍼 daemon 가동
- ✅ V2-Strategy-G engine 통합 (활동 트랙)
- ✅ V2-Strategy-E No-Go 학습 박제 (cycle 1 #5 회피 패턴 검증)
- ✅ 사용자 명시 동의 ("A로 가되 함정 4개 보완" 2026-04-27)

### 종료 조건
- 본 sub-plan §3.4 Go/No-Go 기준 통과 여부 결정
- 결과 그대로 박제 (cherry-pick X)
- candidate-pool.md v10 갱신 (Strategy ML 추가)

---

## 8. 위험 + 완화 종합

| 위험 | 완화 |
|------|------|
| Strategy E와 동일 패턴 (in-sample GO + OOS fail) | DSR + CPCV + 함정 4개 보완으로 OOS 통과 확률 ↑ (그래도 fail 가능성 큼, 사용자 동의) |
| 데이터 수집 시간 큼 (특히 상장폐지 + 글로벌) | ML-01 단계 별도 commit, 데이터 수집 못 하면 baseline (현재 상장만) |
| Feature engineering lookahead | 단위 테스트 강제 (각 feature t-1까지만 사용 verify) |
| LightGBM hyperparameter trial 수 | 사전 박제 (N_trials=1 권장) → DSR 보수적 |
| 한국 시장 break point | 트래블룰 2022.03 / 가상자산이용자보호법 2024.07 dummy variable + sub-period 분석 |
| 거래비용 모델 부정확 | 보수적 박제 (저유동성 0.30% slippage) + 실측 보정 책무 (V2-07 진입 시) |
| Cross-sectional universe alignment lookahead | `universe_at(t)` 함수 + 단위 테스트 (함정 5) |
| Class imbalance (binary target) | percentile regression + LightGBM `lambdarank` (함정 6) |
| 외부 API 가용성 (CoinGecko KRW / Upbit 공지) | ML-01a 사전 검증 step + fallback 박제 (WARNING #4) |
| API 시그니처 추측 (cycle 1 #16) | ML-01a 시점 `inspect.signature` 실측 강제 (LightGBM / CoinGecko / requests) |

---

## 9. V2-07 진입 시점 사용자 결정

ML-06 완료 후:

**OOS PASS 시** (Sharpe>1.0 + DSR>0 + trades≥50):
- 옵션 a: V2-07 라이브 ML 진입 (별도 한도 10만원)
- 옵션 b: V2-06 페이퍼 4주 결과 + ML 결과 종합 판정 후 V2-07 결정
- 옵션 c: ML 별도 페이퍼 4주 추가 운영 (총 8주) → V2-08 결정

**OOS FAIL 시**:
- 학습 가치만 박제 (Strategy E와 동일)
- 함정 분석 (어떤 함정이 OOS fail 원인이었나) → 다음 사이클 학습

---

End of V2-Strategy-ML sub-plan. Generated 2026-04-27.
