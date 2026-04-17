# Task W2-01 - 데이터 확장 + 페어 선정 사전 지정

## 메인 Task 메타데이터

| 항목 | 값 |
|------|-----|
| **메인 Task ID** | W2-01 |
| **Feature ID** | BT-003 |
| **주차** | Week 2 (Day 1-2) |
| **기간** | 2일 (SubTask 순효용 ~1.9일 = 0.2+0.3+0.2+0.5+0.3+0.2+0.2, 사용자 승인/재검증 ~0.1일 buffer) |
| **스토리 포인트** | 5 |
| **작업자** | Solo (Claude + 사용자 기준 승인) |
| **우선순위** | P0 (W2-02/W2-03 차단) |
| **상태** | Pending |
| **Can Parallel** | NO (W2-02, W2-03이 의존) |
| **Blocks** | W2-02, W2-03, W3-* |
| **Blocked By** | W1-06 (No-Go 결정 완료, 2026-04-17) |

## 배경 (Week 2 재범위 후)

Week 1에서 Strategy A/B가 사전 지정 Go 기준 미달(B Sharpe 0.14 FAIL) + Strategy A 최근 481일 Sharpe -1.14. Week 2를 **"전략 후보 재탐색 + 메이저 알트 확장"**으로 재설계. W2-01은 그 첫 단계로 **페어 선정 기준을 사전 지정하고 데이터를 freeze**한다.

**외부 감사 반영 (2026-04-17 리뷰)**: Primary Go 기준은 Tier 1 (BTC+ETH) × 3 전략 = 6셀 + DSR > 0 필수. Tier 2 알트는 exploratory (primary Go 기여 X). Multiple testing 한계 명시. 상세는 `docs/decisions-final.md` "Week 2 한계 및 독립성 서약" 섹션.

**핵심 원칙**:
- **사전 지정 선정 기준** (시총 스냅샷, 상장 cutoff 날짜, 거래대금 측정 창) — 결과 보고 선별 금지
- **Survivorship bias 방지** — 현재 시총 기준만 쓰지 말고 상장 기간 제약 추가
- **데이터 freeze + SHA256** — W1-01 패턴 재사용, advertised 범위 slicing
- **CoinGecko 응답 원본 freeze** — 스냅샷 재현 가능성 보장
- **알트별 파라미터 튜닝 금지** — W2-03에서 동일 파라미터로만 평가
- **임계값 변경 금지** — Tier 2 후보 부족 시 완화 대신 **Fallback (i) Tier 2 제거 (primary 6셀 유지, exploratory만 감소)** 또는 **(ii) Task 재설계** 루프. 상세는 `docs/pair-selection-criteria-week2.md` 섹션 3

## 개요

업비트 KRW 페어 중 사전 지정 기준을 충족하는 **Tier 1 필수 + Tier 2 후보 5-6개**의 5년 일봉/4시간봉 데이터를 pyupbit로 수집, UTC 변환, Parquet freeze, SHA256 기록. 기존 BTC 데이터(W1-01)는 재사용. `data_hashes.txt`에 신규 해시 추가.

## 현재 진행 상태

- 메인 Task 상태: Pending
- 선행 조건: W1-06 No-Go 결정 (완료), Week 2 재범위 승인 (완료 2026-04-17)

| SubTask | 상태 | 메모 |
|---------|------|------|
| W2-01.1 | Pending | 페어 선정 기준 사전 지정 + 사용자 승인 |
| W2-01.2 | Pending | 기준 충족 후보 조회 (CoinGecko + 업비트 API) |
| W2-01.3 | Pending | 최종 후보 확정 + freeze |
| W2-01.4 | Pending | 데이터 수집 노트북 07 (5-6 페어 × 일봉/4h) |
| W2-01.5 | Pending | 데이터 무결성 검증 (갭, 중복, UTC) |
| W2-01.6 | Pending | SHA256 + data_hashes.txt 갱신 |
| W2-01.7 | Pending | Evidence + backtest-reviewer |

