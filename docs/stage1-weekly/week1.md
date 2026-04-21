# Stage 1 Week 1 — 일봉 복제 스프린트

> 상위 계획: [`../stage1-execution-plan.md`](../stage1-execution-plan.md) (EPIC 뷰)
> Task 상세 sub-plan: [`../stage1-subplans/`](../stage1-subplans/)

## 요약

- **기간**: Week 1 (2026-04-14 ~ 2026-04-17 완료)
- **목적**: Padysak/Vojtko 영감 전략 (200MA + Donchian + RSI(4)) 일봉 검증
- **산출물**: 노트북 6개 (`research/notebooks/0{1..6}_*.ipynb`), strategy_*.json, Week 1 리포트
- **결과**: **No-Go (Option B)** — 2026-04-17 사용자 결정. Stage 1 킬 카운터 +1. Week 2 재범위로 전환

## Task 목록

- [x] **W1-01. 데이터 수집 + 환경 세팅** (Feature: DATA-001) — Done 2026-04-14
  - **What**: pyupbit로 KRW-BTC 일봉/4h 5년치 다운로드, 타임존 localize, advertised 범위 slicing, Parquet freeze, SHA256 해시 기록. requirements.lock + git init.
  - **Must NOT**: 4시간봉을 Go/No-Go 기준으로 사용 금지. 데이터 인덱스 timezone naive 방치 금지.
  - **Acceptance**:
    - [x] 일봉 1927 bars, 4h 11561 bars 수집 (advertised [2021-01-01, 2026-04-12) UTC)
    - [x] 갭 < 0.1% (daily 0%, 4h 0.0086%)
    - [x] tz_localize KST → UTC 완료
    - [x] data_hashes.txt 생성 (advertised + actual 범위 헤더)
    - [x] requirements.lock 생성 (142 packages)
    - [x] backtest-reviewer APPROVED
  - **QA**: `jupyter nbconvert --to notebook --execute --inplace notebooks/01_data_collection.ipynb` → 산출물 검증
  - **Evidence**: `.evidence/w1-01-data-collection.txt`
  - **Commit**: `feat(plan): DATA-001 Week 1 데이터 수집 + 환경 세팅`

- [x] **W1-02. Strategy A 일봉 백테스트** (Feature: STR-A-001) — Done 2026-04-14
  - **What**: 200MA + Donchian(20/10) + 거래량 1.5x + 고정 8% 하드 스톱(sl_stop=0.08). 사전 지정 파라미터로 vectorbt 백테스트.
  - **Must NOT**: ts_stop, td_stop 사용 금지. 데이터 스누핑 금지. MA200 윈도우 ≠ 200 금지.
  - **Acceptance**:
    - [x] 사전 지정 파라미터 명시 선언
    - [x] 데이터 해시 검증 통과
    - [x] vectorbt 크래시 없이 실행
    - [x] outputs/strategy_a_daily.json 생성
    - [x] backtest-reviewer 에이전트 APPROVED
  - **결과**: Sharpe 1.0353 (PASS > 0.8), MDD -22.45% (PASS < 50%), Trades 14, PF 2.956, Win Rate 50%
  - **WARNING**: Trade 수 14 < 20 (sub-plan 리스크), W1-06에서 low-N caveat 명시 필요
  - **Evidence**: `.evidence/w1-02-strategy-a-daily.txt`
  - **Commit**: `feat(plan): STR-A-001 Strategy A 일봉 백테스트`

- [x] **W1-03. Strategy B 일봉 백테스트** (Feature: STR-B-001) — Done 2026-04-14
  - **What**: 200MA + RSI(4)<25 진입 + RSI(4)>50 청산 + entries.shift(5) 시간 스톱 + sl_stop=0.08.
  - **Must NOT**: bars_held 변수 참조 금지. RSI 직접 구현 금지 (ta 라이브러리 사용).
  - **Acceptance**:
    - [x] 사전 지정 파라미터 명시
    - [x] 시간 스톱 entries.shift(N) 패턴 사용
    - [x] outputs/strategy_b_daily.json 생성 (v3 schema)
    - [x] backtest-reviewer 에이전트 APPROVED (trace 저장)
  - **결과**: Sharpe 0.1362 (**FAIL < 0.5**), MDD -21.27% (PASS), Trades 39, PF 1.092
  - **해석**: Method 정확, 결과는 W1-06 Go/No-Go 영역. Strategy A 단독 채택 가능성 높음.
  - **Evidence**: `.evidence/w1-03-strategy-b-daily.txt`

