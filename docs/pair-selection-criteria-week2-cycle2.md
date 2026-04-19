# Week 2 페어 선정 기준 — Cycle 2 (Pair Selection Criteria, W2-01 cycle 2)

**목적**: W2-01 cycle 1(v4)이 Fallback (ii) 발동으로 중단된 후, cycle 1 학습을 반영한 새 사이클의 사전 지정 선정 기준을 박제하는 단일 문서. W2-01.2/.3에서 실측 후 확정 리스트 및 common-window 시작일을 같은 파일에 추가 기록.

**cycle 1 (v4) 산출물 격리**: `docs/pair-selection-criteria-week2.md` v4는 "참고 자료"로 격리됨. primary Go 평가 반영 절대 금지. 본 cycle 2 문서가 새 사이클의 진실 박제.

**cycle 1 학습 (cycle 2 적용)**:
- **리스트 사전 박제 제거** (가장 핵심): cycle 1의 "Tier 2 = {XRP,SOL,ADA,DOGE}" 추정 박제가 빗나감(ADA 14위) → cycle 2는 **규칙만 박제하고 코드가 자동 결정**한 결과를 그대로 채택. 인간이 결과를 본 뒤 리스트 변경 절대 금지
- **snapshot_utc 개념 폐기**: cycle 1의 "명목 시각 vs 실제 fetched_at 7시간 차이"는 박제 시점에는 적합한 결정이었으나, 실측 단계에서 CoinGecko 무료 API의 historical snapshot 미제공 외부 제약을 발견함에 따라 cycle 2에서 정책 진화. **fetched_at만 진실 시각**으로 박제 (cycle 1 박제 평가 절하 아님, NIT2-2 해소)
- **cycle 1 산출물 재사용**: snapshot 시점 = cycle 1 동일(2026-04-17, fetched_at 07:08:56 UTC). cycle 1 snapshot JSON 재사용. **새 snapshot 받지 않음** (cherry-pick 동기 차단). cycle 1 JSON은 로컬 보존만 (gitignored, 옵션 B)
- **임계값/측정 창/Tier 1/Fallback = cycle 1 그대로 유지**. 결과 보고 임계값/창 변경 = cherry-pick 차단. soft contamination 인정 (cycle 1 결과를 이미 본 상태에서 cycle 2 박제하지만 임계값 등 그대로 유지하는 것이 정직)
- **새 차단 규칙 추가 안 함**: FIGR_HELOC 형 자동 배제 같은 추가 안전장치는 cycle 1 결과 의존 = soft contamination → 추가 안 함. 우리 시스템의 기존 차단(필수 전제 + 기준 3 거래대금 100억)에 위임

**원칙 (cycle 1과 동일)**:
- **사전 지정 (pre-registration)**: 아래 3개 기준 + 측정 방법 + Tier 분류 규칙은 데이터 적용 전에 freeze. 결과를 보고 선별 금지
- **Survivorship bias 방지**: 현재 시총 기준만 쓰지 않고 상장 기간 제약 병행
- **임계값 완화 금지**: 후보 수가 부족해도 기준 변경은 새 사전 등록 사이클(=새 W2-01 cycle 3) 필요
- **재현성**: snapshot JSON + SHA256 freeze. 모든 시각은 UTC

**상위 문서**:
- `docs/stage1-subplans/w2-01-data-expansion.md` SubTask W2-01.1 (cycle 1 기준 작성. cycle 2 진입 시 sub-plan 갱신 필요)
- `docs/decisions-final.md` "Stage 1 실행 기록 — Week 2 재범위 결정" + "Week 2 한계 및 독립성 서약" + "Week 2 W2-01 v4 사이클 중단 (Fallback ii 발동, 2026-04-17)" + **"cycle 1 격리 양성 목록 박제 (cycle 2 2차 외부 감사 W2-1 해소, 2026-04-19)"** + **"Fallback (ii) 누적 한도 박제 (cycle 2 2차 외부 감사 W2-2 해소, 2026-04-19)"**
- `docs/pair-selection-criteria-week2.md` v4 (cycle 1, 참고 자료 격리)
- `.evidence/agent-reviews/w2-01-pair-criteria-review-2026-04-17.md` (cycle 1 3회 외부 감사 trace)
- `.evidence/agent-reviews/w2-01-cycle2-pair-criteria-review-2026-04-18.md` (cycle 2 외부 감사 trace, **1차 감사 작성 완료, 2차 감사 추가 예정**)

