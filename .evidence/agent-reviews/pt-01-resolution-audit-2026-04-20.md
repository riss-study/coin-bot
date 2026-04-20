# PT-01 해소 외부 감사 — 2026-04-20

감사관: 적대적 외부 감사관 페르소나 (rubber-stamp 금지)
감사 대상: W2-03 v9 + handover v13 + stage1-execution-plan.md PT-01 해소 박제 + memory feedback_api_empirical_verification.md 신규 + feedback_external_audit.md 보강
감사 trigger: 사용자 명시 "PT-01 해소 + 절충안 채택" 박제 직후 검증 라운드
감사 방식: 실측 재현 (venv python vectorbt 0.28.5) + 독립 재계산 + cross-document cherry-pick 스캔

---

## 감사관 태도 요약

rubber-stamp 거부. 실측 재현 결과 박제 수치는 **정확**(5개 관점에서 bit-level 확인). 그러나 절차적/프레이밍 결함 WARNING 3건 존재 + 잔존 추측 박제 가능 lib 2건 식별. APPROVED with follow-up.

---

## 독립 재계산 결과 (scipy + vectorbt 실측 재현)

### 1. vbt.settings 실측

```
vectorbt version: 0.28.5
vbt.settings.returns['year_freq'] = '365 days'  (공식 default)
type: <class 'str'>
```

v9/v13/execution-plan 박제 "default = '365 days'" **정확**.

### 2. 합성 데이터 Sharpe bit-level 동일성

```
default:           0.4534786797
explicit 365 days: 0.4534786797   ← default와 bit-level 동일 (==, not approx)
explicit 252 days: 0.3767998417
ratio 252/365 = 0.830910 = sqrt(252/365)
```

v9/v13 박제 "default == explicit 365 bit-level 동일" **정확**.

### 3. W1-02 Strategy A JSON 독립 재계산 (KRW-BTC 실데이터 1927 bars)

| 항목 | 값 |
|------|-----|
| JSON 저장 Sharpe (strategy_a_daily.json L28) | 1.0352900037639534 |
| 독립 재계산 `pf.sharpe_ratio()` default | 1.0352900037639534 |
| 독립 재계산 `pf.sharpe_ratio(year_freq='365 days')` | 1.0352900037639534 |
| 독립 재계산 `pf.sharpe_ratio(year_freq='252 days')` | 0.8602325247251528 |
| JSON total_return vs 재계산 | 1.71759325910457 == 1.71759325910457 |

**bit-level 일치 (abs diff = 0.00e+00)**. W1-02는 default 호출로 sqrt(365) 기반 저장됨 독립 확인.

### 4. W1-03 Strategy B JSON 독립 재계산

```
JSON 저장: 0.13615418374262483
재계산 default: 0.13615418374262483
abs diff: 0.00e+00
```

### 5. W2-03 primary_grid BTC_A cross-reference

```
w2_03_primary_grid.json L62 "sharpe_max_span": 1.0352900037639534
strategy_a_daily.json L28 "sharpe": 1.0352900037639534
```

bit-level 일치. W1 ↔ W2-03 SR annualization 기준 동일 완전 입증.

### 결론

PT-01 "W1 sqrt(252) vs W1-06 sqrt(365) 일관성 깨짐" 박제는 **오인**. W1 모두 sqrt(365). 재계산 불필요 결정 **학술적으로 방어 가능** (수치 자체가 동일한데 재계산할 대상이 없음).

---

## BLOCKING (수정 필수)

없음.

근거: 박제된 실측 결과는 venv 재현 bit-level 동일. 수치 정확성에 문제 없음. 절차/프레이밍 이슈만 존재.

---

## WARNING (강력 권장)

### WARNING-1: pyupbit 설치 버전 vs 박제 버전 불일치

