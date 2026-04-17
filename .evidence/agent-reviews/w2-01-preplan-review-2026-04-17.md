# W2-01 사전 계획 외부 감사 리뷰 (2026-04-17)

> 리뷰어: external auditor 관점 (adversarial, no-benefit-of-the-doubt)
> 대상: `docs/stage1-subplans/w2-01-data-expansion.md` 및 연쇄 문서
> 기준 문서: CLAUDE.md (data snooping 금지, 사전 지정 원칙, LLM Phase 10+ Immutable), `docs/decisions-final.md`, `docs/stage1-execution-plan.md`
> 리뷰 범주: A–J (사용자 지정)

---

## BLOCKING (사용자 승인/커밋 전 반드시 해결)

### B-1. (Category A) 시총 상위 30위 스냅샷 시점이 미지정

- **파일/위치**: `docs/stage1-subplans/w2-01-data-expansion.md` L59 / `docs/decisions-final.md` L504
- **현재 내용**: "시가총액 (CoinGecko 기준) | 상위 30위"
- **문제**:
  - CoinGecko 시총 상위 30위는 24시간 내에도 바뀐다 (30위권은 특히 불안정).
  - W2-01.2 "CoinGecko API로 시가총액 상위 30위 조회"가 Task 시작일에 수행되는지, W1-06 결정일(2026-04-17)에 snapshot되는지 불명.
  - 페어 후보 산출 뒤 "더 좋은 알트 있다" 재조회를 막으려면 스냅샷 **일시 + 응답 원본 파일** 동결이 필수.
- **왜 중요한가**: 데이터 스누핑 방지는 "freeze 선언"만으로 부족. 스냅샷 원본이 없으면 사후 누구도 "당시 30위"를 재구성 못 한다. 재현성/감사 불가능.
- **수정 제안**:
  1. "**스냅샷 UTC 타임스탬프 고정** (예: 2026-04-17 00:00 UTC, W1-06 결정일 자정 기준)"을 사전 지정 기준에 명시.
  2. `research/data/coingecko_top30_snapshot_20260417.json` 원본 저장 + SHA256 해시 `data_hashes.txt`에 기록.
  3. CoinGecko 응답이 페이지네이션/정렬 불안정 시 동일 스냅샷을 재사용하고 재조회 금지.

### B-2. (Category A) "상장 3년+", "일거래대금 100억+" 측정 방법 미정의

- **파일/위치**: `w2-01-data-expansion.md` L60–61
- **현재 내용**:
  - "업비트 KRW 상장 기간 | ≥ 3년"
  - "업비트 일평균 거래대금 | ≥ 100억 원"
- **문제**:
  - "상장 3년+"의 **기준일**이 없음 (2023-04-17? 2023-04-01? 2023-04-12 데이터 freeze 날짜?). 경계선 코인(예: 2023년 중순 상장)의 포함/제외가 사람의 임의 결정에 달린다 → snooping 창구.
  - "일평균 거래대금 100억+"은 **24h ticker? 7일 평균? 30일 평균?** 안 적혀 있다. SubTask W2-01.2의 "24h ticker" 기재가 결정인지 단지 예시인지도 불명.
  - L87 "업비트 API로 각 후보의 일평균 거래대금 조회 (24h ticker)" — 24h는 스팟(spike) 영향이 크다. 30일 rolling median이 표준.
- **왜 중요한가**: "100억" 임계값만 정해두고 측정 창을 미정의하면, 후보 coin별로 유리한 창을 사후 선택하는 여지가 생긴다.
- **수정 제안**:
  - 상장 cutoff: "**업비트 KRW 페어 상장일 ≤ 2023-04-17** (W1-06 결정일 기준 정확히 3년)" 같이 날짜 박제.
  - 거래대금: "**업비트 일봉 기준, 2026-03-12 ~ 2026-04-11 (30일) rolling 평균 거래대금 (value = close × volume) ≥ 100억 원**" 같이 창+정의 박제.
  - 참고 해시를 `data_hashes.txt`에 기록.

### B-3. (Category B, CRITICAL) W2-03 primary Go 기준 "Sharpe > 0.8 at least 1 cell"은 사실상 다중 검정

