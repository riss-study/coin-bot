"""Discord webhook 알림 + rate limit 방어 + 에러 디바운스.

박제 출처:
- docs/stage1-v2-relaunch.md §2.4 notifier.py
- docs/user-setup-guide.md §6 (Discord rate limit 동적 헤더 기반, 고정 수치 없음)

설계:
- Discord webhook URL 1개 (Keychain `discord-webhook` 서비스)
- 메시지 종류:
  - notify_entry / notify_exit: 시그널 발생 (cell + 행동 + 가격)
  - notify_order_filled: 주문 체결 (가격, 수량, 수수료)
  - notify_error: 에러 (10분 디바운스 — 동일 키 반복 알림 방지)
  - notify_summary: 일일 요약 (포지션 + PnL)
- HTTP 응답 처리:
  - 200/204: 성공
  - 429: Retry-After 헤더 따라 대기 후 1회 재시도
  - 그 외: 로깅만 (실패 시 봇 중단 X)
"""
from __future__ import annotations

import logging
import time
from collections import defaultdict
from datetime import datetime, timezone, timedelta
from threading import RLock
from typing import Any

import requests


_log = logging.getLogger("engine.notifier")


class DiscordNotifier:
    """Discord webhook 클라이언트 (단일 webhook URL).

    Thread-safe. 디바운스 대상 키별로 마지막 발송 시각 보관.
    """

    DEFAULT_DEBOUNCE_S = 600  # 동일 에러 키 10분 디바운스

    def __init__(self, webhook_url: str, debounce_s: int = DEFAULT_DEBOUNCE_S):
        if not webhook_url or not webhook_url.startswith("https://discord.com/api/webhooks/"):
            raise ValueError(f"invalid Discord webhook URL: {webhook_url[:40]}...")
        self.webhook_url = webhook_url
        self.debounce_s = debounce_s
        self._last_sent: dict[str, datetime] = defaultdict(lambda: datetime.min.replace(tzinfo=timezone.utc))
        self._lock = RLock()

    def _send(self, content: str, *, debounce_key: str | None = None) -> bool:
        """webhook POST. 성공 시 True. 디바운스 시 False (전송 안 함). 실패 시 False."""
        if debounce_key:
            with self._lock:
                last = self._last_sent[debounce_key]
                if datetime.now(timezone.utc) - last < timedelta(seconds=self.debounce_s):
                    _log.debug("debounce_skip", extra={"key": debounce_key})
                    return False
                self._last_sent[debounce_key] = datetime.now(timezone.utc)

        payload = {"content": content[:1900]}  # Discord content 제한 2000자, 마진 100
        for attempt in range(2):  # 1회 retry
            try:
                resp = requests.post(self.webhook_url, json=payload, timeout=10)
                if resp.status_code in (200, 204):
                    return True
                if resp.status_code == 429:
                    retry_after = float(resp.headers.get("Retry-After", "1"))
                    _log.warning("discord_rate_limited", extra={"retry_after_s": retry_after})
                    time.sleep(min(retry_after, 30))
                    continue
                _log.warning("discord_send_failed", extra={"status": resp.status_code, "body": resp.text[:200]})
                return False
            except Exception as e:
                _log.warning("discord_exception", extra={"error": str(e), "attempt": attempt})
                if attempt == 0:
                    time.sleep(1)
        return False

    # ---------- 알림 메서드 ----------

    def notify_signal(self, *, cell_key: str, action: str, pair: str, strategy: str,
                      price_krw: float | None = None, reason: dict | None = None) -> bool:
        emoji = {"entry": "📈", "exit": "📉", "sl_exit": "🛑"}.get(action, "ℹ️")
        msg = (
            f"{emoji} **{action.upper()}** signal — {cell_key}\n"
            f"pair={pair} / strategy={strategy}"
        )
        if price_krw is not None:
            msg += f" / price={price_krw:,.0f} KRW"
        if reason:
            msg += f"\nreason: `{reason}`"
        return self._send(msg)

    def notify_order_filled(self, *, cell_key: str, side: str, pair: str,
                            price_krw: float, volume: float,
                            krw_amount: float, fees_krw: float,
                            order_uuid: str, run_mode: str) -> bool:
        emoji = "🟢" if side == "buy" else "🔴"
        msg = (
            f"{emoji} **{side.upper()} filled** ({run_mode}) — {cell_key}\n"
            f"price={price_krw:,.0f} KRW / volume={volume:.8f}\n"
            f"krw_amount={krw_amount:,.0f} / fees={fees_krw:,.2f}\n"
            f"order_uuid=`{order_uuid[:16]}...`"
        )
        return self._send(msg)

    def notify_error(self, *, key: str, message: str, debounce_s: int | None = None) -> bool:
        """에러 알림 (디바운스 적용). 동일 key 10분 내 재호출 시 skip."""
        msg = f"⚠️ **ERROR** [{key}]\n{message[:1500]}"
        if debounce_s is not None:
            saved = self.debounce_s
            self.debounce_s = debounce_s
            try:
                return self._send(msg, debounce_key=key)
            finally:
                self.debounce_s = saved
        return self._send(msg, debounce_key=key)

    def notify_summary(self, *, ts_kst: str, open_positions: int, total_pnl_krw: float,
                       cell_pnls: dict[str, float] | None = None,
                       run_mode: str = "paper") -> bool:
        cell_lines = ""
        if cell_pnls:
            cell_lines = "\n" + "\n".join(f"  {k}: {v:+,.0f} KRW" for k, v in cell_pnls.items())
        sign_emoji = "📊" if abs(total_pnl_krw) < 1 else ("📈" if total_pnl_krw > 0 else "📉")
        msg = (
            f"{sign_emoji} **Daily summary** ({run_mode}) — {ts_kst} KST\n"
            f"open_positions={open_positions} / total_pnl={total_pnl_krw:+,.0f} KRW{cell_lines}"
        )
        return self._send(msg)


