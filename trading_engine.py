# 3_trading_engine.py
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime, timedelta

class PairsTradingEngine:
    def __init__(self, initial_capital=10000):
        self.initial_capital = initial_capital
        self.capital = initial_capital
        self.positions = {}
        self.trade_history = []
        self.current_date = None
        
    def calculate_z_score(self, price_a, price_b, pair_stats):
        """Calculate how extreme the current relationship is"""
        current_ratio = price_a / price_b
        z_score = (current_ratio - pair_stats['ratio_mean']) / pair_stats['ratio_std']
        return z_score, current_ratio
    
    def should_enter_trade(self, z_score, pair):
        """Decide if we should enter a trade based on z-score"""
        entry_threshold = 2.0  # Enter when |z-score| > 2
        exit_threshold = 0.5   # Exit when |z-score| < 0.5
        
        if abs(z_score) > entry_threshold:
            if z_score > 0:
                return 'SELL_A_BUY_B'  # A is overvalued relative to B
            else:
                return 'BUY_A_SELL_B'  # A is undervalued relative to B
        return 'HOLD'
    
    def calculate_position_size(self, z_score, pair_stats, current_prices):
        """Calculate how much to bet based on z-score intensity"""
        base_size = 1000  # Base position size
        intensity = min(abs(z_score) / 2.0, 3.0)  # Cap at 3x
        
        position_value = base_size * intensity
        
        # For demonstration, we'll use fixed share quantities
        shares_a = int(position_value / current_prices['price_a'])
        shares_b = int(position_value / current_prices['price_b'])
        
        return shares_a, shares_b
    
    def execute_trade(self, action, stock_a, stock_b, shares_a, shares_b, current_prices, date, z_score):
        """Execute a pairs trading transaction"""
        
        if action == 'BUY_A_SELL_B':
            # Buy stock A, Short stock B
            cost = shares_a * current_prices['price_a']
            short_proceeds = shares_b * current_prices['price_b']
            
            trade = {
                'date': date,
                'action': 'ENTER',
                'type': 'BUY_A_SELL_B',
                'stock_a': stock_a,
                'stock_b': stock_b,
                'shares_a': shares_a,
                'shares_b': shares_b,
                'price_a': current_prices['price_a'],
                'price_b': current_prices['price_b'],
                'cost': cost,
                'proceeds': short_proceeds,
                'net_cash_flow': short_proceeds - cost,  # Positive if short proceeds > long cost
                'entry_z_score': z_score
            }
            
        elif action == 'SELL_A_BUY_B':
            # Short stock A, Buy stock B
            short_proceeds = shares_a * current_prices['price_a']
            cost = shares_b * current_prices['price_b']
            
            trade = {
                'date': date,
                'action': 'ENTER',
                'type': 'SELL_A_BUY_B',
                'stock_a': stock_a,
                'stock_b': stock_b,
                'shares_a': shares_a,
                'shares_b': shares_b,
                'price_a': current_prices['price_a'],
                'price_b': current_prices['price_b'],
                'cost': cost,
                'proceeds': short_proceeds,
                'net_cash_flow': short_proceeds - cost,
                'entry_z_score': z_score
            }
        
        self.positions[(stock_a, stock_b)] = trade
        self.trade_history.append(trade)
        
        print(f"📈 {date.strftime('%Y-%m-%d')}: ENTER {trade['type']} "
              f"{stock_a}({shares_a} shares) / {stock_b}({shares_b} shares) "
              f"| Z-score: {z_score:.2f}")
        
        return trade
    
    def should_exit_trade(self, z_score, entry_z_score):
        """Decide if we should exit a trade"""
        exit_threshold = 0.5
        
        # Exit if z-score has normalized
        if abs(z_score) < exit_threshold:
            return True
        
        # Exit if trade goes against us (z-score moves further away)
        if (entry_z_score > 0 and z_score > entry_z_score * 1.5) or \
           (entry_z_score < 0 and z_score < entry_z_score * 1.5):
            return True
            
        return False
    
    def exit_trade(self, position_key, current_prices, date, z_score):
        """Close an existing position"""
        position = self.positions[position_key]
        stock_a, stock_b = position_key
        
        if position['type'] == 'BUY_A_SELL_B':
            # Sell stock A, Buy back stock B
            proceeds_a = position['shares_a'] * current_prices['price_a']
            cost_b = position['shares_b'] * current_prices['price_b']
            
            pnl = (proceeds_a - position['cost']) + (position['proceeds'] - cost_b)
            
        else:  # SELL_A_BUY_B
            # Buy back stock A, Sell stock B
            cost_a = position['shares_a'] * current_prices['price_a']
            proceeds_b = position['shares_b'] * current_prices['price_b']
            
            pnl = (position['proceeds'] - cost_a) + (proceeds_b - position['cost'])
        
        exit_trade = {
            'date': date,
            'action': 'EXIT',
            'type': position['type'],
            'stock_a': stock_a,
            'stock_b': stock_b,
            'price_a': current_prices['price_a'],
            'price_b': current_prices['price_b'],
            'pnl': pnl,
            'return_pct': (pnl / abs(position['net_cash_flow'])) * 100 if position['net_cash_flow'] != 0 else 0,
            'exit_z_score': z_score,
            'holding_days': (date - position['date']).days
        }
        
        self.trade_history.append(exit_trade)
        del self.positions[position_key]
        
        print(f"📉 {date.strftime('%Y-%m-%d')}: EXIT {exit_trade['type']} "
              f"{stock_a}/{stock_b} | P&L: ${pnl:.2f} ({exit_trade['return_pct']:.1f}%)")
        
        return exit_trade

