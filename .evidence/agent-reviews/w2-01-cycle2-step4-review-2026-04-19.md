# Backtest-Reviewer Agent Trace — W2-01 cycle 2 단계 4 (데이터 수집)

**호출 시점**: 2026-04-19
**Agent 정의**: `.claude/agents/backtest-reviewer.md`
**검증 대상 박제**: `docs/pair-selection-criteria-week2-cycle2.md` v5 / `docs/stage1-subplans/w2-01-data-expansion.md` W2-01.4

---

## 검증 대상 파일

- `research/_tools/make_notebook_07.py` (314 라인, nbformat 제너레이터)
- `research/notebooks/07_data_expansion.ipynb` (8 셀, 출력 포함, 실행 완료)
- `.evidence/w2-01-cycle2-step4-data-collection-2026-04-19.md`
- `research/data/KRW-{ETH,XRP,SOL,TRX,DOGE}_{1d,4h}_frozen_20260412.parquet` (10개)
- `research/data/data_hashes.txt` (3151 bytes)

---

## 판정

**APPROVED with follow-up**

데이터 수집 단계는 박제 정합성/무결성/코드 품질 모두 검증 통과. BLOCKING 0건. follow-up은 W2-01 cycle 2 외부에서 처리할 사항으로, 본 단계의 다음 흐름(W2-01.5/.6/.7 evidence 통합 + W2-02 진입)을 차단하지 않음.

---

## 검증 결과

### A. Data Integrity

| 항목 | 결과 | 근거 |
|------|------|------|
| 갭 < 0.1% | PASS | 노트북 셀 6 출력 표: max gap_pct = 0.0102% (KRW-SOL 4h). 10 dataset 모두 < 0.1% 충족. `assert ... gap_pct < 0.1` 라인은 명시 assert 형태가 아닌 print 결과 표기, 다만 이후 SOL/ETH assert가 통과 = 데이터셋 자체는 명시적 PASS 라인이 출력됨 |
| `assert df.index.tz is None` → `tz_localize('Asia/Seoul').tz_convert('UTC')` | PASS | `make_notebook_07.py` 라인 150-151 (cell 5). 노트북 셀 5 실행 출력의 모든 actual_range가 `+00:00` UTC offset 표기로 검증 |
| 파일명에 freeze 날짜 포함 | PASS | `_frozen_20260412.parquet` suffix가 10개 파일 모두 ls 결과에서 확인 (라인 5-12 `ls -la`) |
| `data_hashes.txt` 매치 | PASS | shasum -a 256 결과(`Bash` 직접 실행)와 evidence 표 (라인 72-81) 및 data_hashes.txt 라인 20-38이 10개 모두 정확히 일치. 예: KRW-ETH_1d = `2dfbb497...c0f0` |
| W1-01 BTC 행 보존 | PASS | data_hashes.txt 라인 9-10에 W1-01 BTC 해시 보존, 라인 12 이후 cycle 2 추가 (rstrip + 빈 줄 separator + 라인 39 trailing newline 정상) |
| monotonic 증가 | PASS | 노트북 셀 6 출력: 10 dataset 모두 `monotonic=True` |
| 중복 인덱스 없음 | PASS | 노트북 셀 6 출력: 10 dataset 모두 `has_duplicates=False` |
| UTC 타임존 (utcoffset 검증) | PASS | 노트북 셀 6 출력: 10 dataset 모두 `tz_utc=True` (W-4 안전 비교 적용 결과) |

### B. Pre-registered Parameters