**상태**: **v5** (cycle 2 W2-01.2 단계 2 Tier 2 결정 + 단계 2-2 검증 완료 + 사용자 확정 리스트 승인, 2026-04-19). **섹션 6.1 + 6.2 freeze 발효**. cycle 2 W2-01.4 (데이터 수집) 진행 대기.

---

## 1. 선정 기준 (3개, AND 조건) — cycle 1과 동일

후보 페어는 아래 3개 기준을 **모두 동시 충족**해야 한다.

### 기준 1 — 시가총액 (CoinGecko 글로벌)

| 항목 | 값 |
|------|-----|
| **임계값** | CoinGecko KRW 환산 시총 **상위 30위 이내** |
| **snapshot 시각** | **2026-04-17T07:08:56+00:00 (fetched_at 진실 시각)**. cycle 1 snapshot 재사용 — 새 snapshot 받지 않음 (cherry-pick 동기 차단). cycle 1의 "snapshot_utc=2026-04-17T00:00:00+00:00" 명목 시각 개념은 cycle 2에서 폐기 |
| **API 엔드포인트** | `GET https://api.coingecko.com/api/v3/coins/markets` (cycle 1 호출 결과 재사용) |
| **파라미터** | `vs_currency=krw`, `order=market_cap_desc`, `per_page=30`, `page=1` |
| **응답 개수 검증** | `len(response) == 30` (cycle 1 검증 통과 확인됨) |
| **저장 위치** | `research/data/coingecko_top30_snapshot_20260417.json` (cycle 1 산출물, 로컬 보존만, gitignored, 옵션 B) |
| **무결성** | SHA256 `c70a108905566f00f1b5b97fd3b08bf13be38d713f351027861d78869b3fcf59` (cycle 1 박제). cycle 2 실행 시 동일 해시 재검증. 불일치 시 cycle 2 중단 + 사용자 보고 |
| **근거** | 글로벌 유동성 + 시총 필터. 30위 컷오프는 업계 통념 + Week 2 실험 스코프 양립 (cycle 1 박제 그대로) |

### 기준 2 — 업비트 KRW 페어 상장일

| 항목 | 값 |
|------|-----|
| **임계값** | 상장일 **≤ 2023-04-17** (W1-06 결정일 기준 정확히 3년 전, cycle 1 박제 그대로) |
| **측정 방법** | (1) **업비트 공식 공지 우선** (공지 URL + 내용 캡처를 `research/data/upbit_listing_dates_20260417.json`에 병기 저장). (2) 공지 소실 시 `pyupbit.get_ohlcv_from(ticker="KRW-XXX", interval="day", fromDatetime="2017-01-01 00:00:00", to=None)` 호출 후 `df.index.min()`을 상장일로 채택. Sanity check: 최초 30 캔들 사이 7일 이상 갭 없음 |
| **저장 위치** | W2-01.2 조회 후 페어별 상장일을 `research/data/upbit_listing_dates_20260417.json` + 이 문서 섹션 5 실측 표에 동시 기록 |
| **근거** | 5년 advertised 범위 중 60% 이상(3년 이상) 커버 보장 (cycle 1 박제) |

### 기준 3 — 업비트 KRW 30 UTC-day 단순 평균 거래대금

| 항목 | 값 |
|------|-----|
| **임계값** | 측정 창 내 30 UTC-day 단순 평균 **≥ 100억 원** (cycle 1 박제 그대로) |
| **측정 창** | **2026-03-13 ~ 2026-04-11 (UTC, inclusive 양끝, 정확히 30 UTC days)** (cycle 1 박제 그대로) |
| **산식 (기본)** | `daily_value_i = close_i × volume_i` (일봉 OHLCV 종가 × 거래량, KRW 단위, 30개 값의 산술 평균) |
| **산식 (우선 사용)** | 업비트 일봉 API 응답에 실제 거래대금 필드(`value` 또는 `candle_acc_trade_price`) 존재 시 **해당 필드를 직접 사용**. **2026-04-19 W2-01.2 단계 2-2 실측 확인: pyupbit 응답에 `value` 필드 존재 → 4개 후보 모두 `value` 필드 채택**. 부재 시 기본 산식 + evidence 기록 |
| **데이터 출처** | 업비트 일봉(`pyupbit.get_ohlcv`, interval=`day`) |
| **금지 사항** | CoinGecko 24h 스팟 거래대금 **사용 금지** |
| **100억 임계값 근거** | W2 실험 slippage 허용 수준 잠정 추정. 업계 메이저 알트 거래대금 분포 중앙값 수준 (cycle 1 박제) |
| **100억 sanity check 정책** | W2-01.2 실측 후 ① **±30% 이내**: 임계값 100억 유지, 후보 리스트 그대로 진행 / ② **±30% 초과**: 사용자에게 보고하되 **W2-01 cycle 2에서는 100억 그대로 유지하여 완주**. 임계값 변경은 별도 새 사전 등록 사이클(cycle 3)로만 가능 |

