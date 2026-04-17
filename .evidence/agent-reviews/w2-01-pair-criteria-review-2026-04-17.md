# W2-01.1 페어 선정 기준 문서 외부 감사 결과 (2026-04-17)

**감사 대상**: `docs/pair-selection-criteria-week2.md`
**감사관**: external auditor (adversarial, rubber-stamp 금지)
**트리거**: W2-01.1 초안 작성 후 사용자 "팀장/이사급 재검증" 요구
**참조 선행 감사**: `.evidence/agent-reviews/w2-01-preplan-review-2026-04-17.md` (sub-plan APPROVED post-fix)

---

## 초회 감사 (Initial)

### 판정

**CHANGES REQUIRED** — 4 BLOCKING + 7 WARNING + 5 NIT

### 핵심 판정 근거

사전 감사 APPROVED가 sub-plan 수준에서 해결한 freeze 원칙이 본 박제 문서에서 **표현 약화로 regression**. 4 BLOCKING 모두 "박제 문서 자체가 재현성·무모순성을 깸":
1. B-1 측정 창 off-by-one (30일이 아닌 31일)
2. B-2 Fallback 옵션(i) "Tier 1 축소" 라벨 오표현 (실제 축소 대상 Tier 2)
3. B-3 100억 sanity check 문장 자기모순 ("결정" vs "새 사이클")
4. B-4 Tier 2 4개 선정 근거 + 대체 금지 명문 공백

### 발견 사항 (BLOCKING 순)

#### B-1 [BLOCKING] 기준 3 측정 창 off-by-one

- **위치**: L49–50 (본 문서), L65/L107/L277 (sub-plan 전파)
- **현재**: "30일 rolling 평균 ≥ 100억 원 / 측정 창 2026-03-12 ~ 2026-04-11 (30 거래일)"
- **문제**: inclusive 계산 시 `(4/11 - 3/12).days + 1 = 31`. "30 거래일"과 실제 날짜 범위 불일치. 경계 페어 포함/제외가 구현자 해석에 따라 흔들림 (snooping).
- **수정안**: `2026-03-13 ~ 2026-04-11 (UTC inclusive, 정확히 30 UTC days)` 또는 `2026-03-12 ~ 2026-04-10`. W1 freeze 시점(2026-04-12) 직전 논리 유지하려면 전자.

#### B-2 [BLOCKING] Fallback 옵션(i) "Tier 1 축소" 라벨 오표현

- **위치**: L107
- **현재**: "(i) Tier 1 축소 | Tier 1 2개(BTC+ETH)만으로 W2-03 primary grid 축소 (6셀 → 6셀 유지, Tier 2 exploratory 12셀 축소)"
- **문제**: primary 6셀은 원래 6셀이라 "6→6 축소"는 논리 모순. 실제 축소 대상은 Tier 2 exploratory. 제목/본문 모두 "축소"가 오인 유발.
- **수정안**: 제목 "(i) Tier 2 제거"로 교체, 본문 "primary 6셀 **그대로**, Tier 2 exploratory 0~12셀은 실측 통과 수에 따라 감소. Go 기준 (Sharpe>0.8 AND DSR>0) 변경 없음".

#### B-3 [BLOCKING] 100억 sanity check 문장 자기모순

- **위치**: L54
- **현재**: "상위 20위 분포와 괴리 크면 사용자 보고 후 결정. 단 임계값 변경은 새 사전 등록 사이클 필요"
- **문제**: "결정"의 가능 옵션이 "유지" 하나뿐인데 "결정"이라 부르면 운영자에게 자유 재량 오인을 줌. CLAUDE.md "사용자에게 직접 판단 떠넘기지 말 것" 위반 소지.
- **수정안**: 두 시나리오로 분할 — (a) ±30% 이내: 임계값 유지, 진행 / (b) ±30% 초과: **현 사이클에서 100억 유지하여 W2-01 완주**, 변경 결정은 별도 새 사이클.

#### B-4 [BLOCKING] Tier 2 {XRP,SOL,ADA,DOGE} 4개 선정 근거 + 대체 금지 명문 공백