| 항목 | 결과 | 근거 |
|------|------|------|
| PAIRS 박제 명시 | PASS | `make_notebook_07.py` 라인 103 `PAIRS = ["KRW-ETH", "KRW-XRP", "KRW-SOL", "KRW-TRX", "KRW-DOGE"]`. cycle 2 v5 섹션 5 "최종 확정" 라인 237과 정확히 일치 |
| RANGE 박제 명시 | PASS | 라인 104 `RANGE = ("2021-01-01", "2026-04-12")`. cycle 2 v5 섹션 4 라인 200 + sub-plan W2-01.4 라인 182와 일치 |
| FREEZE_DATE 박제 명시 | PASS | 라인 105 `FREEZE_DATE = "20260412"`. W1-01과 동일 |
| COMMON_WINDOW_START 박제 명시 | PASS | 라인 130 `COMMON_WINDOW_START = "2021-10-15"`. cycle 2 v5 섹션 5 라인 238 박제 일치 |
| LISTING_DATE_UTC 박제 | PASS | 라인 121-127. 4개 후보 (XRP/SOL/TRX/DOGE) 상장일이 cycle 2 v5 섹션 5 라인 221-224 표와 정확히 일치. ETH는 None + 자동 검증 |
| cycle 2 v5 인용 정확성 | PASS | 노트북 셀 1 markdown + 코드 주석 (라인 102, 129)에 "cycle 2 v5 박제" 명시 인용 |
| 결과를 보고 박제 변경 X | PASS | 본 노트북은 freeze된 박제(v5)를 입력으로 사용. 코드 산출물(actual_start)은 박제와 일치하는지 자동 assert로만 검증, 박제 갱신 코드 없음 |

### C/D/E. (해당 없음)

본 단계는 데이터 수집 + 무결성 검증만 수행. vectorbt API / 지표 계산 / Sharpe 계산 미적용. 검증 대상 아님.

### F. Evidence 6단 구조

| 단계 | 위치 | 결과 |
|------|------|------|
| 1. 데이터 입력 | evidence 라인 18-29 (10 dataset 표) + 라인 31-35 (advertised vs actual 차이 설명) | PASS |
| 2. 사전 지정 파라미터 | evidence 라인 88-96 (cycle 2 v5 박제 cross-check 표) + make_notebook_07.py 라인 102-130 박제 상수 | PASS |
| 3. 결과 | evidence 라인 16-29 (수집 결과 표) + 라인 67-81 (SHA256 + 크기) | PASS |
| 4. 자동 검증 | evidence 라인 39-46 (4종 강제 assert 통과) + 라인 50-62 (Common-window + ETH 박제 assert) | PASS |
| 5. 룰 준수 | evidence 라인 99-122 (코드 품질 + W1-01 패턴 재사용 + 외부 감사 미실시 사유) | PASS (자가 외부 감사 라운드 W-1 ~ NIT-3 정정 적용 명시) |
| 6. 리뷰 | 본 trace 파일 = evidence가 단계 6에서 참조하는 backtest-reviewer 호출 결과. evidence 라인 130 "W2-01.7 backtest-reviewer 호출"로 본 단계를 명시 예약 | PASS |

