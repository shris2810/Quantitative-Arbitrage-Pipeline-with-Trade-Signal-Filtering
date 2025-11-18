# 2_correlation_analysis.py
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from statsmodels.tsa.stattools import coint

def analyze_correlations(price_data):
    """STEP 2: Find which stocks move together"""
    
    print("=== CORRELATION ANALYSIS ===")
    
    # Calculate daily returns (percentage changes)
    returns = price_data.pct_change().dropna()
    
    # Calculate correlation matrix
    correlation_matrix = returns.corr()
    
    # Display the correlation matrix
    print("\nCorrelation Matrix:")
    print(correlation_matrix.round(3))
    
    # Visualize correlations
    plt.figure(figsize=(12, 10))
    sns.heatmap(correlation_matrix, annot=True, cmap='coolwarm', center=0,
                square=True, fmt='.3f')
    plt.title('Stock Return Correlations')
    plt.tight_layout()
    plt.savefig('correlation_heatmap.png')
    plt.show()
    
    return correlation_matrix, returns

def find_highly_correlated_pairs(correlation_matrix, threshold=0.6):
    """Find stock pairs with high correlation"""
    
    print(f"\n=== HIGHLY CORRELATED PAIRS (>{threshold}) ===")
    
    highly_correlated_pairs = []
    
    # Get all unique pairs
    stocks = correlation_matrix.columns
    for i in range(len(stocks)):
        for j in range(i + 1, len(stocks)):
            stock_a = stocks[i]
            stock_b = stocks[j]
            corr = correlation_matrix.iloc[i, j]
            
            if abs(corr) > threshold:
                highly_correlated_pairs.append({
                    'stock_a': stock_a,
                    'stock_b': stock_b,
                    'correlation': corr,
                    'sector': f"{stock_a}-{stock_b}"
                })
                print(f"{stock_a} - {stock_b}: {corr:.3f}")
    
    return highly_correlated_pairs

def test_cointegration(price_data, pairs):
    """STEP 3: Test for cointegration (long-term relationship)"""
    
    print("\n=== COINTEGRATION TESTING ===")
    
    cointegrated_pairs = []
    
    for pair in pairs:
        stock_a = pair['stock_a']
        stock_b = pair['stock_b']
        
        # Get price series
        series_a = price_data[stock_a].dropna()
        series_b = price_data[stock_b].dropna()
        
        # Align the series (same dates)
        common_dates = series_a.index.intersection(series_b.index)
        series_a_aligned = series_a.loc[common_dates]
        series_b_aligned = series_b.loc[common_dates]
        
        # Test for cointegration
        coint_stat, pvalue, _ = coint(series_a_aligned, series_b_aligned)
        
        print(f"{stock_a} - {stock_b}: p-value = {pvalue:.4f}")
        
        # If p-value < 0.05, they are cointegrated (strong long-term relationship)
        if pvalue < 0.05:
            pair['coint_pvalue'] = pvalue
            pair['coint_stat'] = coint_stat
            cointegrated_pairs.append(pair)
            print(f"  ✅ COINTEGRATED! (strong long-term relationship)")
        else:
            print(f"  ❌ Not cointegrated")
    
    return cointegrated_pairs

