# 세션 인수인계 문서 (2026-04-17/19/20 v13)

## handover 본문 박제 원칙 (2026-04-20 사용자 승인)

변동성 높은 정보는 handover 본문에 박제 금지. 재검증 라운드에서 stale 재발 원천 차단 목적.

**금지 대상 (다른 문서/tool에서 참조)**:
- **커밋 해시** — `git log main` 참조 (옵션 A 루프 차단)
- **잔존 정정 Task 개수/목록** — `docs/stage1-execution-plan.md` "잔존 정정 Task" 섹션 참조 (옵션 나 SSO 일관)
- **현재 상태 수치 (Sharpe, DSR 등)** — 관련 JSON/evidence 참조
- **버전 라벨 (sub-plan vN)** — 해당 sub-plan 파일 참조

**허용 대상 (handover 본문에 박제 가능)**:
- 의사결정 흐름 (사용자 발화 인용 포함)
- 검증 라운드 결과 요약
- 잔존 task의 trigger 설명 (개수/목록 X, 트리거 로직 O)
- 환경 현황 (Python/lib 버전 pip metadata)

> **v1** (오전): W1-06 시작 대기 시점.
> **v2** (오후, 커밋 `99b281d`): W1-06 완료 + Week 2 재범위 + W2-01 sub-plan 외부 감사 APPROVED 시점.
> **v3** (저녁): W2-01.1 페어 선정 기준 문서 v4 3회 감사 APPROVED + 사용자 승인 대기 시점.
> **v4** (저녁, 커밋 `5c1734c`): W2-01.1 기준 승인 완료 (06:25 UTC, "ㅇㅋ ㄱㄱ 해") + 섹션 6.1 freeze 발효 시점.
> **v5** (저녁, 커밋 `2e03ed1` + `b61fc9b`): W2-01.2 단계 1 실측 → ADA top10 밖 (14위) → Fallback (ii) 발동 → cycle 1 v4 사이클 중단 시점.
> **v6** (2026-04-19, 커밋 `cbef953` + `90eb74c` + `2aca62d`): cycle 2 v4 박제 + 사용자 승인 시점.
> **v7** (2026-04-19, 커밋 `84817b4`): cycle 2 W2-01.2 단계 2 + 단계 2-2 + W2-01.3 사용자 확정 리스트 승인 시점.
> **v8** (2026-04-19, 커밋 `0c2044a` + `9e3c3c9`): cycle 2 W2-01.4 데이터 수집 + W2-01.5/.6/.7 통합 완료 + backtest-reviewer APPROVED with follow-up. cycle 2 W2-01 전체 완료 시점.
> **v9** (2026-04-19, 커밋 `2e5624d`): W2-02 v5 사용자 승인 + /verify skill 신설.
> **v10** (2026-04-19, 커밋 `f2052e8`): W2-03 sub-plan v4 사용자 최종 승인 발효.
> **v11 (2026-04-19)**: W2-03.1 W-1 미니 테스트 완료 + 방법 B 사용자 채택. W2-03.0 진입 대기.
> **v12 (2026-04-20)**: **새 PC(riss) 이동 + venv 재생성 + W2-03.0 make_notebook_08.py 작성 + 노트북 빌드/실행 dry-run 검증 + 외부 감사관 페르소나 재검증 + sub-plan v6 정정 (B-1/C-1)**. venv 깨짐 발견 (`/usr/local/opt/python@3.11` ≠ 현 `/opt/homebrew`) → `brew install python@3.11` + venv 재생성 + `pip install -r requirements.lock` (Python 3.11.15, 박제 버전 vectorbt 0.28.5 + pyupbit 0.2.34 일치). **B-1**: vectorbt `Portfolio.from_signals`에 `year_freq` 파라미터 **실측 부재** (`inspect.signature` 확인), sub-plan L53/L98/L130 박제 정정 = `from_signals`에는 freq만, `pf.sharpe_ratio(year_freq='365 days')` 메서드 호출로 연율화. **C-1**: sub-plan L161-163 "V[SR_n] 둘 다 산출 + 비교" 박제 모호 → Go 기준 DSR = **V_reported = max(V_empirical, 1.0)** (Bailey 2014 conservative) 박제 명시화. **노트북 dry-run 결과**: 18셀 grid + DSR 정상 실행, conservative 기준 **is_go=False** (Go 통과 셀 0개, 모든 Primary DSR_z<0). V_empirical=0.1023 기준 결과는 투명 병기 (보고용, Go 기준 X). Secondary 마킹 A/C/D 모두. **W2-03.6 (Week 2 리포트 + backtest-reviewer + 사용자 Go/No-Go 결정) 대기**. 사용자 백과사전 memories/ 01~10 작성 완료 (2026-04-20) — gitignore 처리는 별도 결정.
> **v13 (이 문서, 2026-04-20)** — **커밋 trail은 `git log main` 참조 (v13 내부에 미래 해시 박제 금지 원칙 = 옵션 A 루프 차단, 2026-04-20 사용자 승인)**: **W2-03.6/.7 완료 + 사용자 Option C 명시 채택 + v7/v8 박제 + 2차 외부 감사 + Go 결정 + 검증 라운드 + 잔존 정정 커밋**. 흐름: W2-03.6 리포트/evidence 작성 → backtest-reviewer APPROVED with follow-up (WARNING 0 / NIT 5) → W2-03.7 외부 감사 1차 (WARNING 4: V_reported 수사 / v6 C-1 시간 trace / Option C 수사 억압 / Option B 근거 부재) → **사용자 중립 제시 (Option A/C/D)** → WARNING 4건 sub-plan v7 + 리포트 정정 → 내 Option C 추천 + 근거 제시 → **사용자 "ㄱㄱ" Option C 명시 채택 (2026-04-20)** → sub-plan v8 박제 (V_empirical 채택 + Strategy A Recall 발동) → 외부 감사 2차 (WARNING 4: 원문 복귀 overclaim / N=6 신뢰 한계 / Week 3 V 일관성 사전 박제 / Week 3 실패 소급) → v8에 2차 WARNING 4건 반영 → decisions-final "W2-03 Go 결정" 박제 + candidate-pool v5 Strategy A Active 전이 + execution-plan 상태 Done + 커밋 `512d92a` (8 files / +1096 lines). **v8 최종 Go 결정 수치 (V_empirical=0.1023, SR_0=0.4159)**: is_go=True, 5/6 Go cells (BTC_A/C/D, ETH_A/D / ETH_C FAIL). Strategy A Recall: Retained → Active. Stage 1 킬 카운터: +1 유지 (가산 X). **검증 라운드 후속 정정**: 사용자 명시 "니가 한게 아니라고 생각하고" 검증 요청 → 외부 감사관 재검증 → CRITICAL 1 (handover 미갱신) + WARNING 3 (L518 cross-ref / 2차 감사 WARNING 사용자 재승인 / memory 미갱신) + NIT 3 (추천 편향 / sqrt 일관성 / W3-01 라벨) 발견 → 사용자 "1 다 정정해" 선택 → 본 v13 작성 + L518 cross-ref + memory 작성 + sqrt task 박제 + W3-01 라벨 수정. **절차 약점 + 사후 승인 발효 박제** (decisions-final.md 동명 섹션과 cross-ref 동기화): 사용자 Option C 승인 ("ㄱㄱ") 이후 2차 감사 WARNING 4건 발견 시 사용자 재승인 없이 v8에 자동 반영 진행 = 절차 약점. 본 v13에서 사용자 검증 라운드 통과로 **사후 확인 발효**. **cycle 1 #5 재발 여부**: 2차 감사관 "v8과 본질 구분 어려움" 인정, **Week 3 결과가 retrospective 재판정**으로 박제. **잔존 정정 Task**: `docs/stage1-execution-plan.md` "잔존 정정 Task" 섹션 참조 (SSO 일관, handover 본문에 개수 중복 박제 금지 = 옵션 나 루프 차단 원칙, 2026-04-20 사용자 승인). **2차 재검증 라운드 추가 정정 (v13 본문 추가 정정)**: WARNING 3 (PT-03 마크다운 `|` 이스케이프 / handover 잔존 task 개수 불일치 2개 vs 3개 / "커밋 예정" stale) + NIT 3 (L522 "W-1 cross-ref" 셀프 레퍼런스 / memory 파일 2건 중복 / "사용자 사후 확인 박제" 섹션 제목 모호) 발견 → 사용자 "1 다 정정해" 선택 → v13 본문 정정 완료.

