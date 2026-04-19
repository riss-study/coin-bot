# W2-01 cycle 2 단계 2 — Tier 2 결정 코드 외부 감사 (2026-04-19)

**검증 대상**: `research/_tools/cycle2_tier2_decision.py`
**감사 트리거**: sub-plan W2-01.2 cycle 2 박제 NIT2-3 ("Tier 2 결정 코드 작성 후 외부 감사관 호출 후 실행")
**감사 페르소나**: 적대적 외부 감사관 (rubber-stamp 금지, "ChatGPT가 작성했다고 가정")
**박제 출처**:
- `docs/pair-selection-criteria-week2-cycle2.md` v4 (cycle 2 본 박제, 특히 L40-45/L97-127)
- `docs/decisions-final.md` "cycle 1 격리 양성 목록 박제" L593-604, "Fallback (ii) 누적 한도 박제" L606-611
- `docs/stage1-subplans/w2-01-data-expansion.md` L114-145 (cycle 2 시점 단계)

---

## 판정

**APPROVED with follow-up**

핵심 박제 요건(의사 코드 정확 일치, SHA256 무결성 재검증, stablecoin_set 11개, Tier 1 {BTC,ETH}, 인간 개입 통로 부재, 새 스테이블 안전판) 모두 충족됨을 직접 확인. 단, **실행 시 cwd 의존성** + **새 스테이블 안전판 휴리스틱의 일부 누락** + **출력 형식 가독성** 등 follow-up이 권장되는 항목이 있음. **BLOCKING 0건이므로 사용자에게 보고 후 실행 가능**, 다만 실행 명령은 `cd research`가 아니라 **프로젝트 루트에서 실행**해야 한다는 정정이 동반되어야 함.

---

## 발견 사항

### BLOCKING (0건)

박제 정합성, 안전성, 코드 정확성 측면에서 BLOCKING 수준 결함은 발견되지 않음.

### WARNING (3건)

- **W-1: 실행 cwd 의존성 + docstring 사용법 모순** (코드 L11, L30)
  - 코드 L30 `SNAPSHOT_PATH = Path("research/data/coingecko_top30_snapshot_20260417.json")` — **상대 경로**, cwd가 프로젝트 루트일 때만 동작
  - 그러나 코드 L11 docstring `cd research && source .venv/bin/activate ; python _tools/cycle2_tier2_decision.py` — **research/에서 실행**하라고 안내
  - cwd가 `research/`이면 `research/research/data/...`로 해석되어 L46 "snapshot 파일 없음" 에러로 cycle 2 즉시 중단됨 (= "잘못된" 중단, SHA256 박제 위반과 같은 부류로 오해 가능)
  - **수정 권고 (둘 중 택일)**:
    - (a) `SNAPSHOT_PATH = Path(__file__).resolve().parents[2] / "research" / "data" / "coingecko_top30_snapshot_20260417.json"`로 절대화 + docstring 그대로 둠
    - (b) docstring을 `cd <project root> && source research/.venv/bin/activate ; python research/_tools/cycle2_tier2_decision.py`로 정정
  - 박제 정합성에는 영향 없으나 실행 안정성/사용자 혼란 차단 측면 WARNING