def calculate_price_ratio(price_data, pairs):
    """Calculate and visualize price ratios for cointegrated pairs"""
    
    print("\n=== PRICE RATIO ANALYSIS ===")
    
    for pair in pairs:
        stock_a = pair['stock_a']
        stock_b = pair['stock_b']
        
        # Calculate price ratio
        ratio = price_data[stock_a] / price_data[stock_b]
        
        # Calculate statistics
        mean_ratio = ratio.mean()
        std_ratio = ratio.std()
        
        pair['ratio_mean'] = mean_ratio
        pair['ratio_std'] = std_ratio
        pair['current_ratio'] = ratio.iloc[-1]
        
        print(f"\n{stock_a}/{stock_b}:")
        print(f"  Mean ratio: {mean_ratio:.3f}")
        print(f"  Std dev: {std_ratio:.3f}")
        print(f"  Current: {ratio.iloc[-1]:.3f}")
        print(f"  Z-score: {(ratio.iloc[-1] - mean_ratio) / std_ratio:.2f}")
        
        # Plot the ratio
        plt.figure(figsize=(12, 6))
        
        plt.subplot(1, 2, 1)
        plt.plot(ratio, label=f'{stock_a}/{stock_b} Ratio')
        plt.axhline(mean_ratio, color='red', linestyle='--', label='Mean')
        plt.axhline(mean_ratio + std_ratio, color='orange', linestyle='--', alpha=0.7, label='+1 Std')
        plt.axhline(mean_ratio - std_ratio, color='orange', linestyle='--', alpha=0.7, label='-1 Std')
        plt.title(f'{stock_a}/{stock_b} Price Ratio')
        plt.legend()
        plt.xticks(rotation=45)
        
        plt.subplot(1, 2, 2)
        # Scatter plot to show relationship
        plt.scatter(price_data[stock_a], price_data[stock_b], alpha=0.5)
        plt.xlabel(stock_a)
        plt.ylabel(stock_b)
        plt.title(f'{stock_a} vs {stock_b} Scatter')
        
        plt.tight_layout()
        plt.savefig(f'ratio_{stock_a}_{stock_b}.png')
        plt.show()
    
    return pairs

def main():
    # Load your data from Step 1
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

if __name__ == "__main__":
    main()

