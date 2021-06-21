"""
WeightedMultiparameterHyperOptLoss.py V 0.3
-by Cybergrany

A loss function for Freqtrade's hyperopt feature, which allowes the user
to choose weights, which influence how much each parameter affects the objective.
For example, if I want quick trades and don't care too much about risk, I would
give more weight to trades and less to the sortino.
Most of the code here is based on existing freqtrade code, namely the sortino
function and max drawdown calculations. I've just added a way to incorporate
these into one function.
Known issues:
- keep weights reasonably low - use 1 as a baseline. Hyperopt doesn't
seem to like it when the objective gets close or above 100 (see next issue)
- if you don't see any "Best epochs" within the first 30 epochs, then the
loss function either too sensitive or not sensitive enough.
I don't recommend continuing the hyperopt in this case as it'll never find
an optimal epoch. Instead, think about if your weights and expected values
make sense.
---------------------HOW TO USE-----------------------
Set your EXPECTED paramater to something that makes sense.
There's no point setting profit to 9000% thinking that it'll magicaly make
you a lambo owner.
All values are ratios, so 1.65 = 165%
A good way of using the EXPECTED parameter is if you have a strategy and
you know it can make X profit, but you want to see if you can push it that
extra bit more, so maybe set the profit to X + 25%
Also, say this strategy leaves you with a drawdown of 150%. You can try setting
the EXPECTED DRAWDOWN to 0.8 to see if Hyperopt can narrow down your signals to reach
a better drawdown.
***
    A reccomendation re expected sortino: if you run a hyperopt with the freqtrade
    SortinoHyperOptLossDaily function, then the objective of that is the inverse of my
    hyperopt value.
    Example: if I've run a hyperopt using SortinoHyperOptLossDaily and the best epoch
    is giving an objective of  -20, then I might set the EXPECTED_SORTINO here to 25
    to try and get a slightly better value
***
I've also added THRESHOLD, which essentially tells hyperopt "this is a really unoptimal
value" by increasing the objective a bit more. This is incredibly useful for narrowing
down optimal results.

    Example: PROFIT_THRESHOLD_LOW:  If below this profit, then that's very bad.
    Example: EXPECTED_PROFIT = 4.5 (450%), PROFIT_THRESHOLD = 0.5
    In this case, if we get a profit below 2.25/225% (0.5 of our
    expected profit), we punish the hyperopt.

I suggest starting with a wide range on your thresholds to get an idea of what direction your
strategy likes to lean towards, then using them to hone in on paramaters you'd like to improve.

The thresholds I'm using assume that outside LOW or HIGH is a bad value If LOW, we punish
hyperopt when below that value. Vice-versa for HIGH. If you don't want a certain threshold,
you can set LOW to 0 and High to something insane like 1000.0
NOTE THAT LOW THRESHOLDS ASSUME YOU WANT A VALUE <100%(<0.99), I HAVEN'T TESTED ANYTHING ELSE
---------------------OTHER-----------------------
If any of the weights don't matter to you, just set the weight to 0 and they'll
have no effect.
This function makes the assumption that you want shorter and less trades, if you want it
to hyperopt towards longer and more trades negate the weights as commented below. (I haven't
tested this)
I've also added a commented-out print statement that spits out the values and
calculated weights. This can be very helpful for working out expected parameters,
or to see why hyperopt thinks an epoch that looks good to you isn't actually that
great. Reccomended to use with --print-all, but it will mess up freqtrade's default
output a bit.

This is not financial advice etc etc I am not responsible for any bad decisions
this thing makes.
Happy HyperOpting :)
"""
import math
from datetime import datetime

from pandas import DataFrame, date_range

from freqtrade.optimize.hyperopt import IHyperOptLoss

from freqtrade.data.btanalysis import (calculate_max_drawdown)

"""
CUSTOMIZABLE PARAMETER START
"""
EXPECTED_TRADE_DURATION = 60  # Duration in minutes
DUR_WEIGHT = 1.2  # Not using thresholds here, but if needed you can copy the below code

EXPECTED_DRAWDOWN = 0.8
DD_WEIGHT = 1.7
DD_THRESHOLD_HIGH = 2.0
DD_THRESHOLD_LOW = 0.2

EXPECTED_SORTINO = 42
SORT_WEIGHT = 0.8
SORT_THRESHOLD_HIGH = 2.5
SORT_THRESHOLD_LOW = 0.2

EXPECTED_PROFIT = 12.0
EXPECTED_PROFIT_WEIGHT = 1.6
PROFIT_THRESHOLD_HIGH = 1000.0
PROFIT_THRESHOLD_LOW = 0.42