추가 강점:
- evidence 라인 83 `.gitignore` 누적 문제 명시 + 별도 정정 작업 미룸 표기 (handover v6 #20 신규 버그 유형)
- 라인 89-94 cycle 2 v5 박제 cross-check 표 5행으로 정합성 시각화

### cycle 2 v5 박제 정합성 cross-check

| 박제 항목 | 코드/노트북 실측 | 일치 |
|-----------|-------------------|------|
| Tier 1 = BTC (W1 재사용) + ETH | PAIRS에 KRW-ETH 포함 (라인 103) + ETH 1927 rows 수집 확인 (셀 5/6) | PASS |
| Tier 2 = [XRP, SOL, TRX, DOGE] | PAIRS의 나머지 4개 정확히 일치 | PASS |
| Common-window 시작일 = 2021-10-15 UTC | `COMMON_WINDOW_START = "2021-10-15"` (라인 130) + 노트북 셀 6 SOL day actual_start = `2021-10-15 00:00:00+00:00` + assert 통과 | PASS |
| Advertised RANGE = 2021-01-01 ~ 2026-04-12 UTC | RANGE 라인 104 + 노트북 슬라이싱 라인 154 + ETH actual_start = 2021-01-01 출력 검증 | PASS |
| KRW-DOGE 상장일 = 2021-02-24 | LISTING_DATE_UTC 라인 126 + 노트북 셀 5 출력 actual_start = `2021-02-24 00:00:00+00:00` 일치 | PASS |
| KRW-XRP 상장일 ≤ advertised 시작 | LISTING_DATE_UTC 라인 123 (2017-09-25) + 슬라이싱 후 actual_start = 2021-01-01 (advertised RANGE에 막힘, 박제 가정 일치) | PASS |
| KRW-TRX 상장일 ≤ advertised 시작 | LISTING_DATE_UTC 라인 125 (2018-04-05) + 슬라이싱 후 actual_start = 2021-01-01 (동일) | PASS |
| pyupbit `value` 필드 (단계 2-2 박제) | 본 단계는 OHLCV만 필요, 거래대금 필드 사용 없음 | N/A (정상 — evidence 라인 95에 N/A 명시) |

### 코드 자가 외부 감사 검증

자가 검증 정정 적용 확인 (evidence 라인 102-110 박제):

| ID | 정정 내용 | 코드 위치 | 검증 |
|----|---------|----------|------|
| W-1 | DATA_DIR cwd 의존성 제거 | 라인 107-117 (`if/elif/else` cwd 자동 감지 + 명확한 RuntimeError) | PASS |
| W-2 | Common-window 강제 assert | 라인 130 + 노트북 셀 6의 `assert sol_actual_start.startswith(COMMON_WINDOW_START)` (cell 6에 인라인) | PASS |
| W-3 | ETH 상장일 박제 강제 assert | 노트북 셀 6의 `assert eth_actual_start[:10] <= RANGE[0]` (`make_notebook_07.py` 셀 6 정의에 포함, cell `cc562cd7`) | PASS |
| W-4 | tz UTC 안전 비교 (`utcoffset == Timedelta(0)`) | 라인 168-172 (`df.index.tz.utcoffset(df.index[0]) == pd.Timedelta(0)`). pandas 2.x str(tz) 변동 회피 정확 적용 | PASS |
| NIT-1 | 출력 가독성 (핵심 컬럼 선택) | 셀 6의 `core_cols = ["pair", "interval", "rows", "actual_start", "gap_pct", "monotonic", "has_duplicates", "tz_utc"]` 셀렉터 정확 | PASS |
| NIT-3 | data_hashes.txt newline 안전 처리 | 셀 7의 `existing_stripped = existing.rstrip()` + `separator = "\n\n" if existing_stripped else ""` + trailing `"\n"`. data_hashes.txt 실측 라인 11(빈 줄) 후 라인 12 cycle 2 헤더 + 라인 39 trailing newline 정상 | PASS |

W1-01 패턴 재사용 정확성:

| 함수 | 라인 | 정확성 |
|------|------|---------|
| `fetch_with_retry` | 라인 69-82 | `period=0.2` + `max_retries=5` + `2**attempt` exponential backoff + `None` 처리 + `RuntimeError` raise. W1-01 + research/CLAUDE.md 박제와 일치 |
| `check_gaps` | 라인 85-92 | `pd.date_range(df.index[0], df.index[-1], freq=expected_freq)` + missing % 계산. W1-01 패턴 정확 재사용 |
| `sha256_file` | 라인 95-97 | `hashlib.sha256(Path(path).read_bytes()).hexdigest()`. 파일 단위 1회 읽기 + 표준 |

강제 assert 5종 모두 노트북 셀 5/6에 인라인 존재:
- 셀 5 라인 150: `assert df.index.tz is None`
- 셀 6 라인: `assert all_monotonic`, `assert all_no_dup`, `assert all_utc`
- 셀 6 후반: `assert sol_actual_start.startswith(COMMON_WINDOW_START)` + `assert eth_actual_start[:10] <= RANGE[0]`

자가 외부 감사 미실시 사유의 합리성 (evidence 라인 118-122): cycle 2 v4 박제의 NIT2-3 (Tier 2 결정 코드 외부 감사 의무)는 단계 2-2 (Tier 2 결정 코드)에 적용. 단계 4 데이터 수집은 W1-01과 동일 패턴 재사용 + 강제 assert로 충분. 검증 가능한 차별점이 적어 외부 감사 미실시는 정당화 가능. (다만 follow-up WARNING 1건으로 기록 — 아래 참조)

---

## 발견 사항

### BLOCKING (0건)

없음.

### WARNING (2건)

**[WARNING-1]** `research/notebooks/07_data_expansion.ipynb` 셀 6 (gap_pct < 0.1% assert 부재)

Description: monotonic / dup / UTC는 명시 `assert all_monotonic` 등으로 강제되지만, **`assert all_low_gap`은 print만 되고 강제 assert 없음** (`make_notebook_07.py` 라인 211-215). 현재 max gap_pct = 0.0102% < 0.1%로 통과하지만, 향후 동일 노트북 재실행 시 신규 페어/기간 추가로 gap이 0.1% 초과해도 silent 통과 위험.

Fix: 라인 215 `assert all_utc` 다음에 `assert all_low_gap, f"갭 {results_df['gap_pct'].max():.4f}% > 0.1% 초과"` 추가.

Reference: `.claude/agents/backtest-reviewer.md` Section A "갭 < 0.1%". W1-01 BTC 4h gap 0.0086% 통과 사례와 동일 패턴이지만 강제 assert는 본 노트북이 처음 추가했어야 할 안전장치.

**[WARNING-2]** Evidence 라인 83 `.gitignore` 누적 문제 (gitignored data + data_hashes.txt 미tracked)

Description: `research/data/` .gitignore 룰로 인해 W1-01부터 BTC parquet + data_hashes.txt까지 git tracked X. cycle 2 추가 분(10 parquet + cycle 2 추가 hash 라인)도 동일하게 tracked X. evidence가 "옵션 B 결정 시 미룸, handover v6 #20 신규 버그 유형"으로 정확히 박제했지만, 본 단계 본문 흐름에서 "다음 단계"로 정정 작업이 명시되지 않으면 영구 누락 위험.

Fix (본 단계 외부에서 처리):
- 옵션 1: `.gitignore`에서 `data_hashes.txt`만 예외 처리 (`!research/data/data_hashes.txt`) + `research/data/coingecko_top30_snapshot_20260417.json` 예외 처리 (sub-plan L290 "git tracked, 재현성 위해" 박제 의도와 정렬). parquet 자체는 gitignored 유지.
- 옵션 2: 옵션 B 명시 결정 = 모두 로컬 보존 + 사용자/리뷰어 외부에서 데이터 검증 불가능 인정 + handover에 영구 박제.

Reference: sub-plan L288-291 "데이터 (parquet gitignored, JSON snapshot은 git tracked)" 의도 vs `.gitignore` 실측 충돌. evidence 라인 83이 정확히 지적함, 별도 task로 분리 권고.

### NIT (3건)

**[NIT-1]** `research/_tools/make_notebook_07.py` 라인 174-185 (results 사전에 `freq` 컬럼 없음)

Suggestion: results dict에 `expected_freq` (`"D"` or `"4h"`)도 함께 저장하면 향후 디버깅 + W2-03 백테스트 시 freq 매치 검증에 재사용 가능.

Improves: 데이터 metadata 자기설명성. backtest-reviewer.md Section G "freq 파라미터가 데이터 frequency와 일치"의 사후 검증성.

**[NIT-2]** `research/notebooks/07_data_expansion.ipynb` 셀 5 (시간 측정 + sleep 0.5)

Suggestion: 라인 187 `time.sleep(0.5)` rate limit 안전 마진은 충분하지만, evidence 라인 12에서 "약 2분 소요" 박제와의 정합성을 위해 셀 시작/종료 시각 print 추가 권장. 향후 W2-01 cycle 3 진입 시 비교 baseline.

Improves: 재현성 metadata. 본 단계 결과에는 영향 없음.

**[NIT-3]** Evidence 라인 100-110 자가 외부 감사 라운드 표기 (W-1~W-4, NIT-1/3)

Suggestion: "외부 감사관이 무엇을 발견했는가"가 evidence에 한 줄씩만 박제됨. 향후 cycle 3 또는 다른 작업자가 본 evidence를 트레이스로 사용할 때 W-1~W-4의 원래 발견 내용 + 정정 전 코드 snippet을 별도 trace 파일로 분리 보존 권장 (`.evidence/agent-reviews/w2-01-cycle2-step4-self-audit-2026-04-19.md` 등).

Improves: handover/cycle 3 진입 시 학습 가능 자료. backtest-reviewer.md "Trace 저장 정책" 정신과 정렬.

---

## 종합 평가

### 데이터 수집 단계 품질

- 무결성 8개 항목 (gap/tz/file naming/hash match/W1-01 보존/monotonic/dup/utcoffset) 모두 PASS
- 사전 지정 파라미터 7개 항목 모두 PASS (cycle 2 v5 박제 정확 인용 + 결과를 보고 박제 변경 X)
- 코드 자가 외부 감사 6종 정정 (W-1~W-4 + NIT-1/3) 모두 적용 확인
- W1-01 패턴 (`fetch_with_retry`/`check_gaps`/`sha256_file`/타임존 변환) 정확 재사용
- 강제 assert 5종 (tz None, monotonic, no_dup, UTC, Common-window SOL, ETH 박제) 모두 노트북 인라인 존재

### 박제 정합성

cycle 2 v5 박제 8개 cross-check 항목 모두 PASS. 특히:
- KRW-SOL day actual_start = `2021-10-15` (cycle 2 v5 섹션 5 라인 222 + 섹션 4 Common-window 정책과 정확 일치)
- KRW-DOGE day actual_start = `2021-02-24` (cycle 2 v5 섹션 5 라인 224 일치)
- ETH/XRP/TRX는 advertised RANGE 시작(2021-01-01)에 막힘 = 박제 가정(advertised 이전 상장)과 정합

SHA256 cross-check (Bash `shasum -a 256` 실측 vs evidence vs data_hashes.txt) 10개 모두 정확 일치.

### 다음 단계 권고

1. **즉시 진행 가능**: WARNING 2건은 본 단계 다음 흐름을 차단하지 않음 (WARNING-1은 코드 안전장치 강화로 cycle 2 본문 영향 X / WARNING-2는 별도 task 분리 박제 완료). evidence + sub-plan 갱신 + handover 버전업 + 커밋까지 본 단계로 묶어서 종결 가능.
2. **Follow-up (별도 task로 분리 권고)**:
   - WARNING-1 정정: `make_notebook_07.py` 라인 215에 `assert all_low_gap` 1줄 추가 + 노트북 재빌드 (옵션 — 차회 데이터 수집 시 동시 적용 가능)
   - WARNING-2 정정: `.gitignore` 정책 결정 (옵션 1 vs 2) + 사용자 명시 박제 → handover v8 신규 항목으로 박제
3. **W2-02 진입 가능**: 본 데이터 수집 단계가 완료된 시점에서 W2-02 새 전략 후보 사전 등록 sub-plan 작성에 착수 가능.

### 사전 지정 원칙 준수

- 본 단계는 cycle 2 v5 박제(2026-04-19 사용자 승인 "ㄱㄱ" 발효)를 입력으로 받아 데이터를 수집했을 뿐, 박제값을 변경하거나 결과를 보고 페어 추가/제거한 흔적 없음.
- Common-window 시작일 박제 검증 결과(SOL = 2021-10-15)가 박제와 정확히 일치 → cycle 2 v5 섹션 5 "Common-window 시작일 = 2021-10-15" 박제는 본 단계로 자동 검증됨 (W2-01.5 사전 결정 작업의 필수 입력 산출물).
- "결과를 보고 임계값 변경" 또는 "snapshot 재취득" 등 cherry-pick 동기 행동 0건.

---

## 최종 verdict

**APPROVED with follow-up**

검증 결과:
- A. Data Integrity: PASS (8/8)
- B. Pre-registered Parameters: PASS (7/7)
- C. vectorbt API: N/A (이 단계에서 사용 안 함)
- D. pyupbit API: PASS (검증된 `get_ohlcv_from(ticker, interval, fromDatetime, to, period)` + period=0.2 + None 재시도)
- E. Wilder Smoothing: N/A
- F. Strategy Logic: N/A
- G. Output / Evidence: PASS (Evidence 6단 구조 모두 충족)
- H. Cross-document Consistency: PASS (sub-plan W2-01.4 라인 174-193 + cycle 2 v5 v5 섹션 5 모두 일치)

발견 사항: 0 BLOCKING, 2 WARNING, 3 NIT
WARNING 처리: WARNING-1은 차회 노트북 수정 시 함께 정정 / WARNING-2는 별도 `.gitignore` 정책 결정 task로 분리 (사용자 보고)
NIT 처리: 3건 모두 본 단계 진행 차단 X, 차회 작업 시 검토

다음 단계: W2-01.5/.6/.7 evidence 통합 마무리 + sub-plan + handover 버전업 + 커밋 → W2-02 sub-plan 작성 진행 가능
