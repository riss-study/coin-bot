"""Config 로딩 + Keychain secrets 조회.

V2-01 골격. API 키 실제 호출은 V2-05 (integration test) 단계까지 mock.

박제 출처:
- engine/config.yaml (사전 지정 파라미터)
- docs/stage1-v2-relaunch.md §2.2 (Secrets: macOS Keychain)
"""
from __future__ import annotations

import subprocess
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import yaml

try:
    from zoneinfo import ZoneInfo
except ImportError:
    from backports.zoneinfo import ZoneInfo  # type: ignore


CONFIG_PATH = Path(__file__).parent.parent / "config.yaml"
ENGINE_ROOT = Path(__file__).parent.parent
KST = ZoneInfo("Asia/Seoul")  # 시스템 상수 (NIT #4 단일 출처 정정 2026-04-26)


def ensure_runtime_dirs() -> None:
    """logs/, data/, secrets/ 런타임 디렉토리 자동 생성 (gitignored)."""
    for name in ("logs", "data", "secrets"):
        (ENGINE_ROOT / name).mkdir(parents=True, exist_ok=True)


@dataclass
class StrategyAParams:
    ma_period: int = 200
    donchian_high: int = 20
    donchian_low: int = 10
    vol_avg_period: int = 20
    vol_mult: float = 1.5
    sl_pct: float = 0.08


@dataclass
class StrategyDParams:
    keltner_window: int = 20
    keltner_atr_mult: float = 1.5
    atr_window: int = 14
    bollinger_window: int = 20
    bollinger_sigma: float = 2.0
    sl_hard: float = 0.08


@dataclass
class PortfolioParams:
    init_cash: int
    stake_amount: int
    fees: float
    slippage: float
    year_freq: str
    max_open_positions: int


@dataclass
class ScheduleParams:
    signal_check_hour_kst: int
    signal_check_minute: int


@dataclass
class GoCriteria:
    min_sharpe: float
    max_mdd: float
    min_trades: int
    paper_live_tolerance: float


@dataclass
class KeychainConfig:
    access_key_service: str
    secret_key_service: str
    discord_webhook_service: str
    account: str


@dataclass
class CellConfig:
    ticker: str
    strategy: str
    stake_amount_override: int | None = None  # cell별 stake 박제 (Strategy G 50k vs default)


@dataclass
class StrategyGParams:
    entry_bar_pct: float = 0.02
    vol_avg: int = 20
    vol_mult: float = 1.2
    short_break: int = 3
    sl_pct: float = 0.03
    tp_pct: float = 0.05
    time_stop_bars: int = 3


@dataclass
class Config:
    run_mode: str  # "paper" | "live"
    pairs: list[CellConfig]
    strategy_a: StrategyAParams
    strategy_d: StrategyDParams
    strategy_g: StrategyGParams
    portfolio: PortfolioParams
    schedule: ScheduleParams
    go_criteria: GoCriteria
    keychain: KeychainConfig
    logging: dict[str, Any]
    state: dict[str, Any]


def load_config(path: Path | None = None) -> Config:
    """YAML config 로드 + 타입 검증."""
    if path is None:
        path = CONFIG_PATH
    with open(path) as f:
        raw = yaml.safe_load(f)

    pairs = [CellConfig(**p) for p in raw["pairs"]]
    strategy_a = StrategyAParams(**raw["strategies"]["A"])
    strategy_d = StrategyDParams(**raw["strategies"]["D"])
    strategy_g = StrategyGParams(**raw["strategies"].get("G", {}))
    portfolio = PortfolioParams(**raw["portfolio"])
    schedule = ScheduleParams(**raw["schedule"])
    go_criteria = GoCriteria(**raw["go_criteria"])
    keychain = KeychainConfig(**raw["keychain"])

    if raw["run_mode"] not in ("paper", "live"):
        raise ValueError(f"run_mode must be 'paper' or 'live', got '{raw['run_mode']}'")

    return Config(
        run_mode=raw["run_mode"],
        pairs=pairs,
        strategy_a=strategy_a,
        strategy_d=strategy_d,
        strategy_g=strategy_g,
        portfolio=portfolio,
        schedule=schedule,
        go_criteria=go_criteria,
        keychain=keychain,
        logging=raw["logging"],
        state=raw["state"],
    )


def get_keychain_secret(service: str, account: str) -> str:
    """macOS Keychain에서 secret 조회.

    `security find-generic-password -s <service> -a <account> -w` 명령 사용.
    """
    result = subprocess.run(
        ["security", "find-generic-password", "-s", service, "-a", account, "-w"],
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode != 0:
        raise RuntimeError(
            f"Keychain secret 조회 실패 (service={service}, account={account}): "
            f"{result.stderr.strip()}. "
            f"저장하려면: security add-generic-password -s {service} -a {account} -w <VALUE>"
        )
    return result.stdout.strip()


def load_upbit_credentials(cfg: Config) -> tuple[str, str]:
    """Upbit Access + Secret Key 조회 (Keychain)."""
    access = get_keychain_secret(cfg.keychain.access_key_service, cfg.keychain.account)
    secret = get_keychain_secret(cfg.keychain.secret_key_service, cfg.keychain.account)
    return access, secret


def load_discord_webhook(cfg: Config) -> str:
    """Discord webhook URL 조회 (Keychain)."""
    return get_keychain_secret(cfg.keychain.discord_webhook_service, cfg.keychain.account)


if __name__ == "__main__":
    # 직접 실행 시 config.yaml 로드 sanity check + 런타임 디렉토리 생성
    ensure_runtime_dirs()
    cfg = load_config()
    print(f"run_mode: {cfg.run_mode}")
    print(f"pairs: {[(c.ticker, c.strategy) for c in cfg.pairs]}")
    print(f"portfolio: init_cash={cfg.portfolio.init_cash:,}, stake={cfg.portfolio.stake_amount:,}")
    print(f"strategy_a: MA={cfg.strategy_a.ma_period}, SL={cfg.strategy_a.sl_pct}")
    print(f"strategy_d: Keltner={cfg.strategy_d.keltner_window}, BB sigma={cfg.strategy_d.bollinger_sigma}")
    print(f"keychain services: {cfg.keychain.access_key_service} / {cfg.keychain.secret_key_service}")
    print(f"config OK (V2-01 골격)")
