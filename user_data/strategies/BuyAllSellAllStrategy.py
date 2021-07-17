from freqtrade.strategy.interface import IStrategy
from pandas import DataFrame


class BuyAllSellAllStrategy(IStrategy):
    stoploss = -0.25
    timeframe = '5m'

    def populate_indicators(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        return dataframe

    def populate_buy_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        dataframe["buy"] = 1
        return dataframe

    def populate_sell_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        dataframe["sell"] = 1
        return dataframe
