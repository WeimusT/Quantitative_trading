import os
from datetime import datetime
import pandas as pd
import matplotlib.pyplot as plt
import yfinance as yf

def plot_candle_stick(df:pd.DataFrame, price_col:list=["Open", "High", "Low", "Close"], **kwargs) -> None:
    """Plot the candle stick chart.
    
    Parameters
    ----------
    df: pandas.DataFrame
        The data.
    price_col: list
        The column name for Open, High, Low and Close in sequence.
    
    Returns
    -------
    None
    """
    stock_prices = df.copy()
    stock_prices.rename({
        price_col[0]:"open",
        price_col[1]:"high",
        price_col[2]:"low",
        price_col[3]:"close"
    }, axis=1, inplace=True)
    # Keyword arguments
    figsize=[10, 5] if "figsize" not in kwargs else kwargs["figsize"]
    title='Stock Prices' if "title" not in kwargs else kwargs["title"]
    # Plot
    plt.figure(figsize=figsize)
    # Create a new DataFrame called "up" that stores the stock_prices
    # when the closing stock price is greater than or equal to the opening stock price
    up = stock_prices[stock_prices.close >= stock_prices.open]
    # Create a new DataFrame called "down" that stores the stock_prices
    # when the closing stock price is lesser than the opening stock price
    down = stock_prices[stock_prices.close < stock_prices.open]
    # When the stock prices have decreased, then it
    # will be represented by red color candlestick
    col1 = 'red'
    # When the stock prices have increased, then it
    # will be represented by green color candlestick
    col2 = 'green'
    # Set the width of candlestick elements
    width = 0.4
    width2 = 0.05
    # Plot the up prices of the stock
    plt.bar(up.index, up.close-up.open, width, bottom=up.open, color=col2)
    plt.bar(up.index, up.high-up.close, width2, bottom=up.close, color=col2)
    plt.bar(up.index, up.low-up.open, width2, bottom=up.open, color=col2)
    # Plot the down prices of the stock
    plt.bar(down.index, down.close-down.open, width, bottom=down.open, color=col1)
    plt.bar(down.index, down.high-down.open, width2, bottom=down.open, color=col1)
    plt.bar(down.index, down.low-down.close, width2, bottom=down.close, color=col1)
    # Rotate the x-axis tick labels at 45 degrees towards right
    plt.xticks(rotation=45, ha='right')
    # Display the candlestick chart of stock data
    plt.title(title)
    plt.xlabel('Date')
    plt.ylabel('Price (USD)')
    plt.show()

def download_yf(ticker:str, period:str, interval:str="1d", path:str=None) -> pd.DataFrame:
    """Download OHLC data from yahoo finance.

    Parameters
    ----------
    ticker: str
        Ticker.
    period: str
        Length of the data, e.g. '2y', '1mo'.
    interval: str
        Data interval, e.g. '1d' for daily data.
    path: str
        The path to save the data. The data is saved as CSV. If not specified then
        the data is not saved.

    Returns
    -------
    pandas.DataFrame
    """
    tenb_ticker = yf.Ticker(ticker)
    tenb_df = tenb_ticker.history(period=period, interval=interval, auto_adjust=True)
    if path is not None:
        # Save to local
        first_date = datetime.strftime(tenb_df.index.min(), "%Y%m%d")
        last_date = datetime.strftime(tenb_df.index.max(), "%Y%m%d")
        filename = "%s_%s_%s_%s.csv" % (ticker.lower(), first_date, last_date, interval.lower())
        filepath = os.path.join(path, filename)
        tenb_df.to_csv(filepath, index=True)
    return tenb_df