### 필수 전제 (임계값 아닌, 프로젝트 범위 제약, cycle 1과 동일)

| 항목 | 값 |
|------|-----|
| **업비트 KRW 페어 존재** | 필수 |
| **현물(spot)만** | 선물/파생 금지 |
| **스테이블코인 제외** | 가치 고정 토큰. 추세 전략 대상 아님. **상세 리스트는 섹션 2 `stablecoin_set` 박제 참조** (단일 진실 박제, L76 vs L106 일관성, 자가 검증 W-D 해소) |

---

## 2. Tier 분류 — cycle 2 핵심 변경: 리스트 박제 제거 + 규칙만 박제

### Tier 선정 규칙 (사전 지정, freeze)

**cycle 2의 가장 중요한 변경**: cycle 1의 "Tier 2 = {XRP,SOL,ADA,DOGE}" 추정 리스트 박제를 제거. 대신 **규칙만 박제하고 코드가 snapshot JSON에 규칙을 적용한 결과를 자동 채택**한다.

#### Tier 1 (필수 포함, primary Go 대상)

- **KRW-BTC**: Week 1 freeze 데이터 재사용. baseline 유지
- **KRW-ETH**: 글로벌 시총 2위 추정 + 업비트 KRW 상장 장기. cycle 1 v4 박제 동일

Tier 1 2개는 기준 1~3 자동 충족 전제. W2-01.2에서 실측으로 재확인.

**Tier 1 이례 케이스**: 만약 실측에서 BTC/ETH 중 어느 한쪽이 기준 1~3 중 하나라도 미달하는 이례 상황 발견 시 (사실상 시장 붕괴급으로 발생 확률 극히 낮으나 박제 안전판으로 명시, 자가 검증 NIT-A 해소) → **W2-01 cycle 2 전체 재설계(새 cycle 3)**. Tier 1 구성 자체를 본 사이클에서 수정하지 않음.

#### Tier 2 (exploratory 후보, **규칙만 박제, 리스트 박제 안 함**)

**Tier 2 결정 규칙** (cycle 1 v4와 동일, **W2-01.2 단계에서 실제 Python으로 구현, 자가 검증 W-C/NIT-C 해소**):

```python
# 의사 코드 (실제 코드는 W2-01.2에서 본 의사 코드 정확 구현 + 외부 감사 검증)
import json, pyupbit
snapshot = json.load(open("research/data/coingecko_top30_snapshot_20260417.json"))
# SHA256 무결성 재검증 선행 (불일치 시 cycle 2 중단)
upbit_krw_tickers = pyupbit.get_tickers("KRW")  # ["KRW-XRP", "KRW-SOL", ...]
top10 = snapshot["data"][:10]
tier2_candidates = [
    coin for coin in top10
    if coin["symbol"].upper() not in {"BTC", "ETH"}
    and coin["symbol"].upper() not in stablecoin_set
    and f"KRW-{coin['symbol'].upper()}" in upbit_krw_tickers
]
```

여기서 **`stablecoin_set` 박제** (단일 진실, L76에서 본 박제 참조):

```python
stablecoin_set = {
    "USDT", "USDC", "USDS", "DAI", "USDE", "USD1", "PYUSD",
    "BUSD", "TUSD", "FRAX", "FDUSD"
}  # 사전 박제, 가치 고정 토큰 일반 목록 (2026-04-18 시점, 11개)
```

**stablecoin_set 누락 안전판** (자가 검증 W-D 해소):
- 위 11개 외 새 스테이블 토큰이 top10에 진입한 경우 (예: 향후 등장하는 알고리즘 스테이블, USDD/GUSD/USDQ 등 미포함 토큰) → W2-01.2 코드 산출 결과에서 발견 시 **즉시 사용자 보고 후 결정**
- **단순 추가 금지** (cycle 1 학습: 결과 보고 규칙 변경 = cherry-pick)
- 추가는 **cycle 3 신규 박제** 필요