- 박제 (research/CLAUDE.md, handover v12 L29, decisions-final): `pyupbit 0.2.34`
- 실측 (venv `inspect.signature` + `pyupbit.__version__`): **`0.2.33`**
- 영향: API 시그니처 차이가 있을 수 있음 (특히 `fromDatetime` / `period` default / None 반환). 본 감사 범위 내에서는 `get_ohlcv_from` 시그니처에 `fromDatetime=None, to=None, period=0.1` 확인 — 박제와 일치하는 동작 범위. 그러나 **버전 박제 자체의 정확성 보장 안 됨**.
- PT-01 해소가 "외부 lib default 추측 금지"를 새 memory로 박제한 직후에, 동일 라이브러리군의 버전 숫자가 어긋남 = cycle 1 #16 재발 가능 리스크.
- 권장: 다음 커밋 또는 PT-04 신설 전 `pyupbit.__version__` 실측 결과로 박제 정정 또는 requirements.lock 갱신.

### WARNING-2: "절충안" 학술적 정당화 서술 누락

- v9 / handover v13 / execution-plan L256 모두 "사용자 절충안 채택"이라는 의사결정 박제만 있고, **왜 재계산 X가 학술적으로 방어 가능한지**의 독립 논증이 문서 내부에 자립적으로 존재하지 않음.
- 실제 방어 논증은 "default == explicit 365 bit-level 동일" 실측 1문장이지만, 이것이 "재계산 불필요"라는 학술적 결론과 어떻게 연결되는지 (= numerically identical 코드 경로를 명시 경로로 치환해도 출력 불변) 명시되지 않음.
- 독자가 6개월 후 재검토 시 "절충안"이라는 용어만 보고 편의적 결정으로 오해할 위험.
- 권장: v9 본문에 "재계산 불필요 논증" 1문단 추가 — "default path와 explicit path는 동일 벡터bt 내부 연산 경로 (`returns.py` `year_freq` resolution)를 사용하므로 bit-level 동일. 따라서 명시 호출로 교체해도 출력 불변이며 저장된 모든 W1/W2-03 Sharpe 수치는 이미 sqrt(365) 기반 유효".

### WARNING-3: "향후 W4+ 일괄 갱신" trigger 실행 가능성 부족

- execution-plan L256 / v9 L16 / handover v13 모두 "향후 벡터bt 업그레이드 또는 Freqtrade 이식 시점 (W4+)에 `year_freq='365 days'` 명시 호출로 노트북 일괄 갱신 권고"로 박제.
- 문제: (a) W4+가 도래했을 때 자동으로 이 권고를 환기시킬 메커니즘 없음. (b) "권고"이지 "의무"가 아님. (c) 담당 Task ID 미부여.
- 비교: PT-02 / PT-03는 execution-plan L252 "잔존 정정 Task"에 row로 박제됨. PT-01은 해소로 strikethrough되어 잔존 row에서 **빠짐** — 결과적으로 "W4+ 일괄 갱신"은 **아무 잔존 task 목록에도 없음**.
- 재발 루프 위험: 벡터bt 업그레이드 시 default가 바뀌어도 기존 노트북은 default 호출이므로 silent 숫자 변경. 테스트 없으면 감지 불가.
- 권장: execution-plan "잔존 정정 Task" 테이블에 신규 row PT-04 추가 — "W4+ 노트북 일괄 명시 호출 갱신 (trigger: Freqtrade 이식 sub-plan 작성 또는 vectorbt 0.29+ 업그레이드)". 담당 Task에 의무로 박제.

---

## NIT (개선 제안)

### NIT-1: 추측 박제 책임 소재 추적 "어디서 왔는지" 불명확

- feedback_api_empirical_verification.md 및 handover v13 L19 모두 "handover #21 + W2-03 v6 B-1 정정 당시 추측 기반 박제"로 기재.
- 그러나 "handover #21"이라는 참조 자체가 handover 본문 섹션 번호 또는 외부 감사 발견 번호 중 어느 것인지 **명시 없음** (실제로 본 감사 중 grep으로 확인: handover-2026-04-17.md 본문에 "#21"이 존재하지 않음. v8 2차 외부 감사의 WARNING 참조로 추정되지만 trace 링크 없음).
- 권장: `.evidence/agent-reviews/w2-03-v8-v-empirical-adoption-review-2026-04-20.md` 또는 유사 감사 trace 파일 경로를 직접 링크.

