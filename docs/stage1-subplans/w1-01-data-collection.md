# Task W1-01 - 데이터 수집 + 환경 세팅

## 메인 Task 메타데이터

| 항목 | 값 |
|------|-----|
| **메인 Task ID** | W1-01 |
| **Feature ID** | DATA-001 |
| **주차** | Week 1 (Day 1) |
| **기간** | 1일 |
| **스토리 포인트** | 5 |
| **작업자** | Solo (Claude + 사용자) |
| **우선순위** | P0 |
| **상태** | Done |
| **Can Parallel** | NO (모든 후속 Task가 의존) |
| **Blocks** | W1-02, W1-03, W1-04, W1-05, W1-06, W2-* |
| **Blocked By** | none |

## 개요

업비트 KRW-BTC 5년치 일봉/4시간봉 데이터를 pyupbit로 다운로드하고, 타임존 처리 후 Parquet으로 freeze. SHA256 해시 기록으로 재현성 보장. Python venv + 의존성 잠금 + git init 까지 환경 세팅 완료.

## 현재 진행 상태

- 메인 Task 상태: Done
- 완료일: 2026-04-13
- Evidence: `.evidence/w1-01-data-collection.txt` (APPROVED, self-review)

| SubTask | 상태 | 메모 |
|---------|------|------|
| W1-01.1 | Done | venv 생성 (Python 3.11.4) |
| W1-01.2 | Done | requirements.txt + lock (142 packages) |
| W1-01.3 | Done | git commit f430a8d (Day 0 산출물 포함) |
| W1-01.4 | Done | 01_data_collection.ipynb 생성 (nbformat) |
| W1-01.5 | Done | 일봉 1927 bars + 4h 11563 bars 수집 |
| W1-01.6 | Done | KST→UTC localize + Parquet + SHA256 |
| W1-01.7 | Done | .evidence/w1-01-data-collection.txt 서명 |

## SubTask 목록

### SubTask W1-01.1: 프로젝트 디렉토리 + venv

**작업자**: Solo
**예상 소요**: 0.1일

- [ ] `research/` 하위에 `notebooks/`, `data/`, `outputs/` 생성
- [ ] `python3.11 -m venv research/.venv`
- [ ] `source research/.venv/bin/activate` 동작 확인
- [ ] Python 버전 확인 (`python --version` >= 3.11)

### SubTask W1-01.2: 의존성 + 잠금

**작업자**: Solo
**예상 소요**: 0.1일

- [ ] `research/requirements.txt` 작성:
  ```
  jupyterlab
  pandas>=2.0,<3.0
  numpy
  matplotlib
  seaborn
  pyupbit==0.2.34
  ccxt
  vectorbt==0.28.5
  ta
  pyarrow
  ```
- [ ] `pip install -r research/requirements.txt`
- [ ] `pip install uv`
- [ ] `cd research && uv pip compile requirements.txt -o requirements.lock`

### SubTask W1-01.3: git init + 첫 commit

**작업자**: Solo
**예상 소요**: 0.1일

- [ ] `cd /Users/kyounghwanlee/Desktop/coin-bot`
- [ ] `git init` (이미 있으면 skip)
- [ ] `.gitignore`에 `.venv/`, `data/`, `*.parquet`, `__pycache__/`, `.ipynb_checkpoints/`, `.env`, `secrets/` 포함 확인
- [ ] `.evidence/.gitkeep` 생성 (빈 디렉토리 git tracking용)
- [ ] `.claude/agents/.gitkeep` 생성 (필요 시)
- [ ] `git add .gitignore CLAUDE.md docs/ research/CLAUDE.md AGENTS_md_Master_Prompt.md .claude/ .evidence/.gitkeep`
- [ ] `git commit -m "Day 0: docs, CLAUDE.md system, methodology adoption"`

### SubTask W1-01.4: 노트북 01_data_collection.ipynb

**작업자**: Solo
**예상 소요**: 0.2일

- [ ] `research/notebooks/01_data_collection.ipynb` 생성
- [ ] 첫 셀: import (pyupbit, pandas, hashlib, time, pathlib)
- [ ] 함수 셀: `fetch_with_retry(ticker, interval, start, end, max_retries=5)` 정의
  - period=0.2 (안전 마진)
  - None 반환 시 지수 backoff 재시도
- [ ] 함수 셀: `check_gaps(df, freq)` 정의
- [ ] 함수 셀: `sha256_file(path)` 정의

### SubTask W1-01.5: 데이터 다운로드

**작업자**: Solo
**예상 소요**: 0.2일