- **위치**: L76–85, L110–113
- **현재**: Tier 2 후보 4개가 왜 이 4개인지 근거 없음. "사후 대체 페어 추가" 금지 정책 공백.
- **문제**: Fallback (Tier 2 <2)만 막고, 경계 페어 재해석 + 사후 대체(LINK/SHIB 추가 유혹)는 막히지 않음. 4개 선정 자체가 cherry-pick 공격 여지.
- **수정안**: ① Tier 2 선정 규칙 명시 (예: "CoinGecko 2026-04-17 스냅샷 시총 상위 10 ∩ 업비트 KRW ∩ BTC/ETH 제외"), ② 금지 사항에 "Tier 2 후보 4개 리스트 freeze, 대체 페어 추가는 새 사이클" 추가, ③ 추정 상장일 불일치 시 처리 3규칙 (탈락 확정/대체 금지/Fallback 판정만 가능) 박제.

### 발견 사항 (WARNING)

#### W-1 [WARNING] "rolling" 단어 부적합

- **위치**: L49, L179
- **문제**: 단일 창 단순 평균인데 "rolling"이라고 쓰면 pandas `.rolling(30).mean()` 벡터 연산으로 오인 가능.
- **수정안**: "측정 창 내 단순 평균"으로 교체. 문서 전체 `rolling` 단어 일관 대체.

#### W-2 [WARNING] Common-window 갭 처리 정책 부재

- **위치**: L117–140 (섹션 4)
- **문제**: 거래정지로 인한 결측 캔들 처리 정책이 W2-03으로 미뤄짐. 사전 등록 문서가 이 수준의 미세 정책까지 박제하는 것이 사전 감사 원칙.
- **수정안**: "forward-fill 금지. 결측일 return=0, 포지션은 이전 상태 유지. 3일 초과 연속 갭 페어는 W2-01.5에 별도 표시 + W2-03 metric 신뢰구간 축소 표기" 추가.

#### W-3 [WARNING] 자기 freeze 시점 논리 모순

- **위치**: L16 상태 "초안" vs L175 "변경 금지 서약"
- **문제**: 승인 전인데 "변경 금지 서약"이 이미 활성화된 것처럼 읽힘.
- **수정안**: L175 서약 앞에 "본 서약은 섹션 5 '기준 승인' 기록 시점부터 유효" 조건 삽입.

#### W-4 [WARNING] 승인 2단계 구조(기준 승인 / 확정 리스트 승인)에 서약 이원화 공백

- **위치**: L144–169 (섹션 5) vs L175 서약
- **문제**: 승인이 2단계인데 서약은 한 번에 "기준과 확정 리스트" 둘 다 묶음. 어느 시점에 어디까지 freeze되는지 불명.
- **수정안**: 섹션 6을 "6.1 기준 섹션 freeze (기준 승인 시)" / "6.2 확정 리스트 freeze (확정 리스트 승인 시)"로 이원화. 중간 구간 "실측 값 채움만 허용" 명시.

#### W-5 [WARNING] PEPE "<3년" 수치 근거 누락

- **위치**: L95
- **문제**: 사전 지정 원칙상 "누가 보아도 동일 결론" 위해 PEPE 실제 상장일 명시 필요.
- **수정안**: "PEPE: 업비트 KRW 상장일 202X-XX-XX (업비트 공지 기준) > 2023-04-17 cutoff → 기준 2 FAIL" 형태. W2-01.2 실측 시 정확한 날짜로 채움.

#### W-6 [WARNING] LINK 제외 사유 "Tier 2 6→4 축소 일환" 유령 참조

- **위치**: L90
- **문제**: "원래 Tier 2가 6개였다"는 근거가 어디에도 없음. B-4와 동일 근본 원인.
- **수정안**: Tier 2 선정 규칙 명시(B-4 수정안과 동일)로 LINK 제외 사유 자연 도출.

#### W-7 [WARNING] pyupbit.get_ohlcv_from 세부 명세 공백

- **위치**: L41 (본 문서), sub-plan L106
- **문제**: `start_date`를 페어 상장 추정일보다 훨씬 이전으로 지정하지 않으면 최초 캔들이 상장일이 아닌 오인 발생 가능. 특히 SOL/DOGE cutoff 경계 페어는 결정적.
- **수정안**: 호출 스펙 구체화 (`fromDatetime="2017-01-01"`, `df.index.min()` 추출, sanity check 7일 이상 갭 없음), 결과를 `research/data/upbit_listing_dates_20260417.json`로 저장 + SHA256.