**3차 재검증 라운드 추가 정정 (v13 본문 추가 정정, 옵션 A 루프 차단 포함)**: WARNING 2 ("커밋 예정" stale 재발 / L522 "Bailey 원문 default" overclaim 경계 재발) + NIT 3 (L15 섹션 제목 cross-ref 미동기화 / PT-03 "필요 시 별도" 모호 / "본 v13 갱신" 용어) 발견. **근본 원인**: handover 본문에 미래 커밋 해시 박제 → 매 커밋 후 stale → 재검증 → 정정 → 재 stale 무한 루프. **옵션 A 채택**: 본 v13부터 미래 커밋 해시 박제 금지. 커밋 trail은 `git log main` 참조. 과거 해시도 필요 시 git log에서 확인.

**PT-01 해소 박제 (2026-04-20, 실측 반증)**: PT-01 = "W1 sqrt(252) vs W1-06 sqrt(365) 일관성 정정"으로 박제되어 있었으나 **오인 박제**로 확인. 실측: `vbt.settings.returns['year_freq'] = '365 days'` (vectorbt 0.28.5 공식 default, `vbt.__version__ == '0.28.5'`). `pf.sharpe_ratio()` default 호출 결과 = `pf.sharpe_ratio(year_freq='365 days')` 명시 호출 결과 bit-level 동일 (BTC_A -0.025300 vs BTC_A -0.025300, buy-and-hold 검증). `pf.sharpe_ratio(year_freq='252 days')` 명시해야 다른 값 (-0.021022 = 0.8304배 = 1/1.2035 = sqrt(252/365)). 따라서 **W1-02/03/04/06 노트북 모두 `pf.sharpe_ratio()` default 호출 = 이미 sqrt(365) 기반. W2-03과 100% 일관 (bit-level)**. strategy_a_daily.json BTC_A Sharpe 1.0353 ≡ W2-03 primary_grid BTC_A Sharpe 1.0353. 재계산 불필요. **사용자 선택 = 절충안** ("절충안 ㄱㄱ", 2026-04-20): 재계산 X + 박제 정정 O + 향후 벡터bt 업그레이드 또는 Freqtrade 이식 (W4+) 시점 `year_freq='365 days'` 명시 호출로 노트북 일괄 갱신 권고 박제. **오인의 근본 원인 = cycle 1 학습 #16 "외부 API 추측 금지" 재발**: handover #21 + W2-03 sub-plan v6 B-1 정정 당시 "vectorbt default year_freq='252 days'" 서술이 실측 없이 추측 기반으로 박제됨. W2-03 2차 외부 감사도 이를 잡지 못함 (감사관도 실측 안 함). memory `feedback_external_audit.md` + 신규 memory `feedback_api_empirical_verification.md` 보강 박제. 
## 현재 위치: 어디서 다시 시작하면 되나

**W2-03 전체 완료 (Go 결정, Option C = V_empirical 채택, 사용자 명시 승인 "ㄱㄱ" 2026-04-20). 검증 라운드 정정 누적 완료 (커밋 trail은 `git log main` 참조). PT-01 해소 (2026-04-20 실측 반증, W3-01 선행 차단 해제). 다음: W3-01 walk-forward sub-plan 작성 진입 대기. Strategy A/C/D 대상. V_empirical 일관 + floor 재도입 금지 + 임계값 변경 금지. 실패 시 Stage 1 킬 카운터 +2 소급. 잔존 정정 Task는 `stage1-execution-plan.md` "잔존 정정 Task" 섹션 참조 (SSO 일관).**

## 환경 현황 (riss PC, 2026-04-20)