- **파일/위치**: `stage1-execution-plan.md` L230, `decisions-final.md` L516, `w2-01-data-expansion.md` L21 배경
- **현재 내용**: "Primary: 적어도 1개 전략×페어 조합이 in-sample Sharpe > 0.8"
- **문제**:
  - 3 전략 × 6 페어 = **18 셀**. 독립 가정(이미 낙관적)에서도 귀무가설(진짜 엣지 0) 하에서 18 셀 중 최소 1개가 Sharpe > 0.8을 넘을 확률은 상당히 높다 (크립토 알트 간 상관이 높아 유효 독립 수는 더 적지만, 여전히 family-wise 오류율이 크다).
  - Week 1 Go 기준은 "A Sharpe > 0.8 **사전 단일 셀**"이어서 다중 검정 부담이 없었다. W2에서는 이 부담이 폭발했는데 문서에 **한 줄도 경고가 없다**. DSR(Deflated Sharpe) / Bonferroni / Benjamini-Hochberg 중 무엇도 언급 없음.
  - CLAUDE.md "데이터 스누핑 금지 — 100가지 조합 중 최고값 보고 형태 금지"의 본질을 이 Go 기준이 그대로 위반한다 (18개 중 최고가 0.8 넘으면 Go).
  - 참고: 프로젝트는 DSR/Bailey&LdP을 이미 채택(Part 9, algorithm-validation.md). 정작 **Week 2 Go 기준에서만 빠져 있다.**
- **왜 중요한가**: 이 기준이 그대로면 Week 2 "Go" 결과 자체가 통계적으로 신뢰 불가 → Week 3 Walk-forward에 쓰레기 입력. Stage 1 8주 킬 판단이 오염된다.
- **수정 제안** (택 1 또는 혼합):
  - **(권장) 단일 대상 사전 지정**: Tier 1 BTC+ETH 기본 쌍 각각에 대해 사전 지정 전략으로 평가. primary 기준은 "Tier 1 2개 페어에서 적어도 1개 전략이 Sharpe > 0.8" 같이 축소. 나머지 18셀은 exploratory (참고용) 라벨 명시.
  - **(필요)** DSR을 Primary Go 기준에 포함: "18셀 중 최고 Sharpe > 0.8이면서 해당 셀의 DSR > 0" 같이 다중 검정 보정 필수.
  - **(최소)** 문서에 "이 Go 기준은 명시적 다중 검정이므로 Week 3 DSR 통과가 없으면 공식 Go로 간주 안 함"을 명문화하고 사용자에게 그 리스크를 서면 고지.

### B-4. (Category C) Strategy C/D 파라미터가 W1에서 본 BTC 데이터와 독립이라는 증명/서약 부재

- **파일/위치**: `stage1-execution-plan.md` L215–217, `decisions-final.md` L508–510
- **현재 내용**: "Candidate C: Slow Momentum (MA50/200 crossover + ATR(14)×3 trail) - Moskowitz 2012 근거" / "Candidate D: Volatility Breakout (Keltner + Bollinger)"
- **문제**:
  - Moskowitz et al. 2012는 TSMOM(시계열 모멘텀)로 **룩백 1/3/6/12개월 + 변동성 스케일링**이 원형. MA50/200 crossover는 별개 스키마. "Moskowitz 근거"라는 라벨만으로는 MA50/200이 **W1에서 본 BTC 데이터 덕에 고른 값이 아니라는 근거**가 못 된다.
  - Keltner(20, 1.5 * ATR) + Bollinger(20, 2 sigma) 동시 돌파는 구체 파라미터 (20, 1.5, 20, 2)가 어디서 왔는지 출처 미표기. 질의서엔 파라미터가 있는데 decisions/subplan엔 숫자가 없어 **나중에 W2-02에서 "적절한 값" 채택 시 snooping 구멍**.
  - 리뷰어/사용자 모두 Week 1 전 기간 BTC 곡선을 이미 봤다. 어떤 파라미터든 **"BTC-unseen 환경"에서 고른 것이 아니다**. 이 한계는 인정하고 문서에 명시해야 한다.
- **왜 중요한가**: W2-02 sub-plan이 W2-01 후 작성된다고 하지만, decisions-final/exec-plan에 이미 "MA50/200, ATR×3, KC(20, 1.5), BB(20, 2)"가 사실상 인코딩되어 있다. 이 숫자들이 어디서 왔는지 근거/서약이 없으면 사전 등록이 무의미.
- **수정 제안**:
  - `w2-01-data-expansion.md` 또는 (W2-02 전) `docs/strategy-preregistration-week2.md`에 각 파라미터에 대해: (a) 출처 논문/레퍼런스 섹션 번호, (b) "BTC W1 결과를 보지 않고 확정" 서약, (c) 파라미터 민감도를 **W2-03에서 참고용으로만** 사용.
  - 또는 "BTC는 W2-03 grid에서 out-of-sample 샘플로 간주 불가. primary 판정은 BTC 제외 5개 알트에서 수행" 정책을 도입해 훈련/테스트 분리 흉내를 낸다.
  - 불가피한 contamination은 "Week 2 한계" 섹션에 솔직히 적는다.

### B-5. (Category I) Tier 2 후보가 2개 미만으로 줄 때의 fallback이 추상적

