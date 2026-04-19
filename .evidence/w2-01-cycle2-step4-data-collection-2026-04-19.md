# W2-01 cycle 2 단계 4 — 데이터 수집 결과 박제 (2026-04-19)

**박제 출처**:
- `docs/pair-selection-criteria-week2-cycle2.md` v5 (cycle 2 박제, 특히 섹션 5 확정 리스트 + 섹션 4 Common-window)
- `docs/stage1-subplans/w2-01-data-expansion.md` W2-01.4
- `.evidence/w2-01-cycle2-step2-tier2-decision-2026-04-19.md` (단계 2/2-2 결과)

**실행 코드**:
- `research/_tools/make_notebook_07.py` (nbformat 제너레이터)
- `research/notebooks/07_data_expansion.ipynb` (실행 노트북)

**실행 시점**: 2026-04-19 11:01 UTC (약 2분 소요)

---

## 1. 데이터 수집 결과 (10 dataset)

| 페어 | interval | rows | actual_start (UTC) | actual_end (UTC) | gap_count | gap_pct |
|------|----------|------|--------------------|------------------|-----------|---------|
| KRW-ETH | day | 1927 | 2021-01-01 00:00 | 2026-04-11 00:00 | 0 | 0.0000% |
| KRW-ETH | 4h | 11561 | 2021-01-01 00:00 | 2026-04-11 20:00 | 1 | 0.0086% |
| KRW-XRP | day | 1927 | 2021-01-01 00:00 | 2026-04-11 00:00 | 0 | 0.0000% |
| KRW-XRP | 4h | 11561 | 2021-01-01 00:00 | 2026-04-11 20:00 | 1 | 0.0086% |
| **KRW-SOL** | **day** | **1640** | **2021-10-15 00:00** | 2026-04-11 00:00 | 0 | 0.0000% |
| **KRW-SOL** | **4h** | **9838** | **2021-10-15 04:00** | 2026-04-11 20:00 | 1 | 0.0102% |
| KRW-TRX | day | 1927 | 2021-01-01 00:00 | 2026-04-11 00:00 | 0 | 0.0000% |
| KRW-TRX | 4h | 11561 | 2021-01-01 00:00 | 2026-04-11 20:00 | 1 | 0.0086% |
| **KRW-DOGE** | **day** | **1873** | **2021-02-24 00:00** | 2026-04-11 00:00 | 0 | 0.0000% |
| **KRW-DOGE** | **4h** | **11236** | **2021-02-24 04:00** | 2026-04-11 20:00 | 1 | 0.0089% |

### Advertised vs actual 범위 차이 (cycle 2 v5 박제 동기화)

- **KRW-ETH/XRP/TRX**: actual = advertised RANGE 그대로 (2021-01-01 ~ 2026-04-11). 상장이 2021-01-01 이전임을 실측 확인
- **KRW-SOL**: actual_start = **2021-10-15** (advertised 2021-01-01 → SOL 상장일로 단축). cycle 2 v5 단계 2-2 박제와 정확히 일치 ✓
- **KRW-DOGE**: actual_start = **2021-02-24** (advertised 2021-01-01 → DOGE 상장일로 단축). cycle 2 v5 단계 2-2 박제와 정확히 일치 ✓

---

## 2. 무결성 검증 (강제 assert 통과)

| 검증 | 결과 |
|------|------|
| monotonic 증가 | **PASS** |
| 중복 인덱스 없음 | **PASS** |
| UTC 타임존 (pandas tz_convert) | **PASS** |
| 갭 비율 < 0.1% | **PASS** (max 0.0102% = SOL 4h, W1-01 BTC 4h 0.0086%와 동일 패턴) |

### Common-window 박제 자동 assert (cycle 2 v5)

```python
assert sol_actual_start.startswith("2021-10-15")  # PASS
```

→ SOL day actual_start = `2021-10-15 00:00:00+00:00` 박제와 정확히 일치.

### ETH 박제 자동 assert (cycle 2 v5 가정)

```python
assert eth_actual_start[:10] <= "2021-01-01"  # PASS
```

→ KRW-ETH day actual_start = `2021-01-01 00:00:00+00:00` (advertised 시작과 동일). ETH가 advertised 시작 이전 상장임을 실측 확인.

---

## 3. SHA256 + data_hashes.txt 갱신

`research/data/data_hashes.txt`에 10개 신규 항목 append (gitignored 유지, 로컬 보존, 옵션 B):

