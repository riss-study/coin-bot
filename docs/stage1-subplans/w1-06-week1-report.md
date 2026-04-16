# Task W1-06 - Week 1 종합 리포트 + Go/No-Go 결정

## 메인 Task 메타데이터

| 항목 | 값 |
|------|-----|
| **메인 Task ID** | W1-06 |
| **Feature ID** | REPORT-001 |
| **주차** | Week 1 (Day 6~7) |
| **기간** | 1일 |
| **스토리 포인트** | 3 |
| **작업자** | Solo + 사용자 (승인) |
| **우선순위** | P0 (게이트) |
| **상태** | Done (No-Go 결정, 2026-04-17) |
| **Can Parallel** | NO (모든 W1-* 선행) |
| **Blocks** | W2-* (Go 시), 또는 전략 패밀리 재검토 (No-Go 시) |
| **Blocked By** | W1-02, W1-03, W1-04 (W1-05는 참고만, 차단 X) |

## 개요

Week 1의 모든 결과를 통합한 종합 리포트 작성 + 사전 지정 Go 기준 평가 + 사용자 명시적 승인. Week 2 진행 또는 No-Go 시 전략 패밀리 재검토 결정.

**핵심 원칙**: 사전 지정 파라미터 결과만 평가. 민감도 그리드 최고값 절대 사용 금지.

## 현재 진행 상태

- 메인 Task 상태: **Done (No-Go 결정, 2026-04-17)**

| SubTask | 상태 | 메모 |
|---------|------|------|
| W1-06.1 | Done | 노트북 06_week1_report.ipynb 생성 + 실행 |
| W1-06.1b | Done | 2025-2026 심화 분석 추가 (가격 기반 regime 라벨링) |
| W1-06.2 | Done | week1_report.md 작성 (7.5 섹션에 No-Go 결정 기록) |
| W1-06.3 | Done | Go 기준 5개 자동 평가 + week1_summary.json |
| W1-06.4 | Done | 사용자 승인 수령: No-Go (Option B) |
| W1-06.5 | In Progress | Evidence + backtest-reviewer + 상태 업데이트 |

## 최종 결정 요약 (W1-06.4)

- **결정**: **No-Go (Option B)**
- **결정 일시**: 2026-04-17 (UTC)
- **핵심 근거**:
  1. B Sharpe 0.1362 < 0.5 (사전 지정 기준 FAIL)
  2. A 최근 481일 Sharpe -1.14 (누적 -21.53%): regime shift / edge decay 징후
  3. A/B 모두 Volatile regime 편중 -> 앙상블 보완성 제한적
  4. 5년 Sharpe 1.04는 2024 단년 집중 효과 (68.3%)
- **후속 조치**:
  - Stage 1 킬 카운터 +1
  - Week 2 재범위: 전략 패밀리 재탐색 + 메이저 알트 확장
  - Strategy A 파라미터는 후보 풀 보관, Strategy B 구조적 폐기

## SubTask 목록

### SubTask W1-06.1: 노트북 통합

**작업자**: Solo
**예상 소요**: 0.2일