- 경로: `/Users/riss/project/coin-bot` (이전 PC `kyounghwanlee` → 새 PC `riss`)
- venv: **재생성 완료**. `/Users/riss/project/coin-bot/research/.venv/bin/python` = Python 3.11.15 (`/opt/homebrew/opt/python@3.11` 기반 ARM Homebrew)
- 박제 버전 설치 확인: vectorbt 0.28.5, **pyupbit 0.2.34 (pip metadata 기준; `pyupbit.__version__` 속성은 0.2.33 stale — 패키지 유지보수 미흡이나 pip 설치 버전 0.2.34 기준 채택)**, ta 0.11.0 (pip metadata; `ta.__version__` 속성 부재, `pip show ta` 확인), pandas 2.3.3, numpy 2.3.5, scipy 1.17.1, nbformat 5.10.4 — **2026-04-20 PT-01 해소 외부 감사 WARNING-1 실측 확인**
- 글로벌 memory: `/Users/riss/.claude/projects/-Users-riss-project-coin-bot/memory/` = **빈 디렉토리** (이전 PC `-Users-kyounghwanlee-Desktop-coin-bot` 마이그레이션 안 됨)
- 프로젝트 내 memories/: 01~10 전체 작성 완료 (백과사전, 2026-04-20, 커밋 1588587). gitignore 처리 미결정

**W2-02 v5 사용자 승인 발효 사항** (2026-04-19 "ㄱㄱ"):
- Candidate C (Slow Momentum, MA50/200 + ATR×3 trail): Active/Registered
- Candidate D (Volatility Breakout, Keltner+Bollinger): Active/Registered
- 외부 감사 trace: 1차/2차/3차 (BLOCKING 6건 → 0, WARNING 5+1, NIT 4+1+2)
- ta KeltnerChannel API 호출 박제 (`original_version=False, window_atr=14, multiplier=1.5` 명시 필수)
- W-1 ATR trailing stop 미니 테스트는 W2-03 backtest-reviewer 책무
- W-2/W-3 (cycle 3 위험 인지): 박제 안 함 정직
- W3-1 ta 버전 재검증 책무 박제 (사이클 진입 시 venv signature 확인)

**W2-01.2 단계 2 결과** (`research/_tools/cycle2_tier2_decision.py` 실행, 외부 감사 APPROVED 후): top10 ∩ KRW ∩ BTC/ETH 제외 ∩ 스테이블 제외 → `[XRP, SOL, TRX, DOGE]`. 새 스테이블 발견 0건 (BNB/FIGR_HELOC false positive 사용자 직접 검증).

**W2-01.2 단계 2-2 결과** (`research/_tools/cycle2_tier2_validation.py` 실행, 자가 검증):
- KRW-XRP: 상장 2017-09-25, 거래대금 187.9억 (18.79x), PASS
- KRW-SOL: 상장 2021-10-15, 거래대금 41.1억 (4.11x), PASS
- KRW-TRX: 상장 2018-04-05, 거래대금 13.8억 (1.38x), PASS
- KRW-DOGE: 상장 2021-02-24, 거래대금 29.8억 (2.98x), PASS
- pyupbit 응답 필드 = `value` 사용 확인
- Common-window 시작일 = **2021-10-15 UTC** (SOL 기준)
- 100억 sanity 4.11x 초과 (사용자 결정: 100억 유지 완주, cycle 3 변경)
- 공지 cross-check 스킵 (사용자 결정: pyupbit 결과 신뢰)

**cycle 2 v4 박제 발효 사항** (2026-04-19, 사용자 위임 발화 "너가 결정해줘 모든걸"):
- `docs/pair-selection-criteria-week2-cycle2.md` v4 섹션 6.1 기준 freeze 발효
- `docs/decisions-final.md` "cycle 1 격리 양성 목록 박제" 동시 발효 (양성 목록 = ① Tier 2 리스트 추정 ② snapshot_utc 명목 시각, 그 외는 격리 비대상)
- `docs/decisions-final.md` "Fallback (ii) 누적 한도 박제 = 3회" 동시 발효 (cycle 1+2+3 = 최대 3회, 그 이후 W2-01 자체 폐기)
- cycle 2 사용자 승인 = 2026-04-19 사용자 위임 발화 시점 박제

**cycle 2 v4 핵심 변경 (cycle 1 v4 대비)**:
- 리스트 박제 제거 → 규칙만 박제 + 코드 자동 결정 (인간 추정 단계 제거)
- snapshot_utc 명목 시각 폐기 → fetched_at만 진실 시각 (CoinGecko historical 미제공 외부 제약 발견에 따른 정책 진화)
- cycle 1 snapshot JSON 재사용 (새 fetch 금지, cherry-pick 동기 차단)
- 임계값/측정 창/Tier 1/Fallback = cycle 1 그대로 유지 (soft contamination 인정)
- 새 차단 규칙 (vol/cap 등) 추가 안 함

**cycle 2 외부 감사 + 자가 검증 trace**: `.evidence/agent-reviews/w2-01-cycle2-pair-criteria-review-2026-04-18.md` (1차 + 2차 감사) + 자가 검증 9건 + 2차 감사 5건 + 16+ 라운드 자가 재검증 모두 박제 본문에 반영.

**단계 1 실측 결과 (단계 2~7 미실시)**:
- top10 = `[BTC, ETH, USDT, XRP, BNB, USDC, SOL, TRX, FIGR_HELOC, DOGE]`
- ADA 14위 (top10 밖)
- FIGR_HELOC = **Figure Heloc** (CoinGecko id `figure-heloc`, rank 9). HELOC = Home Equity Line of Credit. Figure (fintech 회사)의 RWA(Real-World Asset) 토큰. 24h 거래량 232억 KRW (시총 25.79조의 **0.09%** = 비율 0.0009, 사실상 정상 spot 거래 없음). 업비트 KRW 미상장 매우 유력 (단계 2 미실시로 미확정)
- snapshot **로컬 보존만** (gitignored, `.gitignore` L24 `research/data/` 룰): `research/data/coingecko_top30_snapshot_20260417.json` + SHA256 `c70a108905566f00f1b5b97fd3b08bf13be38d713f351027861d78869b3fcf59`. 명목 시각 `snapshot_utc=2026-04-17T00:00:00+00:00` 박제, 실제 `fetched_at=2026-04-17T07:08:56+00:00` 차이 약 7시간. CoinGecko 무료 API는 historical snapshot 미제공 → snapshot 재현 불가능. 새 사이클이 동일 명목 snapshot_utc를 그대로 채택하면 본 로컬 JSON 재사용 가능, 다른 명목 시각 채택 시 새 fetch 필요. **git tracked 여부는 새 사이클 설계 시 결정** (sub-plan W2-01.6 박제 "git tracked" vs `.gitignore` 룰 충돌은 별도 정정 작업으로 미정)