| 파일 | SHA256 | 크기 |
|------|--------|------|
| KRW-ETH_1d_frozen_20260412.parquet | `2dfbb4970bc8b69c80d3f629d488d08f2b71411091e6d4682b638b7b3956c0f0` | 99,475 |
| KRW-ETH_4h_frozen_20260412.parquet | `5ac87e970d6b4b4238b595681d2fa91467a5f92db7069cd9d19079f1f348024e` | 497,450 |
| KRW-XRP_1d_frozen_20260412.parquet | `113f833b88d5b2ce51da52d98d57ab7a4d95c5740459e176fd23965cdf10d492` | 88,563 |
| KRW-XRP_4h_frozen_20260412.parquet | `e02eededab08f31239f80d37c4aa6e56c6a33a873c9714143e67b5f6133b48d4` | 459,750 |
| KRW-SOL_1d_frozen_20260412.parquet | `334effa3d90b4c6a2713c34a6f838d9100f291fc256e81191ec846e4c6b5944a` | 87,068 |
| KRW-SOL_4h_frozen_20260412.parquet | `a7bb0fcabfb58f097310c72ef37fff13d12d3dd36baa76fb4837c7c6614b7ed3` | 453,780 |
| KRW-TRX_1d_frozen_20260412.parquet | `bd6aecfeb818388bb3c5840ce80fef32b17b9d68b4b5a732306af75800f384cb` | 80,741 |
| KRW-TRX_4h_frozen_20260412.parquet | `a94755eaced7a1f6f9c15e06dcf2f04142bd62c52f1aef61aa08496caf4192c9` | 419,685 |
| KRW-DOGE_1d_frozen_20260412.parquet | `04a56db696f2ac5c5ccfcb9661ed4476ede05e3e06e76a87432585a7c4700dff` | 81,744 |
| KRW-DOGE_4h_frozen_20260412.parquet | `248e14d318aee96d49ff980ec2a6ec8dee1b8deba0e768c6fc270e266b77d88d` | 433,782 |

**`.gitignore` 누적 문제 박제**: `research/data/` 룰로 parquet + data_hashes.txt 모두 git tracked X. W1-01 시점부터 누락. 별도 정정 작업 (옵션 B 결정 시 미룸, handover v6 #20 신규 버그 유형).

---

## 4. cycle 2 v5 박제 정합성 cross-check

| cycle 2 v5 박제 | 실측 결과 | 일치 |
|-----------------|----------|------|
| Tier 1 = BTC (W1 재사용) + ETH | ETH 1927 rows 수집 ✓ | ✓ |
| Tier 2 = [XRP, SOL, TRX, DOGE] | 4개 모두 수집 ✓ | ✓ |
| Common-window 시작일 = 2021-10-15 UTC (SOL) | SOL day actual_start = 2021-10-15 ✓ | ✓ |
| Advertised RANGE = 2021-01-01 ~ 2026-04-12 UTC | 슬라이싱 적용 ✓ | ✓ |
| pyupbit `value` 필드 (단계 2-2 박제) | 본 단계는 일봉/4h OHLCV만 필요, 검증 X | N/A |

---

## 5. 코드 품질 검증

### make_notebook_07.py 자가 외부 감사 (라운드별)

- **W-1 (cwd 의존성) 해소**: `Path.cwd()` 자동 감지 + 검증 assert 추가
- **W-2 (Common-window assert) 해소**: 강제 assert 추가
- **W-3 (ETH 상장일 박제) 해소**: 강제 assert 추가
- **W-4 (tz UTC 안전 비교) 해소**: `utcoffset(None) == Timedelta(0)` 표현
- **NIT-1 (출력 가독성) 해소**: 핵심 컬럼 선택 출력
- **NIT-3 (data_hashes.txt newline) 해소**: rstrip + 조건부 separator

### W1-01 패턴 재사용

- `fetch_with_retry` (period=0.2 + exponential backoff)
- `check_gaps` (pd.date_range vs 실측 비교)
- `sha256_file`
- 타임존 변환 (naive KST → UTC)
- Advertised RANGE slicing

### 외부 감사 미실시 사유

- W2-01.4 데이터 수집 코드는 cycle 2 v4 박제의 NIT2-3 (Tier 2 결정 코드 외부 감사 의무)에 해당하지 X
- 단순 데이터 수집 + 무결성 검증
- 자가 검증 + 강제 assert로 충분

---

## 6. 다음 단계

| 단계 | 내용 |
|------|------|
| W2-01.7 | backtest-reviewer 호출 (본 evidence + 노트북 검증) |
| (별도) | sub-plan W2-01.5/.6/.7 갱신 (cycle 2 시점 박제) |
| (별도) | handover v7 → v8 갱신 (W2-01.4 완료 박제) |
| 커밋 | 본 evidence + make_notebook_07.py + 노트북 + sub-plan/handover |
| W2-02 | 새 전략 후보 사전 등록 (Candidate C, D) sub-plan 작성 |