- **W-2: 새 스테이블 안전판 휴리스틱이 cycle 2 v4 L123-127 박제 의도를 부분만 충족** (코드 L142-148)
  - cycle 2 v4 L123-124: "위 11개 외 새 스테이블 토큰이 top10에 진입한 경우 (예: 향후 등장하는 알고리즘 스테이블, USDD/GUSD/USDQ 등 미포함 토큰) → W2-01.2 코드 산출 결과에서 발견 시 즉시 사용자 보고"
  - 코드 L143-148이 채택한 휴리스틱: **`sym not in classified` AND `ticker not in upbit_krw_tickers`** = "분류되지 않았고 업비트 KRW 미상장인" 항목만 출력
  - 이 휴리스틱은 다음 케이스를 **놓칠 수 있음**:
    1. **업비트 KRW에 상장된** 신규 스테이블이 top10 진입 시 → `tier2`에 포함되어 `classified`에 들어가므로 위 if 조건 자체가 False → 안전판 출력 없음 = **사용자 보고 누락 위험**
    2. cycle 1 산출물의 `figr_heloc`(L9)는 미분류 + 업비트 KRW 미상장이므로 안전판 라인에 출력될 것 — 그러나 이는 스테이블 가능성보다는 "미상장 자산형 토큰" 케이스. 가짜 양성 발생.
  - **수정 권고**: 휴리스틱을 "가치 가까운 가격(예: $0.99~$1.01) + 분류 안 됨" 또는 "name/id에 'USD'/'stable' 부분 문자열 포함 + 분류 안 됨"로 보완하거나, 최소한 **분류 여부와 무관하게** top10 전체에서 잠재 스테이블 후보를 별도로 점검하는 패스를 추가
  - 박제 의도(인간 보고를 통한 cycle 3 신규 박제 강제)를 정확히 구현하려면 false negative 차단이 핵심
  - 단, 본 사이클(2026-04-17 snapshot)의 top10 stablecoin은 USDT/USDC 두 종 뿐이며 모두 박제 set에 포함되어 있어 **이번 실행 결과 자체에는 영향 없음** → WARNING 수준 (BLOCKING 아님)

- **W-3: `excluded`의 Tier 1 처리가 Tier 1을 "Tier 2 후보 제외" 사유로 표시** (코드 L79-86)
  - cycle 2 v4 L99-104 의사 코드는 단순히 `coin["symbol"].upper() not in {"BTC", "ETH"}` 필터만 명시 → BTC/ETH는 자연스럽게 Tier 2 후보에서 제외됨
  - 코드 L79-80: BTC/ETH가 top10에 있으면 `reasons`에 "Tier 1 (필수, 별도 처리)"가 추가되고 `excluded` 리스트에 들어감
  - 이는 **의사 코드의 결과 동등** (BTC/ETH가 `tier2`에 포함되지 않음) — 산출물은 정확히 같음
  - 그러나 출력 라벨로 "제외 사유"라고 표기하면 사용자가 "BTC/ETH가 Tier 2에서 떨어진 것"으로 오해할 여지. cycle 2 v4 L86-89 의도는 "Tier 1 = primary 필수, Tier 2 ≠ Tier 1"
  - **수정 권고**: 출력 섹션 라벨을 "top10 중 Tier 2 제외 사유"가 아니라 "top10 중 Tier 2 후보가 아닌 코인 사유 (Tier 1 필수 포함, 스테이블 제외, KRW 미상장)"로 정정하면 오해 차단
  - 박제 정확성 자체에는 영향 없으므로 WARNING

### NIT (4건)

- **NIT-1: Pylance/mypy 타입 힌트 미세** (코드 L59)
  - `tuple[list[str], list[tuple[str, list[str]]]]` 반환 타입 정확. Python 3.11+이므로 `from __future__ import annotations` (L20)가 있어 정상 동작. 문제 없음. 단지 가독성 측면에서 `NamedTuple`이나 `dataclass`로 분리하면 호출부 가독성 향상 가능. 채택 여부 작성자 재량.

- **NIT-2: 박제 인용 라인 번호 정확성 — `L40-45`로 표기되었으나 정확히는 `L40 표 + L45 행`** (코드 L29 주석)
  - cycle 2 v4 L40 = 표 헤더 행 (snapshot 시각), L45 = SHA256 행
  - 코드 주석 "박제 값 (cycle 2 v4 L40-45)"는 SNAPSHOT_PATH(L44)와 EXPECTED_SHA256(L45) 두 박제 값을 모두 포괄하므로 합리적인 범위 인용. 정정 강제 사항 아님

- **NIT-3: top10에 stablecoin이 포함되어 있어도 사용자 가시성을 위해 stablecoin_set 11개 적용 결과를 별도로 요약 표시 권장** (코드 L130-132)
  - 현재 출력: `USDT → 스테이블 제외`, `USDC → 스테이블 제외` 처럼 한 줄씩 나열됨 (이미 충분)
  - 추가 권장은 아니며 OK. 단지 수동 검토 시 "박제 set 어느 것이 매칭되었는지"를 보고 싶다면 reason에 매칭 토큰 자체를 포함하는 옵션이 있음. 채택 재량.

