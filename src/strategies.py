"""Strategies
* All strategies extends from the class bt.Strategy
"""
from __future__ import (absolute_import, division, print_function, unicode_literals)
from datetime import datetime
import os
import sys
import logging
from argparse import ArgumentParser
from matplotlib import pyplot as plt

import backtrader as bt

# Set project folder
_PROJECT_FOLDER = "/Users/wtai/Projects/Quantitative_trading/"
sys.path.append(_PROJECT_FOLDER)

# Logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
LOG_LEVEL = logging.DEBUG


class TestStrategy(bt.Strategy):
    """A test strategy that buys the stock when it has been falling
    in the past three days.
    """
    # Parameters
    params = (
        ('exitbars', 5),
    )
    
    def log(self, txt:str, dt:datetime=None) -> None:
        """Print text to console."""
        dt = dt or self.datas[0].datetime.date(0)
        print("%s, %s" % (dt.isoformat(), txt))
    
    def __init__(self):
        # Keep a reference to the "close" line in the data[0] data series.
        self.dataclose = self.datas[0].close
        # Keep track of the current pending order and buy price/commission
        self.order = None
        self.buyprice = None
        self.buycomm = None
    
    def notify_order(self, order):
        """The strategy is notified on the change of order status. The status change
        can be one of 'Submitted', 'Accepted', 'Completed', 'Canceled', 'Margin', 
        or 'Rejected'. This method works as a callback function. The order is passed 
        in as a parameter.

        Parameters
        ----------
        order: Any
            The order whose status is changed. This param is passed in from the system.
        
        Returns
        -------
        None

        Questions
        ---------
        * What is the 'Margin' order status?
        """
        if order.status in [order.Submitted, order.Accepted]:
            # Do nothing when a order is submitted to or accepted by the broker.
            return
        elif order.status in [order.Completed]:
            # Print out the order execution status for a completed buy or sell order.
            if order.isbuy():
                # Buy order executed
                self.log(
                    'BUY EXECUTED, Price: %.2f, Cost: %.2f, Comm %.2f' % 
                    (order.executed.price,
                     order.executed.value,
                     order.executed.comm)
                )
                self.buyprice = order.executed.price
                self.buycomm = order.executed.comm
            elif order.issell():
                # Sell order executed
                self.log(
                    'SELL EXECUTED, Price: %.2f, Cost: %.2f, Comm: %.2f' % 
                    (order.executed.price,
                     order.executed.value,
                     order.executed.comm)
                )
            # Keep a reference of the system clock when an order is executed.
            # The bar_executed can be understood as the elapsed periods
            # since the backtesting started.
            self.bar_executed = len(self)
            self.log("ORDER EXECUTED at %i-th bar" % self.bar_executed)
        elif order.status in [order.Canceled, order.Margin, order.Rejected]:
            self.log("Order Canceled/Margin/Rejected")
        # Set the pending order to none when the order status is Completed,
        # Canceled, Margin, or Rejected.
        self.order = None

    def notify_trade(self, trade):
        """Callback function which is called by the system when the backtesting finishes.
        
        Parameters
        ----------
        trade: Any

        Returns
        -------
        None
        """
        if not trade.isclosed:
            return
        self.log(
            "Operation profit, Gross %.2f, Net %.2f" %
            (trade.pnl, trade.pnlcomm)
        )

    def next(self):
        """This methods is called on each bar of the system clock. In the Backtrader 
        jargon a *bar* is a period - 1 minute, 1 hour, 1 day, 1 week or another time 
        period. This is the major place where the strategy logic is implemented.
        
        Questions
        ---------
        * What is the system clock?
        """
        self.log("Close, %.2f" % self.dataclose[0])
        if self.order is not None:
            # Do nothing at the bar when there is a pending order.
            # The order can be a buy or a sell order.
            return
        if not self.position:
            # Only buy in when hold no shares of this stock.
            if self.dataclose[0] < self.dataclose[-1]:
                # Current close is less than previous close. Note that
                # the subscript 0, -1 and -2 are relative to the current
                # system clock.
                if self.dataclose[-1] < self.dataclose[-2]:
                    # Create a buy order using the closing pricing of
                    # the current system clock. Keep a reference of the
                    # order. A default buy order is a 'market buy order'
                    # - it buys in at the openning price of the next bar
                    # regardless what it is. Similarly, a default sell 
                    # order is a 'market sell order' and would be executed
                    # at the next bar openning price regardless what it is.
                    # In contrast, a limit order is only executed when the
                    # price hit the price set with the order.
                    self.log("BUY CREATE, %.2f" % self.dataclose[0])
                    self.order = self.buy()
        else:
            # Check if the exit criteria is met when hold shares.
            if len(self) >= (self.bar_executed + self.params.exitbars):
                # Sell the stock after holding it for 5 periods since the last
                # recorded bar. Create a sell order using the closing price of
                # the current bar. Update the order reference.
                self.log("SELL CREATED. %.2f" % self.dataclose[0])
                self.order = self.sell()