**규칙 적용 방법**:
1. cycle 1 snapshot JSON 로드 (SHA256 무결성 재검증)
2. `data[0:10]`에서 위 의사 코드로 필터링 → Tier 2 후보 자동 생성
3. 각 후보에 대해 기준 2 (상장일) + 기준 3 (거래대금) 추가 검증
4. 모든 기준 통과 페어가 최종 Tier 2

**금지 사항** (cycle 1 학습 박제):
- **결과를 본 뒤 Tier 2 후보 추가/제거 절대 금지**. 코드 산출 결과 = 최종 (cherry-pick 차단)
- **규칙 자체 변경 금지**. 임계값(top10), stablecoin_set, 제외 조건 변경은 새 cycle 3 필요
- **"메이저 알트"라는 직관으로 누락된 코인 추가 금지** (cycle 1 ADA 사례 학습)

**구체 후보 리스트는 W2-01.2 코드 산출 결과로만 확정** (anchoring 차단을 위해 cycle 2 본문에서 사전 예시 박제 금지). cycle 1 단계 1 실측 결과는 evidence/handover에 trace로 보존되어 있으며, cycle 2 박제값 아님.

#### Tier 3 — Week 2 cycle 2 불포함

Tier 2 결정 규칙으로 자동 제외되는 코인:
- 시총 11~30위 (top10 외)
- 스테이블코인 (필수 전제 위반)
- 업비트 KRW 미상장 (예: BNB, FIGR_HELOC 추정)
- BTC/ETH (Tier 1)

별도 실험 트랙 후보 (Week 2 범위 변경 시 새 사이클 필요).

#### 영구 제외

- **PEPE**: 업비트 KRW 상장일 > 2023-04-17 추정 → 기준 2 FAIL. 정확한 상장일은 W2-01.2 cycle 2 실측에서 확정 후 본 섹션에 기록 (cycle 1 v4 L122 패턴)
- **시총 >30위 전체** (기준 1 FAIL)
- **선물/파생 상품** (필수 전제 FAIL)

---

## 3. Fallback 정책 (Tier 2 <2 통과 시) — cycle 1과 동일

### 3.0 Go 기준 박제 (cycle 2 자족성, 외부 감사 B-1 해소)

본 cycle 2의 W2-03 In-sample 백테스트 게이트 (사전 지정):

- **Primary**: Tier 1 × {A, C, D} = 6셀 중 적어도 1개 전략이 BTC 또는 ETH에서 `Sharpe > 0.8 AND DSR > 0`
- **Secondary 마킹** (Go 기여 X): 동일 전략이 Tier 1+2 3+ 페어에서 `Sharpe > 0.5` → ensemble 후보
- **미달 시**: Stage 1 킬 카운터 +1, Week 3 재탐색

**출처 박제**: `docs/decisions-final.md` "Week 2 재범위 결정 — Week 2 게이트" 섹션이 진실 박제. cycle 1 v4와 동일 임계값 채택. **Go 기준 자체는 페어 선정 cycle별 변경 대상이 아닌 decisions-final.md 박제 진실값**. cycle 1 격리 양성/비대상 분할은 본 cycle 2가 사후 정의하지 않고 `docs/decisions-final.md` "**cycle 1 격리 양성 목록 박제**" 섹션 인용 (cycle 2 2차 외부 감사 W2-1 해소: 다음 사이클 작성자 자가 분할 통로 차단).

**다중 검정 한계 고지**: 6 primary 셀도 family-wise 오류 여지. DSR로 부분 완화, 최종 검증은 Week 3 walk-forward (cycle 1 박제 그대로).

### 3.1 Fallback 옵션

**임계값 완화는 절대 금지**. Tier 2 통과 페어가 2개 미만(=0 또는 1)이면 아래 두 옵션 중 택일, 사용자 명시적 승인 필수.

| 옵션 | 내용 | 영향 |
|------|------|------|
| **(i) Tier 2 제거** | Tier 1 × {A, C, D} = **primary 6셀 그대로 유지**. Tier 2 exploratory는 통과 페어 수 × 3 전략으로 축소 (0개 통과 → exploratory 0셀, 1개 통과 → exploratory 3셀). Go 기준 변경 없음 | W2-03 sub-plan에서 exploratory 범위만 실측 수에 맞게 조정 |
| **(ii) Task 재설계** | W2-01 cycle 3 시작. 새 사전 등록 + 외부 감사 + 사용자 승인 루프. 기존 cycle 2 실측 결과는 "참고 자료"로 격리 | Week 2 일정 +α 지연 |