- **NIT-4: `print()` 출력만 있고 결과를 파일로 영속화하지 않음** (코드 L93-161)
  - cycle 2 v4 L139, sub-plan L139-140은 "Tier 2 후보 자동 산출"을 명시하나, 산출 결과를 evidence 또는 산출물 파일로 저장하라는 박제는 없음
  - 그러나 본 코드 실행 결과를 사용자가 cycle 2 v4 본문 섹션 5 "확정 리스트" 표에 옮겨 적어야 하는데, stdout 캡처가 없으면 재현 시 동일 결과 보장이 어려움
  - 수정 권고: 향후 W2-01.2 evidence 파일에 stdout 전체를 첨부하거나, 코드가 추가로 `outputs/cycle2_tier2_decision_result.json`을 쓰도록 확장. 박제 위반 아니므로 NIT.

---

## 박제 일치 검증 결과

### A. 의사 코드 정확 일치 (cycle 2 v4 L99-104) — **정확 일치**

cycle 2 v4 L99-111의 의사 코드 직접 확인:
```python
upbit_krw_tickers = pyupbit.get_tickers("KRW")  # ["KRW-XRP", "KRW-SOL", ...]
top10 = snapshot["data"][:10]
tier2_candidates = [
    coin for coin in top10
    if coin["symbol"].upper() not in {"BTC", "ETH"}
    and coin["symbol"].upper() not in stablecoin_set
    and f"KRW-{coin['symbol'].upper()}" in upbit_krw_tickers
]
```

검증 대상 코드 L71-90의 산출 동등성 검증:
- L71 `top10 = snapshot["data"][:10]` ↔ 박제 L105: 정확 일치
- L75-76 `for coin in top10: sym = coin["symbol"].upper()` ↔ 박제 L107 + symbol upper: 정확 일치
- L79 `if sym in TIER1_SET (= {BTC, ETH})` 필터 ↔ 박제 L108 `not in {"BTC", "ETH"}`: 동일 결과 (TIER1_SET = frozenset({"BTC","ETH"}), L34)
- L81 `if sym in STABLECOIN_SET` 필터 ↔ 박제 L109 `not in stablecoin_set`: 정확 일치
- L83 `if ticker not in upbit_krw_tickers` (ticker = `f"KRW-{sym}"`, L77) ↔ 박제 L110 `f"KRW-{coin['symbol'].upper()}" in upbit_krw_tickers`: 정확 일치
- L88 `tier2.append(sym)` (모든 reason이 비었을 때만) ↔ 박제 list comprehension: 산출물 동등

**추가/누락 조건 없음**. 의사 코드를 명령형 Python으로 정확히 변환했으며, 추가로 "왜 제외되었는지" reason trace를 더한 것은 박제 의사 코드가 제공하지 않는 정보를 더한 것이지만 산출물(`tier2_candidates`)은 동일.

### B. SHA256 무결성 재검증 (cycle 2 v4 L45) — **박제**

cycle 2 v4 L45 직접 확인: SHA256 = `c70a108905566f00f1b5b97fd3b08bf13be38d713f351027861d78869b3fcf59`, "불일치 시 cycle 2 중단".

검증 대상 코드 L31, L43-56:
- L31 `EXPECTED_SHA256 = "c70a108905566f00f1b5b97fd3b08bf13be38d713f351027861d78869b3fcf59"` — **박제값 정확 일치 (64자 hex 문자 단위 검증)**
- L48 `actual_sha = hashlib.sha256(SNAPSHOT_PATH.read_bytes()).hexdigest()` — 표준 라이브러리 정확 사용
- L49-54 불일치 시 `sys.exit(...)` 호출 + expected/actual 둘 다 출력 → cycle 2 중단 박제 충족
- L45-46 파일 부재 시도 별도 sys.exit으로 처리 (early fail)

박제 위반 없음.

### C. stablecoin_set 박제 (cycle 2 v4 L114-118) — **11개 정확**

cycle 2 v4 L116-120 직접 확인:
```python
stablecoin_set = {
    "USDT", "USDC", "USDS", "DAI", "USDE", "USD1", "PYUSD",
    "BUSD", "TUSD", "FRAX", "FDUSD"
}  # 사전 박제, 가치 고정 토큰 일반 목록 (2026-04-18 시점, 11개)
```