### 발견 사항 (NIT)

- N-1: Tier 1 BTC/ETH 기준 미달 이례 케이스 한 줄 추가 (Fallback (ii) 적용)
- N-2: sub-plan W2-01.2 L100 코드 블록 `data/` → `research/data/` 경로 일관 (본 문서 영향 없음, sub-plan 수정 권장)
- N-3: "기준 4~5" 번호가 "기준 3개"라는 L20 선언과 충돌 → "필수 전제 (임계값 아닌)"로 제목 변경, 번호 제거
- N-4: CoinGecko 응답 `len(response) == 30` assert 추가
- N-5: CLAUDE.md 룰(이모지/Java 용어 풀이) — 직접 위반 없음 (보고 용)

### Cross-document 일관성 재검증 결과

| 항목 | 판정 |
|------|------|
| 시총/상장/Tier 1/Tier 2 후보/Go 기준/Strategy 상태 | 일치 |
| 100억 + 30일 측정 창 | **본 문서 내부 off-by-one 모순 → sub-plan L65/L107/L277 동일 오기 전파** |
| Fallback 라벨 | **본 문서 L107 "축소" 오기. sub-plan L121–124는 OK** |
| Tier 2 4개 선정 근거 | **본 문서 + sub-plan 둘 다 공백** |

---

## 후속 조치 (Action Items)

1. pair-selection-criteria-week2.md 4 BLOCKING + 7 WARNING + 5 NIT 모두 반영 수정
2. sub-plan w2-01-data-expansion.md 측정 창 off-by-one 전파 수정 (L65/L107/L277)
3. 재감사 요청 (별도 agent call). "w2-01-pair-criteria-review-2026-04-17.md"의 본 섹션에 **재감사 결과 추가**.
4. 재감사 APPROVED 후 사용자 보고 + 사용자 명시 승인
5. 승인 후 섹션 6.1 "기준 승인" 기록 채우고 본 문서 freeze

## 재감사 #1 (v2 Post-fix)

### 판정

**CHANGES REQUIRED (1 BLOCKING + 4 WARNING)**

초회 BLOCKING 4건 중 3건 완전 해소, B-4는 부분 해소(신규 B-A 재유입). 초회 WARNING 7건 중 6건 완전 해소, W-1만 본 문서 해소 + sub-plan 전파 누락(W-A). NIT 5건 전부 해소.

### 초회 Closure Table

- B-1 (측정 창 off-by-one): 해소 (2026-03-13 ~ 2026-04-11 inclusive 30일)
- B-2 (Fallback 라벨): 본 문서 해소 / sub-plan + decisions-final 전파 누락 (W-A)
- B-3 (sanity check 자기모순): 해소 (±30% 이원화)
- B-4 (Tier 2 선정 근거): 부분 해소 (B-A 재유입)
- W-1~W-7: W-1 부분(본 문서만), W-2~W-4 + W-6~W-7 해소, W-5 부분(W2-01.2 실측 시 기록)
- N-1~N-5: 전체 해소

### 신규 발견

- **B-A [BLOCKING]**: 본 문서 L77 "규칙 쪽으로 교정" vs L226 "리스트 freeze" 직접 충돌. B-4 취지 무효화. cherry-pick 재유입 가능.
- **W-A [WARNING]**: sub-plan L31/L209/L233/L280 + decisions-final L555 옛 라벨 잔존. "같은 결정은 한 곳만 진실" 원칙 위반.
- **W-B [WARNING]**: 본 문서 L152/L153 백테스트 종료일 2026-04-11이 sub-plan L144 백테스트 범위 2026-04-12와 1일 오차. 측정 창 종료일과 혼동.
- **W-C [WARNING]**: 본 문서 L163 "BTC+ETH 기준 재설정" 유령 표현. Fallback (i) 본문과 충돌.
- **W-D [WARNING]**: L52 `close × volume` 종가 근사임을 명시하지 않음. 업비트 API `value` 필드가 실제 거래대금.

---

## 재감사 #2 (v3 Post-fix)

### 판정

**APPROVED with follow-up**

### 2차 Closure Table