## SubTask 목록

### SubTask W2-01.1: 페어 선정 기준 사전 지정

**작업자**: Solo + 사용자 승인
**예상 소요**: 0.2일

**사전 지정 기준 (측정 방법 박제)**:

| 기준 | 임계값 | 측정 방법 / 근거 |
|------|--------|------------------|
| 시가총액 (CoinGecko) | 상위 30위 | `GET /coins/markets?vs_currency=krw&order=market_cap_desc&per_page=30&page=1`. **스냅샷: 2026-04-17 00:00 UTC (W1-06 결정일 자정 기준)**. 응답 JSON 원본 `research/data/coingecko_top30_snapshot_20260417.json`로 저장 + SHA256 `data_hashes.txt` 기록 |
| 업비트 KRW 페어 상장일 | **≤ 2023-04-17** | W1-06 결정일(2026-04-17) 기준 정확히 3년 전. 5년 advertised 범위 중 60%+ 확보. 상장일 출처: 업비트 공식 공지 또는 `pyupbit.get_ohlcv_from()` 최초 캔들 날짜 |
| 업비트 거래대금 | 측정 창 내 30 UTC-day 단순 평균 **≥ 100억 원** | 측정 창: **2026-03-13 ~ 2026-04-11 (UTC, inclusive 양끝, 정확히 30 UTC days, W1 freeze 2026-04-12 직전)**. 기본 산식: `daily_value_i = close_i × volume_i` (일봉 OHLCV 종가 근사, KRW). **업비트 API 응답에 실측 거래대금 필드(`value`/`candle_acc_trade_price`) 존재 시 해당 필드 직접 사용** (근사 오차 제거, `pair-selection-criteria-week2.md` L53 지시). 평균 산식: `Σ(daily_value_i) / 30`. **pandas `.rolling(30).mean()` 벡터 연산 아닌 단일 창 평균**. **24h 스팟 거래대금 사용 금지** |
| 업비트 KRW 페어 존재 | 필수 | 프로젝트는 KRW 페어만 |
| 선물/파생 여부 | 금지 | 현물만 |
| 100억 임계값 근거 | 추정 | W2-01.2에서 실측 slippage 검증 전 잠정. 업비트 시총 상위 20위 알트의 2025 평균 거래대금 분포 기준 중앙값 수준 (W2-01.2 검증 결과 불일치 시 사용자 보고 후 결정, 임계값 변경은 새 사전 등록 사이클 필요) |

**Tier 분류**:
- **Tier 1 (필수 포함)**: BTC (W1 재사용), ETH
- **Tier 2 (후보, 기준 충족 시 포함)**: XRP, SOL, ADA, DOGE
- **Tier 3 (옵션, Week 2 불포함)**: SHIB, LINK 등 — 밈 특성 또는 유동성 이슈로 별도 실험 트랙 검토
- **영구 제외**: PEPE (상장 <3년), BONK/WIF 등 소형 밈, 시총 >30위

- [ ] 기준 문서화: `docs/pair-selection-criteria-week2.md` 작성
- [ ] 사용자 명시적 승인 (기준 임계값 수정 여지 있음) → **`pair-selection-criteria-week2.md` 섹션 6.1 기준 freeze 발효**
- [ ] 승인 후 기준 freeze (W2 중간에 변경 금지, 변경 시 snooping)

### SubTask W2-01.2: 기준 충족 후보 조회 + 스냅샷 freeze

**작업자**: Solo
**예상 소요**: 0.3일 (스냅샷 저장 + 실측 검증 추가)