검증 대상 코드 L37-40:
```python
STABLECOIN_SET: frozenset[str] = frozenset({
    "USDT", "USDC", "USDS", "DAI", "USDE", "USD1", "PYUSD",
    "BUSD", "TUSD", "FRAX", "FDUSD",
})
```

요소 단위 대조 (11개 모두): USDT ✓, USDC ✓, USDS ✓, DAI ✓, USDE ✓, USD1 ✓, PYUSD ✓, BUSD ✓, TUSD ✓, FRAX ✓, FDUSD ✓.
**11개 정확. 누락/추가 없음**. `frozenset`로 immutable 보장 (Python 런타임 변형 통로 차단). L97 `len(STABLECOIN_SET)` 사용으로 11 출력 확인.

### D. Tier 1 박제 ({BTC, ETH}) — **정확 일치**

cycle 2 v4 L88-89 직접 확인: "Tier 1 (필수 포함): KRW-BTC + KRW-ETH"; v4 L108 의사 코드의 `not in {"BTC", "ETH"}` 박제.

검증 대상 코드 L34: `TIER1_SET: frozenset[str] = frozenset({"BTC", "ETH"})` — **정확 일치**. L127 출력에서도 `"Tier 1 (필수): BTC, ETH"`로 정확히 안내.

### E. 인간 개입 금지 (cycle 1 학습 박제, cycle 2 v4 L8/L84/L134-135) — **통로 부재 확인**

cycle 2 v4 L8 직접 확인: "리스트 사전 박제 제거 (가장 핵심): ... 인간이 결과를 본 뒤 리스트 변경 절대 금지"; L134-135: "결과를 본 뒤 Tier 2 후보 추가/제거 절대 금지. 코드 산출 결과 = 최종 (cherry-pick 차단)".

검증 대상 코드 전체 스캔:
- `input()`, `sys.stdin.read()`, `getpass`, `argparse` 등 사용자 입력 통로 — **부재**
- `tier2.append(...)`/`tier2.remove(...)`이 외부 입력 기반으로 호출되는 분기 — **부재** (L88에서만 호출, 조건은 박제 규칙)
- 환경 변수/CLI 플래그로 동작 변경하는 분기 — **부재**
- 결과를 출력 후 사용자 confirm 받고 다른 결과 산출하는 통로 — **부재**

L95 출력 레이블 "Tier 2 결정 (코드 자동 산출, 인간 개입 금지)" + L125-126 "(코드 자동 산출 = 최종)"로 의도도 명시.

**박제 의도 부합. 인간 개입 통로 발견되지 않음**.

### F. 새 스테이블 안전판 (cycle 2 v4 L123-127) — **부분 충족 (W-2 참조)**

cycle 2 v4 L123-127 직접 확인:
- "위 11개 외 새 스테이블 토큰이 top10에 진입한 경우 → 즉시 사용자 보고 후 결정"
- "단순 추가 금지 (cycle 1 학습: 결과 보고 규칙 변경 = cherry-pick)"
- "추가는 cycle 3 신규 박제 필요"

검증 대상 코드 L135-148:
- L139-140: "박제 stablecoin_set 외 가치 고정 토큰이 top10에 진입했는지 검토 필요" + "발견 시: 즉시 사용자 보고 + cycle 3 신규 박제 (단순 추가 금지)" — **박제 어조 정확 인용**
- L143-148: 휴리스틱 = `sym not in classified AND ticker not in upbit_krw_tickers` — 이는 박제의 "스테이블 토큰" 검출과 정확히 매핑되지 않음 (W-2)

박제 출력 어조는 정확하나, 검출 로직이 false negative를 허용함. 이번 cycle 2 snapshot의 top10에는 박제 set 외 스테이블이 없으므로 실행 결과에는 영향 없음. WARNING 수준.

### G. 외부 라이브러리 호출 정확성 — **정확**

