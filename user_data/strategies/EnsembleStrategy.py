from freqtrade.strategy import IStrategy, IntParameter, DecimalParameter
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
    "CombinedBinHAndClucV6H",
    "CombinedBinHAndClucV7",
    "CombinedBinHAndClucV8",
    "CombinedBinHAndClucV8Hyper",
    "SMAOffset",
    "SMAOffsetV2",
    "NostalgiaForInfinityV1",
    "NostalgiaForInfinityV2",
    "Obelisk_Ichimoku_ZEMA_v1",
    "TheRealPullbackV2",
]

STRAT_COMBINATIONS = reduce(
    lambda x, y: list(combinations(STRATEGIES, y)) + x, range(len(STRATEGIES)+1), []
)


class EnsembleStrategy(IStrategy):
    loaded_strategies = {}

    #  Default config uses mode from all strategies
    buy_mean_threshold = DecimalParameter(0.0, 1, default=0.5, load=True)
    sell_mean_threshold = DecimalParameter(0.0, 1, default=0.5, load=True)
    buy_strategies = IntParameter(0, len(STRAT_COMBINATIONS), default=0, load=True)
    sell_strategies = IntParameter(0, len(STRAT_COMBINATIONS), default=0, load=True)

    stoploss = -0.20

    def __init__(self, config: dict) -> None:
        super().__init__(config)
        logger.info(f"Buy stratrategies: {STRAT_COMBINATIONS[self.buy_strategies.value]}")
        logger.info(f"Sell stratrategies: {STRAT_COMBINATIONS[self.sell_strategies.value]}")

    def informative_pairs(self):
        pairs = self.dp.current_whitelist()
        informative_pairs = [(pair, self.informative_timeframe) for pair in pairs]
        return informative_pairs

    def get_strategy(self, strategy_name):
        cached_strategy = self.loaded_strategies.get(strategy_name)
        if cached_strategy:
            return cached_strategy

        config = self.config
        config["strategy"] = strategy_name
        strategy = StrategyResolver.load_strategy(config)
        strategy.dp = self.dp
        self.loaded_strategies[strategy_name] = strategy
        return strategy

    def populate_indicators(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        return dataframe

    def populate_buy_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        strategies = STRAT_COMBINATIONS[self.buy_strategies.value]
        for strategy_name in strategies:
            strategy = self.get_strategy(strategy_name)
            strategy_indicators = strategy.advise_indicators(dataframe, metadata)
            dataframe[f"strat_buy_signal_{strategy_name}"] = strategy.advise_buy(
                strategy_indicators, metadata
            )["buy"]

        dataframe['buy'] = (
            dataframe.filter(like='strat_buy_signal_').mean(axis=1) > self.buy_mean_threshold.value
        ).astype(int)
        return dataframe

    def populate_sell_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        strategies = STRAT_COMBINATIONS[self.sell_strategies.value]
        strategies = STRATEGIES
        for strategy_name in strategies:
            strategy = self.get_strategy(strategy_name)
            strategy_indicators = strategy.advise_indicators(dataframe, metadata)
            dataframe[f"strat_sell_signal_{strategy_name}"] = strategy.advise_sell(
                strategy_indicators, metadata
            )["sell"]

        dataframe['sell'] = (
            dataframe.filter(like='strat_sell_signal_').mean(axis=1) > self.sell_mean_threshold.value
        ).astype(int)
        return dataframe