- [ ] **시총 스냅샷 조회 + 원본 저장**:
  ```python
  import requests, json, hashlib
  from datetime import datetime, timezone
  
  SNAPSHOT_UTC = "2026-04-17T00:00:00+00:00"  # W1-06 결정일 자정 박제
  r = requests.get("https://api.coingecko.com/api/v3/coins/markets",
      params={"vs_currency": "krw", "order": "market_cap_desc",
              "per_page": 30, "page": 1})
  snapshot = {
      "snapshot_utc": SNAPSHOT_UTC,
      "fetched_at": datetime.now(timezone.utc).isoformat(),
      "api_endpoint": r.url,
      "data": r.json(),
  }
  with open("research/data/coingecko_top30_snapshot_20260417.json", "w") as f:
      json.dump(snapshot, f, indent=2)
  # SHA256 → data_hashes.txt 기록
  ```
- [ ] pyupbit로 KRW 마켓 전체 페어 목록 조회 (`pyupbit.get_tickers("KRW")`)
- [ ] CoinGecko top30 ∩ 업비트 KRW 페어 교집합 산출
- [ ] **각 후보의 업비트 KRW 상장일 조회** (`pyupbit.get_ohlcv_from()` 최초 캔들 날짜 기준). **상장일 ≤ 2023-04-17**인 페어만 통과.
- [ ] **각 후보의 30 UTC-day 단순 평균 거래대금 실측** (측정 창 **2026-03-13 ~ 2026-04-11 UTC inclusive, 정확히 30일**, `daily_value = close × volume`). 구현: `df.loc["2026-03-13":"2026-04-11", "daily_value"].mean()`. **≥ 100억 원**인 페어만 통과.
- [ ] 기준 3개 모두 충족하는 후보 리스트업 (표로 정리, 기록은 `docs/pair-selection-criteria-week2.md`)
- [ ] **100억 임계값 sanity check**: 상위 20위 알트의 거래대금 분포와 비교. 중앙값과 크게 괴리 시 사용자 보고 (단 임계값 변경은 새 사전 등록 사이클 필요)
- [ ] **CoinGecko rate limit 확인** (2026-04-17 공식 docs 기준). Retry-After 헤더 읽기 로직 포함

### SubTask W2-01.3: 최종 후보 확정 + freeze + Strategy A 후보 풀 물리화

**작업자**: Solo + 사용자 승인
**예상 소요**: 0.2일

- [ ] W2-01.2 결과로 Tier 1/2 최종 리스트 확정
  - Tier 1 (primary Go 대상): BTC (재사용), ETH
  - Tier 2 (exploratory 대상): XRP, SOL, ADA, DOGE 중 기준 충족 페어
  - 기준 미달 시 대체 없음 (임의 대체 = snooping)
- [ ] **Tier 2 <2 fallback 정책 명시**:
  - (i) **Tier 2 제거**: Tier 1 × {A,C,D} = primary 6셀 **그대로 유지**. Tier 2 exploratory만 통과 페어 수 × 3 전략으로 감소 (임계값 변경 X, Go 기준 변경 X)
  - (ii) 또는 Task 전체 재설계 → 새 사전 등록 + backtest-reviewer + 사용자 승인 루프
  - **임계값 완화 금지** (snooping의 정의 그대로임)
  - 상세: `docs/pair-selection-criteria-week2.md` 섹션 3
- [ ] 사용자 승인 + 리스트 freeze → **`pair-selection-criteria-week2.md` 섹션 6.2 확정 리스트 freeze 발효**
- [ ] `docs/pair-selection-criteria-week2.md`에 확정 리스트 기록
- [ ] **변경 금지 서약**: "W2 실행 중 결과 보고 페어 추가/제거 금지"
- [ ] **Strategy A 후보 풀 물리화**: `docs/candidate-pool.md` 신설
  - Strategy A 파라미터 (MA=200, Donchian=20/10, Vol>1.5x, SL=8%) 저장
  - W2-03 재검증 시 DSR-adjusted 평가 필수 규정
  - Strategy B는 폐기 로그로 기록 (재등장 방지)

### SubTask W2-01.4: 데이터 수집 노트북 07

