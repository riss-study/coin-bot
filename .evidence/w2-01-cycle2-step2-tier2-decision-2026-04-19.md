# W2-01 cycle 2 단계 2 — Tier 2 결정 결과 박제 (2026-04-19)

**박제 출처**: `docs/pair-selection-criteria-week2-cycle2.md` v4 (코드 산출 결과 = 최종, 인간 개입 금지)
**실행 코드**: `research/_tools/cycle2_tier2_decision.py`
**실행 시점**: 2026-04-19
**박제 의미**: 본 결과는 cycle 2 v4 박제 + 사용자 승인 (2026-04-19 위임 발화)에 의해 자동 채택. 인간이 결과 보고 페어 추가/제거 시도 = cherry-pick = cycle 3 신규 박제 강제 (Fallback (ii) 누적 한도 3회).

---

## 외부 감사 trace

- `.evidence/agent-reviews/w2-01-cycle2-step2-code-review-2026-04-19.md`: 코드 외부 감사 (NIT2-3 절차)
- 판정: APPROVED with follow-up (BLOCKING 0 / WARNING 3 정정 / NIT 4 일부 정정)
- 정정: W-1 path 절대화, W-3 라벨, NIT-1/2/3 (docstring + read 효율 + name truncation)
- 보류: W-2 새 스테이블 안전판 false negative (본 사이클 영향 X, cycle 3 보강 권고)

---

## 코드 stdout (재현성 박제)

```
============================================================
W2-01 cycle 2 단계 2: Tier 2 결정 (코드 자동 산출, 인간 개입 금지)
============================================================
박제 stablecoin_set (11개): ['BUSD', 'DAI', 'FDUSD', 'FRAX', 'PYUSD', 'TUSD', 'USD1', 'USDC', 'USDE', 'USDS', 'USDT']

[OK] SHA256 무결성 검증 PASS: c70a108905566f00f1b5b97fd3b08bf13be38d713f351027861d78869b3fcf59
[OK] snapshot fetched_at (진실 시각): 2026-04-17T07:08:56.048102+00:00

=== snapshot top10 (시총 상위 10) ===
   1. BTC          Bitcoin                        cap= 2,226,779,724,214,312
   2. ETH          Ethereum                       cap=   418,073,171,666,739
   3. USDT         Tether                         cap=   275,680,127,917,531
   4. XRP          XRP                            cap=   130,969,669,938,990
   5. BNB          BNB                            cap=   125,792,671,951,472
   6. USDC         USDC                           cap=   116,762,784,343,460
   7. SOL          Solana                         cap=    75,251,502,933,386
   8. TRX          TRON                           cap=    45,844,118,805,090
   9. FIGR_HELOC   Figure Heloc                   cap=    25,791,371,854,380
  10. DOGE         Dogecoin                       cap=    22,316,363,560,556

=== 업비트 KRW 페어 조회 ===
[OK] 업비트 KRW 페어 수: 247

============================================================
=== Tier 2 결정 결과 (코드 자동 산출 = 최종) ===
============================================================
Tier 1 (필수): BTC, ETH
Tier 2 후보 (top10 ∩ KRW ∩ BTC/ETH 제외 ∩ 스테이블 제외): ['XRP', 'SOL', 'TRX', 'DOGE']

--- top10 중 Tier 2 제외 사유 ---
  BTC          → Tier 1 (필수, 본 단계 Tier 2 결정 대상 아님 — 별도 처리)
  ETH          → Tier 1 (필수, 본 단계 Tier 2 결정 대상 아님 — 별도 처리)
  USDT         → 스테이블 제외
  BNB          → 업비트 KRW 미상장
  USDC         → 스테이블 제외
  FIGR_HELOC   → 업비트 KRW 미상장

============================================================
=== 새 스테이블 안전판 (사용자 검토) ===
============================================================
박제 stablecoin_set 외 가치 고정 토큰이 top10에 진입했는지 검토 필요.
발견 시: 즉시 사용자 보고 + cycle 3 신규 박제 (단순 추가 금지).

--- top10 코인 중 위 분류에 들어가지 않은 항목 (수동 검토 대상) ---
  BNB          (업비트 KRW 미상장이지만 새 스테이블 가능성 검토)
  FIGR_HELOC   (업비트 KRW 미상장이지만 새 스테이블 가능성 검토)
```