if __name__ == "__main__":
    # Sanity: Keychain에서 webhook URL 로드 시도. 없으면 mock 검증만.
    from engine.config import ENGINE_ROOT, ensure_runtime_dirs, load_config, get_keychain_secret
    from engine.logger import setup_logger

    ensure_runtime_dirs()
    cfg = load_config()
    setup_logger(ENGINE_ROOT / "logs", "INFO")

    try:
        url = get_keychain_secret(cfg.keychain.discord_webhook_service, cfg.keychain.account)
        print(f"webhook URL 발견 (Keychain). 길이={len(url)}")
        notif = DiscordNotifier(url)

        ok = notif.notify_signal(
            cell_key="KRW-BTC_A", action="entry", pair="KRW-BTC", strategy="A",
            price_krw=115_000_000, reason={"sanity": True},
        )
        print(f"notify_signal: {'OK' if ok else 'FAILED'}")

        ok = notif.notify_summary(
            ts_kst="2026-04-25 09:05", open_positions=1, total_pnl_krw=12_500,
            cell_pnls={"KRW-BTC_A": 12_500}, run_mode="paper",
        )
        print(f"notify_summary: {'OK' if ok else 'FAILED'}")

        # 에러 디바운스 sanity
        ok1 = notif.notify_error(key="test_error", message="첫 번째 알림")
        ok2 = notif.notify_error(key="test_error", message="두 번째 알림 (디바운스 차단 예상)")
        print(f"notify_error 1차: {'OK' if ok1 else 'SKIP'} / 2차: {'OK' if ok2 else 'SKIP (debounce)'}")
    except RuntimeError as e:
        # Keychain에 webhook 없음 → mock URL로 인스턴스만 생성 검증
        print(f"Keychain webhook 미발견 ({str(e)[:100]}...) → mock 인스턴스 검증으로 대체")
        try:
            DiscordNotifier("invalid-url")
        except ValueError as ve:
            print(f"invalid URL 거부 OK: {ve}")
        mock = DiscordNotifier("https://discord.com/api/webhooks/123/abc")
        print(f"mock 인스턴스 생성 OK (debounce_s={mock.debounce_s})")
