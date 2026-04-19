# 코인봇 프로젝트 전체 히스토리 (Day 0 ~ W2-03.1)

**작성 시점**: 2026-04-20
**범위**: 2026-04-13 (Day 0) ~ 2026-04-19 (W2-03.1 완료)
**목적**: 다른 PC/세션에서 프로젝트 상태 빠르게 복원하기 위한 시간순 정리. handover v11 (`.claude/handover-2026-04-17.md`)이 직전 세션 정확 상태. 본 문서는 전체 흐름 + 학습 패턴 + 의사결정 trace.

## 빠른 요약

- **현재 위치**: W2-03.1 W-1 미니 테스트 완료 + 방법 B 사용자 채택. **W2-03.0 (`make_notebook_08.py` 작성) 진입 대기**
- **Stage 1 진행**: Week 1 No-Go → Week 2 재범위 (W2-01 cycle 1 사이클 중단 → cycle 2 완료, W2-02 Candidate C/D 사전 등록, W2-03 sub-plan + W-1 미니 테스트 완료)
- **마지막 커밋**: `27ece9f` (W2-03.1 + 방법 B 채택)
- **handover**: v11 (`.claude/handover-2026-04-17.md`)
- **별도 task 잔존**: W1 sqrt(252) vs sqrt(365) 일관성 정정 (handover 신규 패턴 #21)

---

## 프로젝트 메타

- **목표**: 업비트 KRW 자동 매매 봇 학습 프로젝트. **북극성 = "안정적인 수익 구조"** (단기 PASS 아니라 검증된 엣지)
- **사용자**: 자바 스프링 백엔드 개발자, 트레이딩/Python/크립토 도메인 신규
- **응답**: 한국어. 전문 용어 풀이 필수
- **단계 게이트**: Stage 1 (Week 8) / Stage 2 (Week 12). 라이브 트레이딩은 Stage 2 게이트 통과 시 50만원 한정
- **Tech**: Python 3.11+, Jupyter + pandas + vectorbt 0.28.5 + pyupbit 0.2.34 (research) / Freqtrade + ccxt (Week 4+)

## 핵심 결정 + 박제 패턴

- **단일 진실 문서**: `docs/decisions-final.md` (모든 결정), `docs/architecture.md` (시스템), `docs/glossary.md` (용어), `docs/candidate-pool.md` (전략)
- **사전 지정 (pre-registration) 원칙**: 결과 보고 파라미터 변경 = data snooping = cycle 강제
- **외부 감사관 자가 재검증**: 모든 박제 후 적대적 외부 감사관 페르소나로 비판적 재검토 (사용자 명시 반복 요구, memory `feedback_verification.md`)
- **NIT까지 해소 후 진행**: cycle 1 학습 = NIT 잔존 거부
- **사용자 명시 결정**: Go/No-Go 자동 X. 박제 시점 = 사용자 발화 인용

---

# 시간순 히스토리

## Phase 0: 프로젝트 초기 (2026-04-13)

### Day 0 — 프로젝트 초기 설정 (커밋 `f430a8d`)

**사용자 요청**: 코인봇 프로젝트 시작 (학습 프로젝트 정의)

**Claude 작업**:
- 단계별 결정 사이클 (Day 0 corrections → decisions-final.md 통합)
- 14 Task EPIC 작성 (`docs/stage1-execution-plan.md`)
- W1-01 ~ W1-06 sub-plan 작성
- CLAUDE.md 시스템 (root + docs + research) 작성
- backtest-reviewer agent 정의
- Immutable 룰 박제 (50만원 한도, 현물 only, LLM 매매 결정 X, Cloudflare Tunnel, 단일 진실 문서)

**핵심 결정**:
- Tech stack: vectorbt 0.28.5 + pyupbit 0.2.34 (Freqtrade는 Week 4+)
- 데이터 freeze 패턴: `KRW-{X}_{1d,4h}_frozen_{YYYYMMDD}.parquet` + SHA256
- 5년 advertised 범위: 2021-01-01 ~ 2026-04-12 UTC

---

## Phase 1: Week 1 백테스트 (2026-04-14 ~ 2026-04-17)

### W1-01 — 데이터 수집 (커밋 `3a051a2`, `fd40b11`)

**사용자**: 데이터 수집 진행 OK

**Claude 작업**:
- `make_notebook_01.py` + `01_data_collection.ipynb` 작성/실행
- KRW-BTC 5년 일봉 + 4시간봉 freeze
- pyupbit naive KST → UTC 변환 (`assert df.index.tz is None` → `tz_localize('Asia/Seoul').tz_convert('UTC')`)
- SHA256 + `data_hashes.txt` 기록
- 외부 감사: 6 BLOCKING 정정 (data freeze + UTC + 무결성 검증)

**evidence**: `.evidence/w1-01-data-collection.txt` + `.evidence/agent-reviews/w1-01-2026-04-14T01-27-review.md`

### W1-02 — Strategy A 일봉 백테스트 (커밋 `552a4e5`, `ae71e52`, `6828ba8`, `9c15ddc`, `0bfea73`, `46b471c`)

**Strategy A**: Trend Following (MA200 + Donchian 20/10 + Volume>1.5x + SL 8%)
**박제 출처**: Padysak/Vojtko 영감 (Padysak 2020 스타일 변형)

**Claude 작업**:
- `02_strategy_a_daily.ipynb` 실행
- vectorbt 0.28.5 검증 (sl_stop, sl_trail 사용법)
- 외부 감사 5회 (v1 → v5): BLOCKING + WARNING + NIT 다수 정정
  - 데이터 freeze 검증, 사전 지정 파라미터 명시, vectorbt API 정확성
  - **금지 패턴 박제**: `ts_stop`, `td_stop` (vectorbt 0.28.5 무료 버전에 없음)

**결과 (W1-02)**:
- BTC 일봉 Sharpe 1.0353, 총수익 +171.76%, MDD -22.45%, 14 trades
- 2024년 단년 집중 (68.3% 기여), 2024-12-17 이후 481일 Sharpe -1.14 (2승 3패)

### W1-03 — Strategy B 일봉 백테스트 (커밋 `55512e4`, `9c15ddc`, `9fc80bb`, `0bfea73`, `46b471c`)

**Strategy B**: Mean Reversion (MA200 + RSI(4)<25 → exit RSI>50 또는 5d time stop, SL 8%)

**Claude 작업**:
- `03_strategy_b_daily.ipynb` 실행
- 외부 감사 4회 (v1 → v4): WARNING + NIT 정정

**결과 (W1-03)**:
- BTC 일봉 Sharpe **0.1362** (Go 기준 0.5 미달) → **No-Go**
- 총수익 +4.94% (5년), PF 1.09, 2021년 -13.16% 손실로 전체 잠식
- 민감도 그리드에서도 유사 → **구조적 엣지 부재 확인**

### W1-04 — 강건성 + 민감도 분석 (커밋 `1fe659d`, `c4e0c87`)

**Claude 작업**:
- Strategy A/B 민감도 그리드 (참고용, Go 평가 X)
- bear/bull regime 분석
- 외부 감사: WARNING 3건 정정

### W1-05 — 4시간봉 포팅 실험 (커밋 `93f71bf`, `5fa8f93`)

**Claude 작업**:
- Strategy A/B를 4시간봉으로 포팅
- A: Sharpe 0.07 (4h decay), B: Sharpe -0.61 (더 악화)
- 4시간봉은 참고용, Go 기준 X (일봉 기준)
- 외부 감사: BLOCKING 1 + WARNING 2 정정

### W1-06 — Week 1 종합 리포트 + No-Go 결정 (커밋 `47e727d`)

**사용자 결정**: W1 종합 리포트 진행 OK

**Claude 작업**:
- Strategy A/B 통합 평가
- W1-06.1b regime 분석 (A regime 편중 발견)
- 사전 지정 Go 기준 적용:
  - Strategy A: Conditional Pass (Sharpe 1.04, 단 2024 집중)
  - Strategy B: **No-Go (Sharpe 0.14)** → Deprecated
- **Stage 1 No-Go 결정** (사용자 명시 승인)
- Week 2 재범위 결정: 전략 후보 재탐색 + 메이저 알트 확장

**중요 박제**:
- decisions-final.md "Week 2 재범위 결정" + "Week 2 한계 및 독립성 서약"
- candidate-pool.md 신설 (2026-04-17, Strategy A Retained / B Deprecated)
- Multiple testing 한계 인정 + DSR Week 2 게이트 부분 포함

---

## Phase 2: Week 2 W2-01 cycle 1 → cycle 2 (2026-04-17 ~ 2026-04-19)

### W2-01 sub-plan 외부 감사 대응 (커밋 `99b281d`)

**Claude 작업**:
- 외부 감사 6 BLOCKING + 7 WARNING 정정
  - B-2: 측정 창 미정의 → 2026-03-13 ~ 2026-04-11 UTC inclusive 30일 박제
  - B-3 CRITICAL: Multiple testing 미보정 → DSR 박제
  - B-4: Soft contamination 간과 → "Week 2 한계 서약" 추가
  - B-5: Fallback "임계값 완화" 함정 → 차단 박제
  - W-A: cross-document 전파 (sub-plan + decisions-final)
- candidate-pool.md 신설 (이 시점)

### W2-01.1 페어 선정 기준 v4 APPROVED (커밋 `5c1734c`)

**사용자 발화**: "ㅇㅋ ㄱㄱ 해" (2026-04-17 06:25 UTC)

**Claude 작업**:
- `pair-selection-criteria-week2.md` v4 작성 (270줄)
- **3회 외부 감사 사이클**:
  - 1차: CHANGES REQUIRED (4 BLOCKING + 7 WARNING + 5 NIT)
  - 2차: 1 BLOCKING + 4 WARNING (B-A cherry-pick 재유입 차단)
  - 3차: 0 BLOCKING + 1 WARNING + 5 NIT → APPROVED
- **사용자 승인 발효** (섹션 6.1 freeze)
- 박제 핵심:
  - 시총 top30 스냅샷 2026-04-17 00:00 UTC
  - 상장 ≤ 2023-04-17 (3년+)
  - 30 UTC-day 평균 거래대금 ≥ 100억
  - **Tier 2 = {XRP, SOL, ADA, DOGE} 추정 박제**
  - Fallback (i) Tier 2 제거 / (ii) 재설계 사이클
  - **실측 불일치 시 cherry-pick 차단: Fallback (ii) 강제** (이 박제가 cycle 1 → cycle 2 전이의 핵심)

### W2-01.2 단계 1 실측 → cycle 1 사이클 중단 (커밋 `2e03ed1`, `b61fc9b`)

**Claude 작업** (`research/_tools/cycle2_tier2_decision.py` 형태로 단계 1 코드 실행):
- CoinGecko top30 KRW snapshot 조회 + JSON freeze + SHA256 (`c70a1089...`)
- **실측 결과**: top10 = `[BTC, ETH, USDT, XRP, BNB, USDC, SOL, TRX, FIGR_HELOC, DOGE]`
- **ADA 14위로 빠짐** → 박제 Tier 2 리스트 {XRP, SOL, ADA, DOGE}와 불일치
- cherry-pick 차단 장치 (criteria L78, L117) 정상 발동

**자가 검증 발견**:
- FIGR_HELOC 정체 추측 차단 (Figure Heloc RWA 토큰, 24h 거래량 232억 = 시총의 0.09%)
- 수치 단위 표기 오류 발견 (0.0009% vs 0.09% 비율 vs % 혼동)
- snapshot JSON gitignored 발견 (W1-01 data_hashes.txt도 누락 = 누적 누락 박제)

**사용자 발화**: "그래 추천한걸로 가" (2026-04-17 07:08 UTC) → **Fallback (ii) 발동 + 사이클 중단**

**중요 결정 사이클** (사용자 + Claude 공동):
1. ADA가 메이저 코인이라 cherry-pick 유혹 (사용자 직관) → Claude 거절: "이게 정확히 사전 지정 원칙 위반의 정의"
2. 옵션 1 (현 기준 유지 Fallback ii) vs 옵션 2/3 (기준 재설계) → **옵션 1 채택**
3. snapshot JSON 처리 옵션 A/B/C → **옵션 B 선택** (로컬 보존, gitignored 유지)
4. follow-up 커밋: criteria 헤더 명칭 일관성 정정 (`b61fc9b`)

### W2-01 cycle 2 v4 박제 + 사용자 승인 (커밋 `cbef953`, `90eb74c`)

**사용자 발화**: "너가 결정해줘 모든걸" (2026-04-19) → 위임 발화 = cycle 2 사용자 승인 시점 박제

**Claude 작업** (cycle 2 설계 사이클):
- cycle 2 v4 신설 (`pair-selection-criteria-week2-cycle2.md`)
- **3회 외부 감사 사이클**:
  - 1차: CHANGES REQUIRED (1 BLOCKING + 4 WARNING + 3 NIT)
  - 자가 추가 검증: 5 WARNING + 4 NIT 추가 발견 → v3 정정
  - 2차: APPROVED with follow-up + W2-1/W2-2 사용자 결정 사항
  - 16+ 라운드 자가 재검증: CRITICAL 1 + WARNING 1 + NIT 2 추가 → 정정
- **W2-1 사용자 결정**: cycle 1 격리 양성 목록 박제 채택 (decisions-final.md 신설)
- **W2-2 사용자 결정**: Fallback (ii) 누적 한도 = 3회 박제 채택 (decisions-final.md 신설)
- **cycle 2 핵심 변경**:
  - "Tier 2 리스트 추정 박제" 제거 → "규칙만 박제 + 코드 자동 결정"
  - snapshot_utc 명목 시각 폐기 → fetched_at만 진실 시각
  - cycle 1 snapshot JSON 재사용 (새 fetch 금지, cherry-pick 동기 차단)
  - 임계값/측정 창/Tier 1/Fallback = cycle 1 그대로 유지 (soft contamination 인정)

**handover v6 잔존 섹션 정리** (`90eb74c`): 라운드 21~30 자가 재검증 NIT 해소

### W2-01.2 sub-plan cycle 2 시점 갱신 (커밋 `2aca62d`)

**Claude 작업**:
- W2-01.2 cycle 2 시점 단계 박제 갱신 (NIT2-3 외부 감사관 절차)
- cycle 1 단계 1 history 박제 (실행 안 함 표시)
- cycle 2 단계 추가 (snapshot 재사용 + Tier 2 결정 코드 + 외부 감사 + 실행)

### W2-01 cycle 2 W2-01.2 + W2-01.3 (커밋 `84817b4`)

**Claude 작업**:
- **W2-01.2 단계 2 (Tier 2 결정 코드)**:
  - `research/_tools/cycle2_tier2_decision.py` 신설
  - 외부 감사 호출 → APPROVED with follow-up (W-1 path 정정, W-3 라벨 정정)
  - 코드 실행 → **Tier 2 = `[XRP, SOL, TRX, DOGE]`** (자동 산출)
  - 새 스테이블 발견 0건 (사용자 직접 검증)
- **W2-01.2 단계 2-2 (상장일 + 거래대금 검증)**:
  - `research/_tools/cycle2_tier2_validation.py` 신설
  - 4개 모두 PASS (XRP/SOL/TRX/DOGE)
  - pyupbit `value` 필드 사용 확인
  - Common-window 시작일 = **2021-10-15 UTC** (SOL 기준)
- **사용자 결정 (2026-04-19 "ㄱㄱ")**:
  - 100억 임계값 sanity 4.11x 초과 → **본 사이클 100억 유지**
  - 업비트 공식 공지 cross-check **스킵** (pyupbit 결과 신뢰)
- **W2-01.3 사용자 확정 리스트 승인** → cycle 2 v4 → v5 박제 (섹션 6.1 + 6.2 freeze 동시 발효)

### W2-01.4 데이터 수집 (커밋 `0c2044a`, `9e3c3c9`)

**Claude 작업**:
- `make_notebook_07.py` + `07_data_expansion.ipynb` 작성/실행
- 5 페어 (ETH/XRP/SOL/TRX/DOGE) × 일봉/4h = **10 dataset Parquet freeze**
- SHA256 + data_hashes.txt 갱신 (gitignored 유지, 옵션 B)
- 자가 외부 감사 (W-1~W-4 + NIT-1/3 정정)
- **무결성 강제 assert**: monotonic + dup + UTC + gap < 0.1% (max 0.0102%)
- **Common-window 박제 자동 assert PASS** (SOL day actual_start = 2021-10-15)
- **ETH 박제 자동 assert PASS** (advertised 시작 이전 상장)
- backtest-reviewer 호출 → **APPROVED with follow-up** (W-1 정정, W-2 별도 task)
- W-1 정정 후 **노트북 재빌드 + 재실행 동기화** (`9e3c3c9`, generator-notebook 박제 일관성)

---

## Phase 3: Week 2 W2-02 + /verify skill (2026-04-19)

### W2-02 v5 사용자 승인 발효 + /verify skill 신설 (커밋 `2e5624d`)

**사용자 결정 흐름**:
1. cycle 2 학습 권고 (vol/cap 차단 장치 추가) → 자가 재검증 결과 cherry-pick 위험 → 추천 정정 (추가 안 함)
2. **사용자 발화**: "검증부터 해야지 당연히" → 외부 감사 사이클 진입

**Claude 작업** (W2-02 sub-plan 작성 + 외부 감사 사이클):
- `w2-02-strategy-candidates.md` 신설
- **외부 감사 사이클 (cycle 1 W2-01.1 패턴 = 3회 감사)**:
  - 1차: CHANGES REQUIRED (BLOCKING 4 + WARNING 5 + NIT 4)
    - **B-1**: candidate-pool.md "신설" 박제 = 사실 오류 (이미 존재). **Claude 자가 검증 부족 인정** + handover #20 패턴 누적
    - **B-2**: KeltnerChannel 출처 사실 오류 (Keltner 1960 ≠ 우리 박제값). ta venv 직접 검증
    - B-3, B-4: Candidate C/D 신호 시점 모호
  - 2차: NEW BLOCKING 2 (NEW-B-1 "신설" 잔존 + NEW-B-2 vectorbt 코드 블록)
  - 3차: APPROVED with follow-up (BLOCKING 0)
  - 옵션 C 정정 5건 (W-1 ATR trailing / W-4 Secondary 정확 / W3-1 ta 버전 / N3-1 라벨 / N3-2 변수명)

**박제 발효** (사용자 "ㄱㄱ" 2026-04-19):
- Candidate C (Slow Momentum, MA50/200 + ATR×3 trail) Active/Registered
- Candidate D (Volatility Breakout, Keltner+Bollinger) Active/Registered
- 변경 금지 서약 발효
- candidate-pool.md v2: Strategy C/D Pending → Active 전이

**`/verify` skill 신설** (`.claude/skills/verify/SKILL.md`):
- **사용자 질문**: "내가 맨날 너한테 뭐끝나면 너가 한게 아니라고 생각하고 검증하라 하잖아? 이거 스킬이나 이벤트 훅으로 만들어야할거같은데 뭐가 나으려나?"
- claude-code-guide 위임 → Skill 추천 (Hook은 토큰 비용 + 토큰 토큰 낭비 위험)
- **자가 재검증 자동화**: 외부 감사관 페르소나 5+ 라운드 (사실 정확성 / 박제 정합성 / 누락 / 자기 모순 / cycle 1 학습 패턴 재발)

---

## Phase 4: Week 2 W2-03 sub-plan + W-1 미니 테스트 (2026-04-19)

### W2-03 sub-plan v4 사용자 승인 발효 (커밋 `f2052e8`)

**Claude 작업**:
- `w2-03-insample-grid.md` v1 신설 (~250줄)
- **외부 감사 사이클 (3회)**:
  - 1차: CHANGES REQUIRED (BLOCKING 4 + WARNING 6 + NIT 5)
    - **B-1, B-2 CRITICAL**: DSR 공식 부정확 (Bailey & López de Prado 2014 원문 vs Claude 추측)
      - 정확: `SR_0 = sqrt(V[SR_n]) × ((1-γ) × Φ⁻¹(1 - 1/N) + γ × Φ⁻¹(1 - 1/(N·e)))`, γ = 0.5772
    - B-3: "5 페어" 산술 오류 (실제 6 페어)
    - B-4: Strategy A Recall vs C/D 비대칭
  - 2차: APPROVED with follow-up (BLOCKING 0) + 신규 W-N1/NIT-N1/N2/N3
  - 3차: APPROVED (BLOCKING 0 + WARNING 0)
- **옵션 A1 정정 (NIT-N1/N2/N3 + NIT-1~4 + W-N1)**: 모두 정정 + cross-document 정합

**핵심 박제**:
- Tier 1 6 primary + Tier 2 12 exploratory
- DSR (Bailey & López de Prado 2014 Wikipedia 직접 cross-check) 정확 공식
- N_trials = 6 (Primary만, Tier 2 Go 기여 X)
- Go 기준: Sharpe > 0.8 AND DSR_z > 0
- Strategy A/C/D Recall 의무 대칭 박제
- sqrt(365) annualization (W1 sqrt(252) 일관성 깨짐 발견 → handover #21 신규 패턴 별도 task)
- vectorbt multi-asset 방식 A 채택
- Common-window vs max-span 비대칭 cherry-pick 차단

**cross-document 정정**:
- decisions-final.md L515 ADA → TRX (cycle 2 v5 정정)
- stage1-execution-plan.md L207/L227 ADA → TRX
- w2-01-data-expansion.md L281 데이터 파일명 ADA → TRX
- candidate-pool.md L41/L55 Strategy C/D Recall 의무 박제

**사용자 발화**: "ㄱㄱㄱㄱ" (2026-04-19) → v4 사용자 승인 발효

### W2-03.1 W-1 미니 테스트 + 방법 B 채택 (커밋 `27ece9f`)

**사용자 결정**: B+외부감사 (별도 스크립트 + 외부 감사관 호출)

**Claude 작업**:
- `research/_tools/w2_03_w1_test.py` 신설 (~200줄)
  - synthetic data (200 bars, 4 phase trend) + ATR_WINDOW=14, ATR_MULT=3.0
  - 방법 A (vectorbt sl_stop Series + sl_trail=True) vs 방법 B (manual exit_mask)
- 외부 감사 → BLOCKING 1 (records_readable 컬럼명 추측 → records raw 정정)
- 재실행 결과:
  - 방법 A: return 23.51%, exit_idx 107
  - 방법 B: return 26.52%, exit_idx 105
  - 차이 3.01%p > 임계값 0.5%p
- **W-2 발견**: vectorbt sl_trail=True는 entry bar 시점 비율 freeze (매 bar 동적 ATR 반영 X) → 방법 A는 박제 의도 위반
- **사용자 명시 채택**: 방법 B (2026-04-19 "ㄱㄱ")

**cross-document 정정 (4 위치 정합, NIT 7번 포함)**:
- sub-plan W2-03 v4 → v5 (W2-03.1 완료 + 방법 B 박제 + synthetic 한계 인정)
- candidate-pool.md v3 → v4 (Strategy C trailing stop 정확화: manual 매 bar 동적 ATR)
- W2-02 sub-plan v5 → v6 (NIT 7번: W-1 결과 박제 추가)
- research/outputs/w2_03_w1_test.json 자동 저장 추가

---

## 사용자 핵심 발화 + 패턴

| 발화 | 의미 | 시점 |
|------|------|------|
| "ㅇㅋ ㄱㄱ 해" | W2-01.1 v4 기준 승인 | 2026-04-17 |
| "그래 추천한걸로 가" | cycle 1 Fallback (ii) 발동 | 2026-04-17 |
| "너가 결정해줘 모든걸" | cycle 2 위임 + 사용자 승인 시점 | 2026-04-19 |
| "ㄱㄱ" | 다양한 결정 채택 (반복) | 다수 |
| "ㄱㄱㄱㄱ" | W2-03 v4 승인 | 2026-04-19 |
| "검증부터 해야지 당연히" | 외부 감사 우선 | 반복 |
| "남이 짠걸 검증한다는 생각으로" | rubber-stamp 금지 | 반복 |
| "왜 처음 검증할때 이걸 얘기안했어?" | 검증 범위 좁게 X | 반복 |
| "직접 판단을 무책임하게 떠넘기지 말 것" | 옵션 + 추천 명확 | 반복 |
| "이상 없는 거야?" | rubber-stamp 재검증 | 반복 |

## 사용자 결정 사항 박제

| 사항 | 결정 | 시점 |
|------|------|------|
| W2-01 cycle 2 박제 | "리스트 박제 제거 + 규칙만 박제" 채택 | 2026-04-19 |
| cycle 1 격리 양성 목록 (W2-1) | decisions-final.md 박제 추가 | 2026-04-19 |
| Fallback (ii) 누적 한도 (W2-2) | = 3회 박제 | 2026-04-19 |
| Tier 2 평가 정책 (#4) | "Secondary 마킹, Go 기여 X" 그대로 유지 | 2026-04-19 |
| 100억 sanity 4.11x 초과 | 본 사이클 100억 유지 (cycle 3 변경) | 2026-04-19 |
| 업비트 공식 공지 cross-check | 스킵 (pyupbit 신뢰) | 2026-04-19 |
| W-1 미니 테스트 방법 채택 | 방법 B (manual 매 bar ATR) | 2026-04-19 |
| .gitignore 처리 | 옵션 B (로컬 보존, 별도 task) | 2026-04-18 |

---

## 학습 패턴 (handover #1~#21, 누적)

| # | 패턴 | 발견 시점 |
|---|------|----------|
| 1 | Evidence 수치 오기재 (W1-06 "1승 4패" 사건) | W1-06 |
| 2 | 문서 버전 라벨 미갱신 | 다수 |
| 3 | execution-plan 체크박스 미체크 | 다수 |
| 4 | backtest-reviewer 좁은 스코프 | W1 |
| 5 | fillna() FutureWarning | W1 |
| 6 | research/outputs gitignore | W1-01 |
| 7 | 사전 지정 기준 측정 창 미정의 (W2-01 B-2) | W2-01 |
| 8 | Multiple testing 미보정 (W2-01 B-3 CRITICAL) | W2-01 |
| 9 | Soft contamination 간과 (W2-01 B-4) | W2-01 |
| 10 | Fallback "임계값 완화" (W2-01 B-5) | W2-01 |
| 11 | 측정 창 inclusive off-by-one (W2-01.1 1차 B-1) | W2-01.1 |
| 12 | Fallback 라벨 misnomer | W2-01.1 |
| 13 | 박제 freeze 시점 순환 정의 | W2-01.1 |
| 14 | 실측 cherry-pick 재유입 차단 | W2-01.1 |
| 15 | sub-plan/decisions-final 전파 누락 (cross-document) | W2-01.1 |
| 16 | 외부 라이브러리 응답 필드 추측 | W2-01.1 |
| 17 | 사전 지정 추정 리스트 빗나감 (cycle 1 ADA) | cycle 1 |
| 18 | 외부 코인 정체 추측 (FIGR_HELOC) | cycle 1 |
| 19 | 수치 단위 표기 오류 (% vs 비율) | cycle 1 |
| 20 | sub-plan 박제 vs .gitignore 룰 충돌 누적 | cycle 1 |
| 21 | W1 sqrt(252) vs sqrt(365) 일관성 깨짐 (별도 task 잔존) | W2-03 1차 감사 |

---

## 외부 감사 사이클 통계

| Task | 감사 횟수 | 누적 BLOCKING | 누적 WARNING | 누적 NIT |
|------|----------|--------------|--------------|---------|
| W1-01 | 1회 | 6 | - | - |
| W1-02 | 5회 | 다수 | 다수 | 다수 |
| W1-03 | 4회 | - | 다수 | 다수 |
| W1-04 | 1회 | - | 3 | - |
| W1-05 | 1회 | 1 | 2 | - |
| W1-06 | 1회 | - | - | - |
| W2-01 사전 | 1회 | 6 | 7 | - |
| W2-01.1 (cycle 1 v4) | 3회 | 5 | 12 | 10 |
| W2-01 cycle 2 v4 | 3회 + 16 라운드 자가 | 1 | 5 | 4+ |
| W2-01.2 cycle 2 단계 2 코드 | 1회 | - | 3 | 4 |
| W2-01.4 데이터 수집 | 1회 (backtest-reviewer) | - | 2 | 3 |
| W2-02 v5 | 3회 + 옵션 C | 6 | 5 | 6 |
| W2-03 sub-plan v4 | 3회 | 4 | 6+1 | 5+3+2 |
| W2-03.1 W-1 미니 테스트 | 1회 | 1 | 3 | 3 |

**총 외부 감사 호출**: ~26회

---

## 다음 작업 가이드 (다른 PC에서 진입)

### 즉시 시작 (W2-03.0 진입)

```bash
# 1. git pull
cd <coin-bot 디렉토리>
git pull origin main

# 2. handover 읽기 (최신 상태 확인)
cat .claude/handover-2026-04-17.md

# 3. 현재 위치: W2-03.1 W-1 미니 테스트 완료, W2-03.0 진입 대기
```

### W2-03.0 작업 내용

**`research/_tools/make_notebook_08.py` 작성** (~400줄):
- 13 셀 (헤더/imports/박제 상수/데이터 로드/Strategy 시그널/Portfolio 함수/Primary grid/Exploratory grid/DSR/Go-NoGo/결과 저장)
- 박제 인용:
  - cycle 2 v5 (페어 + Common-window = 2021-10-15 UTC)
  - W2-02 v6 (Strategy C/D 박제 + 방법 B trailing stop)
  - W2-03 v5 (DSR 정확 공식)
  - candidate-pool.md v4 (Strategy A/C/D 진입/청산)
- 강제 명시:
  - `year_freq='365 days'` (sqrt(365) annualization)
  - ta `KeltnerChannel(window=20, window_atr=14, original_version=False, multiplier=1.5)`
  - DSR_z + DSR_prob 동시 산출 (W-N1)
  - vectorbt multi-asset 방식 A (페어별 단일 Portfolio)
  - Strategy C trailing = manual `trailing_high - ATR_MULT × ATR(t)` exit_mask (방법 B)

**참고 파일**:
- `docs/stage1-subplans/w2-03-insample-grid.md` v5 (W2-03.0 박제 가이드)
- `docs/candidate-pool.md` v4 (Strategy A/C/D 박제)
- `research/_tools/w2_03_w1_test.py` (W-1 결과 참조)
- `research/outputs/w2_03_w1_test.json` (방법 B 채택 결과)

### 별도 task (잔존)

- **handover #21**: W1 노트북 산출물 sqrt(252) vs sqrt(365) 일관성 정정 (W2-03 v4 박제 = sqrt(365))
- **`.gitignore` 정정**: W1-01 data_hashes.txt + parquet 누락 누적 (옵션 B 결정 시 미룸)

### `/verify` skill 사용

채팅창에 `/verify` 입력 → 외부 감사관 페르소나 5+ 라운드 자가 재검증 자동.

---

## 주요 파일 위치 빠른 참조

| 용도 | 경로 |
|------|------|
| 프로젝트 규칙 | `CLAUDE.md` |
| 리서치 규칙 | `research/CLAUDE.md` |
| docs 규칙 | `docs/CLAUDE.md` |
| **모든 결정** | `docs/decisions-final.md` |
| **사용자 용어집** | `docs/glossary.md` |
| **시스템 설계** | `docs/architecture.md` |
| **Stage 1 EPIC** | `docs/stage1-execution-plan.md` |
| **전략 풀** | `docs/candidate-pool.md` v4 |
| **현재 sub-plan** | `docs/stage1-subplans/w2-03-insample-grid.md` v5 |
| **이전 sub-plan** | `docs/stage1-subplans/w2-02-strategy-candidates.md` v6 |
| **W2-01 sub-plan** | `docs/stage1-subplans/w2-01-data-expansion.md` |
| **cycle 1 v4 (격리)** | `docs/pair-selection-criteria-week2.md` v4 |
| **cycle 2 v5** | `docs/pair-selection-criteria-week2-cycle2.md` v5 |
| **세션 인수인계** | `.claude/handover-2026-04-17.md` v11 |
| **/verify skill** | `.claude/skills/verify/SKILL.md` |
| **backtest-reviewer** | `.claude/agents/backtest-reviewer.md` |
| **evidence (Week 1)** | `.evidence/w1-01~06-*.txt` |
| **evidence (cycle 2)** | `.evidence/w2-01-cycle2-step2-tier2-decision-2026-04-19.md` + `step4-data-collection-2026-04-19.md` |
| **외부 감사 trace** | `.evidence/agent-reviews/*.md` |
| **데이터 (gitignored)** | `research/data/KRW-*.parquet` + `data_hashes.txt` + `coingecko_top30_snapshot_20260417.json` |
| **노트북** | `research/notebooks/01~07_*.ipynb` |
| **노트북 생성기** | `research/_tools/make_notebook_0{1..7}.py` |
| **cycle 2 코드** | `research/_tools/cycle2_tier2_decision.py` + `cycle2_tier2_validation.py` + `w2_03_w1_test.py` |
| **memory** | `~/.claude/projects/-Users-kyounghwanlee-Desktop-coin-bot/memory/MEMORY.md` |

---

## 부록: 모든 커밋 (시간순, 28개)

| # | hash | date | 내용 |
|---|------|------|------|
| 1 | f430a8d | 2026-04-13 | Day 0 프로젝트 초기 설정 |
| 2 | 3a051a2 | 2026-04-14 | DATA-001 W1-01 데이터 수집 |
| 3 | fd40b11 | 2026-04-14 | W1-01 감사 6건 정정 |
| 4 | 552a4e5 | 2026-04-14 | STR-A-001 W1-02 Strategy A 백테스트 |
| 5 | ae71e52 | 2026-04-14 | W1-02 감사 6건 정정 |
| 6 | 6828ba8 | 2026-04-14 | W1-02 v3 3차 감사 정정 |
| 7 | 55512e4 | 2026-04-14 | STR-B-001 W1-03 Strategy B (Sharpe 0.14 FAIL) |
| 8 | 9c15ddc | 2026-04-14 | W1-02 v4 + W1-03 v2 공통 schema 정정 |
| 9 | 9fc80bb | 2026-04-15 | W1-03 v3 2차 감사 정정 |
| 10 | 0bfea73 | 2026-04-16 | W1-02 v5 + W1-03 v4 3차 감사 정정 |
| 11 | 46b471c | 2026-04-16 | W1-02/W1-03 재검증 정정 |
| 12 | 1fe659d | 2026-04-16 | BT-001 W1-04 강건성 + 민감도 |
| 13 | c4e0c87 | 2026-04-17 | W1-04 재검증 정정 |
| 14 | 93f71bf | 2026-04-17 | BT-002 W1-05 4시간봉 포팅 |
| 15 | 5fa8f93 | 2026-04-17 | W1-05 재검증 정정 |
| 16 | 47e727d | 2026-04-17 | **W1-06 Week 1 종합 + No-Go 결정** |
| 17 | 99b281d | 2026-04-17 | W2-01 외부 감사 6 BLOCKING + 7 WARNING 정정 |
| 18 | 5c1734c | 2026-04-17 | **W2-01.1 v4 사용자 승인** |
| 19 | 2e03ed1 | 2026-04-18 | **W2-01 v4 cycle 1 사이클 중단 (Fallback ii)** |
| 20 | b61fc9b | 2026-04-18 | W2-01 criteria 헤더 명칭 정정 |
| 21 | cbef953 | 2026-04-19 | **W2-01 cycle 2 v4 박제 + 사용자 승인** |
| 22 | 90eb74c | 2026-04-19 | handover v6 잔존 섹션 정리 |
| 23 | 2aca62d | 2026-04-19 | W2-01.2 sub-plan cycle 2 갱신 |
| 24 | 84817b4 | 2026-04-19 | **W2-01 cycle 2 W2-01.2 + W2-01.3 (Tier 2 = [XRP,SOL,TRX,DOGE])** |
| 25 | 0c2044a | 2026-04-19 | W2-01 cycle 2 W2-01.4 데이터 수집 |
| 26 | 9e3c3c9 | 2026-04-19 | W2-01.4 노트북 W-1 정정 동기화 |
| 27 | 2e5624d | 2026-04-19 | **W2-02 v5 사용자 승인 + /verify skill 신설** |
| 28 | f2052e8 | 2026-04-19 | **W2-03 sub-plan v4 사용자 승인** |
| 29 | 27ece9f | 2026-04-19 | **W2-03.1 W-1 미니 테스트 + 방법 B 채택** |

---

**문서 종료. 다음 작업 = W2-03.0 진입 (`make_notebook_08.py` 작성). 새 PC/세션에서 git pull + handover 읽기 + W2-03.0 진입.**
