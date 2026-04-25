// SummaryCards — 상단 4 카드 (총 PnL / trades / win-loss / 기간).
// Server Component.

import { api, formatKRW, formatPct } from "@/lib/api";

export default async function SummaryCards() {
  let s;
  try {
    s = await api.summary();
  } catch {
    return <div className="text-red-600">summary fetch 실패</div>;
  }

  const pnlClass =
    s.total_realized_krw > 0
      ? "text-green-700"
      : s.total_realized_krw < 0
        ? "text-red-700"
        : "text-gray-700";

  return (
    <div className="grid grid-cols-2 gap-3 sm:grid-cols-4">
      <Card label="총 realized PnL">
        <div className={`text-xl font-bold ${pnlClass}`}>
          {formatKRW(s.total_realized_krw, true)} KRW
        </div>
        <div className="text-xs text-gray-500">{formatPct(s.cumulative_return_ratio)}</div>
      </Card>
      <Card label="누적 trades">
        <div className="text-xl font-bold">{s.trade_count}</div>
        <div className="text-xs text-gray-500">매도 체결 기준</div>
      </Card>
      <Card label="win / loss">
        <div className="text-xl font-bold">
          {s.win_count} <span className="text-gray-400">/</span> {s.loss_count}
        </div>
        <div className="text-xs text-gray-500">
          win rate{" "}
          {s.trade_count > 0
            ? `${((s.win_count / s.trade_count) * 100).toFixed(0)}%`
            : "—"}
        </div>
      </Card>
      <Card label="투자 누적">
        <div className="text-xl font-bold">{formatKRW(s.total_invested_krw)} KRW</div>
        <div className="text-xs text-gray-500">진입 시 사용 자본</div>
      </Card>
    </div>
  );
}

function Card({ label, children }: { label: string; children: React.ReactNode }) {
  return (
    <div className="rounded-lg border border-gray-200 bg-white p-4 shadow-sm">
      <div className="text-xs uppercase tracking-wide text-gray-500">{label}</div>
      <div className="mt-1">{children}</div>
    </div>
  );
}