- [ ] `research/notebooks/06_week1_report.ipynb` 생성
- [ ] 모든 outputs/* JSON 로드
- [ ] equity curve 4개 비교 차트 (A 일봉, B 일봉, A 4h, B 4h)
- [ ] 연도별 분할 표 (W1-04 결과)
- [ ] 민감도 등고선 (W1-04 결과, 사전 지정 위치 표시)
- [ ] 4h 비교 표 (W1-05 결과, 참고용 라벨)
- [ ] Go 기준 체크리스트 자동 평가

### SubTask W1-06.2: week1_report.md 작성

**작업자**: Solo
**예상 소요**: 0.3일

`research/outputs/week1_report.md` 구조:

```markdown
# Week 1 결과 리포트

## 1. 데이터
- 기간: 2021-01-01 ~ 2026-04-12
- 일봉: N bars, gaps X%
- 4h: N bars, gaps X%
- SHA256 해시: ...

## 2. Strategy A (일봉, 사전 지정 파라미터)
- 파라미터: MA=200, Donchian=20/10, Vol=1.5x, SL=8%
- Sharpe: X.XX (목표 > 0.8)
- CAGR: XX.X%
- MDD: XX.X% (목표 < 50%)
- 승률: XX.X%
- PF: X.XX
- 트레이드: N
- Equity curve: [차트]

## 3. Strategy B (일봉, 사전 지정 파라미터)
(동일 형식)

## 4. 강건성 (W1-04)
### 연도별 분할
| 연도 | A Sharpe | B Sharpe | 우세 |
| 2021 | ... | ... |
| 2022 | ... | ... |
| 2023 | ... | ... |
| 2024 | ... | ... |
| 2025 | ... | ... |

### 민감도 (참고용)
- Strategy A 사전 지정: 평탄 영역 PASS/FAIL
- Strategy B 사전 지정: 평탄 영역 PASS/FAIL

## 5. 4시간봉 (참고용, Go/No-Go 영향 없음)
| 전략 | 일봉 | 4h | 차이 |
| A | X.XX | Y.YY | ... |
| B | X.XX | Y.YY | ... |

## 6. Go/No-Go 평가

### 기준 (모두 충족 필요)
- [ ] Strategy A 일봉 사전 지정 Sharpe > 0.8
- [ ] Strategy B 일봉 사전 지정 Sharpe > 0.5
- [ ] 두 전략 중 하나라도 MDD < 50%
- [ ] 두 전략 중 하나라도 5개 연도 중 최소 2개 양수 수익
- [ ] 사전 지정 파라미터가 민감도 평탄 영역

### 결정: [ Go ] / [ No-Go ]
**이유**: ...

### Go 시 다음 단계 (Week 2)
- W2-01 Walk-forward analysis
- W2-02 Deflated Sharpe + Monte Carlo + Bootstrap
- W2-03 알트코인 확장 + 앙상블

### No-Go 시 조치
- Stage 1 킬 카운터 +1주
- Week 2를 "전략 패밀리 탐색"에 사용
- 후보: 평균회귀 only, 모멘텀, 통계적 차익거래 등
```

### SubTask W1-06.3: Go 기준 자동 평가

**작업자**: Solo
**예상 소요**: 0.2일

- [ ] 노트북에서 자동 평가 코드:
  ```python
  go_criteria = {
      'A_sharpe_gt_0.8': stats_a['sharpe'] > 0.8,
      'B_sharpe_gt_0.5': stats_b['sharpe'] > 0.5,
      'mdd_lt_50': min(stats_a['mdd'], stats_b['mdd']) < 0.5,
      'positive_years': max(yearly_a_positive_count, yearly_b_positive_count) >= 2,
      'sensitivity_robust': sensitivity_a_robust or sensitivity_b_robust,
  }
  go = all(go_criteria.values())
  ```
- [ ] 결과 출력 (각 기준별 PASS/FAIL + 최종 Go/No-Go)
- [ ] 사용자 보고용 표 생성

### SubTask W1-06.4: 사용자 보고 + 승인

**작업자**: Solo + 사용자
**예상 소요**: 0.2일

- [ ] week1_report.md 사용자에게 전달
- [ ] 핵심 지표 요약 (한국어):
  ```
  ## Week 1 결과 요약
  
  ### 데이터
  - 일봉: 1932 bars, 갭 0%
  - 4h: 11648 bars, 갭 0.02%
  
  ### Strategy A 일봉 (사전 지정)
  - Sharpe: X.XX | MDD: XX% | 트레이드: N
  
  ### Strategy B 일봉 (사전 지정)
  - Sharpe: X.XX | MDD: XX% | 트레이드: N
  
  ### Go 기준 평가
  - [PASS/FAIL] A Sharpe > 0.8
  - [PASS/FAIL] B Sharpe > 0.5
  - [PASS/FAIL] MDD < 50%
  - [PASS/FAIL] 2+ 연도 양수
  - [PASS/FAIL] 민감도 평탄
  
  ### 권장: Go / No-Go
  
  진행하시겠습니까?
  ```
- [ ] 사용자 명시적 답변 대기 ("Go" / "No-Go" / "추가 분석 요청")

### SubTask W1-06.5: Evidence + 리뷰

**작업자**: Solo + backtest-reviewer
**예상 소요**: 0.1일

- [ ] `.evidence/w1-06-week1-report.txt` 작성
- [ ] backtest-reviewer 호출 (전체 Week 1 일관성 검증)
- [ ] APPROVED 받음
- [ ] sub-plan + execution-plan 상태 업데이트
- [ ] 사용자 결정 기록

## 인수 완료 조건 (Acceptance Criteria)

- [x] week1_report.md 생성
- [x] 모든 W1-* 결과 통합 (5개 노트북 출력)
- [x] Go 기준 5개 항목 자동 평가
- [x] 사전 지정 파라미터만 평가 (민감도 그리드 최고값 사용 X)
- [x] 4시간봉 결과는 "참고용" 라벨
- [x] 사용자 명시적 Go/No-Go 답변 받음 (No-Go, Option B, 2026-04-17)
- [x] backtest-reviewer APPROVED (BLOCKING-1 수정 후 재승인 기준 충족)
- [x] sub-plan + execution-plan status 업데이트
- [x] **No-Go 시 자동으로 라이브 진행 안 함** (Stage 1 킬 카운터 +1 기록)

## 의존성 매트릭스

| From | To | 관계 |
|------|-----|------|
| W1-02 | W1-06 | A 결과 |
| W1-03 | W1-06 | B 결과 |
| W1-04 | W1-06 | 강건성 결과 |
| W1-05 | W1-06 | 4h 참고 결과 |
| W1-06 (Go) | W2-01 | Week 2 진행 |
| W1-06 (No-Go) | (재검토) | 전략 패밀리 탐색 |

## 리스크 및 완화 전략

| 리스크 | 영향 | 완화 |
|--------|------|------|
| 결과 부풀리기 (그리드 최고값 사용) | High | 룰 강제 + reviewer 검증 |
| 사용자가 No-Go 거부 (감정적 결정) | Medium | 객관적 기준 표 제시, 결정 데이터 기반 |
| 한 기준만 약간 미달인데 Go 유혹 | Medium | "모두 충족" 룰 엄격 |
| 사용자 응답 없이 진행 | High | 명시적 승인 받기 전 W2 시작 금지 |

## 산출물 (Artifacts)

### 코드
- `research/notebooks/06_week1_report.ipynb`

### 결과
- `research/outputs/week1_report.md`
- `research/outputs/week1_summary.json` (자동 평가 결과)

### 검증
- `.evidence/w1-06-week1-report.txt`

### 테스트 시나리오

- **Happy**: 모든 Go 기준 충족 → 사용자 Go 승인 → W2-01 시작
- **Denial 1 (No-Go)**: 한 기준 이상 미달 → No-Go → 사용자 결정 대기
- **Denial 2 (사용자 추가 요청)**: 사용자가 "추가 분석 해줘" → 별도 노트북 생성, 다시 보고
- **Edge**: 4시간봉이 일봉보다 훨씬 좋게 나옴 → 그래도 일봉 기준 평가, 4h는 W2에서 walk-forward 검증

## Commit

```
docs(plan): Week 1 종합 리포트 + Go/No-Go 결정

Strategy A 일봉: Sharpe X.XX, MDD XX%
Strategy B 일봉: Sharpe X.XX, MDD XX%
4h 비교: 참고용 only

Go 기준 5개 평가:
- A Sharpe > 0.8: PASS/FAIL
- B Sharpe > 0.5: PASS/FAIL
- MDD < 50%: PASS/FAIL
- 2+ 연도 양수: PASS/FAIL
- 민감도 평탄: PASS/FAIL

결정: Go / No-Go
사용자 승인: 받음 (또는 대기)

Evidence: w1-06-week1-report.txt (APPROVED)
```

---

**이전 Task**: [W1-05 4시간봉 포팅 실험](./w1-05-4h-experiment.md)
**다음 Task**: 
- Go: W2-01 Walk-forward analysis (sub-plan은 W1-06 통과 후 작성)
- No-Go: 전략 패밀리 재검토 (별도 세션)
