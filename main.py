import pandas as pd

from find_pair import find_stocks_that_move_together 
from correlation_analysis import analyze_correlations,find_highly_correlated_pairs,test_cointegration,calculate_price_ratio
from trading_engine import analyze_backtest_results,backtest_pairs_trading
# from ml_filter import integrate_ml_with_trading

price_data = find_stocks_that_move_together()

price_data = pd.read_csv('stock_prices.csv', index_col=0, parse_dates=True)

# Step 2: Correlation analysis
correlation_matrix, returns = analyze_correlations(price_data)

# Step 3: Find highly correlated pairs
highly_correlated = find_highly_correlated_pairs(correlation_matrix, threshold=0.6)

# Step 4: Test for cointegration
cointegrated_pairs = test_cointegration(price_data, highly_correlated)

# Step 5: Analyze price ratios
final_pairs = calculate_price_ratio(price_data, cointegrated_pairs)

# Save the best pairs for trading
pairs_df = pd.DataFrame(final_pairs)
if not pairs_df.empty:
    pairs_df.to_csv('trading_pairs.csv', index=False)
    print(f"\n🎉 Found {len(final_pairs)} trading pairs! Saved to trading_pairs.csv")
    
    print("\n=== BEST TRADING PAIRS ===")
    for pair in final_pairs:
        z_score = (pair['current_ratio'] - pair['ratio_mean']) / pair['ratio_std']
        print(f"{pair['stock_a']} - {pair['stock_b']}: "
                f"corr={pair['correlation']:.3f}, "
                f"p-value={pair['coint_pvalue']:.4f}, "
                f"current_z={z_score:.2f}")
else:
    print("\n❌ No suitable trading pairs found. Try lowering correlation threshold.")

# Load price data and trading pairs
price_data = pd.read_csv('stock_prices.csv', index_col=0, parse_dates=True)
trading_pairs = pd.read_csv('trading_pairs.csv').to_dict('records')

print("Loaded trading pairs:")
for pair in trading_pairs:
    print(f"  {pair['stock_a']} - {pair['stock_b']} "
            f"(corr: {pair['correlation']:.3f}, p-value: {pair['coint_pvalue']:.4f})")

# Run backtest
trading_engine = backtest_pairs_trading(price_data, trading_pairs)

# Analyze results
results = analyze_backtest_results(trading_engine, price_data)

print("\n🎯 TRADING STRATEGY INSIGHTS:")
print("=" * 40)
if results and results['total_trades'] > 0:
    if results['win_rate'] > 60:
        print("✅ Strategy appears profitable!")
    else:
        print("⚠️ Strategy needs optimization")
    
    print(f"💡 Key Insight: Your pairs are mean-reverting with {results['win_rate']:.1f}% accuracy")
else:
    print("❌ No trading signals generated. Consider:")
    print("   - Adjusting z-score thresholds")
    print("   - Adding more volatile pairs")
    print("   - Extending the backtest period")



# Initialize ML filter (auto-loads or trains from your backtest data)
# ml_filter = integrate_ml_with_trading()

# # Pass to your trading engine
# # should_enter_trade(self, z_score, pair_stats, ml_filter=None)
# results = run_backtest(price_data, trading_pairs, ml_filter=ml_filter)