- **파일/위치**: `w2-01-data-expansion.md` L195, L220
- **현재 내용**:
  - 리스크: "기준 미달 페어가 많아 Tier 2가 적게 남음 | Medium | 임계값 일부 완화 가능, 단 변경 전에 사용자 승인 + snooping 방지"
  - Denial 1: "Tier 2 후보 2개 이하 → 사용자와 기준 재협의 (완화 여부)"
- **문제**:
  - "임계값 완화"는 snooping의 정의 그 자체 — 후보 수 늘리려 기준 움직이기. 사용자 승인만 붙이면 "형식만 맞추는 snooping"이다.
  - "완화 시 반드시 새 사전 등록 문서 + 데이터 재freeze + Week 1 수준 감사" 같은 **무거운 장치**가 필요.
  - 또는 "Tier 2 <2면 W2 전체를 reschedule, Tier 1 2개만으로 축소 grid"가 합리적 기본값.
- **왜 중요한가**: 이 fallback은 실제 발생 확률이 높다(SOL 상장 <3년 이슈). 모호한 승인 프로세스는 "일단 한 번 완화"가 영원한 완화로 이어지는 경사면.
- **수정 제안**:
  - Denial 1을 재작성: "Tier 2 <2 인 경우 (i) 완화 없이 Tier 1만 (BTC+ETH) 2-pair grid로 축소, 또는 (ii) Task 전체 재설계 → 새 사전 등록 + 승인 루프. 이 외 임계값 완화 금지."
  - "재협의"는 **다음 사이클**로 미루고 현 Week 2에서는 freeze된 기준만 유효.

### B-6. (Category F) execution-plan "Week 2 재범위" 서술이 decisions-final과 미세하게 불일치

- **파일/위치**: `stage1-execution-plan.md` L202 vs `decisions-final.md` L497
- **현재 내용**:
  - execution-plan L202: "Week 2를 **전략 후보 재탐색 + 알트 확장**으로 재설계"
  - decisions-final L497: "**전략 후보 재탐색 + 메이저 알트 확장**으로 재설계"
- **문제**: "메이저" 수식어 유무. 메이저 알트 = Tier 1/2로 한정하는 의미가 실어져야 하는데, execution-plan에서 단어가 빠져 있다. Tier 1/2만 포함한다는 것이 두 문서에서 동일하게 읽혀야 한다.
- **왜 중요한가**: 단일 진실 문서 원칙을 지키려면 표현 일치가 기본. 미세한 차이라도 감사 시 "의도 불명"의 공격 벡터.
- **수정 제안**: execution-plan L202를 decisions-final과 동일하게 "**메이저 알트 확장**"으로 통일.

---

## WARNING (승인 전 개선 권장, 블로킹은 아님)

### W-1. (Category A) "일거래대금 100억+" 임계값의 정당성 근거 부재

- `w2-01-data-expansion.md` L61 "50만원 라이브 투입 시 슬리피지 허용" — 50만원 × 전체 포지션 40% = 20만원 주문. 업비트 주요 알트 호가 깊이에서는 일거래대금 1억만 넘어도 슬리피지는 0.05% 내외. 100억은 과도하게 보수적일 수도, 혹은 그냥 큰 숫자를 고른 것일 수도.
- 실측 근거나 이전 slippage 분석 없이 100억을 박제하면, 후보 수가 줄어들 때 완화 유혹 발생.
- **수정 제안**: "업비트 BTC 기준 slippage 모델로 50만원 주문 slippage < 0.1% 가 되는 최소 거래대금을 실측 뒤 임계값 설정" 또는 "정당성: 업비트 상위 20위 알트의 2025 평균 거래대금 분포 기준 중앙값/하위 25% 참조" 같이 숫자 근거.

### W-2. (Category D) 페어별 상이한 데이터 범위에서 grid 공정성 미보장

- `w2-01-data-expansion.md` L124 "상장 <2021-01-01 페어의 경우 실제 첫 캔들부터 수집 + metadata에 실제 범위 기록".
- SOL (업비트 상장 ~2021 말), DOGE (업비트 상장 2021-07경) 등은 5년 중 3~4년만 존재. 이 상태에서 Sharpe/MDD 비교는 공정 비교 아님(볼 시장 구간 다름).
- `w2-01`에서 "metadata에 기록"만 하고 W2-03 grid에서 어떻게 normalize할지 계획이 없다.
- **수정 제안**:
  - W2-01 Acceptance에 "각 페어 common-window Sharpe (예: 상장 가장 늦은 페어 기준 공통 2022-07 ~ 2026-04-12) 를 **보조 metric으로 함께 계산**" 같은 정책을 사전에 박아두자.
  - 또는 primary는 페어별 max-span, secondary는 common-window. 둘을 사전 지정.

