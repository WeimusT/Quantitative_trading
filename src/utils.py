import pandas as pd
import matplotlib.pyplot as plt

def plot_candle_stick(df, price_col=["Open", "High", "Low", "Close"], **kwargs):
    """Plot the candle stick chart.
    Args
    ----
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