- B-A (L77 freeze vs 교정 충돌): RESOLVED. L78 "불일치 시 Fallback (ii) 재설계", L80 "새 리스트 = 새 사이클", L168 시나리오 표 5행 추가.
- W-A (sub-plan + decisions-final 라벨 전파): RESOLVED. sub-plan L31/L122/L209/L233/L280 + decisions-final L555 모두 "Tier 2 제거" 라벨 통일.
- W-B (백테스트 종료일 1일 오차): RESOLVED. L154/L158 2026-04-12 통일 + 설계 주석.
- W-C (L163 "BTC+ETH 기준 재설정" 유령 표현): RESOLVED. Fallback (i) 명시로 교체.
- W-D (거래대금 산식 종가 근사 명시 공백): RESOLVED. 실측 필드 `value`/`candle_acc_trade_price` 우선 사용 + deferred verification + fallback 박제.

### 신규 발견

- **W-E [WARNING]** (L256 변경 이력 vs L53 본문 미세 불일치): ACCEPTABLE 수용 가능, 사전 지정 위반 아님. 단 팀장/이사급 책임상 수정 권장.
- **NIT-3-1~5**: BNB/TRX carve-out, sub-plan 체크박스 발효 주석, SOL 추정 범위, 오탈자 예외, sub-plan 실측 필드 전파.

### 감사관 권고

섹션 6.1 기준 freeze 발효를 위한 사용자 명시적 승인 **진행 가능**.

---

## 재감사 #3 (v4 Post-fix, NIT 전부 해소)

### 판정

**APPROVED** (모든 WARNING/NIT 반영 완료)

### 3차 Closure Table

- W-E: RESOLVED. L256 변경 이력 "`value`/`candle_acc_trade_price` 중 실측 필드 우선 사용 (W2-01.1 확인 후 확정)"로 본문과 통일.
- NIT-3-1: RESOLVED. Tier 3 carve-out에 BNB (업비트 KRW 미상장 자동 탈락) + TRX (10위 경계, 실측 10위 이내 시 Fallback (ii)) 명시.
- NIT-3-2: RESOLVED. sub-plan L77 → 섹션 6.1 기준 freeze 발효 주석, L125 → 섹션 6.2 확정 리스트 freeze 발효 주석 추가.
- NIT-3-3: RESOLVED. sub-plan L170 "SOL 상장 2021-04-07" → "SOL 상장일(2021년 추정, W2-01.2 실측 확정)"로 범위 통일.
- NIT-3-4: RESOLVED. 본 문서 L214 끝에 "의미 변경 없는 오탈자/서식/링크/라인 번호 교정은 섹션 7 변경 이력 기록 후 허용" 추가.
- NIT-3-5: RESOLVED. sub-plan L65 산식 셀에 "업비트 API 응답에 실측 거래대금 필드(`value`/`candle_acc_trade_price`) 존재 시 해당 필드 직접 사용" 조항 전파.

### 최종 상태

- 박제 문서 v4는 1차/2차/3차 감사 지적 사항 **전부 해소**.
- 3개 문서(`pair-selection-criteria-week2.md`, `w2-01-data-expansion.md`, `decisions-final.md`) cross-document 일관성 **완전 통일**.
- CLAUDE.md "공식 docs 추측 금지" 룰: W2-01.1 시점 deferred verification으로 룰 정신 준수. W2-01.2 실행 시 실제 API 응답 확인 후 필드명 확정 예정.

### 감사관 서명

- 감사 시각: 2026-04-17
- 감사 서명: external auditor (adversarial, rubber-stamp 금지)
- 총 감사 횟수: 3회 (초회 + 재감사 #1 + 재감사 #2)
- 총 발견 사항: 1차 4 BLOCKING + 7 WARNING + 5 NIT / 2차 1 BLOCKING + 4 WARNING / 3차 0 BLOCKING + 1 WARNING + 5 NIT
- 총 해소 사항: 5 BLOCKING + 12 WARNING + 10 NIT (전부 해소)
- 최종: **APPROVED**. 사용자 명시적 승인 시점에 섹션 6.1 기준 freeze 발효 가능.

---

**감사 메타**
- 감사 시각: 2026-04-17
- 감사 서명: external auditor (adversarial, rubber-stamp 금지)
- 사전 감사 대비: sub-plan APPROVED였으나 박제 문서에서 표현 regression 발견. off-by-one은 사전 감사가 놓친 부분 (본 문서가 처음으로 포착).