EXPECTED_TRADES = 1500
EXPECTED_TRADES_WEIGHT = 0.8
TRADE_THRESHOLD_HIGH = 2.0
TRADE_THRESHOLD_LOW = 0.55


"""
CUSTOMIZABLE PARAMETER END
"""


class WeightedMultiParameterHyperOptLoss(IHyperOptLoss):

    @staticmethod
    def hyperopt_loss_function(results: DataFrame, trade_count: int,
                               min_date: datetime, max_date: datetime,
                               *args, **kwargs) -> float:
        """
        Sortino Loss function from Freqtrade Project
        Objective function, returns smaller number for more optimal results.
        Uses Sortino Ratio calculation.
        Sortino Ratio calculated as described in
        http://www.redrockcapital.com/Sortino__A__Sharper__Ratio_Red_Rock_Capital.pdf
        """
        resample_freq = '1D'
        slippage_per_trade_ratio = 0.0005
        days_in_year = 365
        minimum_acceptable_return = 0.0

        # apply slippage per trade to profit_ratio
        results.loc[:, 'profit_ratio_after_slippage'] = \
            results['profit_ratio'] - slippage_per_trade_ratio

        # create the index within the min_date and end max_date
        t_index = date_range(start=min_date, end=max_date, freq=resample_freq,
                             normalize=True)

        sum_daily = (
            results.resample(resample_freq, on='close_date').agg(
                {"profit_ratio_after_slippage": sum}).reindex(t_index).fillna(0)
        )
        total_profit = sum_daily["profit_ratio_after_slippage"] - minimum_acceptable_return
        expected_returns_mean = total_profit.mean()

        sum_daily['downside_returns'] = 0
        sum_daily.loc[total_profit < 0, 'downside_returns'] = total_profit
        total_downside = sum_daily['downside_returns']
        # Here total_downside contains min(0, P - MAR) values,
        # where P = sum_daily["profit_ratio_after_slippage"]
        down_stdev = math.sqrt((total_downside**2).sum() / len(total_downside))
        if down_stdev != 0:
            sortino_ratio = expected_returns_mean / down_stdev * math.sqrt(days_in_year)
        else:
            # Define high (negative) sortino ratio to be clear that this is NOT optimal.
            sortino_ratio = -20.

        # Calculate max drawdown
        try:
            max_drawdown, _, _, _, _ = calculate_max_drawdown(
                results, value_col='profit_ratio')
        except ValueError:
            max_drawdown = 0.0

        total_profit = results['profit_ratio'].sum()
        trade_duration = results['trade_duration'].mean()

        """
        Calculate weights and objective value.
        Note that a lower objective is good, so if we want a paramater to go up, we must output
        the inverse of its weight function.
        """

        # Assuming shorter dur is better, negate the below if you prefer aiming for longer
        duration_weight = DUR_WEIGHT * trade_duration / EXPECTED_TRADE_DURATION

        # Assuming LESS trades are better, to reverse see below note.
        tradeno = EXPECTED_TRADES_WEIGHT * (trade_count/EXPECTED_TRADES)
        if tradeno < TRADE_THRESHOLD_LOW:
            tradeno_weight = (1 - tradeno) * 2
        elif tradeno > TRADE_THRESHOLD_HIGH:
            tradeno_weight = tradeno  # Swap this...
        else:
            tradeno_weight = (-tradeno)  # With this...

        # Higher profit is better
        prof = EXPECTED_PROFIT_WEIGHT * (total_profit/EXPECTED_PROFIT)
        if prof < PROFIT_THRESHOLD_LOW:
            profit_weight = (1 - prof) * 2
        elif prof > PROFIT_THRESHOLD_HIGH:
            profit_weight = prof
        else:
            profit_weight = (-prof)

        # Higher sortino is better
        sortino = SORT_WEIGHT * (sortino_ratio/EXPECTED_SORTINO)
        if sortino > SORT_THRESHOLD_HIGH:
            sortino_weight = (sortino)
        elif sortino < SORT_THRESHOLD_LOW:
            sortino_weight = (1 - sortino) * 2
        else:
            sortino_weight = (-sortino)

        # Lower DD is better
        drawdown = DD_WEIGHT * (max_drawdown/EXPECTED_DRAWDOWN)
        if drawdown < DD_THRESHOLD_LOW:
            drawdown_weight = (1 - drawdown) * 2
        elif drawdown > DD_THRESHOLD_HIGH:
            drawdown_weight = drawdown * 1.25
        else:
            drawdown_weight = drawdown

        if trade_duration is None:
            trade_duration = 0.0

        if duration_weight is None:
            duration_weight = 0.0

        return sortino_weight+drawdown_weight+duration_weight+profit_weight+tradeno_weight
