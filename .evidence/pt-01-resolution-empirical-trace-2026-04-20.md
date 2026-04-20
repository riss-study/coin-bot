# PT-01 해소 실측 Raw Trace — 2026-04-20

Task: PT-01 (W1 sqrt 일관성 정정) 해소
Feature: ENV-001 (환경 실측 검증)
Date: 2026-04-20
Status: Resolved (재계산 불필요, 오인 박제 반증)
Related audit: `.evidence/agent-reviews/pt-01-resolution-audit-2026-04-20.md` (APPROVED with follow-up)

---

## 1. 실측 환경

- venv: `/Users/riss/project/coin-bot/research/.venv/`
- Python: 3.11.15
- vectorbt: `0.28.5` (`pip show vectorbt` Version + `vbt.__version__` 양쪽 일치)
- pyupbit: `0.2.34` (`pip show pyupbit` Version) / `pyupbit.__version__` = `0.2.33` stale
- ta: `0.11.0` (`pip show ta` Version; `ta.__version__` 속성 부재)
- pandas: 2.3.3 / numpy: 2.3.5 / scipy: 1.17.1

---

## 2. 실측 명령 + Raw 출력

### 2.1 vectorbt default year_freq 설정 확인

```python
import vectorbt as vbt
from vectorbt import settings
print(dict(settings.returns))
print(vbt.__version__)
```

**출력**:

```
{'year_freq': '365 days', 'defaults': {'start_value': 0.0, 'window': 10, 'minp': None, 'ddof': 1, 'risk_free': 0.0, 'levy_alpha': 2.0, 'required_return': 0.0, 'cutoff': 0.05}, ...}
0.28.5
```

**결론**: vectorbt 0.28.5 공식 default `year_freq = '365 days'`. W2-03 v6 B-1 박제의 "vectorbt 0.28.5 default `year_freq='252 days'`" 서술은 **오인 박제 (추측 기반)**.

### 2.2 pf.sharpe_ratio() default vs 명시 호출 bit-level 비교

BTC-BTC daily 1927 bars, buy-and-hold with sl_stop=0.08.

```python
pf = vbt.Portfolio.from_signals(close=close, entries=entries, exits=exits,
    sl_stop=0.08, sl_trail=False, init_cash=1_000_000, fees=0.0005,
    slippage=0.0005, freq='1D')

sr_default = pf.sharpe_ratio()
sr_252 = pf.sharpe_ratio(year_freq='252 days')
sr_365 = pf.sharpe_ratio(year_freq='365 days')
```

**출력**:

```
sharpe_ratio() default: -0.025300
sharpe_ratio(year_freq='252 days'): -0.021022
sharpe_ratio(year_freq='365 days'): -0.025300
ratio 365/252: 1.2035001862952486
```

**수학 검증**: `sqrt(365/252) = sqrt(1.4484) = 1.2035001862952486` ✓ bit-level 일치.

**결론**: `pf.sharpe_ratio()` default = `pf.sharpe_ratio(year_freq='365 days')` 명시 호출과 **bit-level 동일**. 이는 vectorbt 0.28.5 default가 `'365 days'`임을 의미.

### 2.3 W1-02 JSON 저장 Sharpe의 실측 재현 (감사관 독립 재계산)

```python
# W1-02 strategy_a_daily.json 저장된 값: Sharpe = 1.0352900037639534
# 실측 재현: default 호출로 동일 파라미터 백테스트 → Sharpe 값 비교
import json
with open('outputs/strategy_a_daily.json') as f:
    saved = json.load(f)
saved_sharpe = saved['metrics']['sharpe']  # 1.0352900037639534

# 노트북 02와 동일 파라미터로 백테스트 재실행 (default 호출)
# 결과 Sharpe = 1.0352900037639534 (bit-level 동일, diff 0.00e+00)
# year_freq='365 days' 명시 호출도 동일
# year_freq='252 days' 명시 호출만 다름 (0.8602)
```

**결론**: W1-02 저장된 Sharpe는 sqrt(365) 기반. W2-03 BTC_A Sharpe와 **bit-level 일치** (1.0352900037639534 ≡ 1.0352900037639534).

---

## 3. pyupbit 버전 불일치 투명 기록

```
$ python3 -c "import pyupbit; print(pyupbit.__version__)"
0.2.33

$ pip show pyupbit | grep Version
Version: 0.2.34
```

- pip metadata 기준 설치 버전 = `0.2.34` (박제 값, 정확)
- `pyupbit.__version__` 속성 = `0.2.33` (패키지 내부 stale, pyupbit 유지보수 미흡)
- 실제 코드 동작은 0.2.34 기준 (pip 설치 버전 우선)

---

## 4. 오인 박제 반증 결론

| 박제 출처 | 내용 | 실측 결과 | 판정 |
|----------|------|-----------|------|
| handover #21 (v6 시점 박제 예정) | W1 sqrt(252) vs W1-06 sqrt(365) 일관성 깨짐 | W1 JSON Sharpe = sqrt(365) 기반 (bit-level 확인) | **오인 (반증)** |
| W2-03 sub-plan v6 B-1 | vectorbt 0.28.5 default `year_freq='252 days'` | 실측 default = `'365 days'` | **오인 (실측 반증)** |
| PT-01 잔존 정정 Task | W1 JSON Sharpe 재계산 필요 | 재계산 결과 bit-level 동일, 변화 없음 | **해소 (no-op)** |

---

## 5. 정정 박제

- `docs/stage1-execution-plan.md` PT-01 상태 = "해소 (2026-04-20 실측 반증)"
- `docs/stage1-subplans/w2-03-insample-grid.md` v9 변경 이력 행 + "SR annualization 박제" 정정
- `.claude/handover-2026-04-17.md` v13 본문 PT-01 해소 + #21/#22 박제
- memory `feedback_api_empirical_verification.md` 신설 (외부 lib API 실측 필수 원칙)
- PT-04 신설 (Freqtrade 이식 시점 `year_freq='365 days'` 명시 호출 일괄 갱신)
- PT-05 신설 (기계적 가드 hook 검토, cycle 1 #16 누적 3회째 재발 대응)

---

## 6. 학습 기록 (cycle 1 #16 누적 재발)

외부 lib default/파라미터 추측 박제 누적:

1. vectorbt `td_stop`/`ts_stop` 파라미터 존재 추측 (초기 week1-plan.md)
2. vectorbt `Portfolio.from_signals`의 `year_freq` 파라미터 존재 추측 (W2-03 v6 B-1 `inspect.signature` 실측 정정)
3. **vectorbt default `year_freq`** 추측 (`'252 days'` 추측 → 실측 `'365 days'`, 본 PT-01 해소)

**교훈**: 외부 lib default/파라미터 박제 전 반드시 실측 (`inspect.signature` + `settings` + 실제 호출 결과 비교). 감사관 호출 시 "API default는 실측 확인" 명시 지시 추가.

---

End of PT-01 empirical trace. Generated 2026-04-20 by claude-opus-4-7.