**금지 사항** (cycle 1 박제 그대로):
- 기준 임계값(30위, 2023-04-17, 100억)을 "하나만 통과"로 완화 금지
- Tier 2 결정 규칙 변경 금지 (top10, stablecoin_set 등 사후 조정 금지)
- "거의 충족" 페어 승격 금지

---

## 4. Common-window 사전 결정 — cycle 1과 동일

### 결정

1. W2-01.2 실측 후 **Tier 1-2 최종 페어 중 상장일이 가장 늦은 페어**의 업비트 KRW 상장일을 common-window 시작점으로 채택
2. W2-03 grid에서 **두 metric을 동시 계산**:
   - **Primary metric**: 페어별 max-span Sharpe (각 페어 자체 상장일부터 **2026-04-12 UTC**까지)
   - **Secondary metric**: common-window Sharpe (공통 시작점부터 **2026-04-12 UTC**까지)
3. Go 기준 평가는 **primary metric** 기준. Secondary는 페어 간 비교 공정성 확인용
4. Common-window 시작일은 W2-01.2 실측 완료 후 본 문서 "5. 확정 리스트" 섹션에 기록 + freeze

**참고 (종료일 정의)**: 백테스트 metric 산출 종료일(`2026-04-12 UTC`)은 W1 advertised freeze 종료일과 동일 (sub-plan L145 `RANGE = ('2021-01-01', '2026-04-12')`, NIT2-1 라인 drift 정정). 기준 3 측정 창 종료일(`2026-04-11 UTC`)과 1일 차이는 의도된 설계 (cycle 1 박제 그대로).

### 갭 처리 사전 정책 (cycle 1과 동일)

1. **Forward-fill 금지**
2. **결측일 `return=0` + 포지션 상태 유지**
3. **3일 초과 연속 갭 페어는 플래그** + W2-03에서 신뢰구간 축소 표기
4. **상장폐지 확정 페어**: common-window 내 영구 상장폐지 이력 있으면 즉시 탈락

---

## 5. 확정 리스트 (W2-01.2/.3 완료 후 기록)

> W2-01.2 실측 후 이 섹션을 채움. 현재는 placeholder.

### 실측 결과 표

| 페어 | 기준 1 시총 순위 (snapshot fetched_at 기준) | 기준 2 업비트 KRW 상장일 | 기준 3 30 UTC-day 평균 거래대금 | 3기준 모두 충족 |
|------|---------------------------------------------|----------------------------|-----------------------------------|------------------|
| KRW-BTC | 1위 (cap 2,226조) | (W1 재사용, 자동 통과) | (W1 재사용, 자동 통과) | **Tier 1 확정** |
| KRW-ETH | 2위 (cap 418조) | 자동 통과 (장기 상장) | 자동 통과 | **Tier 1 확정** |
| KRW-XRP | 4위 (cap 130.97조) | 2017-09-25 (5.5년 마진) | 187,899,424,186 KRW (18.79x) | **Tier 2 확정 (PASS)** |
| KRW-SOL | 7위 (cap 75.25조) | 2021-10-15 (1.5년 마진) | 41,060,227,303 KRW (4.11x) | **Tier 2 확정 (PASS)** |
| KRW-TRX | 8위 (cap 45.84조) | 2018-04-05 (5년 마진) | 13,782,597,882 KRW (1.38x) | **Tier 2 확정 (PASS)** |
| KRW-DOGE | 10위 (cap 22.32조) | 2021-02-24 (2.1년 마진) | 29,809,287,649 KRW (2.98x) | **Tier 2 확정 (PASS)** |

**Tier 2 행 처리 절차** (cycle 2 신규 박제, 외부 감사 W-4 해소):
- W2-01.2 코드가 cycle 1 snapshot JSON에 Tier 2 결정 규칙 적용 → 후보 리스트 산출
- 산출된 각 후보에 기준 2 (상장일) + 기준 3 (거래대금) 추가 검증
- **Tier 2 통과 0개 케이스** (자가 검증 W-E 해소): 위 placeholder 행을 `Tier 2 (0개 통과, Fallback 발동)`로 표기 + 별도 행 또는 주석에 Fallback (i)/(ii) 선택 결과 명시
- **Tier 2 통과 1개 이상 케이스**: placeholder 행을 **페어별 행으로 자동 분리** (예: 결과가 4개면 4행으로 확장)
- **인간 개입으로 페어 추가/제거 절대 금지** (cycle 1 학습)
- 분리 결과를 섹션 6.2 "확정 리스트 freeze" 발효 시점에 박제