class MaStrategy(bt.Strategy):
    """Moving Average Strategy.
    """
    # Parameters
    params = (
        # 3 weeks moving average
        ('maperiod', 15),
        ('printlog', False),
    )
    
    def log(self, txt:str, dt:datetime=None, doprint:bool=False) -> None:
        """Print text to console."""
        if self.params.printlog or doprint:
            dt = dt or self.datas[0].datetime.date(0)
            print("%s, %s" % (dt.isoformat(), txt))
    
    def __init__(self):
        # Keep a reference to the "close" line in the data[0] data series.
        self.dataclose = self.datas[0].close
        # Keep track of the current pending order and buy price/commission
        self.order = None
        self.buyprice = None
        self.buycomm = None
        # Trading indicator
        self.sma = bt.indicators.MovingAverageSimple(
            self.datas[0], period=self.params.maperiod
        )
        # Informational indicators (for plotting)
        bt.indicators.ExponentialMovingAverage(self.datas[0], period=25)
        bt.indicators.WeightedMovingAverage(self.datas[0], period=25, subplot=True)
        bt.indicators.StochasticFast(self.datas[0])
        bt.indicators.MACDHisto(self.datas[0])
        rsi = bt.indicators.RSI(self.datas[0])
        bt.indicators.SmoothedMovingAverage(rsi, period=10)
        bt.indicators.ATR(self.datas[0], plot=False)
    
    def notify_order(self, order):
        """The strategy is notified on the change of order status. The status change
        can be one of 'Submitted', 'Accepted', 'Completed', 'Canceled', 'Margin', 
        or 'Rejected'. This method works as a callback function. The order is passed 
        in as a parameter.

        Parameters
        ----------
        order: Any
            The order whose status is changed. This param is passed in from the system.
        
        Returns
        -------
        None

        Questions
        ---------
        * What is the 'Margin' order status?
        """
        if order.status in [order.Submitted, order.Accepted]:
            # Do nothing when a order is submitted to or accepted by the broker.
            return
        elif order.status in [order.Completed]:
            # Print out the order execution status for a completed buy or sell order.
            if order.isbuy():
                # Buy order executed
                self.log(
                    'BUY EXECUTED, Price: %.2f, Cost: %.2f, Comm %.2f' % 
                    (order.executed.price,
                     order.executed.value,
                     order.executed.comm)
                )
                self.buyprice = order.executed.price
                self.buycomm = order.executed.comm
            elif order.issell():
                # Sell order executed
                self.log(
                    'SELL EXECUTED, Price: %.2f, Cost: %.2f, Comm: %.2f' % 
                    (order.executed.price,
                     order.executed.value,
                     order.executed.comm)
                )
            # Keep a reference of the system clock when an order is executed.
            # The bar_executed can be understood as the elapsed periods
            # since the backtesting started.
            self.bar_executed = len(self)
            self.log("ORDER EXECUTED at %i-th bar" % self.bar_executed)
        elif order.status in [order.Canceled, order.Margin, order.Rejected]:
            self.log("Order Canceled/Margin/Rejected")
        # Set the pending order to none when the order status is Completed,
        # Canceled, Margin, or Rejected.
        self.order = None

    def notify_trade(self, trade):
        """Callback function which is called by the system when the backtesting finishes.
        
        Parameters
        ----------
        trade: Any

        Returns
        -------
        None
        """
        if not trade.isclosed:
            return
        self.log(
            "Operation profit, Gross %.2f, Net %.2f" %
            (trade.pnl, trade.pnlcomm)
        )

    def next(self):
        """This methods is called on each bar of the system clock. In the Backtrader 
        jargon a *bar* is a period - 1 minute, 1 hour, 1 day, 1 week or another time 
        period.
        
        Questions
        ---------
        * What is the system clock?
        """
        self.log("Close, %.2f" % self.dataclose[0])
        if self.order is not None:
            # Do nothing at the bar when there is a pending order.
            # The order can be a buy or a sell order.
            return
        if not self.position:
            # Only buy in when hold no shares of this stock.
            if self.dataclose[0] > self.sma[0]:
                # Current close is above the 15 day moving average.
                    self.log("BUY CREATE, %.2f" % self.dataclose[0])
                    self.order = self.buy()
        else:
            # Check if the exit criteria is met when hold shares.
            if self.dataclose[0] < self.sma[0]:
                # Current close is below the 15 day moving average.
                self.log("SELL CREATED. %.2f" % self.dataclose[0])
                self.order = self.sell()

    def stop(self):
        """"""
        self.log('(MA Period %2d) Ending Value %.2f' %
                 (self.params.maperiod, self.broker.getvalue()), doprint=True)