### 작업 history 박제 (v5 + v6 완료, 추가 미커밋 변경사항 없음)

**v5 시점 작업 (cycle 1 사이클 중단)** — 커밋 `2e03ed1` + `b61fc9b` 완료:
- `docs/pair-selection-criteria-week2.md` v4 헤더/섹션 5/섹션 7 사이클 중단 박제
- `docs/decisions-final.md` 새 섹션 "W2-01 v4 사이클 중단 (Fallback ii 발동, 2026-04-17)" 추가
- `.claude/handover-2026-04-17.md` v4 → v5 갱신
- snapshot JSON (`research/data/coingecko_top30_snapshot_20260417.json`) 로컬 보존만 (gitignored 유지, 옵션 B)

**v6 시점 작업 (cycle 2 v4 박제 + 사용자 승인)** — 커밋 `cbef953` 완료:
- `docs/pair-selection-criteria-week2-cycle2.md` v4 신설 (cycle 1 학습 반영, 1차 외부 감사 + 자가 검증 + 2차 외부 감사 + W2-1/W2-2 사용자 결정 + 16+ 라운드 자가 재검증)
- `docs/decisions-final.md` 박제 추가: "cycle 1 격리 양성 목록" + "Fallback (ii) 누적 한도 = 3회"
- `.evidence/agent-reviews/w2-01-cycle2-pair-criteria-review-2026-04-18.md` cycle 2 evidence trace (1차 + 2차 감사)
- `.claude/handover-2026-04-17.md` v5 → v6 갱신 (이 파일)
- 사용자 위임 발화 박제: 2026-04-19 "너가 결정해줘 모든걸"

