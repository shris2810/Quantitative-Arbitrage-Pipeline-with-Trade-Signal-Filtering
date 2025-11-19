
import pandas as pd

from find_pair import find_stocks_that_move_together 
from correlation_analysis import analyze_correlations, find_highly_correlated_pairs, test_cointegration, calculate_price_ratio
from trading_engine import backtest_pairs_trading
from ml_filter import load_model, train_ml_model


def main():

    price_data = find_stocks_that_move_together()
    price_data = pd.read_csv("stock_prices.csv", index_col=0, parse_dates=True)

    correlation_matrix, returns = analyze_correlations(price_data)
    high_corr = find_highly_correlated_pairs(correlation_matrix, threshold=0.6)
    cointegrated = test_cointegration(price_data, high_corr)
    final_pairs = calculate_price_ratio(price_data, cointegrated)

    pd.DataFrame(final_pairs).to_csv("trading_pairs.csv", index=False)
    trading_pairs = pd.read_csv("trading_pairs.csv").to_dict("records")

    print("\n🔄 BACKTEST #1: Building history...")
    engine = backtest_pairs_trading(price_data, trading_pairs)

    print("\n🤖 TRAINING ML MODEL...")
    ml_model = train_ml_model(engine.trade_history)

    print("\n🔄 BACKTEST #2: With ML Predictions...")
    backtest_pairs_trading(price_data, trading_pairs, ml_model=ml_model)

    print("\n🎉 Done! Check console for ML predictions for each trade.")


if __name__ == "__main__":
    main()
