// MarketsPanel — KRW 마켓 top 변동률 (참고용, 매매 X).
// Client Component (60s 폴링 + 정렬 토글).

"use client";

import { useEffect, useState } from "react";
import { api, formatKRW, formatPct } from "@/lib/api";
import type { MarketTicker } from "@/lib/types";

type SortKey = "change_rate" | "volume" | "loser";

const SORT_LABEL: Record<SortKey, string> = {
  change_rate: "급등 top",
  loser: "급락 top",
  volume: "거래대금 top",
};

export default function MarketsPanel() {
  const [sort, setSort] = useState<SortKey>("change_rate");
  const [rows, setRows] = useState<MarketTicker[]>([]);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let alive = true;
    const load = async () => {
      try {
        const res = await api.marketsTop(15, sort);
        if (alive) {
          setRows(res.markets);
          setError(null);
        }
      } catch (e) {
        if (alive) setError(e instanceof Error ? e.message : "fetch 실패");
      }
    };
    load();
    const id = setInterval(load, 60_000);
    return () => {
      alive = false;
      clearInterval(id);
    };
  }, [sort]);

  return (
    <div className="rounded-lg border border-gray-200 bg-white p-3 shadow-sm">
      <div className="mb-2 flex flex-wrap items-center gap-2">
        {(Object.keys(SORT_LABEL) as SortKey[]).map((k) => (
          <button
            key={k}
            onClick={() => setSort(k)}
            className={`rounded-md px-2 py-1 text-xs ${
              sort === k
                ? "bg-blue-600 text-white"
                : "bg-gray-100 text-gray-700 hover:bg-gray-200"
            }`}
          >
            {SORT_LABEL[k]}
          </button>
        ))}
        <span className="ml-auto text-xs text-gray-500">참고용 · 매매 X · 60s 갱신</span>
      </div>
      {error ? (
        <div className="text-sm text-red-600">{error}</div>
      ) : rows.length === 0 ? (
        <div className="text-sm text-gray-500">로딩...</div>
      ) : (
        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-gray-200 text-sm">
            <thead className="bg-gray-50 text-xs uppercase tracking-wide text-gray-600">
              <tr>
                <th className="px-3 py-1.5 text-left">market</th>
                <th className="px-3 py-1.5 text-left">name</th>
                <th className="px-3 py-1.5 text-right">price</th>
                <th className="px-3 py-1.5 text-right">24h</th>
                <th className="px-3 py-1.5 text-right">vol (24h)</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-100">
              {rows.map((t) => {
                const rate = t.signed_change_rate;
                const cls =
                  rate > 0 ? "text-red-700" : rate < 0 ? "text-blue-700" : "text-gray-600";
                return (
                  <tr key={t.market}>
                    <td className="px-3 py-1.5 font-mono text-xs">{t.market}</td>
                    <td className="px-3 py-1.5 text-xs">{t.korean_name}</td>
                    <td className="px-3 py-1.5 text-right font-mono">
                      {formatKRW(t.trade_price)}
                    </td>
                    <td className={`px-3 py-1.5 text-right font-mono ${cls}`}>
                      {formatPct(rate)}
                    </td>
                    <td className="px-3 py-1.5 text-right font-mono text-xs text-gray-500">
                      {(t.acc_trade_price_24h / 1e8).toFixed(0)}억
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}
