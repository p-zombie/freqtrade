# --- Do not remove these libs ---
from freqtrade.strategy.interface import IStrategy
from pandas import DataFrame
from functools import lru_cache
# --------------------------------

from freqtrade.resolvers import StrategyResolver


class EnsembleStrategy(IStrategy):
    stoploss = -0.99
    inf_1h = '1h'

    strategies = [
        "CombinedBinHAndClucV8",
        "CombinedBinHAndClucV8Hyper",
        "SMAOffsetV2",
        "CombinedBinHAndClucV6H",
        "BbandRsi",
        "GodStraNew",
        "CombinedBinHAndClucV7"
    ]

    @lru_cache
    def get_strategy(self, strategy_name):
        config = self.config
        config["strategy"] = strategy_name
        strategy = StrategyResolver.load_strategy(config)
        strategy.dp = self.dp
        return strategy

    def populate_indicators(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        return dataframe

    def populate_buy_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        for strategy_name in self.strategies:
            strategy = self.get_strategy(strategy_name)
            strategy_indicators = strategy.advise_indicators(dataframe, metadata)
            dataframe[f"strat_signal_{strategy_name}"] = strategy.advise_buy(strategy_indicators, metadata)["buy"]

        # Finding the mode of the decisions (most common decision).
        dataframe['buy'] = dataframe.filter(like='strat_signal_').mode(axis=1).iloc[:, 0]
        return dataframe

    def populate_sell_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        for strategy_name in self.strategies:
            strategy = self.get_strategy(strategy_name)
            strategy_indicators = strategy.advise_indicators(dataframe, metadata)
            dataframe[f"strat_signal_{strategy_name}"] = strategy.advise_sell(strategy_indicators, metadata)["sell"]

        # Finding the mode of the decisions (most common decision).
        dataframe['sell'] = dataframe.filter(like='strat_signal_').mode(axis=1).iloc[:, 0]
        return dataframe