### W-3. (Category F) 상태표 vs 실제 파일 일치하나 "Sub-plan 미작성"이라는 상태 라벨 없음

- `stage1-execution-plan.md` L82–83: W2-02 "TBD — 새 전략 후보 사전 등록 (W2-01 완료 후 작성)", W2-03 "TBD — In-sample 백테스트 grid (W2-02 완료 후 작성)".
- 현재 문구는 "Pending" 상태인데 "TBD"가 sub-plan 링크 자리에 들어가 있어, 앞으로 실제 파일 작성 시 링크가 갈리는 추적 어려움.
- **수정 제안**: Sub-plan 미작성임을 상태 컬럼에 명시 ("Pending (sub-plan pending)") 또는 Status 표에 "sub-plan drafted" 컬럼 추가.

### W-4. (Category G) SubTask 시간 합산 vs 선언 기간 불일치

- SubTask 합: 0.2+0.2+0.1+0.5+0.3+0.2+0.2 = **1.7일**. 메타에서 "기간 2일"은 여유 0.3일(약 15% buffer).
- W1-01 sub-plan은 합산 = 1.0일, 선언 1일로 정확히 0 buffer였다.
- 문제는 작진 않으나 역사 패턴과 불일치. Buffer 정당화(감사 반복, 사용자 승인 대기)가 본문에 안 적혀 있다.
- **수정 제안**: "기간 2일 = SubTask 1.7일 + 사용자 승인/재검증 0.3일" 명시.

### W-5. (Category C) Strategy A "후보 풀"의 물리적 정의/레시피 부재

- `decisions-final.md` L488 "Strategy A 파라미터 (MA=200, Donchian=20/10, Vol>1.5x, SL=8%)는 **후보 풀에 보관**"
- "후보 풀"이라는 단어만 있고 **어느 파일에 어떤 스키마로 저장되는지** 없다.
- W2-02 "전략 사전 등록 문서" 또는 별도 `docs/candidate-pool.md`로 물리화 권장.
- **수정 제안**: `docs/strategy-preregistration-week2.md` 내 "보관 전략" 섹션 또는 `docs/candidate-pool.md` 신설. A가 W2-03 재실패 시 deprecated로 이동하는 recall mechanism도 포함.

### W-6. (Category H) CoinGecko rate limit "Low"의 근거 박약

- 리스크 표 L197 "CoinGecko rate limit | Low | 무료 엔드포인트 분당 10-30 request 제한, 30개 조회는 1 request"
- 사실상 정확하지만, CoinGecko 공공 API는 **2024년 이후 분당 5-15 requests로 축소**되는 변경이 잦았다. 공식 docs 참조 날짜 명시 권장 (CLAUDE.md "외부 라이브러리 API 사용 시 공식 docs 확인" 룰).
- **수정 제안**: 리스크 행에 "(2026-04-17 docs 확인 기준)" 또는 실제 호출 전 retry-after 헤더 읽기 로직 명시.

### W-7. (Category J) Regime 정의의 W1 leakage 가능성

- `decisions-final.md` L480 "A/B 모두 Volatile regime에서 최고 Sharpe → 앙상블 보완성 제한적"
- 이 regime 분류가 W1-06.1b에서 "가격 기반 regime 라벨링"으로 이뤄졌음 (L474).
- W2-02에서 "Candidate C: Slow Momentum" 채택은 이 regime 분석의 결과에 영향을 받았을 수 있다. 즉 "W1에서 Volatile regime에 몰림 → Slow Momentum으로 Bull regime 보완" 같은 추론은 **이미 BTC 곡선을 본 뒤의 파라미터 선택**이다.
- CLAUDE.md "데이터 스누핑 금지"의 가장 교묘한 형태.
- **수정 제안**:
  - W2-02 sub-plan 작성 시 "Candidate 선택이 W1 regime 분석으로부터 얼마만큼 독립적인가" 자가감사 섹션 필수.
  - 최소한 W2-01에 "Candidate C/D는 W1 regime 분석을 본 뒤 결정되었음을 명시 (soft contamination)"라는 경고를 달아 사용자가 알게 한다.

---

## NIT (polish)

### N-1. (Category G) Happy/Denial 시나리오 수 비대칭

- W1-01: Happy 1 + Denial 2 + Edge 1 = 4.
- W2-01: Happy 1 + Denial 3 = 4. 비슷한 수이지만 "Edge" 케이스가 W2에서는 없다. 상장 <2021 경계 상황은 Edge에 해당(Denial 2에 섞임).
- 가능하면 Edge 케이스(예: 거래정지 이력 있는 페어 포함 시 grid 해석 주의)를 분리.

### N-2. (Category F) 커밋 메시지 템플릿의 날짜 플레이스홀더

