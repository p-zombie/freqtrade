from freqtrade.strategy import IStrategy, IntParameter, DecimalParameter
import logging
from pandas import DataFrame
from freqtrade.resolvers import StrategyResolver
from itertools import combinations
from functools import reduce
from functools import wraps
logger = logging.getLogger(__name__)


def suspend_logging(func):
    @wraps(func)
    def inner(*args, **kwargs):
        previousloglevel = logger.getEffectiveLevel()
        try:
            return func(*args, **kwargs)
        finally:
            logger.setLevel(previousloglevel)
    return inner


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
    "NostalgiaForInfinityV7",
]

STRAT_COMBINATIONS = reduce(
    lambda x, y: list(combinations(STRATEGIES, y)) + x, range(len(STRATEGIES)+1), []
)

MAX_COMBINATIONS = len(STRAT_COMBINATIONS) - 1


class EnsembleStrategy(IStrategy):
    loaded_strategies = {}

    buy_mean_threshold = DecimalParameter(0.0, 1, default=0.302, load=True)
    sell_mean_threshold = DecimalParameter(0.0, 1, default=0.142, load=True)
    buy_strategies = IntParameter(0, MAX_COMBINATIONS, default=8914, load=True)
    sell_strategies = IntParameter(0, MAX_COMBINATIONS, default=3369, load=True)

    # ROI table:
    minimal_roi = {
        "0": 0.137,
        "15": 0.073,
        "33": 0.011,
        "107": 0
    }

    # Stoploss:
    stoploss = -0.138

    # Trailing stop:
    trailing_stop = True
    trailing_stop_positive = 0.15
    trailing_stop_positive_offset = 0.221
    trailing_only_offset_is_reached = False

    def __init__(self, config: dict) -> None:
        super().__init__(config)
        logger.info(f"Buy stratrategies: {STRAT_COMBINATIONS[self.buy_strategies.value]}")
        logger.info(f"Sell stratrategies: {STRAT_COMBINATIONS[self.sell_strategies.value]}")

    def informative_pairs(self):
        pairs = self.dp.current_whitelist()
        informative_pairs = [(pair, self.informative_timeframe) for pair in pairs]
        return informative_pairs

    @suspend_logging
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
            logger.debug(f"buy_signals_{strategy_name}: {values}")

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
            logger.debug(f"sell_signals_{strategy_name}: {values}")

        dataframe['sell'] = (
            dataframe.filter(like='strat_sell_signal_').mean(axis=1) > self.sell_mean_threshold.value
        ).astype(int)
        return dataframe
