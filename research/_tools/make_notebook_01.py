"""Create notebook 01_data_collection.ipynb programmatically.

Run with: python _tools/make_notebook_01.py
Output: notebooks/01_data_collection.ipynb
"""
import nbformat as nbf
from pathlib import Path

nb = nbf.v4.new_notebook()

cells = []

# Cell 1: Header
cells.append(nbf.v4.new_markdown_cell("""\
# Task W1-01 — 데이터 수집

**Feature ID**: DATA-001
**Sub-plan**: `docs/stage1-subplans/w1-01-data-collection.md`

업비트 KRW-BTC 5년치 일봉 + 4시간봉 다운로드. 타임존 localize (KST → UTC). Parquet freeze + SHA256 해시 기록.

## 검증된 API (Day 0)
- pyupbit 0.2.34: `get_ohlcv_from(ticker, interval, fromDatetime, to, period)`. `to=` 존재. 결과는 naive KST.
- 에러 시 None 반환 → 재시도 wrapper 필수.
- Upbit rate limit: 10 req/sec → `period=0.2` (안전 마진).
"""))

# Cell 2: Imports
cells.append(nbf.v4.new_code_cell("""\
import pyupbit
import pandas as pd
import numpy as np
import hashlib
import time
from pathlib import Path
from datetime import datetime, timezone

# 버전 검증
from importlib.metadata import version
print(f"pyupbit: {version('pyupbit')}")
print(f"pandas: {version('pandas')}")
"""))

# Cell 3: Helpers
cells.append(nbf.v4.new_code_cell("""\
def fetch_with_retry(ticker, interval, start, end, max_retries=5, period=0.2):
    \"\"\"pyupbit get_ohlcv_from with exponential backoff retry.

    검증된 pyupbit 0.2.34 API.
    반환: pd.DataFrame (naive KST index) or raise RuntimeError.
    \"\"\"
    for attempt in range(max_retries):
        df = pyupbit.get_ohlcv_from(
            ticker=ticker,
            interval=interval,
            fromDatetime=start,
            to=end,
            period=period,
        )
        if df is not None and not df.empty:
            return df
        wait = 2 ** attempt
        print(f"Attempt {attempt+1} returned None/empty. Sleeping {wait}s...")
        time.sleep(wait)
    raise RuntimeError(f"Failed to fetch {ticker} {interval} after {max_retries} retries")


# 주: check_gaps 범용 헬퍼는 Cell 7에서 inline으로 대체됨 (advertised 범위 기준).
# 후속 노트북에서 재사용 시 start 파라미터 명시 필수.


def sha256_file(path):
    \"\"\"Compute SHA256 hash of a file in chunks.\"\"\"
    h = hashlib.sha256()
    with open(path, 'rb') as f:
        for chunk in iter(lambda: f.read(65536), b''):
            h.update(chunk)
    return h.hexdigest()
"""))

# Cell 4: Download daily
cells.append(nbf.v4.new_code_cell("""\
FREEZE_DATE = "20260412"
START = "2021-01-01 00:00:00"
END = "2026-04-12 00:00:00"

print("Downloading KRW-BTC daily candles...")
df_daily = fetch_with_retry(
    ticker="KRW-BTC",
    interval="day",
    start=START,
    end=END,
    period=0.2,
)
print(f"Daily: {len(df_daily)} bars, first={df_daily.index[0]}, last={df_daily.index[-1]}")
df_daily.head()
"""))

# Cell 5: Download 4h
cells.append(nbf.v4.new_code_cell("""\
print("Downloading KRW-BTC 4h candles (may take ~30s for 5 years)...")
df_4h = fetch_with_retry(
    ticker="KRW-BTC",
    interval="minute240",
    start=START,
    end=END,
    period=0.2,
)
print(f"4h: {len(df_4h)} bars, first={df_4h.index[0]}, last={df_4h.index[-1]}")
df_4h.head()
"""))