**작업자**: Solo
**예상 소요**: 0.5일

- [ ] `research/_tools/make_notebook_07.py` 작성 (nbformat)
- [ ] `research/notebooks/07_data_expansion.ipynb` 빌드
- [ ] W1-01의 `fetch_with_retry` 함수 재사용
- [ ] 각 Tier 1-2 페어 (BTC 제외) × 일봉 + 4시간봉 = 총 10개 dataset 수집
  ```python
  PAIRS = ["KRW-ETH", "KRW-XRP", "KRW-SOL", "KRW-ADA", "KRW-DOGE"]
  RANGE = ("2021-01-01", "2026-04-12")  # W1-01과 동일 advertised 범위
  for pair in PAIRS:
      for interval, suffix in [("day", "1d"), ("minute240", "4h")]:
          df = fetch_with_retry(pair, interval, *RANGE)
          assert df.index.tz is None  # naive KST
          df.index = df.index.tz_localize('Asia/Seoul').tz_convert('UTC')
          df = df.loc[RANGE[0]:RANGE[1]]  # advertised slicing
          df.to_parquet(f"research/data/{pair}_{suffix}_frozen_20260412.parquet")
  ```
- [ ] 상장 <2021-01-01 페어의 경우 실제 첫 캔들부터 수집 + metadata에 실제 범위 기록
- [ ] period=0.2 (rate limit 안전 마진)
- [ ] 재시도 wrapper (None 반환 대응)

### SubTask W2-01.5: 데이터 무결성 검증 + common-window 사전 결정

**작업자**: Solo
**예상 소요**: 0.3일

- [ ] 각 페어별 갭 < 0.1% 검증 (W1-01 `check_gaps` 재사용)
- [ ] 중복 인덱스 0 확인
- [ ] `df.index.is_monotonic_increasing` == True
- [ ] `df.index.tz == UTC` 확인
- [ ] bars 수 기대치 근사 확인 (일봉 ~1927, 4h ~11561)
- [ ] 상장 <2021-01-01 페어는 실제 범위 기록 (예: ADA가 2021-03-01 상장이면 bars=1867)
- [ ] **Common-window 사전 결정 (W-2 대응)**:
  - 각 페어 actual 범위 수집 후, 상장 가장 늦은 페어의 start date를 common window 시작점으로 채택
  - 예: SOL 상장일(2021년 추정, W2-01.2 실측 확정)이 가장 늦으면 common window = SOL 상장일 ~ 2026-04-12 UTC (W1 freeze 종료일)
  - W2-03 grid에서 **primary metric은 페어별 max-span Sharpe**, **secondary metric은 common-window Sharpe** 둘 다 계산
  - Common-window 시작점을 `docs/pair-selection-criteria-week2.md`에 기록 (사전 freeze)
- [ ] 샘플 시각화: 각 페어 normalized price plot + common-window 시작선 표시 (outputs에 저장)

### SubTask W2-01.6: SHA256 + data_hashes.txt 갱신

**작업자**: Solo
**예상 소요**: 0.2일

- [ ] 각 Parquet SHA256 계산
- [ ] `research/data/data_hashes.txt`에 신규 hash 추가 (BTC 기존 행 유지)
  ```
  # Week 1 (BTC only, 2026-04-14)
  KRW-BTC_1d_frozen_20260412.parquet: <hash>
  KRW-BTC_4h_frozen_20260412.parquet: <hash>
  # Week 2 expansion (2026-MM-DD)
  KRW-ETH_1d_frozen_20260412.parquet: <hash>
  KRW-ETH_4h_frozen_20260412.parquet: <hash>
  ...
  ```
- [ ] Advertised + actual 범위 헤더 기록
- [ ] 상장 <2021-01-01 페어는 actual 범위 별도 표기

### SubTask W2-01.7: Evidence + 리뷰

**작업자**: Solo + backtest-reviewer
**예상 소요**: 0.2일