### NIT-2: cycle 1 #16 재발 인정 서술 정직성 - 충분

- v9 L16 "cycle 1 학습 #16 '외부 API 추측 금지' 재발 사례" 명시 박제됨.
- feedback_api_empirical_verification.md L22 "W2-03 v8 2차 외부 감사도 이 추측을 잡지 못함 = 감사관 자체도 실측 안 하면 간과 위험" 자기 비판 박제됨.
- 축소/회피 서술 없음. 정직한 인정으로 판정.
- NIT 수준 제안: feedback_external_audit.md L17에 동일 자기 비판이 중복 박제되어 있음. 두 파일의 관계 명시 필요 (feedback_external_audit.md L19 cross-link 존재 확인). OK.

### NIT-3: ta 라이브러리 `__version__` 부재

- `import ta; ta.__version__` → `AttributeError`. 박제는 `ta 0.11.0`.
- 실측 방법 제약 (ta는 `__version__` 제공 안 함) — 박제 검증은 `pip show ta` 등 별도 수단 필요.
- 본 감사에서는 KeltnerChannel `original_version=True, multiplier=2` default 실측 확인 (candidate-pool.md "default와 다름, 명시 필수" 박제 정확).
- 권장: `feedback_api_empirical_verification.md`에 "lib별 `__version__` 제공 여부 편차 — ta는 없음. `pip show` fallback" 주석 추가.

### NIT-4: 실측 결과 evidence 파일 저장 위치 일관성

- PT-01 해소 실측 결과 raw trace는 v9 본문 1줄로만 박제됨. 별도 `.evidence/pt-01-resolution-evidence-2026-04-20.md` 또는 해당 노트북 셀 저장 없음 (본 감사 trace가 최초 독립 저장).
- 권장: 본 감사 파일 (`pt-01-resolution-audit-2026-04-20.md`)을 v9 / handover v13 / execution-plan L256에서 cross-link하여 재현 trace 위치 명시.

---

## 추측 박제 잔존 스캔 결과

감사 중 전체 docs/ 재스캔:

| 박제 대상 | 박제 위치 | 실측 결과 | 판정 |
|-----------|-----------|-----------|------|
| vectorbt 0.28.5 default `year_freq` | v6 B-1 (오인) → v9 정정 | `'365 days'` | 해소 |
| pyupbit 0.2.34 설치 | research/CLAUDE.md + handover | 실제 0.2.33 | **WARNING-1 (불일치)** |
| pyupbit `get_ohlcv_from` default period | week1-plan.md "기본 0.1, 0.2 권장" | `period=0.1` confirmed | 정확 |
| pyupbit `get_ohlcv_from` `fromDatetime` (camelCase) | w2-01-data-expansion.md | signature 확인 | 정확 |
| ta KeltnerChannel default `original_version`, `multiplier` | candidate-pool.md "default와 다름 명시 강제" | `original_version=True, multiplier=2` | 정확 |
| ta ATR/RSI Wilder 스무딩 | 여러 위치 | ta 소스 Wilder RMA 기본 (본 감사 범위 내 미실측, 관행적 확인 필요) | 미확인 |
| ta `__version__` = 0.11.0 | research/CLAUDE.md | ta 모듈 `__version__` attr 부재 | **NIT-3** |

잔존 미확인: ta Wilder 스무딩 내부 구현 (실측해도 무해하지만 본 감사 범위 외).

---

## 최종 verdict: APPROVED with follow-up

### 근거

