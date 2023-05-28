"""Strategies
"""

import datetime
import os.path
import sys
import logging
from argparse import ArgumentParser
from matplotlib import pyplot as plt

import backtrader as bt

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
LOG_LEVEL = logging.DEBUG

class KDJStrategy(bt.Strategy):
    """"""
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

def run(strategy, dataname):
    cerebro = bt.Cerebro()
    cerebro.addstrategy(strategy)
    data = bt.feeds.GenericCSVData(
        dataname=dataname,
        dtformat='%Y-%m-%d %H:%M:%S%z',
        datetime=0,
        time=-1,
        open=1,
        high=2,
        low=3,
        close=4,
        volume=5
    )
    cerebro.adddata(data)
    cerebro.broker.setcash(10000)
    cerebro.addsizer(bt.sizers.FixedSize, stake=100)
    cerebro.broker.setcommission(commission=5e-3)
    logger.info("START PORTFOLIO VALUE: %.2f" % cerebro.broker.getvalue())
    cerebro.run()
    logger.info("FINAL PORTFOLIO VALUE: %.2f" % cerebro.broker.getvalue())
    cerebro.plot()

if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument("--dataname", type=str)
    args = parser.parse_args()
    run(KDJStrategy, args.dataname)