def backtest_pairs_trading(price_data, trading_pairs, initial_capital=10000):
    """Backtest the pairs trading strategy"""
    
    engine = PairsTradingEngine(initial_capital)
    
    print("🚀 STARTING PAIRS TRADING BACKTEST")
    print("=" * 60)
    
    # Convert trading_pairs to dictionary for easy access
    pair_stats = {}
    for pair in trading_pairs:
        key = (pair['stock_a'], pair['stock_b'])
        pair_stats[key] = {
            'ratio_mean': pair['ratio_mean'],
            'ratio_std': pair['ratio_std'],
            'correlation': pair['correlation'],
            'coint_pvalue': pair['coint_pvalue']
        }
    
    # Run through each trading day
    for date in price_data.index[30:]:  # Skip first month for stability
        engine.current_date = date
        
        # Check each pair for trading opportunities
        for pair_key, stats in pair_stats.items():
            stock_a, stock_b = pair_key
            
            # Get current prices
            current_prices = {
                'price_a': price_data.loc[date, stock_a],
                'price_b': price_data.loc[date, stock_b]
            }
            
            # Calculate current z-score
            z_score, current_ratio = engine.calculate_z_score(
                current_prices['price_a'], 
                current_prices['price_b'], 
                stats
            )
            
            # Check if we have an existing position
            if pair_key in engine.positions:
                # Check if we should exit
                entry_trade = engine.positions[pair_key]
                entry_z_score = entry_trade.get('entry_z_score', 0)
                
                if engine.should_exit_trade(z_score, entry_z_score):
                    engine.exit_trade(pair_key, current_prices, date, z_score)
            
            else:
                # Check if we should enter a new trade
                action = engine.should_enter_trade(z_score, stats)
                
                if action != 'HOLD':
                    shares_a, shares_b = engine.calculate_position_size(z_score, stats, current_prices)
                    
                    engine.execute_trade(action, stock_a, stock_b, shares_a, shares_b, current_prices, date, z_score)
    
    print("=" * 60)
    print("✅ BACKTEST COMPLETE")
    
    return engine

def analyze_backtest_results(trading_engine, price_data):
    """Analyze and visualize backtest results"""
    
    print("\n📊 BACKTEST RESULTS ANALYSIS")
    print("=" * 50)
    
    # Convert trade history to DataFrame
    trades_df = pd.DataFrame(trading_engine.trade_history)
    
    if trades_df.empty:
        print("No trades were executed during the backtest period.")
        return None
    
    # Calculate performance metrics
    entry_trades = trades_df[trades_df['action'] == 'ENTER']
    exit_trades = trades_df[trades_df['action'] == 'EXIT']
    
    total_trades = len(exit_trades)
    winning_trades = len(exit_trades[exit_trades['pnl'] > 0])
    losing_trades = len(exit_trades[exit_trades['pnl'] < 0])
    
    total_pnl = exit_trades['pnl'].sum()
    avg_trade_pnl = exit_trades['pnl'].mean()
    win_rate = (winning_trades / total_trades * 100) if total_trades > 0 else 0
    
    print(f"Total Trades: {total_trades}")
    print(f"Winning Trades: {winning_trades} ({win_rate:.1f}%)")
    print(f"Losing Trades: {losing_trades}")
    print(f"Total P&L: ${total_pnl:.2f}")
    print(f"Average Trade P&L: ${avg_trade_pnl:.2f}")
    
    # Plot equity curve
    plt.figure(figsize=(12, 8))
    
    # Calculate cumulative P&L over time
    exit_trades_sorted = exit_trades.sort_values('date')
    exit_trades_sorted['cumulative_pnl'] = exit_trades_sorted['pnl'].cumsum()
    
    plt.subplot(2, 1, 1)
    plt.plot(exit_trades_sorted['date'], exit_trades_sorted['cumulative_pnl'], 
             linewidth=2, color='blue', label='Cumulative P&L')
    plt.axhline(0, color='black', linestyle='-', alpha=0.3)
    plt.title('Pairs Trading Strategy - Equity Curve')
    plt.ylabel('Cumulative P&L ($)')
    plt.legend()
    plt.grid(True, alpha=0.3)
    
    # Plot individual trade P&L
    plt.subplot(2, 1, 2)
    colors = ['green' if pnl > 0 else 'red' for pnl in exit_trades_sorted['pnl']]
    plt.bar(range(len(exit_trades_sorted)), exit_trades_sorted['pnl'], color=colors, alpha=0.7)
    plt.title('Individual Trade P&L')
    plt.xlabel('Trade Number')
    plt.ylabel('P&L ($)')
    plt.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig('backtest_results.png', dpi=300, bbox_inches='tight')
    plt.show()
    
    # Save detailed trade log
    trades_df.to_csv('trading_log.csv', index=False)
    print(f"✅ Detailed trade log saved to: trading_log.csv")
    
    return {
        'total_trades': total_trades,
        'winning_trades': winning_trades,
        'losing_trades': losing_trades,
        'win_rate': win_rate,
        'total_pnl': total_pnl,
        'avg_trade_pnl': avg_trade_pnl
    }



def main():
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

if __name__ == "__main__":
    main()