**별도 처리 예정 (의도된 후처리)**:
- NIT2-3: sub-plan W2-01.2에 "Tier 2 결정 코드 외부 감사 절차" 박제 (cycle 2 W2-01.2 진입 직전)
- `.gitignore` 정정: W1-01 `data_hashes.txt` 한 번도 git 커밋 안 됨 + cycle 1 snapshot JSON gitignored = sub-plan 박제 vs 실제 git 상태 누적 괴리 (handover v6 #20 신규 버그 유형)

---

## 프로젝트 한 줄 요약

업비트 KRW-BTC 자동 매매 봇 학습 프로젝트. **Week 1 No-Go 완료 → cycle 1 v4 Fallback (ii) 사이클 중단 → cycle 2 v4 박제 발효 (2026-04-19, 사용자 위임 승인). cycle 2 W2-01.2 (단계 2: 업비트 KRW 페어 + 상장일 + 거래대금) 진행 대기.**

- 사용자: 자바 스프링 백엔드 개발자, 트레이딩/Python/크립토 도메인 신규
- 응답: **한국어**. 전문용어 풀이 필수
- 목표: **"안정적인 수익 구조"** (단기 PASS 아니라 검증된 엣지, `~/.claude/projects/.../memory/project_goal.md`)

---

## Week 1 최종 결과 (v2에서 유지)

Strategy A Conditional Pass (Sharpe 1.04, 2024 집중) / Strategy B No-Go (Sharpe 0.14, Deprecated). 커밋 `47e727d`. Strategy A 최근 481일 Sharpe -1.14 (2승 3패). 상세는 `research/outputs/week1_report.md`.

---

## Week 2 재범위 (v2에서 유지)

### 3-Task 재설계

| Task | 내용 | 일수 | 상태 |
|------|------|-----|------|
| **W2-01** 데이터 확장 + 페어 선정 | Tier 1 BTC+ETH, Tier 2 = [XRP,SOL,TRX,DOGE] | 2일+α | **cycle 2 전체 완료 (2026-04-19). 10 dataset Parquet freeze + backtest-reviewer APPROVED w/ follow-up. W2-02 진입** |
| **W2-02** 새 전략 후보 사전 등록 | Candidate C (Slow Momentum), D (Volatility Breakout) | 2일 | **v5 사용자 승인 발효 (2026-04-19). Strategy C/D Active/Registered. W2-03 진입** |
| **W2-03** In-sample 백테스트 grid + Week 2 리포트 | 6셀 primary + 12셀 exploratory, DSR 포함 | 2.5일 | **v4 사용자 승인 발효 (2026-04-19). 변경 금지 서약. W2-03.0 진입 대기** |

### Week 3로 이전

- W3-01 Walk-forward / W3-02 DSR + Bootstrap + MC / W3-03 전략 채택 결정

---

## W2-01.1 cycle 1 완료 상태 (v3 작성, v6 보존 — cycle 2 v4가 현행 진실 박제)

### 3회 외부 감사 trace

모든 감사는 `general-purpose` 에이전트에게 "적대적 팀장/이사급 외부 감사관" 페르소나로 위임. rubber-stamp 금지 명시.

| 회차 | 판정 | 발견 | 해소 후 상태 |
|------|------|------|-------------|
| 1차 (initial) | CHANGES REQUIRED | 4 BLOCKING + 7 WARNING + 5 NIT | 측정 창 off-by-one, Fallback 라벨 오기, Tier 2 선정 근거 공백, sanity check 자기모순 |
| 2차 (re-audit #1 on v2) | CHANGES REQUIRED | 1 BLOCKING + 4 WARNING | L77 freeze vs 교정 충돌(B-A), sub-plan 전파 누락, 백테스트 종료일 1일 오차 |
| 3차 (re-audit #2 on v3) | APPROVED with follow-up → NIT 해소 → **APPROVED** | 0 BLOCKING + 1 WARNING + 5 NIT | W-E 변경 이력 vs 본문 미세 불일치 / BNB·TRX carve-out / 체크박스 발효 주석 / SOL 추정 범위 / 오탈자 예외 / sub-plan 실측 필드 전파 |

감사 기록 파일: `.evidence/agent-reviews/w2-01-pair-criteria-review-2026-04-17.md` (3회 전부 기록)

### 핵심 설계 (박제 완료, v4)

| 항목 | 값 |
|------|-----|
| 시총 스냅샷 시각 | 2026-04-17 00:00 UTC |
| CoinGecko 엔드포인트 | `GET /coins/markets?vs_currency=krw&order=market_cap_desc&per_page=30&page=1` |
| 응답 개수 검증 | `len(response) == 30` assert 필수, 불일치 시 W2-01.2 중단 + 보고 |
| 스냅샷 저장 | `research/data/coingecko_top30_snapshot_20260417.json` + SHA256 |
| 상장 cutoff | **≤ 2023-04-17** (3년+) |
| 상장일 조회 | 업비트 공지 우선, 소실 시 `pyupbit.get_ohlcv_from(fromDatetime="2017-01-01", interval="day")` + `df.index.min()`, 최초 30캔들 7일 이상 갭 없음 sanity check |
| 거래대금 측정 창 | **2026-03-13 ~ 2026-04-11 UTC inclusive 정확히 30일** (W1 freeze 2026-04-12 직전) |
| 거래대금 산식 | **실측 필드 `value`/`candle_acc_trade_price` 우선** (W2-01.1 실행 시 pyupbit 응답 확인 후 확정), 부재 시 `close × volume` 근사 + evidence 기록 |
| 거래대금 임계값 | **≥ 100억 원**, sanity check ±30% 이원화: 이내 유지 / 초과 현 사이클 완주 후 새 사이클 |
| Tier 1 | {BTC (W1 재사용), ETH} = primary Go 대상 |
| Tier 2 | {XRP, SOL, ADA, DOGE} — 선정 규칙 = "시총 상위 10 ∩ 업비트 KRW ∩ BTC/ETH 제외", **실측 불일치 시 Fallback (ii) 사이클 중단** (cherry-pick 차단) |
| Tier 3 carve-out | SHIB, LINK (10위 바깥 추정), BNB (업비트 KRW 미상장 자동 탈락), TRX (10위 경계, 실측 10위 이내 시 Fallback (ii)), USDT/USDC (스테이블 제외) |
| 영구 제외 | PEPE (<3년, W2-01.2 실측 날짜 기록), 시총 >30위, 선물/파생 |
| Fallback (i) Tier 2 제거 | primary 6셀 **그대로 유지**, Tier 2 exploratory만 통과 수 × 3 전략으로 감소, Go 기준 변경 X |
| Fallback (ii) Task 재설계 | 새 W2-01 사이클, 기존 실측은 참고 자료 격리 |
| Common-window | Tier 1-2 중 상장 가장 늦은 페어 기준, W2-03 grid에서 페어별 max-span Sharpe (primary Go) + common-window Sharpe (secondary 비교) 둘 다 계산. 백테스트 종료일 = **2026-04-12 UTC** (측정 창 종료일 2026-04-11과 1일 차이는 의도) |
| 갭 처리 | forward-fill 금지 / 결측일 return=0 포지션 유지 / 3일 초과 갭 플래그 / 상장폐지 탈락 |
| 승인 2단계 | 기준 승인(W2-01.1 완료) → 섹션 6.1 기준 freeze 발효 / 확정 리스트 승인(W2-01.3 완료) → 섹션 6.2 확정 리스트 freeze 발효 |

### 실측으로만 최종 확정되는 가정 4가지 (사용자에게 투명하게 보고됨)

문서 결함이 아니라 **본질적으로 W2-01.2 실행 단계에서만 확정 가능**한 항목. 깨질 때의 경로는 이미 박제됨.

| 가정 | 깨질 때 경로 |
|------|-------------|
| 100억 임계값이 합리적 추정 | ±30% 초과 괴리 시 현 사이클 완주 후 새 사이클 |
| `value` 또는 `candle_acc_trade_price` 필드 존재 | 부재 시 `close × volume` 근사 + evidence 기록 |
| SOL/DOGE 상장일 ≤ 2023-04-17 | 초과 시 Tier 2 탈락 → Fallback (i) 또는 (ii) |
| 2026-04-17 실측 시총 10위 = {XRP, SOL, ADA, DOGE} | 불일치(예: TRX 진입) 시 Fallback (ii) 사이클 중단 |

---

## 다음 세션 시작 체크리스트 (v6, cycle 2 사용자 승인 후)

1. [ ] 이 handover 읽기 + `git status` 확인 + 마지막 커밋 메시지 확인
2. [ ] **cycle 2 W2-01.2 시작** (단계 2 = 업비트 KRW 페어 + 상장일 + 30일 거래대금 실측):
   - cycle 1 snapshot JSON 로드 + SHA256 무결성 재검증 (`c70a108905566f00f1b5b97fd3b08bf13be38d713f351027861d78869b3fcf59`)
   - 업비트 KRW 페어 목록 조회 (`pyupbit.get_tickers("KRW")`)
   - **Tier 2 결정 규칙 코드 자동 적용** (cycle 2 v4 L99-122 의사 코드 정확 구현):
     - top10에서 BTC/ETH 제외 + stablecoin_set 11개 제외 + 업비트 KRW 페어 존재 필터
     - 각 후보 상장일 ≤ 2023-04-17 검증
     - 각 후보 30 UTC-day 평균 거래대금 ≥ 100억 검증
   - **인간 개입으로 페어 추가/제거 절대 금지** (코드 산출 결과 = 최종)
   - **새 스테이블 토큰 (USDD/GUSD/USDQ 등 미포함) top10 진입 발견 시 사용자 보고** (단순 추가 금지, cycle 3 신규 박제 필요)
   - **pyupbit 일봉 응답 실측 필드 확인** (`value`/`candle_acc_trade_price`) → cycle 2 v4 L64 + sub-plan L65 갱신
3. [ ] cycle 2 W2-01.3 최종 후보 확정 + 페어별 행 분리 (Tier 2 0개 통과 시 'Fallback 발동' 표기) + 사용자 확정 리스트 승인 → cycle 2 v4 섹션 6.2 발효
4. [ ] cycle 2 W2-01.4~.7 `make_notebook_07.py` 작성 + 실행 + 무결성 검증 + SHA256 + evidence + backtest-reviewer APPROVED
5. [ ] **sub-plan 갱신** (NIT2-3 처리): cycle 2 v4 NIT2-3 = "Tier 2 결정 코드 작성 후 외부 감사관 호출 후 실행" 단계 sub-plan W2-01.2에 박제 추가
6. [ ] (선택) `git push origin main`

### cycle 1 (v4) 산출물 격리 처리 (v6 박제)

- cycle 1 v4 본문은 "참고 자료". primary Go 평가 반영 **절대 금지**.
- **격리 양성 목록 = ① Tier 2 리스트 추정 박제 ② snapshot_utc 명목 시각 박제** (decisions-final.md 박제 진실값. 사이클 작성자 자가 분할 통로 차단)
- 그 외 cycle 1 결정 (임계값 100억, 측정 창, Tier 1, Fallback (i)/(ii), Common-window, 갭 처리, 승인 2단계, 다중 검정 한계 등) = **격리 비대상**, cycle 2/3에서 채택 가능.
- snapshot JSON + SHA256은 cycle 2가 동일 명목 시각(2026-04-17) 채택했으므로 재사용 (gitignored, 옵션 B).

### Fallback (ii) 사이클 한도 (v6 박제)

- **누적 한도 = 3회** (cycle 1 + cycle 2 + cycle 3)
- 3회 누적 후 추가 발동 시: W2-01 자체 폐기 + Stage 1 킬 카운터 +1 + Week 2 재범위 결정 사용자 승인
- 박제 시점 = 2026-04-19 (cycle 3 결과 보고 한도 변경 차단, 시간적 미러)

---

## 코드베이스 구조 (v2에서 유지 + v3 추가)

```
research/
  _tools/
    make_notebook_0{1..6}.py   # nbformat 제너레이터 (Week 1)
    make_notebook_07.py        # W2-01.4에서 작성 예정
  notebooks/0{1..6}_*.ipynb    # 실행된 노트북 (git tracked)
  outputs/*.json, *.md, *.png, *.csv   # 결과 (gitignored)
  data/
    KRW-BTC_{1d,4h}_frozen_20260412.parquet   # W1 frozen (gitignored)
    data_hashes.txt                            # SHA256 해시 (git tracked)
    coingecko_top30_snapshot_20260417.json     # W2-01.2에서 저장 예정 (git tracked)
    upbit_listing_dates_20260417.json          # W2-01.2에서 저장 예정 (git tracked)
docs/
  stage1-execution-plan.md                     # EPIC (Week 2 재설계 반영)
  stage1-subplans/
    w1-0{1..6}-*.md                            # Week 1 완료
    w2-01-data-expansion.md                    # Week 2 W2-01 sub-plan (v3 전파 수정 완료)
  decisions-final.md                           # 모든 결정 (L555 Fallback 라벨 통일)
  pair-selection-criteria-week2.md             # W2-01.1 v4 APPROVED (신규)
  candidate-pool.md                            # Strategy 통합 관리 (Retained/Deprecated/Pending)
.evidence/
  w1-0{1..6}*.txt                              # Week 1 전체 APPROVED
  agent-reviews/
    w1-0{4..6}*-review.md                      # Week 1 리뷰 trace
    w2-01-preplan-review-2026-04-17.md         # W2-01 사전 감사 (APPROVED post-fix)
    w2-01-pair-criteria-review-2026-04-17.md   # W2-01.1 3회 감사 trace (APPROVED)
.claude/
  agents/backtest-reviewer.md                  # 리뷰어 체크리스트
  handover-2026-04-17.md                       # 이 파일 v3
CLAUDE.md                                      # 프로젝트 root 규칙
~/.claude/projects/-Users-kyounghwanlee-Desktop-coin-bot/memory/
  MEMORY.md + project_*.md + feedback_*.md
```

---

## 작업 패턴 (v2에서 유지)

### 노트북 생성 플로우

1. `research/_tools/make_notebook_0N.py` 작성 (nbformat)
2. `cd research && source .venv/bin/activate && python _tools/make_notebook_0N.py`
3. `jupyter nbconvert --to notebook --execute --inplace notebooks/0N_*.ipynb`
4. outputs 확인, evidence 작성, backtest-reviewer 호출

### 검증 패턴 (v3에서 강화)

- **커밋 전 외부 감사관 관점 재검증** (rubber-stamp 금지)
- **사전 계획(sub-plan) + 박제 문서(criteria)도 감사 대상** — v3에서 pair-criteria 문서 3회 감사 사례
- 리뷰어 에이전트 호출 → CHANGES REQUIRED 시 수정 → 재리뷰 (별도 agent call) → APPROVED 후에만 커밋
- **NIT까지 전부 해소 후 커밋** 권장 (팀장/이사급 책임 원칙, 후속 정정 남기지 않기)
- evidence 수치는 JSON 원본과 대조 (W1-06 "1승 4패" 오기재 재발 방지)
- **"추측 금지" 원칙**: 외부 API 필드명 등은 deferred verification으로 명시 (W2-01.1에서 pyupbit 응답 실측)

### 커밋 패턴

- 접두사: `feat(plan):` 새 Task 완료, `fix(plan):` 감사 지적 수정, `docs(plan):` 문서 재구성
- `research/outputs/`는 gitignored — `git add`에 포함 시 에러
- `git add`에서 특정 파일만 지정 권장

---

## 사용자 피드백 / 행동 패턴 (v2 + v3 추가)

1. **"검증부터 해야지 당연히"** — 모든 작업 후 검증 먼저. 검증 없이 다음 단계 금지.
2. **"남이 짠걸 검증한다는 생각으로"** — rubber-stamp 금지. 적대적 관점 필수.
3. **"왜 처음 검증할때 이걸 얘기안했어?"** — 리뷰 범위 좁게 잡으면 안 됨. 영향 문서 전체 점검.
4. **결정은 사용자에게** — Go/No-Go 자동 X. 근거 제시 후 승인 대기.
5. **한국어 응답** — 코드는 영어, 설명/보고는 한국어.
6. **"ㄱㄱ", "A rr", "추천 ㄱ"** — 간단한 승인 표현. 옵션 제시 시 **추천을 선호** (내 추천 명확히 제시 후 사용자가 OK/수정).
7. **목표 명확**: "안정적인 수익 구조" (memory/project_goal.md)
8. **뉴스 기반 예측 관심** — Phase 10+ 또는 별도 프로젝트 (memory/project_news_driven_roadmap.md)
9. **"1 2 3 4 차례대로"** — 다단계 진행 순서 유지, 각 단계 내 결정은 내 추천 허용 함축
10. **"너의 수정을 믿고 맡길게. 팀장/이사급이 돼서 확실하게 검증해"** (v3 신규) — 내가 판정을 내릴 때 책임지고 내림. 단 "APPROVED"라도 실측으로 깨질 수 있는 가정이 남아있으면 투명하게 보고 (사용자가 문서를 직접 안 읽어도 리스크를 알 수 있도록).
11. **"이상 없는 거야?" 재확인** (v3 신규) — APPROVED 판정 후에도 사용자가 재확인 요청 시, "문서 품질은 OK + 실측으로만 확정되는 가정들"을 정직하게 분리해서 답변. rubber-stamp 재검증.

---

## 과거 반복된 버그 유형 (v2 + v3 추가)

1. Evidence 수치 오기재 (W1-06 "1승 4패" 사건)
2. 문서 버전 라벨 미갱신
3. execution-plan 체크박스 미체크
4. backtest-reviewer 좁은 스코프
5. fillna() FutureWarning
6. research/outputs gitignore
7. 사전 지정 기준 측정 창 미정의 (W2-01 B-2)
8. Multiple testing 미보정 (W2-01 B-3 CRITICAL)
9. Soft contamination 간과 (W2-01 B-4)
10. Fallback "임계값 완화" (W2-01 B-5)
11. **측정 창 inclusive off-by-one** (v3 W2-01.1 1차 B-1): `2026-03-12 ~ 2026-04-11`이 31일임을 놓침. `python3 -c "(d2-d1).days + 1"`로 검증 필수
12. **Fallback 라벨 misnomer** (v3 W2-01.1 1차 B-2): "Tier 1 축소"인데 실제 primary 불변 → "Tier 2 제거"가 정답
13. **박제 문서 자기 freeze 시점 순환 정의** (v3 W2-01.1 2차 B-A): "승인 전 초안"인데 "변경 금지 서약" 활성화처럼 읽히는 문구. "승인 시점부터 발효" 조건 필수
14. **실측 cherry-pick 경로 재유입** (v3 W2-01.1 2차 B-A): "규칙 쪽으로 교정 허용"이 freeze와 충돌. "불일치 시 Fallback (ii) 사이클 중단"이 정답
15. **sub-plan/decisions-final 전파 누락** (v3 W2-01.1 2차 W-A): 본 문서만 수정하고 하위/상위 문서에 옛 라벨 잔존 → "한 곳만 진실" 원칙 위반
16. **외부 라이브러리 응답 필드 추측** (v3 W2-01.1 3차 W-E 예방): pyupbit 응답 `value` 단언 금지. "실측 필드 확인 후 확정" deferred verification 박제
17. **사전 지정 추정 리스트의 빗나감 위험** (v5 W2-01 cycle1 사례): "Tier 2 = {XRP,SOL,ADA,DOGE}" 추정 박제 → 단계 1 실측 결과 ADA 14위로 빠짐 → cherry-pick 차단 장치(L78, L117) 정상 발동 → Fallback (ii) 사이클 중단. **시스템은 의도대로 작동했음**. 다음 사이클 권고: "리스트 박제" 대신 "**규칙만 박제 + 코드 자동 채택**" 방식으로 추정 빗나감 위험 자체를 제거. 인간 개입 단계 (= cherry-pick 유혹 발생 지점)를 코드로 차단
18. **외부 코인 정체 추측** (v5 FIGR_HELOC 사례 예방): 상위 시총에 등장하는 미지 토큰을 "RWA 추정" 등 단언 금지. CoinGecko 응답의 `id`/`name` 필드를 직접 확인 후 박제 (단계 1 자가 검증에서 발견)
19. **수치 단위 표기 오류** (v5 FIGR_HELOC 비율 0.0009 vs 0.09% 사례): 비율과 % 표기 혼동 금지. 작은 비율을 % 변환 시 ×100 명시. 자가 검산 권장 (라운드 4 자가 검증에서 발견)
20. **sub-plan 박제 vs .gitignore 실제 룰 충돌** (v5 W1-01 + W2-01.2 누적 발견): W1-01부터 `data_hashes.txt` git tracked 박제됐으나 `.gitignore` `research/data/` 룰에 의해 한 번도 커밋 안 됨. CLAUDE.md Maintenance Policy "괴리 즉시 보고" 누적 위반. 별도 정정 작업 (`.gitignore` 예외 + sub-plan 정정 또는 산출물 위치 이동) 필요
21. **~~W1-06 sqrt(365) vs W1-04 sqrt(252) 일관성 깨짐~~** (v6 시점 박제 예정, **오인 박제**): W2-03 sub-plan v6 B-1 정정 당시 "vectorbt 0.28.5 default year_freq='252 days'"로 추측 박제 → 결과적으로 W1 노트북이 vectorbt default(= 추측된 252)를 쓴다고 믿어 "일관성 깨짐"으로 박제됨 → PT-01로 잔존 정정 task 생성 → **2026-04-20 PT-01 실행 단계 실측 반증**: `vbt.settings.returns['year_freq']` = `'365 days'` (vectorbt 0.28.5 공식 default) → W1/W2-03 모두 sqrt(365) 기반 bit-level 일치 → #21 자체가 오인. **해소 (PT-01 reclosed as no-op 박제)**. 실측 권고: `handover` 본문 박제 시 `vbt.settings.<section>` 실측 이후 박제
22. **외부 lib default 추측 박제** (cycle 1 학습 #16 누적 3회째 재발, W2-03 v9 PT-01 해소 시점 인지, 2026-04-20): (1) vectorbt `td_stop`/`ts_stop` 존재 추측 (초기 week1-plan.md), (2) vectorbt `Portfolio.from_signals`의 `year_freq` 파라미터 존재 추측 (W2-03 v6 B-1 `inspect.signature` 실측으로 정정), (3) **vectorbt default `year_freq`** 추측 박제 (`'252 days'` 추측 → 실측 `'365 days'`, PT-01 해소). 감사관도 실측 안 하면 간과 위험 (W2-03 2차 외부 감사 APPROVED 때 놓침). **대응**: memory `feedback_api_empirical_verification.md` 신설 + PT-05 "기계적 가드 hook 검토" 잔존 task 박제

---

## 파일 경로 빠른 참조

| 용도 | 경로 |
|------|------|
| 프로젝트 규칙 | `CLAUDE.md` |
| 리서치 규칙 | `research/CLAUDE.md` |
| 실행 계획 (EPIC) | `docs/stage1-execution-plan.md` |
| **W2-01 sub-plan** | `docs/stage1-subplans/w2-01-data-expansion.md` (v3 전파 수정 완료) |
| **W2-01.1 산출물 (APPROVED)** | `docs/pair-selection-criteria-week2.md` (v4) |
| Candidate Pool | `docs/candidate-pool.md` |
| 결정 문서 | `docs/decisions-final.md` (L555 Fallback 라벨 통일) |
| backtest-reviewer spec | `.claude/agents/backtest-reviewer.md` |
| W2-01 사전 감사 trace | `.evidence/agent-reviews/w2-01-preplan-review-2026-04-17.md` |
| **W2-01.1 3회 감사 trace** | `.evidence/agent-reviews/w2-01-pair-criteria-review-2026-04-17.md` |
| venv 활성화 | `cd research && source .venv/bin/activate` |
| 메모리 인덱스 | `~/.claude/projects/-Users-kyounghwanlee-Desktop-coin-bot/memory/MEMORY.md` |

---

## 세션 말미 상태 (v6)

- **W2-01.1 기준 승인 완료** + 커밋 (`5c1734c`, 2026-04-17 06:25 UTC) — cycle 1 사이클
- **W2-01.2 cycle 1 단계 1 실시 + cycle 1 Fallback (ii) 사이클 중단** + 커밋 (`2e03ed1` + `b61fc9b`, 2026-04-17 07:08 UTC)
- **cycle 2 v4 박제 + 사용자 승인** (2026-04-19, 사용자 위임 발화 "너가 결정해줘 모든걸"):
  - 1차 외부 감사 → CHANGES REQUIRED → v2 정정
  - 자가 추가 검증 5W+4NIT → v3 정정
  - 2차 외부 감사 → APPROVED with follow-up + W2-1/W2-2 사용자 결정 사항 발견
  - W2-1/W2-2 사용자 결정 (decisions-final.md 박제 채택 + 한도 3회) → v4 정정
  - 16+ 라운드 자가 재검증 + CRITICAL 1 + WARNING 1 + NIT 2 추가 발견 → 정정
  - 최종 자가 OK 판정 + 사용자 위임 시점 발효
- **decisions-final.md 박제 동시 발효** (2026-04-19):
  - "cycle 1 격리 양성 목록 박제" (양성 = 2개 한정)
  - "Fallback (ii) 누적 한도 박제 = 3회"
- **cycle 2 W2-01.2 진행 대기** (단계 2 = 업비트 KRW 페어 + 상장일 + 거래대금)
- Task #1 W2-01.1 = completed (cycle 1 + cycle 2 모두)
- Task #2~#7 (W2-01.2~.7) = pending (cycle 2)

### v6 자가 검증 기록 (16+ 라운드, 외부 감사관 관점)

- **라운드 1 적용 정확성**: ✓ (3건 정정 + 추가 1건 정정 모두 박제됨)
- **라운드 2 인용 일관성**: ✓ (cycle 2 v4 ↔ decisions-final.md 인용 정확)
- **라운드 3 시점 발효 논리**: 격리 양성 목록 박제 시점 명시 추가 (CRITICAL 정정) → ✓
- **라운드 4 cross-reference**: cycle 2 v4 L22 + L329 비대칭 정정 (NIT) → ✓
- **라운드 5 cycle 1 BLOCKING 7건 패턴**: 재발 X
- **라운드 6 1차 감사 5건 패턴**: 재발 X
- **라운드 7 자가 검증 9건 패턴**: 재발 X
- **라운드 8 2차 감사 5건 패턴**: 재발 X (NIT2-3는 sub-plan 갱신 시 처리 의도된 미룸)
- **라운드 9 새 정정 도입 약점**: 위 라운드 3, 4 정정 후 없음
- **라운드 10 자기 모순**: 변경 요약 표 헤더 v1 → v4 정정 (NIT) → ✓
- **라운드 11 누락 박제**: handover/sub-plan 갱신 = 의도된 후처리
- **라운드 12 메타 정책 일관성**: 격리/한도 박제 일관 ✓
- **라운드 13 의사 코드 정확성**: ✓ (2차 감사 + 직접 검증)
- **라운드 14 soft contamination 정직 보고**: ✓
- **라운드 15 외부 감사관 시각 종합**: BLOCKING 0, WARNING/NIT 모두 정정
- **라운드 16+ 추가 정정 후 OK 판정**: 자가 OK + 사용자 위임 발효
