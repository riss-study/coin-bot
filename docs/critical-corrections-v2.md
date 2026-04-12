# Critical Corrections v2 — CLAUDE.md 시스템 재검증

> 외부 감사관 재검증 결과. **Commit 불가 상태**.
> 핵심 발견: Day 0 수정사항이 실제로 적용 안 된 상태에서 CLAUDE.md를 마치 적용된 것처럼 작성함.

---

## 가장 큰 문제: SSoT 원칙 자체가 깨짐

CLAUDE.md를 만들면서 `day0-proposed-diffs.md`의 **승인 안 된 변경**을 사실로 가정하고 작성했습니다.

| 가정한 내용 (CLAUDE.md) | 실제 상태 (decisions-final.md) |
|--------------------------|----------------------------|
| Stage 1 (Week 8 페이퍼 2주 평가) | "Stage" 용어 자체 없음. 8주 킬은 DSR 기반 |
| Stage 2 (Week 12 라이브 게이트) | 12주 게이트 없음. 라이브는 4주 페이퍼 후 어디든 |
| 일일 손실 -2% 소프트 / -3% 하드 | -2% L2 청산 vs -3% 매매중단 모순 그대로 |
| Strategy A=1%, B=1% 통일 | A=1%, B=2% 그대로 (모순) |

**결과**: root CLAUDE.md L84-87이 가리키는 "단일 진실 문서"가 자기 모순 상태.

---

## 치명적: research/CLAUDE.md의 코드가 또 버그 (방금 수정한 것과 같은 클래스)

`week1-plan.md`의 5개 코드 버그를 "수정"하면서 만든 `research/CLAUDE.md`의 패턴 코드가 **여전히 작동 안 할 가능성** 발견:

### 9.7: pyupbit `to=` 파라미터
```python
pyupbit.get_ohlcv_from(
    ticker="KRW-BTC",
    interval="day",
    fromDatetime="2021-01-01",
    to="2026-04-12"  # ← pyupbit 공식 API에 to= 파라미터 없을 수 있음
)
```
- pyupbit 공식 시그니처 직접 확인 안 함
- 가능성: TypeError 또는 silent ignore

### 9.9: vectorbt `td_stop` 파라미터
```python
pf = vbt.Portfolio.from_signals(
    close=close,
    entries=entry,
    exits=exit_,
    sl_stop=0.08,
    ts_stop=...,
    td_stop=pd.Timedelta('5d'),  # ← vectorbt에 td_stop 파라미터 없을 수 있음
)
```
- vectorbt 실제 시간 스톱 파라미터는 `max_duration` 또는 다른 이름일 가능성
- **만약 td_stop이 없다면 Strategy B의 5일 시간 스톱은 여전히 미구현**
- 즉, **week1-plan 버그 #4 "수정됨"이 거짓**일 가능성

### 9.10: `freq='1d'` 대문자 문제
- vectorbt는 `'1D'` 요구할 수 있음
- pandas FutureWarning 또는 silent error

**이 3개는 실제 라이브러리 docs/소스 확인 없이 작성한 코드**. 외부 감사관 지적이 정확하면, week1-plan 버그를 "고친다"고 만든 코드가 새로운 같은 종류 버그.

---

## docs/CLAUDE.md가 자기 룰을 위반

L50: "이모지 사용 금지 (CLAUDE.md 시스템 정책)"