---

## 직접 검증 결과 (사용자 "재검증" 요청 응답)

### FIGR_HELOC 스테이블 가능성 검증

| 필드 | 값 | 판정 |
|------|-----|------|
| id | `figure-heloc` | — |
| name | Figure Heloc | — |
| current_price | **1,534.08 KRW** (≈ $1.05) | 스테이블 가격대 X |
| ATH | 1,574.03 | — |
| ATL | **222.00** (현재 대비 7배 변동) | **스테이블 X 확정** |
| 24h price_change | 1.23% | 변동성 있음 |

→ HELOC = Home Equity Line of Credit RWA 토큰. 가격 변동성으로 스테이블 X 확정 (CLAUDE.md "추측 금지" 검증 완료).

### 업비트 KRW 페어 직접 검증 (코드 결과 cross-check)

| ticker | 코드 결과 | 직접 검증 | 일치 |
|--------|----------|----------|------|
| KRW-BNB | 없음 | 없음 ✗ | ✓ |
| KRW-TRX | 있음 | 있음 ✓ | ✓ |
| KRW-FIGR_HELOC | 없음 | 없음 ✗ | ✓ |
| KRW-XRP | 있음 | 있음 ✓ | ✓ |
| KRW-SOL | 있음 | 있음 ✓ | ✓ |
| KRW-DOGE | 있음 | 있음 ✓ | ✓ |
| KRW-ADA | — | **있음 ✓** | (Tier 2 후보 아님 — top10 외) |

→ 코드 결과 100% 정확 (외부 라이브러리 호출 검증 완료).

### 핵심 발견 — ADA 자동 배제 사유

**ADA: 14위, market_cap 14,005,043,792,178, current_price 379.24 KRW, 업비트 KRW 상장 ✓**

→ ADA가 KRW 상장됨에도 **시총 top10 외(14위)**라서 cycle 2 규칙(top10 ∩ KRW ∩ ...)에 의해 **자동 배제**. cycle 1 박제 ({XRP,SOL,ADA,DOGE}) 빗나감의 정확한 원인.

---

## 최종 박제 (cycle 2 v4 섹션 5 인용용)

| 필드 | 값 |
|------|-----|
| **Tier 1 (primary 필수)** | KRW-BTC (W1 재사용), KRW-ETH |
| **Tier 2 (코드 자동 결정 결과)** | **KRW-XRP, KRW-SOL, KRW-TRX, KRW-DOGE** (4개) |
| Tier 2 후보 수 | 4 (Fallback 미발동, ≥ 2 충족) |
| snapshot 시각 (진실) | 2026-04-17T07:08:56.048102+00:00 |
| snapshot SHA256 | c70a108905566f00f1b5b97fd3b08bf13be38d713f351027861d78869b3fcf59 |
| 업비트 KRW 페어 수 | 247 |

**박제 강도**: 본 결과는 cycle 2 v4 + decisions-final.md "cycle 1 격리 양성 목록 박제" + "Fallback (ii) 누적 한도 박제" 동시 발효 시점(2026-04-19) 채택. 다음 단계(상장일 + 거래대금 검증)에서 일부 페어가 기준 미달로 탈락 가능. 단 본 4개 후보 자체는 "코드 자동 산출 = 최종" 박제이며, **인간 개입으로 대체 페어 추가 절대 금지**.

---

## 단계 2-2 결과 (상장일 + 거래대금 검증, 2026-04-19)

**실행 코드**: `research/_tools/cycle2_tier2_validation.py`

### 페어별 검증 결과 (4개 모두 PASS)

