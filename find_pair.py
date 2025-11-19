
import yfinance as yf
import pandas as pd

def find_stocks_that_move_together():
    stock_universe = {
        'tech': ['AAPL', 'MSFT', 'GOOGL', 'META'],
        'soda': ['KO', 'PEP'],
        'retail': ['WMT', 'TGT'],
        'banks': ['JPM', 'BAC'],
        'oil': ['XOM', 'CVX'],
        'tech': ['AAPL', 'MSFT', 'GOOGL', 'META'],
        'etf_pairs': ['SPY', 'IVV', 'GLD', 'IAU'],
        'classes': ['GOOG', 'GOOGL', 'BRK-B', 'BRK-A']
    }
    

    all_data = {}

    for sector, stocks in stock_universe.items():
        for stock in stocks:
            print(f"Downloading {stock}...")

            # MORE RELIABLE THAN yf.download()
            data = yf.Ticker(stock).history(period="2y")

            # Check empty
            if data.empty:
                print(f"⚠️ No data found for {stock}. Skipping...")
                continue

            # Extract Close price
            all_data[stock] = data["Close"]

    # Build DataFrame
    price_data = pd.DataFrame(all_data)
    price_data.to_csv("stock_prices.csv")
    print("✔ Data saved to stock_prices.csv")

    return price_data


if __name__ == "__main__":
    price_data = find_stocks_that_move_together()
    print(price_data.head())
