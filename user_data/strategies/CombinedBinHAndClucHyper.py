# --- Do not remove these libs ---
import freqtrade.vendor.qtpylib.indicators as qtpylib
import numpy as np
# --------------------------------
import talib.abstract as ta
from freqtrade.strategy.interface import IStrategy
from freqtrade.strategy import CategoricalParameter, DecimalParameter, IntParameter
from abc import ABC, abstractmethod
from pandas import DataFrame


def bollinger_bands(stock_price, window_size, num_of_std):
    rolling_mean = stock_price.rolling(window=window_size).mean()
    rolling_std = stock_price.rolling(window=window_size).std()
    lower_band = rolling_mean - (rolling_std * num_of_std)
    return np.nan_to_num(rolling_mean), np.nan_to_num(lower_band)


class CombinedBinHAndClucHyper(IStrategy):
    # Based on a backtesting:
    # - the best perfomance is reached with "max_open_trades" = 2 (in average for any market),
    #   so it is better to increase "stake_amount" value rather then "max_open_trades" to get more profit
    # - if the market is constantly green(like in JAN 2018) the best performance is reached with
    #   "max_open_trades" = 2 and minimal_roi = 0.01
    timeframe = '1m'

    use_sell_signal = True
    sell_profit_only = True
    ignore_roi_if_buy_signal = False

    # ----------------------------------------------------------------
    # Hyper Params
    #
    # # Buy
    buy_a_bbdelta_rate = DecimalParameter(0.004, 0.016, default=0.016, decimals=3)
    buy_a_closedelta_rate = DecimalParameter(0.0080, 0.04, default=0.0087, decimals=4)
    buy_a_tail_rate = DecimalParameter(0.12, 0.5, default=0.28, decimals=2)
    buy_b_close_rate = DecimalParameter(0.4, 1.8, default=0.979, decimals=3)

    buy_a_time_window = IntParameter(40, 100, default=30)
    buy_volume_mean_slow_window = IntParameter(100, 300, default=30)
    buy_ema_slow = IntParameter(40, 100, default=50)
    buy_b_time_window = IntParameter(100, 300, default=20)
    buy_volume_mean_slow_num = IntParameter(10, 100, default=20)
    # Sell
    sell_bb_middleband_window = IntParameter(50, 200, default=20)

    # ----------------------------------------------------------------
    # Buy hyperspace params:
    buy_params = {
        'buy_a_bbdelta_rate': 0.016,
        'buy_a_closedelta_rate': 0.0087,
        'buy_a_tail_rate': 0.28,
        'buy_b_close_rate': 0.979,


        'buy_a_time_window': 40,
        'buy_b_time_window': 20,
        'buy_ema_slow': 50,
        'buy_volume_mean_slow_num': 20,
        'buy_volume_mean_slow_window': 30
    }

    # Sell hyperspace params:
    sell_params = {
        'sell_bb_middleband_window': 91
    }

    # ROI table:
    minimal_roi = {
        "0": 0.027,
        "2": 0.019,
        "14": 0.014,
        "23": 0
    }

    # Stoploss:
    stoploss = -0.70

    # ----------------------------------------------------------------
    # Reset Params
    buy_a_bbdelta_rate = 0.016
    buy_a_closedelta_rate = 0.0087
    buy_a_tail_rate = 0.28
    buy_b_close_rate = 0.979


    buy_a_time_window = 40
    buy_b_time_window = 20
    buy_ema_slow = 50
    buy_volume_mean_slow_num = 20
    buy_volume_mean_slow_window = 30
    sell_bb_middleband_window = 91


    def populate_indicators(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        # strategy BinHV45
        for x in self.buy_a_time_window.range if isinstance(self.buy_a_time_window, ABC) else [self.buy_a_time_window]:
            mid, lower = bollinger_bands(dataframe['close'], window_size=x, num_of_std=2)
            dataframe[f'lower_{x}'] = lower
            dataframe[f'bbdelta_{x}'] = (mid - dataframe[f'lower_{x}']).abs()
            dataframe[f'closedelta_{x}'] = (dataframe['close'] - dataframe['close'].shift()).abs()
            dataframe[f'tail_{x}'] = (dataframe['close'] - dataframe['low']).abs()

        # strategy ClucMay72018
        for x in self.buy_b_time_window.range if isinstance(self.buy_b_time_window, ABC) else [self.buy_b_time_window]:
            bollinger = qtpylib.bollinger_bands(qtpylib.typical_price(dataframe), window=x, stds=2)
            dataframe[f'bb_lowerband_{x}'] = bollinger['lower']

        for x in self.buy_ema_slow.range if isinstance(self.buy_ema_slow, ABC) else [self.buy_ema_slow]:
            dataframe[f'ema_slow_{x}'] = ta.EMA(dataframe, timeperiod=x)

        for x in self.buy_volume_mean_slow_window.range if isinstance(self.buy_volume_mean_slow_window, ABC) else [self.buy_volume_mean_slow_window]:
            dataframe[f'volume_mean_slow_{x}'] = dataframe['volume'].rolling(window=x).mean()

        for x in self.sell_bb_middleband_window.range if isinstance(self.sell_bb_middleband_window, ABC) else [self.sell_bb_middleband_window]:
            sell_bollinger = qtpylib.bollinger_bands(qtpylib.typical_price(dataframe), window=x, stds=2)
            dataframe[f'bb_middleband_{x}'] = sell_bollinger['mid']

        return dataframe

    def populate_buy_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        buy_a_time_window = self.buy_a_time_window.value if isinstance(self.buy_a_time_window, ABC) else self.buy_a_time_window
        buy_a_bbdelta_rate = self.buy_a_bbdelta_rate.value if isinstance(self.buy_a_bbdelta_rate, ABC) else self.buy_a_bbdelta_rate
        buy_a_closedelta_rate = self.buy_a_closedelta_rate.value if isinstance(self.buy_a_closedelta_rate, ABC) else self.buy_a_closedelta_rate
        buy_a_tail_rate = self.buy_a_tail_rate.value if isinstance(self.buy_a_tail_rate, ABC) else self.buy_a_tail_rate
        buy_ema_slow = self.buy_ema_slow.value if isinstance(self.buy_ema_slow, ABC) else self.buy_ema_slow
        buy_b_close_rate = self.buy_b_close_rate.value if isinstance(self.buy_b_close_rate, ABC) else self.buy_b_close_rate
        buy_b_time_window = self.buy_b_time_window.value if isinstance(self.buy_b_time_window, ABC) else self.buy_b_time_window
        buy_volume_mean_slow_window = self.buy_volume_mean_slow_window.value if isinstance(self.buy_volume_mean_slow_window, ABC) else self.buy_volume_mean_slow_window
        buy_volume_mean_slow_num = self.buy_volume_mean_slow_num.value if isinstance(self.buy_volume_mean_slow_num, ABC) else self.buy_volume_mean_slow_num

        dataframe.loc[
            (  # strategy BinHV45
                    dataframe[f'lower_{buy_a_time_window}'].shift().gt(0) &
                    dataframe[f'bbdelta_{buy_a_time_window}'].gt(dataframe['close'] * buy_a_bbdelta_rate) &
                    dataframe[f'closedelta_{buy_a_time_window}'].gt(dataframe['close'] * buy_a_closedelta_rate) &
                    dataframe[f'tail_{buy_a_time_window}'].lt(dataframe[f'bbdelta_{buy_a_time_window}'] * buy_a_tail_rate) &
                    dataframe['close'].lt(dataframe[f'lower_{buy_a_time_window}'].shift()) &
                    dataframe['close'].le(dataframe['close'].shift())
            ) |
            (  # strategy ClucMay72018
                    (dataframe['close'] < dataframe[f'ema_slow_{buy_ema_slow}']) &
                    (dataframe['close'] < buy_b_close_rate * dataframe[f'bb_lowerband_{buy_b_time_window}']) &
                    (dataframe['volume'] < (dataframe[f'volume_mean_slow_{buy_volume_mean_slow_window}'].shift(1) * buy_volume_mean_slow_num))
            ),
            'buy'
        ] = 1

        return dataframe

    def populate_sell_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        """
        """
        # dataframe.loc[(dataframe['close'] > dataframe['bb_middleband']), 'sell'] = 1
        sell_bb_middleband_window = self.sell_bb_middleband_window.value if isinstance(self.sell_bb_middleband_window, ABC) else self.sell_bb_middleband_window
        dataframe.loc[(dataframe['close'] > dataframe[f'bb_middleband_{sell_bb_middleband_window}']), 'sell'] = 1
        return dataframe