#!/usr/bin/env python3
import yfinance as yf
import pandas as pd
from pathlib import Path
import matplotlib.pyplot as plt


def run_pipeline(ticker: str, start_date: str, end_date: str, output_dir: Path):

    try:
        # Fetch historical stock data
        data = yf.download(
            ticker,
            start=start_date,
            end=end_date,
            progress=False,
            auto_adjust=True,
            group_by="column"
             )

        # Check if data exists
        if data.empty:
            print(f"No data found for {ticker} between {start_date} and {end_date}.")
            return None
        close_prices = data['Close'].squeeze()

        # Calculate moving averages
        data['MA20'] = data['Close'].rolling(window=20).mean()
        data['MA50'] = data['Close'].rolling(window=50).mean()
        plt.figure(figsize=(12, 6))
        plt.plot(data.index, close_prices, label='Close Price')
        plt.plot(data.index, data['MA20'], label='20-day MA')
        plt.plot(data.index, data['MA50'], label='50-day MA')
        plt.legend()
        plt.title(f"{ticker} Price and Moving Averages")
        plt.xlabel("Date")
        plt.ylabel("Price")
        plt.grid()
        plt.savefig(output_dir / f"{ticker}_price_ma.png")
        plt.close()
        delta = close_prices.diff()
        gain = delta.where(delta > 0, 0)
        loss = -delta.where(delta < 0, 0)
        avg_gain = gain.rolling(window=14).mean()
        avg_loss = loss.rolling(window=14).mean()
        rs = avg_gain / avg_loss
        data['RSI'] = 100 - (100 / (1 + rs))

        # Initialize signal column
        data['Signal'] = 0

        # Buy condition
        buy_condition = (
            (data['MA20'] > data['MA50']) &
            (data['MA20'].shift(1) <= data['MA50'].shift(1))
        )

        # Sell condition
        sell_condition = (
            (data['MA20'] < data['MA50']) &
            (data['MA20'].shift(1) >= data['MA50'].shift(1))
        )

        # Apply signals
        data.loc[buy_condition, 'Signal'] = 1
        data.loc[sell_condition, 'Signal'] = -1

        # Check today's signal
        today_signal = int(data['Signal'].iloc[-1])
        today_price = float(data['Close'].squeeze().iloc[-1])

        print(f"Today's signal for {ticker}: {today_signal} at price {today_price:.2f}")

        if today_signal == 1:
            print(f"Strategy: BUY signal for {ticker}")

        elif today_signal == -1:
            print(f"Strategy: SELL signal for {ticker}")

        else:
            print(f"No clear signal for {ticker}")

        # Check enough data
        if pd.isna(data['MA20'].iloc[-1]) or pd.isna(data['MA50'].iloc[-1]):
            print(f"Not enough data to generate signals for {ticker}.")
            return None

        # Save CSV inside output directory
        output_file = output_dir / f"{ticker}_processed_data.csv"

        data.to_csv(output_file)

        print(f"Processed data saved to {output_file.resolve()}")

        return {
            "ticker": ticker,
            "today_signal": today_signal,
            "today_price": today_price
        }

    except Exception as e:
        print(f"An error occurred: {e}")
        return None


if __name__ == "__main__":

    watchlist = ["AAPL", "MSFT", "GOOGL", "AMZN", "TSLA"]

    output_dir = Path("./market_data")
    output_dir.mkdir(exist_ok=True)

    print("Running pipeline for watchlist...")

    results = []

    for stock in watchlist:

        result = run_pipeline(
            stock,
            "2020-01-01",
            "2021-01-01",
            output_dir
        )

        if result:
            results.append(result)

    # Save summary CSV
    pd.DataFrame(results).to_csv(
        output_dir / "watchlist_signals.csv",
        index=False
    )

    print("----- Pipeline completed successfully -----")
           
        
    