- [ ] 일봉 다운로드: `fetch_with_retry("KRW-BTC", "day", "2021-01-01", "2026-04-12")`
- [ ] 4시간봉 다운로드: `fetch_with_retry("KRW-BTC", "minute240", "2021-01-01", "2026-04-12")`
- [ ] 두 DataFrame이 None 아님 확인
- [ ] 행 수 확인 (일봉 ~1930, 4h ~11600 예상)

### SubTask W1-01.6: 타임존 + freeze + 해시

**작업자**: Solo
**예상 소요**: 0.2일

- [ ] 두 DataFrame에 대해 `assert df.index.tz is None` (pyupbit 검증된 동작)
- [ ] `df.index = df.index.tz_localize('Asia/Seoul').tz_convert('UTC')`
- [ ] gap detection 실행 (일봉/4h)
- [ ] 갭 < 0.1% 확인
- [ ] Parquet 저장:
  - `data/KRW-BTC_1d_frozen_20260412.parquet`
  - `data/KRW-BTC_4h_frozen_20260412.parquet`
- [ ] SHA256 해시 계산 + `data/data_hashes.txt` 기록

### SubTask W1-01.7: Evidence 파일 + 마무리

**작업자**: Solo + backtest-reviewer 에이전트
**예상 소요**: 0.1일

- [ ] `.evidence/w1-01-data-collection.txt` 작성 (6단 구조)
- [ ] backtest-reviewer 에이전트 호출 (데이터 무결성 검증)
- [ ] APPROVED 확인
- [ ] sub-plan 메타데이터 상태 → Done
- [ ] execution-plan status 표 업데이트

## 인수 완료 조건 (Acceptance Criteria)

- [ ] Python 3.11+ venv 작동
- [ ] vectorbt 0.28.5, pyupbit 0.2.34 설치 + import 성공
- [ ] requirements.lock 생성
- [ ] git 첫 commit 완료 (Day 0 산출물 + 환경)
- [ ] 일봉 ~1930 bars 수집 (실제 행 수 기록)
- [ ] 4h ~11600 bars 수집
- [ ] 갭 < 0.1% (일봉, 4h 모두)
- [ ] 인덱스 timezone = UTC
- [ ] Parquet 파일 2개 생성
- [ ] data_hashes.txt 생성
- [ ] backtest-reviewer 에이전트 APPROVED

## 의존성 매트릭스

| From | To | 관계 |
|------|-----|------|
| (none) | W1-01 | 시작 Task |
| W1-01 | W1-02 | 일봉 데이터 필요 |
| W1-01 | W1-03 | 일봉 데이터 필요 |
| W1-01 | W1-05 | 4시간봉 데이터 필요 |

## 리스크 및 완화 전략

| 리스크 | 영향 | 완화 |
|--------|------|------|
| 업비트 API rate limit | Medium | period=0.2, 재시도 wrapper |
| pyupbit None 반환 | Medium | fetch_with_retry로 5회 재시도 |
| 5년치 데이터 부재 (페어 상장 늦음) | High | KRW-BTC는 2017.10 상장이므로 OK |
| 타임존 처리 누락 | High | assert로 강제 + research/CLAUDE.md 룰 |
| 갭 > 0.1% | Medium | 두 번째 소스(바이낸스)로 교차 검증 |

## 산출물 (Artifacts)

### 코드
- `research/notebooks/01_data_collection.ipynb`
- `research/requirements.txt`
- `research/requirements.lock`

### 데이터
- `research/data/KRW-BTC_1d_frozen_20260412.parquet`
- `research/data/KRW-BTC_4h_frozen_20260412.parquet`
- `research/data/data_hashes.txt`

### 검증
- `.evidence/w1-01-data-collection.txt`

### 테스트 시나리오

- **Happy**: 두 데이터셋 다운로드 → 타임존 localize → freeze → 해시 기록 → 검증 통과
- **Denial 1**: pyupbit None 반환 → 재시도 wrapper로 자동 복구
- **Denial 2**: 갭 > 0.1% → 두 번째 소스 교차 검증, 또는 사용자 보고
- **Edge**: 5년 시작 시점 (2021-01-01) 캔들 누락 가능성 → 시작일 다음 가용 캔들로 자동 조정

## Commit

```
feat(plan): DATA-001 Week 1 데이터 수집 + 환경 세팅 완료

- Python 3.11 venv + requirements.lock
- pyupbit KRW-BTC 일봉 1930 bars, 4h 11600 bars
- 타임존 KST → UTC 변환
- Parquet freeze + SHA256 해시 기록
- git 첫 commit (Day 0 산출물 포함)
- Evidence: w1-01-data-collection.txt
```

---

**이전 Task**: (none, 시작 Task)
**다음 Task**: [W1-02 Strategy A 일봉 백테스트](./w1-02-strategy-a-daily.md)