`pyupbit.get_tickers("KRW")` 정확성 검증 — 직접 venv 소스 확인:
- `/research/.venv/lib/python3.11/site-packages/pyupbit/quotation_api.py:15` 시그니처 = `def get_tickers(fiat="", is_details=False, limit_info=False, verbose=False)`
- 본 코드 호출 (L117) `pyupbit.get_tickers("KRW")` → fiat="KRW", 나머지 default. L33-35에서 `[x['market'] for x in markets if x['market'].startswith(fiat)]` 반환 = `["KRW-BTC", "KRW-ETH", ...]` 형태
- 박제 L104 주석 `# ["KRW-XRP", "KRW-SOL", ...]` 와 일치
- **정확 호출**

`json.loads(SNAPSHOT_PATH.read_text())` (L56): 표준 사용. L43에서 `read_bytes()`로 SHA256 계산 후 동일 파일을 `read_text()`로 다시 읽음 — 두 번 읽기지만 정확성 위해 의도적이며 부작용 없음.

`hashlib.sha256(...).hexdigest()` (L48): 표준 사용.

import 누락 검사 — L22-27: `hashlib`, `json`, `sys`, `pathlib.Path`, `pyupbit` 모두 사용처 존재. 누락 없음.

### H. 안전성 — **안전**

- **파일 쓰기**: 본 코드는 `read_bytes`/`read_text`만 호출. **`open(..., "w")` / `Path.write_*` 등 쓰기 작업 부재**. 부작용 없음.
- **외부 API 호출**: `pyupbit.get_tickers("KRW")` 1회 (L117). 업비트 공개 API, 인증 불필요, 무료. rate limit 영향 미미 (단발 호출).
- **실행 실패 시 상태 일관성**:
  - 파일 부재 → `sys.exit` (L46): 부작용 없이 종료
  - SHA256 불일치 → `sys.exit` (L50): 부작용 없이 종료
  - pyupbit 호출 실패 (네트워크 에러) → 미캐치 예외로 즉시 traceback. 부분 결과 저장 없음 (애초에 저장 코드 없음). 사용자가 재실행하면 동일하게 무결성 검증부터 다시 시작.
- 멱등성: 동일 입력(snapshot JSON 동일 SHA + 동일 업비트 KRW 페어 응답) 시 동일 출력. snapshot SHA는 박제, 업비트 페어는 새 코인 상장 외 변동 없음 → 단기 멱등.

### I. 박제 일관성 — **정확 인용**

코드 docstring/주석의 cycle 2 v4 라인 인용 검증:
- L4 "cycle 2 v4 L99-122 의사 코드 정확 구현" — cycle 2 v4 본문 L99-122 = 의사 코드 코드 블록 + stablecoin_set 박제 + 안전판 일부 → **정확 (포괄 인용)**
- L29 "박제 값 (cycle 2 v4 L40-45)" — L40 (snapshot 시각 행) ~ L45 (SHA256 행) → SNAPSHOT_PATH(L44) + EXPECTED_SHA256(L45) 박제 출처 → **정확 (포괄 인용)**
- L33 "박제 값 (cycle 2 v4 Tier 1)" — Tier 1 섹션 L86-93 → **정확 (포괄 인용)**
- L36 "박제 값 (cycle 2 v4 L114-118 stablecoin_set, 11개)" — cycle 2 v4 L116-120 (코드 블록 본문) ↔ 코드는 L114-118로 인용. **1-2행 오차 (포괄 인용 범위 내)**. NIT 수준.
- L60 "cycle 2 v4 L99-104 의사 코드 정확 구현" — L99-104 = 의사 코드 첫 4행 (필터 핵심부) → **정확**
- L135 "cycle 2 v4 L123-127" — cycle 2 v4 L123-127 = 안전판 박제 → **정확**

전반적으로 인용 정확. NIT 수준의 1-2행 범위 오차 외 박제 위반 없음.

---

## 종합 평가

**코드 품질**: 박제 의사 코드의 정확한 명령형 구현. `frozenset` 사용 + 별도 함수 분리(`load_snapshot_with_integrity_check`, `decide_tier2`) + tuple unpacking 반환 등 Python idiomatic 작성. 타입 힌트 일관. 표준 라이브러리만 의존 (pyupbit 외).

**cycle 2 박제 정신 준수**: 핵심 박제 6개 (의사 코드 / SHA256 / stablecoin_set 11개 / Tier 1 / 인간 개입 차단 / 새 스테이블 안전판) 중 5개 완전 충족, 1개(F. 안전판 검출 휴리스틱) 부분 충족. 본 사이클 snapshot 적용 시에는 100% 정확한 결과 산출 보장.