### 최종 확정

- **Tier 1 (primary Go 대상)**: KRW-BTC (W1 재사용), KRW-ETH
- **Tier 2 (exploratory, 코드 자동 결정 + 기준 2/3 통과)**: **KRW-XRP, KRW-SOL, KRW-TRX, KRW-DOGE (4개 모두 PASS)**
- **Common-window 시작일 (UTC)**: **2021-10-15** (Tier 1-2 중 상장 가장 늦은 SOL 기준)
- **Fallback 발동 여부**: **미발동** (Tier 2 통과 ≥ 2)
- **100억 sanity check 결과**: ±30% **초과** (중앙값 4.11x). 사용자 결정 = 본 사이클 100억 유지 완주, 임계값 변경은 cycle 3
- **상장일 cross-check**: 사용자 결정 = 업비트 공식 공지 수동 cross-check **스킵** (pyupbit 결과 신뢰)
- **pyupbit 응답 필드**: `value` 사용 확인 (cycle 2 v4 L64 박제 "필드 우선" 조건 충족)

### 사용자 승인 기록 (승인 2단계)

- **기준 승인** (W2-01.1 cycle 2 완료 시점, 섹션 1~4 내용 확정): **2026-04-19 사용자 위임 발화 ("너가 결정해줘 모든걸") 시점** — **섹션 6.1 기준 freeze 발효**
- **확정 리스트 승인** (W2-01.3 cycle 2 완료 시점): **2026-04-19 사용자 명시 OK ("ㄱㄱ", 거래대금 sanity 100억 유지 + 공지 cross-check 스킵 + 다음 단계 진행 동시 결정)** — **섹션 6.2 확정 리스트 freeze 발효**

기준 승인 ~ 확정 리스트 승인 사이 구간에는 **실측 결과 값을 표에 채워 넣는 작업만 허용**.

**의미 변경 = 금지 (변경 시 cycle 3 필요, 외부 감사 W-3 해소)**:
- 기준 임계값 (시총 30위, 상장 2023-04-17, 거래대금 100억) 변경
- 측정 창 이동
- Tier 1 구성 변경
- Fallback 옵션 추가/제거
- Tier 2 결정 규칙 변경 (top10, stablecoin_set, 제외 조건)
- snapshot SHA256 변경 (= 다른 snapshot 재사용)

**의미 변경 없음 = 섹션 7 변경 이력 기록 후 허용**:
- 라인 번호 갱신 / 오탈자 / 링크 / 서식 수정

---

## 6. 변경 금지 서약

본 서약은 **섹션 5 승인 기록에 해당 승인이 기록된 시점부터 발효**된다.

### 6.1 기준 freeze (섹션 1~4)

**발효 시점**: 섹션 5 "기준 승인" 기록 채움 시.

발효 후 W2 실행 종료까지 아래 변경 금지:
- 기준 3개(시총 상위 30위, 상장 ≤ 2023-04-17, 30 UTC-day 평균 ≥ 100억) 임계값 변경 금지
- 측정 창 이동 금지
- snapshot 재취득 금지 (cycle 1 JSON 그대로 재사용, fetched_at 변경 금지)
- **Tier 2 결정 규칙 변경 금지** (top10, stablecoin_set, 제외 조건 사후 조정 금지)
- Fallback 정책 옵션 변경 금지

### 6.2 확정 리스트 freeze (섹션 5 실측 결과 표 + 최종 확정 값)

**발효 시점**: 섹션 5 "확정 리스트 승인" 기록 채움 시.

발효 후 W2 실행 종료까지 아래 변경 금지:
- 실측 결과 보고 페어 추가/제거 금지 (코드 자동 산출 결과 = 최종)
- Common-window 시작일 변경 금지
- Fallback 발동 여부 재판정 금지

### 6.3 변경이 불가피한 경우

