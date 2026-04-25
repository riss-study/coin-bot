// LogsPanel — 최근 engine 로그 (Client Component, 30s 폴링).
// 학습 포인트: useState/useEffect + setInterval cleanup

"use client";

import { useEffect, useState } from "react";
import { api } from "@/lib/api";
import type { LogEntry } from "@/lib/types";

export default function LogsPanel() {
  const [logs, setLogs] = useState<LogEntry[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchLogs = async () => {
      try {
        const res = await api.logs(20);
        setLogs(res.logs.reverse());
        setError(null);
      } catch (e) {
        setError(e instanceof Error ? e.message : "fetch 실패");
      } finally {
        setLoading(false);
      }
    };
    fetchLogs();
    const id = setInterval(fetchLogs, 30_000);
    return () => clearInterval(id);
  }, []);

  if (loading) {
    return <div className="text-sm text-gray-500">로그 로딩...</div>;
  }
  if (error) {
    return <div className="text-sm text-red-600">로그 fetch 실패: {error}</div>;
  }
  if (logs.length === 0) {
    return (
      <div className="rounded-lg border border-gray-200 bg-white p-4 text-sm text-gray-500">
        오늘 로그 없음
      </div>
    );
  }

  return (
    <div className="max-h-72 overflow-y-auto rounded-lg border border-gray-200 bg-gray-900 p-3 font-mono text-xs text-gray-100">
      {logs.map((log, idx) => {
        const lvl = String(log.level || "").toUpperCase();
        const lvlColor =
          lvl === "ERROR"
            ? "text-red-400"
            : lvl === "WARNING"
              ? "text-yellow-400"
              : "text-blue-300";
        return (
          <div key={idx} className="mb-1">
            <span className="text-gray-500">{log.asctime || log.ts_utc}</span>{" "}
            <span className={lvlColor}>[{lvl}]</span>{" "}
            <span className="text-gray-300">{log.logger || ""}</span>{" "}
            <span>{log.message}</span>
          </div>
        );
      })}
    </div>
  );
}