- 실측 수치 정확성: 5개 관점 bit-level 일치 독립 확인 (합성 + 실데이터 W1-02 + W1-03 + W2-03 primary + default/explicit 동치성).
- PT-01 "오인 박제" 판정: **학술적으로 방어 가능**. default path == explicit path bit-level 동일이므로 "재계산 불필요" 결론 정당.
- 사용자 절충안 채택 결정: 감사관 관점에서 합리적. "재계산 없이 박제만 정정 + 미래 리팩터 권고"는 최소 침습적이며 증거 부담 없음.
- cycle 1 #16 재발 자기 비판 인정: 축소/회피 없음. feedback_api_empirical_verification.md + external_audit.md 두 memory 동시 보강으로 재발 방지 메커니즘 박제됨.
- 책임 소재 추적: v6 B-1 정정 시점 + handover #21 연결 (NIT-1 참조 불명확 잔존).

### Follow-up 필수

- WARNING-1 pyupbit 버전 불일치 → 별도 정정 (차기 커밋 권장).
- WARNING-2 "재계산 불필요 학술 논증" v9에 1문단 추가 → 재검토 시 오해 방지.
- WARNING-3 PT-04 "W4+ 일괄 명시 호출 갱신" 잔존 task 박제 → execution-plan "잔존 정정 Task" 테이블에 row 추가.

### Blocking 없음 근거

- 숫자 불변 (bit-level), 박제 정정은 서술 교정만, 사용자 명시 선택 ("절충안 ㄱㄱ") 존재, 자기 비판 memory 박제로 재발 방지, external_audit.md 감사관 플로우 강화.

---

## 감사관 개인 의견 (bias 명시)

### Bias

- 감사관 페르소나는 자가 invoke로 "적대적" 프롬프트 받음 → WARNING 과다 탐지 경향 bias 존재.
- PT-01 해소는 프로젝트 책임자(Claude + 사용자)가 직전 작업한 내용 → 감사 대상이 내부. 외부 3자 감사 대비 내부 방어 편향 보정 위해 실측 재현 5가지 수행.

### 개인 의견

1. "절충안"이라는 의사결정 용어가 **박제 문서에 등장하는 것은 이례적**. 보통은 "채택 근거"로 서술. 그러나 사용자 명시 언어 ("절충안 ㄱㄱ")를 그대로 박제한 것은 **투명성 측면에서 긍정적**.
2. cycle 1 #16 재발이 누적 3회 (vectorbt `td_stop`, `from_signals`의 `year_freq`, default `year_freq`) — 단순 "재발 사례" 박제 넘어 **시스템적 예방책** 필요. memory 박제로 끝내지 말고 skill 또는 hook으로 "외부 lib default 박제 시 `inspect.signature` 결과를 동일 문장 내 인용 강제" 같은 기계적 가드 검토 권장 (NIT 수준 권고, WARNING 아님).
3. W2-03 v6 B-1 정정 시 `inspect.signature(from_signals)`로 `year_freq` 없음은 확인했으나, **`sharpe_ratio` default 값까지는 확인 안 함**. 이것이 v9 반증의 근본 원인. 감사관 스스로도 "full default chain 실측" 원칙 추가 학습.
4. 실측 재현으로 W1 JSON 1.0353 = W2-03 JSON 1.0353 **bit-level 일치 독립 확인**은 이 감사의 핵심 가치. 만약 불일치가 나왔다면 "재계산 불필요" 결론이 REJECTED 되었을 것. 이 독립 재계산 없이 "default = 365" 실측만으로 APPROVED 했다면 감사 불충분.
5. 박제 품질: 정직. "오인 박제"를 명시적으로 인정하고 책임 소재 (v6 B-1 + handover #21) 추적. cycle 1 학습 #16 재발 인정. 서술 오류 교정 프로세스로 v9 박제된 것은 프로젝트 건강도 신호.

### 최종

감사관으로서 rubber-stamp 거부하되 "거부를 위한 거부"도 아니며, WARNING 3건 + NIT 4건 외에는 실측/서술 정확. **APPROVED with follow-up**.