6.1 또는 6.2에 해당하는 변경 요구 발생 시: **W2-01 cycle 3 시작**. 새 사전 등록 + 외부 감사 + 사용자 승인을 모두 거쳐야 한다. 기존 cycle 2 실측 결과는 "참고 자료"로 격리.

### 6.4 Fallback (ii) 사이클 반복 한도 박제 (cycle 2 2차 외부 감사 W2-2 해소)

cycle 1 → cycle 2 → cycle 3 → ... 무한 반복 위험 차단을 위한 박제. cycle 2 사용자 승인 시점에 즉시 발효 (cycle 3 결과 보고 한도 변경 시도 = cherry-pick 차단, 시간적 미러):

- **W2-01 Fallback (ii) 누적 한도 = 3회** (cycle 1 + cycle 2 + cycle 3 = 최대 3회)
- 3회 누적 후 추가 Fallback (ii) 발동 시: **W2-01 자체 폐기 + Stage 1 킬 카운터 +1 + Week 2 재범위 결정 사용자 승인 강제**
- **출처 박제**: `docs/decisions-final.md` "**Fallback (ii) 누적 한도 박제 (cycle 2 2차 외부 감사 W2-2 해소, 2026-04-19)**" 섹션. cycle 2 본문은 그 박제를 인용
- 한도 3회 근거: cycle 1 외부 감사 3회 사례 + 학습 곡선 상한 + Week 2 일정 균형 (3 cycle × ~2일 = 6일+α)

---

## 7. 변경 이력

| 날짜 | 변경 | 트리거 |
|------|------|--------|
| 2026-04-18 | **초안 v1 작성**. cycle 1(v4) 기반 + cycle 2 핵심 변경 4가지 적용: (1) 리스트 박제 제거 → 규칙만 박제 + 코드 자동 결정 / (2) snapshot_utc 명목 시각 폐기, fetched_at만 진실 시각 / (3) cycle 1 snapshot JSON 재사용 (새 snapshot 받지 않음, cherry-pick 동기 차단) / (4) 임계값/측정 창/Tier 1/Fallback = cycle 1 그대로 유지. soft contamination 인정 명시 | W2-01 cycle 2 시작 |
| 2026-04-18 | **초안 v2** (1차 외부 감사 CHANGES REQUIRED 반영). 1 BLOCKING + 4 WARNING + 2 NIT 해소: B-1 (Go 기준 자족성 박스 섹션 3.0 추가) / W-1 (섹션 8 snapshot 재취득 행 cycle 1 정책 정확 인용) / W-2 (섹션 2 예상 결과 anchoring 블록 제거) / W-3 (섹션 5 의미 변경 판단 기준 명시) / W-4 (섹션 5 Tier 2 페어별 행 분리 절차 박제) + NIT (PEPE 표기 + 종료일 sub-plan 인용). 2차 외부 감사 대기 | W2-01 cycle 2 1차 외부 감사 |
| 2026-04-18 | **초안 v3** (자가 추가 검증 5 WARNING + 4 NIT 해소): W-A (상태 라벨 v1→v3 동기화) / W-B (cycle 2 evidence "작성 예정" → "1차 작성 완료") / W-C (의사 코드 stablecoin 비교 표현 정확화 + Python 의사 코드 박제) / W-D (L76 vs L106 stablecoin 일관성 + 누락 안전판) / W-E (Tier 2 0개 통과 표 행 처리 절차) / NIT-A (Tier 1 이례 케이스 발생 확률 명시) / NIT-B (snapshot 재취득 두 단계 박제 명확화) / NIT-C (의사 코드에 "W2-01.2 단계 구현" 시점 명시) / NIT-D (섹션 6.4 Fallback ii 사이클 반복 한도 권고 신설). 2차 외부 감사 대기 | cycle 2 자가 검증 |
| 2026-04-19 | **초안 v4** (2차 외부 감사 APPROVED with follow-up + W2-1/W2-2 사용자 결정 채택 반영). NIT2-1 (sub-plan L144→L145 정정) + NIT2-2 (cycle 1 어조 정정, "약점 제거"→"외부 제약 발견에 따른 정책 진화") + W2-1 (decisions-final.md "cycle 1 격리 양성 목록 박제" 신설 + cycle 2 L149 인용 변경) + W2-2 (decisions-final.md "Fallback (ii) 누적 한도 = 3회" 박제 + cycle 2 섹션 6.4 권고→박제 인용 격상). NIT2-3은 사용자 승인 후 sub-plan 갱신 시 처리 예정. 사용자 최종 승인 대기 | cycle 2 2차 외부 감사 + W2-1/W2-2 사용자 결정 |
| 2026-04-19 | **v5** (cycle 2 W2-01.2 단계 2 + 단계 2-2 완료 + 사용자 확정 리스트 승인). Tier 2 코드 산출 = `[XRP, SOL, TRX, DOGE]` (4개 모두 PASS) / 상장일 + 거래대금 검증 통과 / pyupbit `value` 필드 확인 / 100억 sanity 4.11x 초과 (사용자 100억 유지 결정) / 공지 cross-check 스킵 (사용자 결정) / Common-window 시작일 = 2021-10-15 (SOL 기준). **섹션 6.1 + 6.2 freeze 동시 발효**. evidence: `.evidence/w2-01-cycle2-step2-tier2-decision-2026-04-19.md` | cycle 2 W2-01.2/.3 사용자 승인 |
| TBD | 실측 결과 + 확정 리스트 추가 | W2-01.2/.3 cycle 2 완료 |