- L152 `# Week 2 expansion (2026-MM-DD)` — 실제 Task 실행일로 치환해야 한다는 주석은 좋지만, "MM-DD를 실행일 KST 기준 date로" 같은 명령문을 한 줄 더. 감사관이 사람이 아닐 때 명확.

### N-3. (Category E) "후보 풀 보관" 표현 통일

- sub-plan은 "후보 풀 보관"(한국어), decisions-final도 동일. execution-plan은 "candidate pool"/"후보 풀"을 혼용. 용어집에 추가하거나 통일.

### N-4. (Category A) Tier 3 "SHIB, LINK 등"의 carve-out 근거

- L68 "SHIB, LINK 등 — 밈 특성 또는 유동성 이슈" — LINK는 밈이 아니다(Chainlink, DeFi 오라클 블루칩). "유동성 이슈"만이 LINK 제외 사유면 그렇게 명시. 그렇지 않다면 LINK는 Tier 2 후보로 들어가야 정합적.

### N-5. (Category G) SubTask 7 Evidence 파일명

- L165 `.evidence/w2-01-data-expansion.txt`. W1-01 파일명(`w1-01-data-collection.txt`)과 패턴 일치. OK.

### N-6. (Category A) "2023-04 이전 상장, 5년 데이터 중 60%+ 확보"의 계산

- L60 근거 "5년 데이터 중 60%+ 확보" — 3년/5년 = 60%, 맞음. 단 업비트 상장일과 CoinGecko 페어 상장일이 다를 수 있어 "업비트 KRW 상장일" 명시는 잘 되어 있지만, 상장 이후 일시 상장폐지 이력(LUNA, UST 등)을 데이터셋에서 처리하는 방식이 Week 2에 없어도 W3에서 재발 가능. 미리 "거래정지/상폐 구간 제외 정책" 문서화 권장 (이미 리스크 표에 있음 OK, but 정책 산출물 없음).

---

## 점검 체크리스트 요약

| Category | 발견 수 | 요약 |
|----------|:--:|------|
| A. 사전 지정 엄격성 | 2 BLOCKING + 1 WARNING + 2 NIT | 스냅샷 시점/상장 cutoff/거래대금 창 미정의 |
| B. Week 2 Go 기준 다중 검정 | 1 BLOCKING (CRITICAL) | 18셀 family-wise error 미보정, DSR 언급 없음 |
| C. Strategy C/D 사전 등록 contamination | 1 BLOCKING + 1 WARNING | BTC 데이터 본 후 파라미터 선택 여지, 근거 서약 부재 |
| D. 알트 데이터 범위 상이 | 1 WARNING | Common-window metric 사전 지정 필요 |
| E. Strategy A "후보 풀" | 1 WARNING | 물리 파일/recall 정의 부재 |
| F. 문서 일관성 | 1 BLOCKING + 1 WARNING | "메이저 알트" 누락, sub-plan 상태 표현 |
| G. Sub-plan 형식 | - | W1-01 대비 parallel OK |
| H. 불명확 추정치 | 1 WARNING | 100억 거래대금 근거, CoinGecko docs 날짜 |
| I. 방어선 | 1 BLOCKING | Tier 2 <2 fallback이 snooping 유혹 |
| J. Immutable 룰 (LLM/snooping) | 1 WARNING | W1 regime 분석으로부터의 soft leakage |

- 총 BLOCKING: **6**
- 총 WARNING: **7**
- 총 NIT: **6**

---

## 최종 판정

**CHANGES REQUIRED**

핵심 막힘 포인트:
1. **B-3 (CRITICAL)**: W2-03 primary Go 기준이 사실상 다중 검정이고 DSR/Bonferroni 보정 언급이 전혀 없다. 이 상태로 Go 판정이 내려지면 Week 3 입력이 오염되고 Stage 1 킬 판정이 무의미해진다. CLAUDE.md "데이터 스누핑 금지" 룰의 직접 위반.
2. **B-1/B-2**: 사전 지정 기준의 측정 세부가 비어서, "사전 지정"이라는 단어만 있고 실질 freeze가 안 되어 있다.
3. **B-4**: Strategy C/D 파라미터가 W1 BTC 데이터를 본 후에 선택되었을 가능성을 전혀 주소하지 않는다.
4. **B-5**: Tier 2 부족 시 "임계값 완화"는 snooping의 정의 그대로다.
5. **B-6**: 단일 진실 문서 원칙 위반의 작은 사례이지만 즉시 정정 가능.

위 6개 BLOCKING을 해결한 개정판을 받은 뒤 재리뷰 요청 권장. WARNING들은 동시에 반영하면 좋지만 재리뷰 블로커는 아니다.

---

## 참고 파일 경로