- [ ] `.evidence/w2-01-data-expansion.txt` 작성 (6단 구조)
- [ ] backtest-reviewer 호출
- [ ] APPROVED 받음
- [ ] sub-plan + execution-plan 상태 업데이트
- [ ] 커밋: `feat(plan): BT-003 W2-01 데이터 확장 + 페어 선정 사전 지정`

## 인수 완료 조건 (Acceptance Criteria)

- [ ] 페어 선정 기준 문서 (`docs/pair-selection-criteria-week2.md`) 생성 + 사용자 승인 (측정 방법 박제 포함)
- [ ] CoinGecko 시총 스냅샷 원본 JSON 저장 + SHA256 기록 (`research/data/coingecko_top30_snapshot_20260417.json`)
- [ ] 각 후보의 상장일 + 30 UTC-day 단순 평균 거래대금 실측 완료 (측정 창 2026-03-13 ~ 2026-04-11 UTC inclusive)
- [ ] 최종 페어 리스트 확정 (Tier 1 2개 필수, Tier 2 0~4개)
- [ ] Tier 2 <2 시 B-5 fallback 정책 적용 + 사용자 승인
- [ ] Strategy A 후보 풀 물리화 (`docs/candidate-pool.md` 신설)
- [ ] `07_data_expansion.ipynb` 실행 성공
- [ ] Tier 1-2 모든 페어 일봉 + 4h 데이터 Parquet freeze 완료
- [ ] 각 페어 갭 < 0.1%, UTC 변환, monotonic 확인
- [ ] Common-window 시작일 사전 결정 + `pair-selection-criteria-week2.md`에 기록
- [ ] `research/data/data_hashes.txt` 갱신 (parquet + CoinGecko JSON 포함, advertised + actual 범위 헤더)
- [ ] backtest-reviewer APPROVED
- [ ] sub-plan + execution-plan status 업데이트

## 의존성 매트릭스

| From | To | 관계 |
|------|-----|------|
| W1-06 | W2-01 | 결정 선행 (No-Go 후 재범위) |
| W2-01 | W2-02 | 데이터 freeze 후 전략 사전 등록 |
| W2-01 | W2-03 | 데이터 + 페어 리스트가 grid 입력 |

## 리스크 및 완화 전략

| 리스크 | 영향 | 완화 |
|--------|------|------|
| Tier 2 후보 <2개 | Medium | **임계값 완화 금지**. **Fallback (i) Tier 2 제거** (primary 6셀 그대로 유지, exploratory 통과 수 × 3 전략으로 감소) 또는 **(ii) Task 재설계** 루프 중 택일. 상세는 `docs/pair-selection-criteria-week2.md` 섹션 3 (B-5 fallback 정책) |
| 상장 기간 <5년 페어 (SOL, DOGE 등) | Medium | 실제 상장일 기록 + **common-window 사전 결정** (W-2). W2-03에서 페어별 max-span + common-window 둘 다 metric 계산 |
| CoinGecko rate limit | Low | **2026-04-17 공식 docs 기준** 무료 분당 10-30 requests. Retry-After 헤더 처리 + 단일 스냅샷 재사용 (재조회 금지) |
| CoinGecko 스냅샷 비재현성 | Medium | 스냅샷 원본 JSON `coingecko_top30_snapshot_20260417.json` 저장 + SHA256 freeze. W2 중 재조회 절대 금지 |
| pyupbit rate limit | Low | period=0.2, 재시도 wrapper (W1-01 패턴 재사용) |
| 페어 거래정지/상장폐지 이력 | Medium | 업비트 공지 확인. 과거 거래정지 구간 metadata 기록. W2-03에서 해당 기간 gap 처리 정책 명시 |
| 페어 선정 후 "더 좋은 알트 있다" 유혹 | **High** | freeze 원칙 엄수. 변경은 새 사전 등록 사이클(새 W2-01) 필요 |
| Strategy C/D 파라미터 soft contamination | **High** | 완전 독립 불가 인정. 문헌 기본값 사용 서약(`decisions-final.md` "Week 2 한계" 섹션). 최종 검증은 Week 3 walk-forward |
| 100억 임계값 실측 불일치 | Medium | W2-01.2에서 20위 알트 거래대금 분포와 비교 sanity check. 변경 시 새 사전 등록 |
| Multiple testing (6 primary 셀) | **High** | DSR > 0 필수 + Week 3 walk-forward 최종 검증. Tier 2 12셀은 exploratory로 격리 |

