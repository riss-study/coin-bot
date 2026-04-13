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


def check_gaps(df, freq):
    \"\"\"Detect missing candles by comparing to expected date_range.\"\"\"
    expected = pd.date_range(start=df.index[0], end=df.index[-1], freq=freq)
    missing = expected.difference(df.index)
    pct = len(missing) / max(len(expected), 1) * 100
    return len(missing), pct


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

# Cell 6: Timezone localize
cells.append(nbf.v4.new_code_cell("""\
# pyupbit는 timezone-naive KST 반환 (검증됨).
# UTC로 변환하여 일관성 확보.

for name, df in [('daily', df_daily), ('4h', df_4h)]:
    assert df.index.tz is None, f"{name}: Expected naive timestamps from pyupbit"

df_daily.index = df_daily.index.tz_localize('Asia/Seoul').tz_convert('UTC')
df_4h.index = df_4h.index.tz_localize('Asia/Seoul').tz_convert('UTC')

print(f"Daily tz: {df_daily.index.tz}, range: {df_daily.index[0]} ~ {df_daily.index[-1]}")
print(f"4h tz: {df_4h.index.tz}, range: {df_4h.index[0]} ~ {df_4h.index[-1]}")
"""))

# Cell 7: Gap detection
cells.append(nbf.v4.new_code_cell("""\
daily_gaps, daily_pct = check_gaps(df_daily, '1D')
h4_gaps, h4_pct = check_gaps(df_4h, '4h')

print(f"Daily: {len(df_daily)} bars, {daily_gaps} gaps ({daily_pct:.3f}%)")
print(f"4h:    {len(df_4h)} bars, {h4_gaps} gaps ({h4_pct:.3f}%)")

# 갭 > 0.1%면 경고 (룰)
if daily_pct > 0.1:
    print(f"WARNING: Daily gaps {daily_pct:.3f}% > 0.1% threshold")
if h4_pct > 0.1:
    print(f"WARNING: 4h gaps {h4_pct:.3f}% > 0.1% threshold")
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

# Cell 9: SHA256 + freeze record
cells.append(nbf.v4.new_code_cell("""\
daily_hash = sha256_file(daily_path)
h4_hash = sha256_file(h4_path)

hashes_path = data_dir / 'data_hashes.txt'
with open(hashes_path, 'w') as f:
    f.write(f"# Generated by 01_data_collection.ipynb on {datetime.now(timezone.utc).isoformat()}\\n")
    f.write(f"# Freeze date: {FREEZE_DATE}\\n")
    f.write(f"# Data range: {START} ~ {END}\\n")
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
print(f"Daily: {len(df_daily)} bars, gaps {daily_pct:.3f}%, hash {daily_hash[:16]}...")
print(f"4h:    {len(df_4h)} bars, gaps {h4_pct:.3f}%, hash {h4_hash[:16]}...")
print(f"TZ:    UTC (localized from naive KST)")
print(f"Range: {df_daily.index[0]} ~ {df_daily.index[-1]}")
print(f"Files: {daily_path.name}, {h4_path.name}")
"""))

nb.cells = cells

# Save
out_path = Path(__file__).parent.parent / 'notebooks' / '01_data_collection.ipynb'
out_path.parent.mkdir(exist_ok=True)
with open(out_path, 'w') as f:
    nbf.write(nb, f)

print(f"Notebook created: {out_path}")