**실행 시 위험**:
- W-1 cwd 의존성 → 사용자가 docstring 그대로 실행 시 SHA256 검증 전 단계에서 "snapshot 파일 없음" 에러로 중단됨. **혼란 가능. 즉시 정정 권장**.
- W-2 새 스테이블 안전판 false negative → 본 사이클에는 영향 없음. cycle 3 이후 향후 신규 스테이블 등장 시 재발 위험.
- W-3 출력 라벨 → 사용자 가독성 측면. 박제 정확성에는 영향 없음.
- 외부 API 호출은 단발 + 인증 불필요 + 부작용 없음. 안전.

**박제 위반 사항**: BLOCKING 수준 0건.

---

## 외부 감사관 의견

**APPROVED with follow-up**. 박제 핵심 요건은 충족되었으며 BLOCKING 결함이 없으므로 **사용자에게 본 감사 결과를 보고한 뒤 다음 절차로 진행 권고**:

1. **즉시 정정 (실행 전 권장)**:
   - W-1 cwd 의존성 정정 — `Path(__file__).resolve().parents[2] / "research" / "data" / "..."`로 절대화 또는 docstring 정정.
2. **권장 (실행 전 또는 직후)**:
   - W-2 새 스테이블 안전판 휴리스틱 강화 (가격 근사 + name/id substring 검사). 본 사이클에는 영향 없으므로 cycle 3 이전 정정도 가능.
   - W-3 출력 라벨 정정 ("Tier 2 제외 사유" → "Tier 2 후보가 아닌 코인 사유").
3. **실행 시점 권고**:
   - W-1 정정 후 사용자 명시적 실행 승인 받고, 산출 stdout 전체를 evidence (예: `.evidence/w2-01-cycle2-step2-tier2-decision-result-2026-04-19.txt`)로 저장. 코드 산출 결과 = 최종 (인간 변경 절대 금지, cycle 2 v4 L134-135 박제).
   - 새 스테이블 발견 시(=top10에 박제 set 외 가치 고정 토큰 진입) → **즉시 사용자 보고 + cycle 3 신규 박제** (cycle 2 v4 L123-127). 단순 추가 절대 금지.
   - 산출물 적용은 cycle 2 v4 섹션 5 "확정 리스트" 실측 표에 페어별 행 분리 기록 + sub-plan W2-01.2 체크박스 진행.

본 코드는 cycle 2 v4 박제의 핵심 정신("리스트 박제 제거 → 규칙만 박제 + 코드 자동 결정 → 인간 cherry-pick 통로 차단")을 정확히 구현했음을 외부 감사관으로서 확인함. follow-up 항목은 보강 차원이며, 박제 정합성 자체에 대한 부정은 아님.

---

## Evidence Trace

- 검증 대상 파일: `/Users/kyounghwanlee/Desktop/coin-bot/research/_tools/cycle2_tier2_decision.py` (165 lines, 2026-04-19)
- 박제 본문 직접 확인 (Read tool):
  - `/Users/kyounghwanlee/Desktop/coin-bot/docs/pair-selection-criteria-week2-cycle2.md` v4 (L1-334 전체)
  - `/Users/kyounghwanlee/Desktop/coin-bot/docs/stage1-subplans/w2-01-data-expansion.md` (L1-328 전체)
  - `/Users/kyounghwanlee/Desktop/coin-bot/docs/decisions-final.md` L590-611 (cycle 1 격리 + Fallback (ii) 한도)
  - `/Users/kyounghwanlee/Desktop/coin-bot/research/data/coingecko_top30_snapshot_20260417.json` (cycle 1 산출물, top30 데이터 직접 확인)
  - `/Users/kyounghwanlee/Desktop/coin-bot/research/.venv/lib/python3.11/site-packages/pyupbit/quotation_api.py` L15-40 (`get_tickers` 시그니처/반환값 직접 검증)
- 검증 항목 9개 (A~I) 모두 박제 본문 직접 인용 후 차이 분석
- 감사 작성자: Claude (외부 감사관 페르소나, rubber-stamp 금지 모드)
- 감사 일시: 2026-04-19
