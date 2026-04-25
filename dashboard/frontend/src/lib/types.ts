// Backend API 응답 타입 (FastAPI 응답 스키마와 일치).
// 박제 출처: dashboard/backend/app/routers/*.py

export interface HealthResponse {
  status: string;
  ts_utc: string;
  ts_kst: string;
  state_db: string;
  last_run_ts_utc: string | null;
  last_run_kst?: string;
  seconds_since_last_run?: number;
  daemon_alive: boolean | null;
  note?: string;
}

export interface Position {
  cell_key: string;
  pair: string;
  strategy: string;
  entry_ts_utc: string;
  entry_price_krw: number;
  volume: number;
  krw_invested: number;
  order_uuid: string | null;
  metadata: Record<string, unknown>;
  current_price_krw: number | null;
  market_value_krw: number | null;
  unrealized_pnl_krw: number | null;
  unrealized_pnl_ratio: number | null;
}

export interface PositionsResponse {
  positions: Position[];
  count: number;
  note?: string;
}

export interface Trade {
  ts_utc: string;
  pair: string;
  strategy: string;
  side: "buy" | "sell";
  order_type: string;
  price_krw: number;
  volume: number;
  krw_amount: number;
  fees_krw: number;
  order_uuid: string;
  client_oid: string;
  run_mode: string;
  realized_pnl_krw?: number;
  realized_pnl_pct?: number;
  entry_price_krw?: number;
  entry_fees_krw?: number;
  exit_fees_krw?: number;
}

export interface TradesResponse {
  trades: Trade[];
  count: number;
}

export interface SummaryResponse {
  trade_count: number;
  total_realized_krw: number;
  total_invested_krw: number;
  cumulative_return_ratio: number;
  win_count: number;
  loss_count: number;
  filter_days: number | null;
}

export interface Order {
  order_uuid: string;
  client_oid: string;
  cell_key: string;
  pair: string;
  strategy: string;
  side: string;
  order_type: string;
  status: string;
  requested_krw: number;
  filled_volume: number | null;
  filled_price_krw: number | null;
  fees_krw: number | null;
  requested_ts_utc: string;
  updated_ts_utc: string;
}

export interface OrdersResponse {
  orders: Order[];
  count: number;
  note?: string;
}

export interface LogEntry {
  ts_utc?: string;
  asctime?: string;
  level: string;
  logger?: string;
  message: string;
  [key: string]: unknown;
}

export interface LogsResponse {
  logs: LogEntry[];
  count: number;
  log_file: string;
  level_filter: string | null;
}
