# Stage 1 Week 2 — 재범위 (Week 1 No-Go 후, 2026-04-17 결정)

> 상위 계획: [`../stage1-execution-plan.md`](../stage1-execution-plan.md) (EPIC 뷰)
> Task 상세 sub-plan: [`../stage1-subplans/`](../stage1-subplans/)

## 배경

**원래 Week 2** (walk-forward/DSR 중심)는 Strategy A/B 확정 엣지 전제였으나 Week 1에서 엣지 확보 실패. Week 2를 **"전략 후보 재탐색 + 메이저 알트 확장"**으로 재설계. Walk-forward는 Week 3로 이전. DSR은 Week 2 Go 기준에 **부분 포함** (B-3 CRITICAL 이슈 해소).

## 요약

- **기간**: 2026-04-18 ~ 2026-04-20
- **결과**: **Go (Option C, V_empirical 채택)** — 사용자 명시 승인 "ㄱㄱ" (2026-04-20). W3-01 walk-forward 진입 대기.
- **Strategy A Recall**: 발동 (Retained → Active). Week 3 walk-forward 재검증 의무.

## Task 목록

- [x] **W2-01. 데이터 확장 + 페어 선정 사전 지정** (Feature: BT-003) — Done cycle 2 v5, 2026-04-19
  - 페어 선정 기준 사전 지정 (시총 상위, 상장 3년+, 유동성)
  - Tier 1 필수: BTC (W1 재사용), ETH
  - Tier 2 후보 (cycle 1 박제, **cycle 2 v5에서 ADA → TRX 정정** 2026-04-19): **XRP, SOL, TRX, DOGE**
  - 영구 제외: 상장 <3년 (PEPE), 시총 <50위
  - SHIB는 옵션 (밈 특성으로 Week 2 불포함, 추후 별도 실험 트랙 검토)
  - 5년 일봉/4h 데이터 수집 + SHA256 freeze + data_hashes.txt 갱신
  - Sub-plan: `../stage1-subplans/w2-01-data-expansion.md`
  - Depends: W1-06 (No-Go 결정 완료)
  - **상태**: cycle 1 v4 사이클 중단 (Fallback ii) → cycle 2 v5 완료 (2026-04-19, Tier 2 = [XRP, SOL, TRX, DOGE], Common-window = 2021-10-15 UTC)

- [x] **W2-02. 새 전략 후보 사전 등록** (Feature: STR-NEW-001) — Done v5 사용자 승인 발효, 2026-04-19
  - Candidate C: Slow Momentum (MA50/200 crossover + ATR(14)×3 trailing stop) - Moskowitz et al. 2012 시계열 모멘텀 기반
  - Candidate D: Volatility Breakout (Keltner Channel + Bollinger Band 동시 돌파)
  - (옵션) Candidate E: BTC/ETH 스프레드 차익거래 - 복잡도 높아 Week 4+로 이전 가능
  - 파라미터 freeze (BTC 데이터 보지 않고 문헌 근거로 결정)
  - Strategy A 파라미터는 **후보 풀에 보관** (W2-03 grid 포함)
  - Strategy B는 구조적 엣지 부재 확인으로 폐기 (grid 미포함)
  - Sub-plan: `../stage1-subplans/w2-02-strategy-candidates.md`
  - Depends: W2-01

- [x] **W2-03. In-sample 백테스트 grid + Week 2 리포트** (Feature: BT-005) — **Done Go 결정, 2026-04-20**
  - **Primary 대상 (Go 기준 적용)**: Tier 1 {BTC, ETH} × {A, C, D} = **6셀**
  - **Exploratory 대상 (참고용, Go 기여 X)**: Tier 2 {XRP, SOL, **TRX**, DOGE} × {A, C, D} = 12셀 (cycle 2 v5 박제 ADA → TRX 정정)
  - 사전 지정 파라미터 고정 (알트별 튜닝 금지, data snooping 금지)
  - 결과 표: Sharpe, MDD, PF, Trades + **DSR (Bailey & López de Prado 2014)** per primary cell
  - **Week 2 게이트 기준 (사전 지정, 다중 검정 보정 포함)**:
    - Primary: Primary 6셀 중 적어도 **1개 전략이 BTC 또는 ETH에서 Sharpe > 0.8 AND DSR > 0**
    - Secondary (마킹용, Go 기여 X): 동일 전략이 Tier 1+2 3+ 페어에서 Sharpe > 0.5 → ensemble 후보로 표시
    - 미달 → Stage 1 킬 카운터 +1, Week 3 재탐색
    - **"DSR > 0" V 선택 최종 박제**: V_empirical (Bailey 원문 sample variance). v6 C-1 `V_reported=max(V_empirical,1.0)` 도입 후 v8 복귀. 상세: `../decisions-final.md` "W2-03 In-sample grid Go 결정"
  - **다중 검정 한계 인정**: 6 primary 셀은 여전히 family-wise 오류 여지 있음. DSR은 이를 부분적으로 완화. 최종 엣지 검증은 Week 3 walk-forward에서 이뤄짐.
  - 사용자 명시적 Go/No-Go 승인
  - Sub-plan: `../stage1-subplans/w2-03-insample-grid.md` (v9)
  - Depends: W2-01, W2-02
  - **결과**: is_go=True, 5/6 Go cells (BTC_A/C/D, ETH_A/D / ETH_C FAIL). Strategy A Recall 발동 (Retained → Active). 외부 감사 2회 APPROVED with follow-up + PT-01 해소 (vectorbt default year_freq='365 days' 실측 반증)

## Week 2 결과 요약

- **Go 결정**: Option C (V_empirical 채택) — 사용자 명시 승인 "ㄱㄱ" 2026-04-20
- **Go cells (5/6)**:
  - BTC_A: Sharpe 1.0353, DSR_z +23.22
  - BTC_C: Sharpe 0.9380, DSR_z +18.12
  - BTC_D: Sharpe 1.1818, DSR_z +27.27
  - ETH_A: Sharpe 1.1445, DSR_z +29.37
  - ETH_D: Sharpe 1.0928, DSR_z +22.71
- **FAIL**: ETH_C (Sharpe 0.3237 < 0.8)
- **Strategy A Recall**: Retained → Active (BTC_A + ETH_A Tier 1 양 페어 충족)
- **Stage 1 킬 카운터**: +1 유지 (가산 X, W1 종료 시점 값)
- **Secondary 마킹** (Go 기여 X, Week 3 ensemble 후보): A[BTC,ETH,SOL,DOGE] / C[BTC,XRP,SOL] / D[BTC,ETH,SOL,TRX,DOGE]

## Week 3 진입 의무

- V_empirical 일관 적용 (fold별 sample variance 산출)
- Floor 재도입 금지 (v6 C-1 복귀 X)
- 임계값 변경 금지 (Sharpe > 0.8, DSR_z > 0 고정)
- Fold별 DSR 재산정 의무
- 실패 시 Stage 1 킬 카운터 +2 소급 (W2-03 Go 결정을 사후에 "실패"로 재분류)

자세한 의사결정 근거 + 외부 감사 2회 trace + cycle 1 #5 재발 판단: `docs/decisions-final.md` "W2-03 In-sample grid Go 결정" 섹션 + `.evidence/agent-reviews/w2-03-*-review-2026-04-20.md` 참조.