- 대상 sub-plan: `/Users/kyounghwanlee/Desktop/coin-bot/docs/stage1-subplans/w2-01-data-expansion.md`
- 배경 결정: `/Users/kyounghwanlee/Desktop/coin-bot/docs/decisions-final.md` Stage 1 실행 기록 Part 11 (L456–523)
- 실행 계획: `/Users/kyounghwanlee/Desktop/coin-bot/docs/stage1-execution-plan.md` Week 2 섹션 (L200–235)
- 선행 결정 sub-plan: `/Users/kyounghwanlee/Desktop/coin-bot/docs/stage1-subplans/w1-06-week1-report.md`
- 형식 기준 sub-plan: `/Users/kyounghwanlee/Desktop/coin-bot/docs/stage1-subplans/w1-01-data-collection.md`
- 룰: `/Users/kyounghwanlee/Desktop/coin-bot/CLAUDE.md` (Immutable + Don'ts)

---

## Re-review (Post-fix 2026-04-17 pm)

> 리뷰어: external auditor 관점 (adversarial, no rubber-stamp)
> 대상: 원 리뷰 6 BLOCKING + 7 WARNING 수정본
> 변경 파일: `docs/stage1-execution-plan.md`, `docs/decisions-final.md`, `docs/stage1-subplans/w2-01-data-expansion.md`, `docs/candidate-pool.md` (신규)

### BLOCKING 재검증

#### B-1 (시총 스냅샷 시점 고정) — **RESOLVED**

- 근거:
  - `w2-01-data-expansion.md` L63 "스냅샷: 2026-04-17 00:00 UTC (W1-06 결정일 자정 기준)" 박제됨.
  - L85–103 SubTask W2-01.2에 원본 JSON 저장 + SHA256 기록 코드 포함.
  - 산출물 표 L252 `research/data/coingecko_top30_snapshot_20260417.json` git tracked.
- 남은 미세 이슈 (NIT-NEW-1로 별도 지정): 경로 표기 `research/data/...` (L63, L252) vs `data/...` (L100 코드, L208 acceptance)가 혼재. W1-01 패턴은 `research/data/`. 코드 실행 시 cwd에 따라 파일이 `research/data/`가 아닌 `data/`에 떨어질 위험. 블로커 아님 (SubTask 실행 중 cwd 통일하면 됨).
- 판정: RESOLVED.

#### B-2 (상장 cutoff + 거래대금 창) — **RESOLVED**

- L64 "업비트 KRW 페어 상장일 ≤ 2023-04-17" 박제.
- L65 "30일 rolling 평균 ≥ 100억 원, 측정 창 2026-03-12 ~ 2026-04-11 (30 trading days, UTC), value = close × volume. 24h 스팟 거래대금 사용 금지" 박제. 측정 정의, 창, 금지 사항 모두 포함.
- 일관성 체크: SubTask W2-01.2 L106–107이 동일 정의로 실측 절차 명시. 통과.
- 판정: RESOLVED.

#### B-3 (다중 검정 — CRITICAL) — **RESOLVED (with reservation)**

- 재정의된 Go 기준: execution-plan L230–234 / decisions-final L517–521.
  - Primary 6셀 (Tier 1 × 3 전략) 중 "BTC 또는 ETH에서 Sharpe > 0.8 AND DSR > 0" 1개 이상.
  - Tier 2 12셀은 exploratory, Go 기여 X.
  - Secondary 마커 (ensemble 후보 표시용)는 Go 가중치 없음 명시.
  - "다중 검정 한계 인정 + Week 3 walk-forward 최종 검증" 문구 양 문서 모두 포함.
- 개선 정도: 원 18셀 → 6셀로 축소 + DSR 필수 조건 추가. 원 권고 중 "(권장) 단일 대상 사전 지정" + "(필요) DSR 포함" 두 가지 동시 반영.
- **Reservation (BLOCKING 해소 범위 내 코멘트)**: DSR > 0은 매우 약한 threshold (사실상 "원 Sharpe와 deflated가 같은 방향") — Bailey-LdP 원 논문 맥락에서는 대개 DSR > 0.5 또는 p < 0.05 형태를 권장. 그러나 (i) W2 In-sample 단계라는 점, (ii) Week 3 walk-forward가 최종 아비터라는 점, (iii) 한계를 양 문서에 명시한 점으로 BLOCKING 재부과는 하지 않음. Week 3 gate 설계 시 **DSR threshold를 명시적으로 상향** 할 것을 WARNING-NEW-1으로 기록.
- 판정: RESOLVED.

#### B-4 (Strategy C/D 파라미터 독립성) — **RESOLVED**

- decisions-final.md L530–547 "Week 2 한계 및 독립성 서약" 신설 섹션이 요구사항을 정면으로 다룸:
  - 파라미터별 출처: Faber 2007 / Wilder 1978 / Keltner 1960 / Bollinger 1983 — 모두 검증 가능한 1차 문헌, 2차 인용 아님 (CLAUDE.md 룰 준수).
  - "문헌 기본값" 서약 + soft contamination 명시 인정.
  - Week 3 walk-forward가 최종 아비터라는 구조적 보상 명시.
- candidate-pool.md Strategy C/D 항목에서도 "독립성 한계: soft contamination" 행이 반복되어 cross-document 일관.
- 남은 아쉬움: "BTC W1 결과를 보지 않고 확정"이라는 서약 문구 자체가 decisions-final L545에는 있는데 sub-plan의 리스크 표(L240)에는 간접 참조만 있음. 매우 경미 — NIT-NEW-2로 기록.
- 판정: RESOLVED.

#### B-5 (Tier 2 <2 fallback) — **RESOLVED**

- sub-plan L121–124 SubTask W2-01.3: (i) Tier 1 축소 / (ii) Task 재설계 루프 두 옵션 + "임계값 완화 금지" 명문화.
- decisions-final L553–557이 동일 정책으로 반영, 문서 간 일관.
- 리스크 표 L233 + Denial 시나리오 L264도 "완화 금지" 재강조.
- 판정: RESOLVED.

#### B-6 (execution-plan "메이저" 누락) — **RESOLVED**

- execution-plan L202 "전략 후보 재탐색 + **메이저** 알트 확장" 표현 통일됨.
- decisions-final L486, L497, sub-plan L21, w1-06 L49 모두 동일 표현. cross-doc grep으로 일관성 확인.
- 판정: RESOLVED.

### WARNING 재검증

- **W-1 (100억 임계값 근거)**: ACCEPTABLE. L68 "추정, W2-01.2 실측 검증" + L109 "상위 20위 sanity check". 완벽하진 않지만 (실측 후 임계값을 바꾸려면 새 사전 등록이라는 게 약간 모순적 — 실측 전에 확정한 임계값이 실측 결과와 괴리시 무엇을 해야 하는가가 모호). 그러나 "변경은 새 사이클"이라는 guard가 있어 snooping 구멍은 닫혀 있음.
- **W-2 (Common-window)**: RESOLVED. L168–173 common-window 사전 결정 + primary max-span + secondary common-window 둘 다 계산 명시.
- **W-3 (Sub-plan 상태 라벨)**: RESOLVED. execution-plan L82–83 "Pending (sub-plan 미작성)" 명시.
- **W-4 (SubTask 시간 합산)**: RESOLVED. L10 "SubTask 순효용 ~1.8일 + 사용자 승인/재검증 ~0.2일 buffer". 합산은 0.2+0.3+0.2+0.5+0.3+0.2+0.2 = 1.9일 (원 리뷰 1.7일 대비 W2-01.2를 0.2→0.3로 늘린 변경 반영). 선언 2일 = 순효용 1.9 + buffer 0.1 → 문구와 실제 숫자가 0.1일 차이. STILL OPEN으로 둘 만한 NIT. WARNING-NEW-2로 기록.
- **W-5 (Strategy A 후보 풀)**: RESOLVED. `docs/candidate-pool.md` 신설 + 3단계 상태(Active/Retained/Deprecated) + Recall Mechanism 명시. Strategy B Deprecated 로그 포함(재도입 방지). 품질 양호.
- **W-6 (CoinGecko rate limit)**: RESOLVED. L235 "2026-04-17 공식 docs 기준" + "Retry-After 헤더 처리" 포함.
- **W-7 (Regime 분석 → C/D 선택 soft leakage)**: RESOLVED. decisions-final L544–546 "철학 자체 선택은 W1 regime 편중 발견의 영향을 받았다 → soft contamination" 명시 서약. CLAUDE.md snooping 룰의 "교묘한 형태" 경고까지 인용하진 않았지만, 문구 자체로 해당 내용 포함.

### 새로 발견된 이슈 (fix로 인한 regression 포함)

- **WARNING-NEW-1** (B-3 reservation에서 derived): DSR threshold가 "> 0"으로만 규정. Bailey-LdP 논문 정신에 비춰 약함. Week 2 Go는 그대로 두되, **W3-03 전략 채택 기준**에서 DSR threshold를 명시적으로 상향(예: DSR > 0.5, 또는 p < 0.05)할 것. decisions-final Part 11 Stage 1 킬 크라이테리아와 Week 3 sub-plan 작성 시점에 반영 권장. 현 시점 BLOCKING 아님.
- **WARNING-NEW-2** (W-4 산수 잔차): L10 "1.8일 + 0.2일"인데 SubTask 실제 합산 1.9일. 0.1일 차이. 문서 자체-일관성 미세 어긋남. 수치 맞추거나 "~1.8~1.9일" 범위 표기 권장.
- **NIT-NEW-1** (B-1 파생): `research/data/...` vs `data/...` 경로 표기가 sub-plan 내부에서 혼재. W1-01 convention은 `research/data/`. L100 코드 블록 / L208 acceptance / L217 data_hashes.txt 경로 / L236 리스크 표 모두 `data/...`로 쓰여 있어 cwd 의존 위험. 실행 시점에 통일해도 늦지 않음.
- **NIT-NEW-2** (B-4 잔여): sub-plan 리스크 표(L240)는 decisions-final "Week 2 한계" 섹션을 참조하지만 본문 내 직접 서약은 없음. 경미.
- **REGRESSION 체크**: BLOCKING 수정이 기존 원칙(데이터 freeze, 단일 진실 문서, 외부 감사 반복)을 훼손하거나 다른 문서를 불일치시킨 흔적은 없음. `메이저` 단어 통일, Go 기준 축소, 한계 섹션 추가는 모두 **보수적(더 엄격한) 방향**이라 snooping 구멍을 더 막는 쪽.

### 체크리스트 (Re-review)

| 원 발견 | 원 심각도 | 재검증 판정 |
|---------|:--------:|:-----------:|
| B-1 스냅샷 시점 | BLOCKING | RESOLVED |
| B-2 상장/거래대금 창 | BLOCKING | RESOLVED |
| B-3 다중 검정 | BLOCKING (CRITICAL) | RESOLVED (w/ W3 DSR threshold 상향 권고) |
| B-4 C/D 독립성 서약 | BLOCKING | RESOLVED |
| B-5 Tier 2 fallback | BLOCKING | RESOLVED |
| B-6 메이저 문구 | BLOCKING | RESOLVED |
| W-1 100억 근거 | WARNING | ACCEPTABLE |
| W-2 common-window | WARNING | RESOLVED |
| W-3 sub-plan 상태 | WARNING | RESOLVED |
| W-4 시간 합산 | WARNING | RESOLVED (0.1일 잔차 = WARNING-NEW-2) |
| W-5 후보 풀 물리화 | WARNING | RESOLVED |
| W-6 CoinGecko 근거 | WARNING | RESOLVED |
| W-7 regime leakage | WARNING | RESOLVED |
| — | NEW | WARNING-NEW-1: DSR threshold 상향 (Week 3) |
| — | NEW | WARNING-NEW-2: Meta 기간 산수 0.1일 잔차 |
| — | NEW | NIT-NEW-1: 경로 표기 `research/data/` vs `data/` 혼재 |
| — | NEW | NIT-NEW-2: sub-plan 리스크 표에 C/D 서약 직접 문구 없음 |

### 최종 재검증 판정

**APPROVED**

이유:
1. 6 BLOCKING 전부 RESOLVED. 원 리뷰의 권고안보다 엄격한 방향으로 수정됨 (18→6셀, DSR 필수, snooping guard 추가, soft contamination 명시).
2. 7 WARNING 중 6개 RESOLVED, 1개 (W-1) ACCEPTABLE.
3. 새로 발견된 2 WARNING-NEW + 2 NIT-NEW 중 어느 것도 사용자 승인 직전 블로커가 아님. W2-01 SubTask 실행 중 또는 W2-02 sub-plan 작성 시 반영 가능.
4. cross-document 일관성: execution-plan ↔ decisions-final ↔ sub-plan의 Go 기준 표현이 셋 다 "Primary 6셀, BTC 또는 ETH, Sharpe > 0.8 AND DSR > 0, Secondary 마커, Week 3 최종 검증"으로 일치.
5. CLAUDE.md Immutable 룰(데이터 스누핑 금지, 외부 감사 반복, 2차 인용 금지) 위반 없음.

**권장 후속 조치 (APPROVE에 영향 X, 후속 cycle 과제)**:
- WARNING-NEW-1: W3-03 sub-plan 작성 시 DSR threshold를 명시적으로 상향 (예: DSR > 0.5).
- WARNING-NEW-2: sub-plan L10 산수를 "1.9일 + 0.1일 buffer" 또는 "~1.8–1.9일 + 0.1–0.2일 buffer"로 정정.
- NIT-NEW-1: W2-01.2 구현 전 `research/data/` 경로로 통일.
- NIT-NEW-2: sub-plan 리스크 표 L240에 "문헌 기본값 사용 서약" 문구 직접 삽입 고려.

---

**재리뷰 완료 타임스탬프**: 2026-04-17 pm UTC
**리뷰어 서명**: external auditor (adversarial, no-benefit-of-the-doubt)