| 페어 | 상장일 (UTC) | 기준 2 (≤2023-04-17) | 30일 평균 거래대금 | 기준 3 (≥100억) | 종합 |
|------|-------------|----------------------|-------------------|----------------|------|
| KRW-XRP | 2017-09-25 | PASS (5.5년 마진) | 187,899,424,186 (187.9억) | PASS (18.79x) | **확정** |
| KRW-SOL | 2021-10-15 | PASS (1.5년 마진) | 41,060,227,303 (41.1억) | PASS (4.11x) | **확정** |
| KRW-TRX | 2018-04-05 | PASS (5년 마진) | 13,782,597,882 (13.8억) | PASS (1.38x) | **확정** |
| KRW-DOGE | 2021-02-24 | PASS (2.1년 마진) | 29,809,287,649 (29.8억) | PASS (2.98x) | **확정** |

### 박제 사실

- **pyupbit 일봉 응답 필드 = `value`** 존재 확인 (cycle 2 v4 L64 박제 우선 사용 조건 충족, sub-plan L65 갱신 사항)
- 측정 창 30 rows 모두 OK (2026-03-13 ~ 2026-04-11 UTC inclusive)
- 상장일 sanity check 모두 OK (최초 30캔들 max gap < 7일, XRP=4일 / SOL=1일 / TRX=1일 / DOGE=1일)

### 100억 sanity check (cycle 2 v4 L68)

- 본 4개 후보 거래대금 중앙값 = 41.1억 KRW (임계값 대비 4.11x)
- **±30% 초과** → 사용자 보고 발동
- 사용자 결정 (2026-04-19 "ㄱㄱ"): **본 사이클 100억 유지 완주, 임계값 변경은 cycle 3로만**
- 4개 모두 통과로 사실상 영향 없음 (Fallback 미발동)

### 박제 우선순위 cross-check (cycle 2 v4 L52-53)

- 박제 우선순위: (1) 업비트 공식 공지 우선 (2) pyupbit 폴백
- 사용자 결정 (2026-04-19 "ㄱㄱ"): **수동 cross-check 스킵** (pyupbit 결과 신뢰)
- 위험: 업비트 공식 공지와 pyupbit 결과 불일치 시 미발견 가능. 단 4개 모두 cutoff 2023-04-17 대비 1.5~5.5년 마진으로 ±수일 어긋남 시 결과 변하지 않음

### Common-window 시작일 산출 (cycle 2 v4 섹션 4 박제)

- Tier 1-2 최종 페어 중 상장일 가장 늦은 페어 = **SOL (2021-10-15 UTC)**
- **Common-window 시작일 = 2021-10-15 UTC** (W2-03 secondary metric 산출 기준)

---

## 최종 확정 (cycle 2 v4 섹션 5 박제 입력)

| 필드 | 값 |
|------|-----|
| **Tier 1 (primary Go 대상)** | KRW-BTC (W1 재사용), KRW-ETH |
| **Tier 2 (exploratory, 코드 자동 결정 + 기준 2/3 통과)** | **KRW-XRP, KRW-SOL, KRW-TRX, KRW-DOGE** (4개 모두 PASS) |
| **Common-window 시작일 (UTC)** | 2021-10-15 (SOL 상장일 기준) |
| **Fallback 발동 여부** | **미발동** (Tier 2 통과 ≥ 2) |
| **사용자 확정 리스트 승인** | **2026-04-19 사용자 명시 OK ("ㄱㄱ", 거래대금 sanity 100억 유지 + 공지 cross-check 스킵 동시 결정)** |
| **cycle 2 v4 섹션 6.2 freeze** | **발효** (사용자 확정 리스트 승인 시점) |

## 다음 단계 (cycle 2 W2-01.4)

- `make_notebook_07.py` 작성 (Tier 1 + Tier 2 = 6 페어 × 일봉/4h = 12 dataset)
- 데이터 수집 + UTC 변환 + Parquet freeze + SHA256
- 무결성 검증 + Common-window 시작일 (2021-10-15) 적용
- backtest-reviewer APPROVED