'''# 2_correlation_analysis_FIXED.py
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from statsmodels.tsa.stattools import coint

def clean_and_align_data(price_data):
    """Clean the data and handle missing values"""
    print("=== CLEANING DATA ===")
    
    # Drop rows with too many missing values
    cleaned_data = price_data.dropna()
    
    print(f"Original shape: {price_data.shape}")
    print(f"After cleaning: {cleaned_data.shape}")
    print(f"Columns with NaN: {price_data.isna().sum().sum()}")
    
    return cleaned_data

def analyze_correlations(price_data):
    """STEP 2: Find which stocks move together"""
    
    print("=== CORRELATION ANALYSIS ===")
    
    # Calculate daily returns (percentage changes)
    returns = price_data.pct_change().dropna()
    
    # Calculate correlation matrix
    correlation_matrix = returns.corr()
    
    # Display the correlation matrix
    print("\nCorrelation Matrix:")
    print(correlation_matrix.round(3))
    
    # Visualize correlations
    plt.figure(figsize=(12, 10))
    sns.heatmap(correlation_matrix, annot=True, cmap='coolwarm', center=0,
                square=True, fmt='.3f')
    plt.title('Stock Return Correlations')
    plt.tight_layout()
    plt.savefig('correlation_heatmap.png')
    plt.show()
    
    return correlation_matrix, returns

def find_highly_correlated_pairs(correlation_matrix, threshold=0.6):
    """Find stock pairs with high correlation"""
    
    print(f"\n=== HIGHLY CORRELATED PAIRS (>{threshold}) ===")
    
    highly_correlated_pairs = []
    
    # Get all unique pairs
    stocks = correlation_matrix.columns
    for i in range(len(stocks)):
        for j in range(i + 1, len(stocks)):
            stock_a = stocks[i]
            stock_b = stocks[j]
            corr = correlation_matrix.iloc[i, j]
            
            if abs(corr) > threshold:
                highly_correlated_pairs.append({
                    'stock_a': stock_a,
                    'stock_b': stock_b,
                    'correlation': corr,
                    'sector': f"{stock_a}-{stock_b}"
                })
                print(f"{stock_a} - {stock_b}: {corr:.3f}")
    
    # Sort by correlation strength
    highly_correlated_pairs.sort(key=lambda x: abs(x['correlation']), reverse=True)
    
    return highly_correlated_pairs

def test_cointegration(price_data, pairs):
    """STEP 3: Test for cointegration (long-term relationship)"""
    
    print("\n=== COINTEGRATION TESTING ===")
    
    cointegrated_pairs = []
    
    for pair in pairs:
        stock_a = pair['stock_a']
        stock_b = pair['stock_b']
        
        # Get price series
        series_a = price_data[stock_a]
        series_b = price_data[stock_b]
        
        # Test for cointegration
        try:
            coint_stat, pvalue, _ = coint(series_a, series_b)
            
            print(f"{stock_a} - {stock_b}: p-value = {pvalue:.4f}")
            
            # If p-value < 0.05, they are cointegrated (strong long-term relationship)
            if pvalue < 0.05:
                pair['coint_pvalue'] = pvalue
                pair['coint_stat'] = coint_stat
                cointegrated_pairs.append(pair)
                print(f"  ✅ COINTEGRATED! (strong long-term relationship)")
            else:
                print(f"  ❌ Not cointegrated")
        except Exception as e:
            print(f"  ❌ Error testing {stock_a}-{stock_b}: {e}")
    
    return cointegrated_pairs

def calculate_price_ratio(price_data, pairs):
    """Calculate and visualize price ratios for cointegrated pairs"""
    
    print("\n=== PRICE RATIO ANALYSIS ===")
    
    analyzed_pairs = []
    
    for pair in pairs:
        stock_a = pair['stock_a']
        stock_b = pair['stock_b']
        
        try:
            # Calculate price ratio
            ratio = price_data[stock_a] / price_data[stock_b]
            
            # Calculate statistics
            mean_ratio = ratio.mean()
            std_ratio = ratio.std()
            current_z = (ratio.iloc[-1] - mean_ratio) / std_ratio
            
            pair['ratio_mean'] = mean_ratio
            pair['ratio_std'] = std_ratio
            pair['current_ratio'] = ratio.iloc[-1]
            pair['current_z'] = current_z
            
            print(f"\n{stock_a}/{stock_b}:")
            print(f"  Mean ratio: {mean_ratio:.3f}")
            print(f"  Std dev: {std_ratio:.3f}")
            print(f"  Current: {ratio.iloc[-1]:.3f}")
            print(f"  Z-score: {current_z:.2f}")
            
            # Plot the ratio
            plt.figure(figsize=(12, 6))
            
            plt.subplot(1, 2, 1)
            plt.plot(ratio.index, ratio.values, label=f'{stock_a}/{stock_b} Ratio')
            plt.axhline(mean_ratio, color='red', linestyle='--', label='Mean')
            plt.axhline(mean_ratio + std_ratio, color='orange', linestyle='--', alpha=0.7, label='+1 Std')
            plt.axhline(mean_ratio - std_ratio, color='orange', linestyle='--', alpha=0.7, label='-1 Std')
            plt.title(f'{stock_a}/{stock_b} Price Ratio\nZ-score: {current_z:.2f}')
            plt.legend()
            plt.xticks(rotation=45)
            
            plt.subplot(1, 2, 2)
            # Scatter plot to show relationship
            plt.scatter(price_data[stock_a], price_data[stock_b], alpha=0.5)
            plt.xlabel(stock_a)
            plt.ylabel(stock_b)
            plt.title(f'{stock_a} vs {stock_b} Scatter')
            
            plt.tight_layout()
            plt.savefig(f'ratio_{stock_a}_{stock_b}.png', dpi=150, bbox_inches='tight')
            plt.show()
            
            analyzed_pairs.append(pair)
            
        except Exception as e:
            print(f"Error analyzing {stock_a}-{stock_b}: {e}")
    
    return analyzed_pairs

def expand_stock_universe():
    """Add more stocks to get better pairs"""
    print("\n=== EXPANDING STOCK UNIVERSE ===")
    
    additional_pairs = {
        'tech': ['AAPL', 'MSFT', 'GOOGL', 'META', 'NVDA', 'AMD'],
        'banks': ['JPM', 'BAC', 'WFC', 'C'],
        'oil': ['XOM', 'CVX', 'COP', 'SLB'],
        'retail': ['WMT', 'TGT', 'COST', 'HD'],
        'soda': ['KO', 'PEP'],
        'pharma': ['PFE', 'JNJ', 'MRK'],
        'auto': ['F', 'GM'],
        'airlines': ['DAL', 'UAL', 'AAL']
    }
    
    return additional_pairs

def main():
    # Load your data from Step 1
    price_data = pd.read_csv('stock_prices.csv', index_col=0, parse_dates=True)
    
    # Clean the data first
    price_data = clean_and_align_data(price_data)
    
    # If we don't have enough good pairs, let's download more data
    if len(price_data.columns) < 8:
        print("Not enough stocks with good data. Let's download more...")
        # We'll handle this in the next step
    
    # Step 2: Correlation analysis
    correlation_matrix, returns = analyze_correlations(price_data)
    
    # Try different correlation thresholds
    for threshold in [0.6, 0.5, 0.4]:
        print(f"\n{'='*50}")
        print(f"TRYING THRESHOLD: {threshold}")
        print('='*50)
        
        # Step 3: Find highly correlated pairs
        highly_correlated = find_highly_correlated_pairs(correlation_matrix, threshold=threshold)
        
        if not highly_correlated:
            print("No pairs found at this threshold.")
            continue
            
        # Step 4: Test for cointegration
        cointegrated_pairs = test_cointegration(price_data, highly_correlated)
        
        if cointegrated_pairs:
            # Step 5: Analyze price ratios
            final_pairs = calculate_price_ratio(price_data, cointegrated_pairs)
            
            # Save the best pairs for trading
            pairs_df = pd.DataFrame(final_pairs)
            pairs_df.to_csv('trading_pairs.csv', index=False)
            print(f"\n🎉 Found {len(final_pairs)} trading pairs! Saved to trading_pairs.csv")
            
            print("\n=== BEST TRADING PAIRS ===")
            for pair in final_pairs:
                print(f"{pair['stock_a']} - {pair['stock_b']}: "
                      f"corr={pair['correlation']:.3f}, "
                      f"p-value={pair['coint_pvalue']:.4f}, "
                      f"current_z={pair['current_z']:.2f}")
            break
    else:
        print("\n❌ No suitable trading pairs found with any threshold.")
        print("\nLet's try with more stocks...")
        
        # We'll need to download more data
        download_more_stocks()

def download_more_stocks():
    """Download additional stocks to find better pairs"""
    print("\n=== DOWNLOADING ADDITIONAL STOCKS ===")
    
    additional_stocks = [
        'NVDA', 'AMD',  # More tech
        'WFC', 'C',     # More banks  
        'COP', 'SLB',   # More oil
        'COST', 'HD',   # More retail
        'PFE', 'JNJ',   # Pharma
        'F', 'GM',      # Auto
        'DAL', 'UAL'    # Airlines
    ]
    
    from datetime import datetime, timedelta
    import yfinance as yf
    
    end_date = datetime.now()
    start_date = end_date - timedelta(days=730)
    
    new_data = {}
    for stock in additional_stocks:
        try:
            print(f"Downloading {stock}...")
            data = yf.download(stock, start=start_date, end=end_date)
            new_data[stock] = data['Close']
        except Exception as e:
            print(f"Error downloading {stock}: {e}")
    
    # Combine with existing data
    existing_data = pd.read_csv('stock_prices.csv', index_col=0, parse_dates=True)
    new_df = pd.DataFrame(new_data)
    combined_data = pd.concat([existing_data, new_df], axis=1)
    combined_data = combined_data.dropna()
    
    combined_data.to_csv('expanded_stock_prices.csv')
    print("Expanded data saved to expanded_stock_prices.csv")
    
    return combined_data

if __name__ == "__main__":
    main()'''