## 산출물 (Artifacts)

### 코드
- `research/_tools/make_notebook_07.py`
- `research/notebooks/07_data_expansion.ipynb`

### 데이터 (parquet gitignored, JSON snapshot은 git tracked)
- `research/data/KRW-{ETH,XRP,SOL,ADA,DOGE}_{1d,4h}_frozen_20260412.parquet` (gitignored)
- `research/data/coingecko_top30_snapshot_20260417.json` (git tracked, 재현성 위해)
- `research/data/data_hashes.txt` (갱신, git tracked, parquet + JSON 해시 포함)

### 문서
- `docs/pair-selection-criteria-week2.md` (기준 + 확정 리스트 + common-window 시작일)
- `docs/candidate-pool.md` (신규, Strategy A 파라미터 + Strategy B 폐기 로그 + recall 규정)

### 검증
- `.evidence/w2-01-data-expansion.txt`

### 테스트 시나리오
- **Happy**: Tier 1 2개 + Tier 2 4개 모두 기준 충족 → 6 페어 데이터 freeze (BTC 재사용 포함)
- **Denial 1 (Tier 2 <2)**: **임계값 완화 금지**. (i) Tier 1 2개(BTC+ETH) primary 축소 or (ii) Task 재설계 루프 중 택일. 사용자 보고 + 명시적 선택
- **Denial 2 (상장 <5년)**: SOL 등 상장 2021-04 이후인 페어 → 실제 범위 기록 + common-window 사전 결정 + primary/secondary metric 이원화
- **Denial 3 (거래정지 이력)**: LUNA/UST 같은 과거 폐지 이력 페어 포함 시 metadata 기록 + W2-03에서 해당 gap 처리 정책 문서화
- **Edge (시총 스냅샷 불안정)**: CoinGecko 30위 경계 코인이 순위 변동 시 freeze된 스냅샷만 사용, 재조회 금지

## Commit

```
feat(plan): BT-003 W2-01 데이터 확장 + 페어 선정 사전 지정

- 페어 선정 기준 박제:
  - CoinGecko 시총 상위 30 (스냅샷 2026-04-17 00:00 UTC, JSON 원본 freeze)
  - 업비트 KRW 상장일 <= 2023-04-17
  - 30 UTC-day 단순 평균 거래대금 >= 100억 원 (측정 창 2026-03-13 ~ 2026-04-11 UTC inclusive, 정확히 30일)
- Tier 1 필수: BTC (W1 재사용), ETH
- Tier 2 확정: {XRP, SOL, ADA, DOGE} 중 기준 충족 페어
- Tier 2 <2 fallback: 완화 금지, Tier 2 제거(primary 6셀 그대로) or 재설계 루프
- Strategy A 후보 풀 물리화 (candidate-pool.md)
- 5년 일봉/4h 데이터 freeze (UTC, SHA256)
- Common-window 시작일 사전 결정 (페어별 max-span + common-window 이원 metric)

Evidence: w2-01-data-expansion.txt (APPROVED)
```

---

**이전 Task**: [W1-06 Week 1 리포트 + Go/No-Go](./w1-06-week1-report.md) (No-Go 결정 완료)
**다음 Task**: W2-02 새 전략 후보 사전 등록 (W2-01 완료 후 sub-plan 상세 작성)