그러나 `decisions-final.md` (🎯, 📖, ✅), `day0-proposed-diffs.md` (📁, ✅, 🎬, 📖) 등 docs/* 안의 다른 문서들이 이모지 다수 사용. 룰 알면서 방치.

**선택**:
- (a) 룰 강화: docs/* 모든 파일 이모지 제거
- (b) 룰 완화: "CLAUDE.md 파일에만 이모지 금지"로 명확화

---

## architecture.md의 day0-proposed-diffs.md 수정사항이 0개 적용

CLAUDE.md가 architecture.md를 "authoritative system design"으로 가리키는데, 그 파일에는 여전히:

| 버그 | 위치 | 영향 |
|-----|------|------|
| `trades` FK가 `signals` 보다 먼저 정의 | architecture.md L230-247 | CREATE 실패 |
| `docker secrets external: true` | L463-471 | Swarm 모드 필요, 일반 compose 실패 |
| `cloudflared TUNNEL_TOKEN_FILE` | L453 | 미지원 환경변수 |
| 대시보드 → 업비트 직접 경로 | L315-319 | 보안 구멍 |

→ **사용자가 CLAUDE.md 따라가면 보안 구멍이 있는 설계로 안내됨**.

---

## Master Prompt 필수 섹션 누락

`AGENTS_md_Master_Prompt.md` L56-62는 nested 파일에 다음을 요구:
- Module Context ✓
- Tech Stack & Constraints
- Implementation Patterns
- Testing Strategy
- Local Golden Rules ✓

`docs/CLAUDE.md`에 누락:
- Tech Stack & Constraints (없음)
- Implementation Patterns (없음)
- Testing Strategy (없음)

`research/CLAUDE.md`는 필수 섹션 모두 포함 (다른 이름이지만 내용 있음).

---

## Operational Commands 6개 모두 현재 실행 불가

root CLAUDE.md L30-35:
```
source research/.venv/bin/activate    # .venv 없음
pip install -r research/requirements.txt  # 파일 없음
uv pip compile research/...            # uv 없음
cd research && jupyter lab             # jupyter 없음
git status && git diff                 # git init 안 됨
TaskList tool                          # 명령어 아님 (도구 이름)
```

자바 개발자가 그대로 복붙 → 6/6 실패. "Day 0 미적용 상태" 경고는 있지만 명령들은 그대로 실행 가능한 형태로 노출.

---

## 외부 감사관 자가 재검증 룰 격하

사용자가 명시적으로 반복 요구한 "외부 감사관 관점 자가 재검증"이 root CLAUDE.md L52에서 "Do's"(권장 수준)로만 표시. **Immutable**(절대 위반 금지)으로 격상해야 사용자 의도와 일치.

---

## glossary.md가 자기 광고와 다름

docs/CLAUDE.md L13: "모든 전문용어 풀이"

실제 누락:
- Donchian
- Walk-Forward
- Padysak/Vojtko
- Politis-Romano bootstrap
- CPCV
- Almgren-Chriss
- Wilder smoothing

이 용어들은 decisions-final/architecture/research에 등장. docs/CLAUDE.md L49 "풀이 없는 용어 금지" 자기 룰 위반.

---

## 내부 모순 상세

### Stage/Week/Phase 용어 soup

| 문서 | "Phase 10" 의미 |
|------|----------------|
| root CLAUDE.md L44 | "LLM 도입 시점" |
| decisions-final.md L108 | "LLM 5개 역할 추가" 시점 |
| architecture.md L24 | "Month 5+" 로드맵 슬롯 |

같은 단어, 다른 의미.

### docs/CLAUDE.md L9 vs L18 자체 모순
- L9 Active Documents에 `week1-plan.md` 포함
- L14 "(Day 0 수정 대기)" 표시
- 동시에 L18에서 `day0-proposed-diffs.md`를 "Pending"으로 분류
- → week1-plan은 Active인지 Pending인지 불명

---

## 누락된 룰 (가장 중요한 5개)

기존 발견 패턴인데 룰로 인코딩 안 됨:

1. **"결정 변경 시 decisions-final.md + 모든 연쇄 문서를 동시에 갱신, 누락 시 stale 경고"**
   - day0-proposed-diffs가 정확히 이 한계로 limbo 상태
2. **"논문 인용 시 arXiv ID + 직접 확인한 섹션/페이지 주석"**
   - arXiv:2410.12464 오독 사례 기반
3. **"외부 라이브러리 API 사용 시 공식 문서 직접 확인 후 코드 작성"**
   - vectorbt/pyupbit API 가정 코드 사례 기반
4. **"docker compose는 `docker compose config` 검증 통과 필수"**
   - external:true / TUNNEL_TOKEN_FILE 사례 기반
5. **"dashboard-backend는 거래소 API 키 접근 권한 없음 (물리적 분리)"**
   - T5 보안 구멍 사례. Immutable이어야 함

---

## 사용자가 결정해야 할 것

이 문제들을 어떻게 처리할지:

### 옵션 A: 제대로 순서 다시 잡기 (권장)

```
1. day0-proposed-diffs.md 실제 적용 (decisions-final, architecture, week1-plan 수정)
2. vectorbt + pyupbit API 실제 확인 (필요 시 wsearch agent 사용)
3. CLAUDE.md 3개 파일 SSoT 동기화 다시
4. nested CLAUDE.md 필수 섹션 보강
5. glossary 누락 용어 추가
6. operational commands 현재 상태로 축소
7. 다시 외부 감사
8. 그 후 git init + 첫 커밋
```

예상 시간: 2~3시간

### 옵션 B: CLAUDE.md를 현재 SSoT 상태(미수정 decisions-final)에 맞춰 되돌리기

```
1. CLAUDE.md에서 Stage 1/2 용어 제거
2. day0 미반영 상태로 일관되게 작성
3. day0 승인은 별도로 받기
4. 그 후 한꺼번에 day0 + CLAUDE.md 동기화
```

예상 시간: 30분

### 옵션 C: 그냥 진행

위 문제 다 알면서도 일단 commit. **권장 안 함** — Week 1 시작 시 즉시 깨짐.

---

## 솔직한 자기 비판

이번 audit에서 드러난 것:

1. **사용자가 명시적으로 요구한 "외부 감사관 자가 재검증"을 또 안 함.** CLAUDE.md 만든 직후 스스로 검증했어야 함. 사용자가 요청해서야 했음.

2. **vectorbt/pyupbit API를 직접 확인 안 하고 코드 작성.** week1-plan의 같은 종류 버그를 "고친다"면서 같은 패턴 반복.

3. **day0-proposed-diffs가 미승인 상태인 걸 알면서 그 내용을 사실처럼 CLAUDE.md에 인코딩.** 미래 결정을 현재로 끌어옴.

4. **"Active Documents"와 "Pending"을 자체 모순되게 분류.**

이 audit이 commit 이전에 잡혀서 다행. 사용자가 요청 안 했으면 commit 후에 깨졌을 것.

---

## 권장 결정

**Option A** (제대로 다시 하기). 30분 vs 2~3시간 차이지만, Option B는 같은 작업을 두 번 해야 함 (지금 되돌리고 → Day 0 후 또 다시).

승인 부탁드립니다:

- [ ] **A. 제대로 순서 다시 잡기 (권장)** — Day 0 적용 + API 확인 + CLAUDE.md 재작성
- [ ] B. CLAUDE.md만 일단 되돌리기 (Day 0 별도 작업)
- [ ] C. 그냥 진행 (비추천)

**A 선택 시 첫 단계**: vectorbt와 pyupbit의 실제 API를 web search agent로 확인 → 정확한 코드 패턴 확정 → 그 기반으로 모든 수정 진행.