# Cell 6: Timezone localize + advertised range slicing
cells.append(nbf.v4.new_code_cell("""\
# pyupbit는 timezone-naive KST 반환 (검증됨).
# 1) KST로 localize → UTC로 convert
# 2) Advertised UTC 범위로 슬라이싱 (사용자 의도: 2021-01-01 00:00 UTC ~ 2026-04-11 23:59 UTC)
#    - pyupbit는 START/END를 KST로 해석하므로 4h 결과가 2020-12-31 16:00 UTC부터 시작함.
#    - 이를 advertised 범위로 정렬해야 data_hashes.txt 헤더와 실제 데이터가 일치.

ADVERTISED_START_UTC = pd.Timestamp('2021-01-01 00:00:00', tz='UTC')
ADVERTISED_END_UTC   = pd.Timestamp('2026-04-12 00:00:00', tz='UTC')  # exclusive upper bound

for name, df in [('daily', df_daily), ('4h', df_4h)]:
    assert df.index.tz is None, f"{name}: Expected naive timestamps from pyupbit"

df_daily.index = df_daily.index.tz_localize('Asia/Seoul').tz_convert('UTC')
df_4h.index = df_4h.index.tz_localize('Asia/Seoul').tz_convert('UTC')

# Slice to advertised range (half-open [START, END))
before_daily = len(df_daily)
before_h4 = len(df_4h)
df_daily = df_daily[(df_daily.index >= ADVERTISED_START_UTC) & (df_daily.index < ADVERTISED_END_UTC)]
df_4h    = df_4h[(df_4h.index >= ADVERTISED_START_UTC) & (df_4h.index < ADVERTISED_END_UTC)]

print(f"Daily: sliced {before_daily} -> {len(df_daily)}, range: {df_daily.index[0]} ~ {df_daily.index[-1]}")
print(f"4h:    sliced {before_h4} -> {len(df_4h)}, range: {df_4h.index[0]} ~ {df_4h.index[-1]}")
print(f"Advertised: {ADVERTISED_START_UTC} ~ {ADVERTISED_END_UTC} (exclusive)")
"""))

# Cell 7: Gap detection (against advertised range, not just actual bounds)
cells.append(nbf.v4.new_code_cell("""\
# 갭은 advertised 시작 시점 기준으로 계산 (시작 경계 누락 감지).
# 끝 경계는 df.index[-1] 까지 — freeze 시점에 마지막 bar가 아직 존재하지 않을 수 있기 때문.
# 이 정책은 의도적이며, 만약 끝단 누락도 감지하고 싶으면 end=ADVERTISED_END_UTC-1bar로 수정.

expected_daily = pd.date_range(start=ADVERTISED_START_UTC, end=df_daily.index[-1], freq='1D', tz='UTC')
expected_h4    = pd.date_range(start=ADVERTISED_START_UTC, end=df_4h.index[-1],    freq='4h', tz='UTC')

daily_missing = expected_daily.difference(df_daily.index)
h4_missing    = expected_h4.difference(df_4h.index)

daily_pct = len(daily_missing) / len(expected_daily) * 100
h4_pct    = len(h4_missing)    / len(expected_h4)    * 100

print(f"Daily: expected {len(expected_daily)}, actual {len(df_daily)}, missing {len(daily_missing)} ({daily_pct:.4f}%)")
print(f"4h:    expected {len(expected_h4)},    actual {len(df_4h)},    missing {len(h4_missing)}    ({h4_pct:.4f}%)")

if len(daily_missing) > 0:
    print(f"Daily missing (first 5): {list(daily_missing[:5])}")
if len(h4_missing) > 0:
    print(f"4h missing (first 5): {list(h4_missing[:5])}")

# 갭 > 0.1%면 경고 (룰)
assert daily_pct < 0.1, f"Daily gaps {daily_pct:.4f}% exceed 0.1% threshold"
assert h4_pct    < 0.1, f"4h gaps {h4_pct:.4f}% exceed 0.1% threshold"
print("\\nGap check PASSED (both < 0.1%)")
"""))

