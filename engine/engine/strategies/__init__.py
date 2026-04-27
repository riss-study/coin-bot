"""Engine strategies — Strategy A (Trend Following) + Strategy D (Volatility Breakout).

박제 출처:
- docs/candidate-pool.md v7 Strategy A/D 파라미터
- docs/stage1-v2-relaunch.md §1.1 채택 3 cells (BTC_A, ETH_A, BTC_D)
- research/CLAUDE.md pyupbit/ta 검증 패턴
"""
from engine.strategies.base import SignalAction, SignalResult, Strategy
from engine.strategies.strategy_a import StrategyA
from engine.strategies.strategy_d import StrategyD
from engine.strategies.strategy_g import StrategyG

__all__ = ["SignalAction", "SignalResult", "Strategy", "StrategyA", "StrategyD", "StrategyG"]