- [x] **W1-04. 강건성 + 민감도 분석** (Feature: BT-001) — Done 2026-04-16
  - **What**: 연도별 분할 (2021~2026Q1) + 파라미터 민감도 그리드 (참고용)
  - **Must NOT**: 그리드 최고값을 Go/No-Go에 사용 금지. 사전 지정 파라미터만 결정 근거.
  - **Acceptance**:
    - [x] 5개 연도별 Sharpe/MDD/Return 계산
    - [x] 민감도 등고선 차트 (MA, Donchian, RSI 임계)
    - [x] 사전 지정 파라미터가 평탄 영역에 위치 확인
  - **결과**: A 평탄성 std=0.044 PASS, B std=0.170 PASS. A 3/5년 양수, B 4/5년 양수.
  - **목표**: 5개 연도 중 최소 2개 양수 수익 — Strategy A PASS (3개), B PASS (4개)
  - **Evidence**: `.evidence/w1-04-robustness.txt`
  - **Commit**: `feat(plan): BT-001 강건성 + 민감도 분석`

- [x] **W1-05. 4시간봉 포팅 실험** (Feature: BT-002) — Done 2026-04-17
  - **What**: 동일 전략을 4시간봉으로 (MA1200, Donchian 120/60, RSI(4))
  - **Must NOT**: Week 1 Go/No-Go 기준으로 사용 금지 (참고용 only)
  - **Acceptance**:
    - [x] 4h 윈도우 환산 정확 (200일 = 1200 bars)
    - [x] 일봉 결과와 비교 표
    - [x] outputs/strategy_4h_comparison.json
  - **결과**: A 4h Sharpe 1.12 (robust), B 4h Sharpe -0.61 (실패). 참고용.
  - **Evidence**: `.evidence/w1-05-4h-experiment.txt`
  - **Commit**: `feat(plan): BT-002 4시간봉 포팅 실험`

- [x] **W1-06. Week 1 리포트 + Go/No-Go** (Feature: REPORT-001) — Done 2026-04-17 (No-Go, Option B)
  - **What**: 모든 결과 통합 + Go/No-Go 결정 + 사용자 보고
  - **Must NOT**: 결과 부풀리기 금지. 한계/경고 명시.
  - **Acceptance**:
    - [x] week1_report.md 작성
    - [x] 사전 지정 파라미터 결과만 평가
    - [x] Go 기준 모두 충족 여부 명시
    - [x] 사용자 명시적 승인
  - **Go 기준 (모두 충족)**:
    - Strategy A 일봉 Sharpe > 0.8 — **PASS** (1.0353)
    - Strategy B 일봉 Sharpe > 0.5 — **FAIL** (0.1362)
    - 두 전략 중 하나라도 MDD < 50% — **PASS**
    - 두 전략 중 하나라도 5개 연도 중 최소 2개 양수 — **PASS**
    - 사전 지정 파라미터가 민감도 평탄 영역 — **PASS**
  - **결정**: **No-Go (Option B)** — Strategy B 구조적 엣지 부재 확인 + Strategy A 2024-12-17 이후 481일 regime decay (Sharpe -1.14) → Stage 1 킬 카운터 +1 + Week 2 재범위 사용
  - **Evidence**: `.evidence/w1-06-week1-report.txt`
  - **Commit**: `docs(plan): Week 1 리포트 + Go/No-Go 결정`

## Week 1 결과 요약

- **Strategy A**: Sharpe 1.0353, 총수익 +171.76%, MDD -22.45%, 14 trades — Sharpe 단독 관문 통과, 그러나 2024년 단년 집중 + 최근 481일 열화
- **Strategy B**: Sharpe 0.1362, 구조적 엣지 부재 확인 → 폐기
- **4시간봉**: A Sharpe 1.12 (robust), B Sharpe -0.61 (실패) — 참고용

## 후속 조치

- Strategy A 파라미터 → 후보 풀 보관 (candidate-pool.md, 즉시 메인 X)
- Strategy B → Deprecated 로그 (재도입 금지)
- Week 2 재범위: "walk-forward/DSR" → "전략 후보 재탐색 + 메이저 알트 확장"
- Walk-forward + DSR은 Week 3로 이전

자세한 의사결정 근거: [`../decisions-final.md`](../decisions-final.md) "Week 1 No-Go 결정" 섹션 참조.
