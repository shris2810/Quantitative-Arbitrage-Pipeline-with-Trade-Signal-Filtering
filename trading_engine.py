
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime


class PairsTradingEngine:
    def __init__(self, initial_capital=10000, ml_model=None):
        self.initial_capital = initial_capital
        self.capital = initial_capital
        self.positions = {}
        self.trade_history = []
        self.current_date = None
        self.ml_model = ml_model


    def calculate_z_score(self, price_a, price_b, pair_stats):
        current_ratio = price_a / price_b
        z_score = (current_ratio - pair_stats['ratio_mean']) / pair_stats['ratio_std']
        return z_score, current_ratio


    def should_enter_trade(self, z_score, pair_stats):
        entry_threshold = 2.0

        if abs(z_score) > entry_threshold:
            if z_score > 0:
                return 'SELL_A_BUY_B'
            else:
                return 'BUY_A_SELL_B'
        return 'HOLD'


    def calculate_position_size(self, z_score, pair_stats, current_prices):
        base_size = 1000
        intensity = min(abs(z_score) / 2.0, 3.0)
        position_value = base_size * intensity

        shares_a = int(position_value / current_prices['price_a'])
        shares_b = int(position_value / current_prices['price_b'])
        return shares_a, shares_b


    def execute_trade(self, action, stock_a, stock_b, shares_a, shares_b, current_prices, date, z_score, ml_pred):
        """Execute and print ML prediction."""

        if action == 'BUY_A_SELL_B':
            cost = shares_a * current_prices['price_a']
            proceeds = shares_b * current_prices['price_b']
            trade_type = 'BUY_A_SELL_B'
        else:
            proceeds = shares_a * current_prices['price_a']
            cost = shares_b * current_prices['price_b']
            trade_type = 'SELL_A_BUY_B'

        trade = {
            'date': date,
            'action': 'ENTER',
            'type': trade_type,
            'stock_a': stock_a,
            'stock_b': stock_b,
            'shares_a': shares_a,
            'shares_b': shares_b,
            'price_a': current_prices['price_a'],
            'price_b': current_prices['price_b'],
            'cost': cost,
            'proceeds': proceeds,
            'net_cash_flow': proceeds - cost,
            'entry_z_score': z_score
        }

        self.positions[(stock_a, stock_b)] = trade
        self.trade_history.append(trade)

        print(f"📈 {date.date()}: ENTER {trade_type} {stock_a}/{stock_b} | Z-score: {z_score:.2f}")

        # ML prediction
        if ml_pred is not None:
            if ml_pred == 1:
                print("🤖 ML Model Prediction: GOOD signal ✔️")
            else:
                print("🤖 ML Model Prediction: BAD signal ❌")

        return trade


    def should_exit_trade(self, z_score, entry_z_score):
        return abs(z_score) < 0.5


    def exit_trade(self, position_key, current_prices, date, z_score):
        pos = self.positions[position_key]
        stock_a, stock_b = position_key

        if pos['type'] == 'BUY_A_SELL_B':
            proceeds_a = pos['shares_a'] * current_prices['price_a']
            cost_b = pos['shares_b'] * current_prices['price_b']
            pnl = (proceeds_a - pos['cost']) + (pos['proceeds'] - cost_b)
        else:
            cost_a = pos['shares_a'] * current_prices['price_a']
            proceeds_b = pos['shares_b'] * current_prices['price_b']
            pnl = (pos['proceeds'] - cost_a) + (proceeds_b - pos['cost'])

        exit_trade = {
            'date': date,
            'action': 'EXIT',
            'type': pos['type'],
            'stock_a': stock_a,
            'stock_b': stock_b,
            'price_a': current_prices['price_a'],
            'price_b': current_prices['price_b'],
            'pnl': pnl,
            'exit_z_score': z_score,
            'return_pct': (pnl / abs(pos['net_cash_flow'])) * 100 if pos['net_cash_flow'] != 0 else 0,
            'holding_days': (date - pos['date']).days
        }

        self.trade_history.append(exit_trade)
        del self.positions[position_key]

        print(f"📉 {date.date()}: EXIT {pos['type']} {stock_a}/{stock_b} | P&L: ${pnl:.2f}")

        return exit_trade



def backtest_pairs_trading(price_data, trading_pairs, initial_capital=10000, ml_model=None):

    engine = PairsTradingEngine(initial_capital, ml_model)

    for date in price_data.index[30:]:
        for pair in trading_pairs:

            stock_a = pair['stock_a']
            stock_b = pair['stock_b']

            current_prices = {
                'price_a': price_data.loc[date, stock_a],
                'price_b': price_data.loc[date, stock_b]
            }

            z_score, _ = engine.calculate_z_score(current_prices['price_a'], current_prices['price_b'], pair)

            # ML prediction features
            features = [
                z_score,
                pair['ratio_mean'],
                pair['ratio_std'],
                pair['correlation']
            ]


            ml_pred = None
            if ml_model:
                try:
                    feature_names = ["entry_z_score", "exit_z_score", "return_pct", "holding_days"]

                    df_features = pd.DataFrame([[
                        z_score,  # entry_z_score
                        0,        # exit_z_score (unknown yet)
                        0,        # return_pct (future)
                        0         # holding_days (future)
                    ]], columns=feature_names)

                    ml_pred = ml_model.predict(df_features)[0]

                except Exception as e:
                    print("ML Prediction Error:", str(e))
                    ml_pred = None


            # ENTER
            if (stock_a, stock_b) not in engine.positions:
                action = engine.should_enter_trade(z_score, pair)
                if action != 'HOLD':
                    sh_a, sh_b = engine.calculate_position_size(z_score, pair, current_prices)
                    engine.execute_trade(action, stock_a, stock_b, sh_a, sh_b, current_prices, date, z_score, ml_pred)

            # EXIT
            else:
                entry_z = engine.positions[(stock_a, stock_b)]["entry_z_score"]
                if engine.should_exit_trade(z_score, entry_z):
                    engine.exit_trade((stock_a, stock_b), current_prices, date, z_score)

    return engine