---

## 8. cycle 1 → cycle 2 변경 요약 (외부 감사용)

| 항목 | cycle 1 (v4, 격리) | cycle 2 (v4, 본 문서) | 변경 사유 |
|------|-------------------|-----------------------|----------|
| Tier 2 박제 방식 | 추정 리스트 {XRP, SOL, ADA, DOGE} 박제 | 규칙만 박제 + 코드 자동 결정 | cycle 1 ADA top10 밖(14위) 빗나감 사례. 인간 추정 단계 = cherry-pick 유혹 발생점, 코드로 차단 |
| snapshot 시각 박제 | snapshot_utc=2026-04-17T00:00:00 명목 + fetched_at=07:08:56 (7시간 차이) | **fetched_at=2026-04-17T07:08:56만 진실 시각**, snapshot_utc 개념 폐기 | CoinGecko 무료 API historical 미제공이라는 외부 제약을 cycle 2 단계에서 발견함에 따라 정책 진화. cycle 1 박제는 박제 시점 적합한 결정이었음 (NIT2-2 해소) |
| snapshot 재취득 | "W2 실행 중 재조회 금지" 박제 (cycle 1 v4 L34/L233) | **cycle 1 JSON 재사용 + SHA256 무결성 재검증, 새 fetch 금지** | cycle 1 정책 강화 (자가 검증 NIT-B 해소): cycle 1의 "cycle 1 사이클 내 재조회 금지" → cycle 2의 "cycle 1 JSON 재사용 + cycle 2 사이클 내 새 fetch 금지" (두 단계 박제). 새 snapshot = "ADA 다시 top10 진입 기대" cherry-pick 동기 차단 |
| 임계값 (시총 30위, 상장 3년+, 거래대금 100억) | 박제 | **그대로 유지** | 결과 보고 임계값 변경 = cherry-pick. soft contamination 인정 |
| 측정 창 (2026-03-13~04-11 UTC) | 박제 | **그대로 유지** | 동일 |
| Tier 1 ({BTC, ETH}) | 박제 | **그대로 유지** | 동일 |
| Fallback (i)/(ii) | 박제 | **그대로 유지** | 동일 |
| Common-window 정책 | 박제 | **그대로 유지** | 동일 |
| 갭 처리 정책 | 박제 | **그대로 유지** | 동일 |
| 승인 2단계 + 이원 freeze | 박제 | **그대로 유지** | 동일 |
| 새 차단 규칙 (vol/cap 등) | 없음 | **추가 안 함** | 추가 검토했으나 cycle 1 결과 의존 = soft contamination → 제거. 우리 시스템 기존 차단(필수 전제 + 거래대금 100억)에 위임 |

---

**관련 문서**:
- `docs/pair-selection-criteria-week2.md` v4 (cycle 1, 참고 자료 격리)
- `docs/stage1-subplans/w2-01-data-expansion.md` (cycle 2 진입 시 sub-plan 갱신 필요)
- `docs/decisions-final.md` 관련 섹션 (전체 리스트는 L22 상위 문서 참조: 사이클 중단 + cycle 1 격리 양성 목록 + Fallback (ii) 누적 한도 박제)
- `docs/candidate-pool.md` (Strategy A/C/D + B Deprecated)
- `research/data/coingecko_top30_snapshot_20260417.json` (cycle 1 산출물 재사용, 로컬 보존, gitignored, 옵션 B)