class KDJStrategy(bt.Strategy):
    """KDJ Strategy."""
    @staticmethod
    def percent(today, yesterday):
        return float(today - yesterday) / today
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(LOG_LEVEL)

        self.data_close = self.datas[0].close
        self.volume = self.datas[0].volume

        self.order = None
        self.buyprice = None
        self.buycomm = None

        # Highest high in 9 days
        self.high_nine = bt.indicators.Highest(self.data.high, period=9)
        # Lowest low in 9 days
        self.low_nine = bt.indicators.Lowest(self.data.low, period=9)
        # Relative Strength Value (RSV)
        self.rsv = 100 * bt.DivByZero(self.data_close - self.low_nine, self.high_nine - self.low_nine)
        # K is 3-period EMA of RSV
        self.K = bt.indicators.ExponentialMovingAverage(self.rsv, period=3)
        # D is 3-period EMA of K
        self.D = bt.indicators.ExponentialMovingAverage(self.K, period=3)
        # J = 3*K+2*D
        self.J = 3 * self.K - 2 * self.D
    
    def notify_order(self, order):
        """A callback function after order is completed."""
        if order.status in [order.Submitted, order.Accepted]:
            return
        elif order.status in [order.Completed]:
            if order.isbuy():
                self.logger.info(
                    "BUY EXECUTED, Price: %.2f, Cost: %.2f, Comm %.2f" 
                     % (order.executed.price, order.executed.value, order.executed.comm)
                )
                self.buyprice = order.executed.price
                self.buycomm = order.executed.comm
                self.bar_executed_close = self.data_close[0]
            else:
                self.logger.info(
                    "SELL EXECUTED, Price: %.2f, Cost: %.2f, Comm %.2f"
                    % (order.executed.price, order.executed.value, order.executed.comm)
                )
            self.bar_executed = len(self)
        elif order.status in [order.Canceled, order.Margin, order.Rejected]:
            self.logger.info("ORDER CANCELED/MARGIN/REJECTED")
        self.order = None
    
    def notify_trade(self, trade):
        if not trade.isclosed:
            return
        self.logger.info("OPERATION PROFIT, GROSS %.2f, NET %.2f" % (trade.pnl, trade.pnlcomm))
    
    def next(self):
        self.logger.info("Close, %.2f" % self.data_close[0])
        if self.order:
            return
        condition1 = self.J[-1] - self.D[-1]
        condition2 = self.J[0] - self.D[0]
        if not self.position:
            # J - D
            if condition1 < 0 and condition2 > 0:
                self.logger.info("BUY CREATE, %.2f" % self.data_close[0])
                self.order = self.buy()
        else:
            if condition1 > 0 or condition2 < 0:
                self.logger.info("SELL CREATED. %.2f" % self.data_close[0])
                self.order = self.sell()

def run(strategy, dataname, plot=0, optimize=0):
    """Test run a strategy.
    
    Parameters
    ----------
    strategy: class
        The strategy class
    dataname: str
        File name of the test data, e.g. 'TENB_20210527_20230526_1d.csv'. Only 
        YahooFinance csv files are supported.
    
    Returns
    -------
    None
    """
    # Data file
    # Create Cerebro engine.
    cerebro = bt.Cerebro()
    if optimize != 0:
        # Optimize strategy
        cerebro.optstrategy(strategy, maperiod=range(10, 31))
    else:
        # Add a strategy
        cerebro.addstrategy(strategy)
    # Crate a data object from local CSV data downloaded from YahooFinance.
    # The YahooFinanceCSVData does not comply with today's YahooFinance data.
    # Hence use GenericCSVData instead.
    data = bt.feeds.GenericCSVData(
        dataname=os.path.join(_PROJECT_FOLDER, "data", dataname),
        # Datetime format
        dtformat='%Y-%m-%d %H:%M:%S%z',
        # Do not pass values before this date.
        fromdate=datetime(2021, 5, 27),
        # Do not pass values after this date.
        todate=datetime(2023, 5, 26),
        # Datetime column position
        datetime=0,
        # Time column not exist (-1)
        time=-1,
        # Open column position
        open=1,
        # High column position
        high=2,
        # Low column position
        low=3,
        # Close column position
        close=4,
        # Volume column position
        volume=5,
        # Reverse ordered
        reverse=False
    )
    # Add data object to the Cerebro engine.
    cerebro.adddata(data)
    # Set the initial cash value.
    cerebro.broker.setcash(1e5)
    # Sizer seems to be the amount of shares to buy or sell per order.
    cerebro.addsizer(bt.sizers.FixedSize, stake=10)
    # Set the commision to be 0.1%. Degiro has a fixed 2$ commission per transaction for US stocks.
    cerebro.broker.setcommission(commission=1e-3)
    # Run backtesting
    print("Starting Portfolio Value: %.2f" % cerebro.broker.getvalue())
    cerebro.run()
    print("Final Portfolio Value: %.2f" % cerebro.broker.getvalue())
    if plot != 0:
        cerebro.plot()

if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument("--strategy", type=str)
    parser.add_argument("--dataname", type=str)
    parser.add_argument("--optimize", default=0, type=int)
    parser.add_argument("--plot", default=0, type=int)
    args = parser.parse_args()
    class_ = getattr(sys.modules[__name__], args.strategy)
    run(
        strategy=class_, 
        dataname=args.dataname,
        plot=args.plot,
        optimize=args.optimize
    )