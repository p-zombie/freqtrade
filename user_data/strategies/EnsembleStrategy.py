from freqtrade.strategy import IStrategy, DecimalParameter, IntParameter
import logging
from pandas import DataFrame
from freqtrade.resolvers import StrategyResolver
from itertools import combinations
from functools import reduce

logger = logging.getLogger(__name__)

STRATEGIES = [
    "AwesomeMacd",
    "CombinedBinHAndCluc",
    "CombinedBinHAndClucV2",
    "CombinedBinHAndClucV5",
    "CombinedBinHAndClucV7",
    "CombinedBinHAndClucV8",
    "SMAOffset",
    "SMAOffsetV2",
    "SMAOffsetProtectOptV0",
    "SMAOffsetProtectOptV1",
    "NostalgiaForInfinityV1",
    "NostalgiaForInfinityV2",
    "NostalgiaForInfinityV3",
    "NostalgiaForInfinityV4",
    "NostalgiaForInfinityV5",
    "NostalgiaForInfinityV7",
    "Obelisk_Ichimoku_ZEMA_v1"
]

STRAT_COMBINATIONS = reduce(
    lambda x, y: list(combinations(STRATEGIES, y)) + x, range(len(STRATEGIES) + 1), []
)

MAX_COMBINATIONS = len(STRAT_COMBINATIONS) - 2


class EnsembleStrategy(IStrategy):
    loaded_strategies = {}
    informative_timeframe = "1h"

    use_sell_signal = False
    ignore_roi_if_buy_signal = False
    sell_profit_only = False

    buy_action_diff_threshold = DecimalParameter(0, 1, default=0, decimals=2, optimize=True, load=True)
    buy_strategies = IntParameter(0, MAX_COMBINATIONS, default=0, optimize=True, load=True)

    stoploss = -0.3

    buy_params = {
    }

    sell_params = {}

    # ROI table:
    minimal_roi = {
        "0": 0.187,
        "23": 0.043,
        "72": 0.011,
        "163": 0
    }

    # Trailing stop:
    trailing_stop = True
    trailing_stop_positive = 0.074
    trailing_stop_positive_offset = 0.121
    trailing_only_offset_is_reached = False

    protections = [
        {
            "method": "CooldownPeriod",
            "stop_duration_candles": 2
        },
        {
            "method": "StoplossGuard",
            "lookback_period_candles": 100,
            "trade_limit": 4,
            "stop_duration_candles": 10,
            "only_per_pair": True
        },
    ]

    def __init__(self, config: dict) -> None:
        super().__init__(config)
        logger.info(f"Buy stratrategies: {STRAT_COMBINATIONS[self.buy_strategies.value]}")

    def informative_pairs(self):
        pairs = self.dp.current_whitelist()
        informative_pairs = [(pair, self.informative_timeframe) for pair in pairs]
        return informative_pairs

    def get_strategy(self, strategy_name):
        strategy = self.loaded_strategies.get(strategy_name)
        if not strategy:
            config = self.config
            config["strategy"] = strategy_name
            strategy = StrategyResolver.load_strategy(config)

        strategy.dp = self.dp
        strategy.wallets = self.wallets
        self.loaded_strategies[strategy_name] = strategy
        return strategy

    def populate_indicators(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        strategies = STRATEGIES
        for strategy_name in strategies:
            strategy = self.get_strategy(strategy_name)
            strategy_indicators = strategy.advise_indicators(dataframe, metadata)
            dataframe[f"buy_signal_{strategy_name}"] = strategy.advise_buy(
                strategy_indicators, metadata
            )["buy"]

        buy_strategies = STRAT_COMBINATIONS[self.buy_strategies.value]
        buy_strategies = [f"buy_signal_{name}" for name in buy_strategies]

        dataframe["buy_mean"] = dataframe[buy_strategies].fillna(0).mean(axis=1)
        return dataframe

    def populate_buy_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        dataframe["buy"] = (
            dataframe["buy_mean"] > self.buy_action_diff_threshold.value
        ).astype(int)
        return dataframe

    def populate_sell_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        dataframe["sell"] = 0
        return dataframe
