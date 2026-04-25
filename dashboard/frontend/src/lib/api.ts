// Backend fetch wrapper.
// 박제: env NEXT_PUBLIC_API_BASE_URL (default http://127.0.0.1:8001)
//        cache: "no-store" (대시보드 실시간 모니터링)

import type {
  HealthResponse,
  LogsResponse,
  OrdersResponse,
  PositionsResponse,
  SummaryResponse,
  TradesResponse,
} from "./types";

const BASE = process.env.NEXT_PUBLIC_API_BASE_URL || "http://127.0.0.1:8001";

async function get<T>(path: string): Promise<T> {
  const res = await fetch(`${BASE}${path}`, { cache: "no-store" });
  if (!res.ok) {
    throw new Error(`API ${path} failed: ${res.status} ${res.statusText}`);
  }
  return res.json() as Promise<T>;
}

export const api = {
  health: () => get<HealthResponse>("/api/health"),
  positions: () => get<PositionsResponse>("/api/positions"),
  trades: (days?: number) =>
    get<TradesResponse>(`/api/trades${days ? `?days=${days}` : ""}`),
  summary: (days?: number) =>
    get<SummaryResponse>(`/api/summary${days ? `?days=${days}` : ""}`),
  ordersRecent: (n: number = 20) =>
    get<OrdersResponse>(`/api/orders/recent?n=${n}`),
  ordersOpen: () => get<OrdersResponse>("/api/orders/open"),
  logs: (n: number = 50, level?: string) => {
    const qs = new URLSearchParams({ n: String(n) });
    if (level) qs.set("level", level);
    return get<LogsResponse>(`/api/logs?${qs.toString()}`);
  },
};

// 포맷 helper
export function formatKRW(value: number | null | undefined, sign = false): string {
  if (value == null) return "—";
  const abs = Math.round(Math.abs(value)).toLocaleString("ko-KR");
  if (sign && value > 0) return `+${abs}`;
  if (value < 0) return `-${abs}`;
  return abs;
}

export function formatPct(ratio: number | null | undefined): string {
  if (ratio == null) return "—";
  const pct = ratio * 100;
  const sign = pct > 0 ? "+" : "";
  return `${sign}${pct.toFixed(2)}%`;
}

export function formatKstShort(isoUtc: string | null | undefined): string {
  if (!isoUtc) return "—";
  const d = new Date(isoUtc);
  if (isNaN(d.getTime())) return "—";
  return d.toLocaleString("ko-KR", {
    timeZone: "Asia/Seoul",
    month: "2-digit",
    day: "2-digit",
    hour: "2-digit",
    minute: "2-digit",
  });
}