# Cell 8: Save Parquet
cells.append(nbf.v4.new_code_cell("""\
data_dir = Path('../data')
data_dir.mkdir(exist_ok=True)

daily_path = data_dir / f'KRW-BTC_1d_frozen_{FREEZE_DATE}.parquet'
h4_path = data_dir / f'KRW-BTC_4h_frozen_{FREEZE_DATE}.parquet'

df_daily.to_parquet(daily_path)
df_4h.to_parquet(h4_path)

print(f"Saved: {daily_path} ({daily_path.stat().st_size / 1024:.1f} KB)")
print(f"Saved: {h4_path} ({h4_path.stat().st_size / 1024:.1f} KB)")
"""))

# Cell 9: SHA256 + freeze record (accurate range)
cells.append(nbf.v4.new_code_cell("""\
daily_hash = sha256_file(daily_path)
h4_hash = sha256_file(h4_path)

# data_hashes.txt 헤더는 actual 데이터 범위 (advertised 범위 아님)
daily_actual_start = df_daily.index[0].isoformat()
daily_actual_end   = df_daily.index[-1].isoformat()
h4_actual_start    = df_4h.index[0].isoformat()
h4_actual_end      = df_4h.index[-1].isoformat()

hashes_path = data_dir / 'data_hashes.txt'
with open(hashes_path, 'w') as f:
    f.write(f"# Generated by 01_data_collection.ipynb on {datetime.now(timezone.utc).isoformat()}\\n")
    f.write(f"# Freeze date: {FREEZE_DATE}\\n")
    f.write(f"# Advertised range (UTC, half-open): {ADVERTISED_START_UTC.isoformat()} ~ {ADVERTISED_END_UTC.isoformat()}\\n")
    f.write(f"# Daily actual range: {daily_actual_start} ~ {daily_actual_end}\\n")
    f.write(f"# 4h actual range:    {h4_actual_start} ~ {h4_actual_end}\\n")
    f.write(f"# Daily bars: {len(df_daily)}, gaps: {len(daily_missing)} ({daily_pct:.4f}%)\\n")
    f.write(f"# 4h bars: {len(df_4h)}, gaps: {len(h4_missing)} ({h4_pct:.4f}%)\\n")
    f.write(f"\\n")
    f.write(f"{daily_path.name}: {daily_hash}\\n")
    f.write(f"{h4_path.name}: {h4_hash}\\n")

print(f"Hashes written to {hashes_path}")
print(f"  {daily_path.name}: {daily_hash}")
print(f"  {h4_path.name}: {h4_hash}")
"""))

# Cell 10: Verification summary
cells.append(nbf.v4.new_code_cell("""\
# Final verification summary (printed for evidence file)
print("=" * 60)
print("W1-01 Data Collection Verification")
print("=" * 60)
print(f"Advertised range: {ADVERTISED_START_UTC} ~ {ADVERTISED_END_UTC} (half-open)")
print(f"Daily: {len(df_daily)} bars, gaps {len(daily_missing)} ({daily_pct:.4f}%), hash {daily_hash[:16]}...")
print(f"  range: {df_daily.index[0]} ~ {df_daily.index[-1]}")
print(f"4h:    {len(df_4h)} bars, gaps {len(h4_missing)} ({h4_pct:.4f}%), hash {h4_hash[:16]}...")
print(f"  range: {df_4h.index[0]} ~ {df_4h.index[-1]}")
print(f"TZ: UTC (localized from naive KST)")
print(f"Files: {daily_path.name}, {h4_path.name}")
if len(h4_missing) > 0:
    print(f"\\n4h missing timestamps:")
    for ts in h4_missing:
        print(f"  {ts}")
"""))

nb.cells = cells

# Save
out_path = Path(__file__).parent.parent / 'notebooks' / '01_data_collection.ipynb'
out_path.parent.mkdir(exist_ok=True)
with open(out_path, 'w') as f:
    nbf.write(nb, f)

print(f"Notebook created: {out_path}")
