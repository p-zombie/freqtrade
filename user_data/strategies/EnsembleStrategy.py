from freqtrade.strategy import IStrategy, IntParameter, DecimalParameter
import logging
from pandas import DataFrame
from freqtrade.resolvers import StrategyResolver
from itertools import combinations
from functools import reduce

logger = logging.getLogger(__name__)


STRATEGIES = [
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
]

STRAT_COMBINATIONS = reduce(
    lambda x, y: list(combinations(STRATEGIES, y)) + x, range(len(STRATEGIES)+1), []
)

MAX_COMBINATIONS = len(STRAT_COMBINATIONS) - 1


class EnsembleStrategy(IStrategy):
    loaded_strategies = {}

    stoploss = -0.20
    buy_mean_threshold = DecimalParameter(0.0, 1, default=0.5, load=True)
    sell_mean_threshold = DecimalParameter(0.0, 1, default=0.5, load=True)
    buy_strategies = IntParameter(0, MAX_COMBINATIONS, default=0, load=True)
    sell_strategies = IntParameter(0, MAX_COMBINATIONS, default=0, load=True)

    def __init__(self, config: dict) -> None:
        super().__init__(config)
        logger.info(f"Buy stratrategies: {STRAT_COMBINATIONS[self.buy_strategies.value]}")
        logger.info(f"Sell stratrategies: {STRAT_COMBINATIONS[self.sell_strategies.value]}")

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
        return dataframe

    def populate_buy_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        strategies = STRAT_COMBINATIONS[self.buy_strategies.value]
        for strategy_name in strategies:
            strategy = self.get_strategy(strategy_name)
            strategy_indicators = strategy.advise_indicators(dataframe, metadata)
            dataframe[f"strat_buy_signal_{strategy_name}"] = strategy.advise_buy(
                strategy_indicators, metadata
            )["buy"]
            values = dataframe[f"strat_buy_signal_{strategy_name}"].tolist()
            logger.info(f"buy_signals_{strategy_name}: {values}")

        dataframe['buy'] = (
            dataframe.filter(like='strat_buy_signal_').mean(axis=1) > self.buy_mean_threshold.value
        ).astype(int)
        return dataframe

    def populate_sell_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        strategies = STRAT_COMBINATIONS[self.sell_strategies.value]
        for strategy_name in strategies:
            strategy = self.get_strategy(strategy_name)
            strategy_indicators = strategy.advise_indicators(dataframe, metadata)
            dataframe[f"strat_sell_signal_{strategy_name}"] = strategy.advise_sell(
                strategy_indicators, metadata
            )["sell"]
            values = dataframe[f"strat_sell_signal_{strategy_name}"].tolist()
            logger.info(f"sell_signals_{strategy_name}: {values}")

        dataframe['sell'] = (
            dataframe.filter(like='strat_sell_signal_').mean(axis=1) > self.sell_mean_threshold.value
        ).astype(int)
        return dataframe
