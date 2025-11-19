# 📈 TwinTrade — ML-Enhanced Pairs Trading Engine

A complete **Pairs Trading System** that uses:

* Statistical analysis (correlation, cointegration, z-score)
* Automated trading engine
* Backtesting framework
* A lightweight **ML model** to classify signals as **GOOD / BAD**
* A fully automated pipeline that downloads data → analyzes pairs → backtests → trains ML → evaluates signals

This project is ideal for **quant beginners**, **DSA/ML learners**, and **trading enthusiasts** building practical quant projects.

---

# 🚀 Features

### ✅ 1. **Automated Data Download**

Downloads 20+ stocks from Yahoo Finance using `yfinance` and saves:

```
stock_prices.csv
trading_pairs.csv
```

---

### ✅ 2. **Correlation & Cointegration Analysis**

Finds:

* Highly correlated stock pairs
* Cointegrated pairs using the **Engle-Granger test**
* Price ratio + mean reversion z-score

---

### ✅ 3. **Pairs Trading Engine**

Implements:

* Z-score based entry signals
* Long/short hedged positions
* Exit rules
* Position sizing
* Trade logging
* P&L calculations

All trades are printed during backtest:

```
📈 ENTER TRADE...
📉 EXIT TRADE...
```

---

### ✅ 4. **Machine Learning Signal Classifier**

After running the backtest once, the system:

* Collects all EXIT trades
* Labels them as profitable / non-profitable
* Trains a simple ML model (Logistic Regression)
* Saves model as `ml_model.pkl`
* Uses the ML model to classify future signals:

```
🤖 ML Model Prediction: GOOD signal ✔️
```

---

### ✅ 5. **Backtest Results Dashboard**

Backtest logs include:

* Total trades
* Winning vs losing trades
* Win rate
* Total P&L
* Avg trade P&L
* Equity curve plot
* Individual P&L bar chart
* CSV export of full trade log

---

# 📁 Project Structure

```
📦 TwinTrade
│
├── correlation_analysis.py    # Finds correlations, cointegration, ratios
├── find_pair.py               # Prepares list of tradable pairs
├── trading_engine.py          # Core trading engine + ML inference integration
├── ml_filter.py               # ML model training + saving/loading
├── main.py                    # Full automated pipeline entry point
│
├── stock_prices.csv           # Auto-generated price data
├── trading_pairs.csv          # Auto-generated best pairs
├── trading_log.csv            # Auto-generated backtest log
├── ml_model.pkl               # Saved ML model
│
└── README.md                  # Project documentation
```

---

# 🧠 How the ML Model Works

The ML model is **not used to decide trades**.
The strategy still relies on:

* Z-score
* Cointegration
* Ratio divergence

The ML model adds **extra validation**:

> “Based on past trades, is this type of signal usually GOOD or BAD?”

Inputs used during prediction:

| Feature       | Meaning                           |
| ------------- | --------------------------------- |
| entry_z_score | How extreme the pair was at entry |
| exit_z_score  | (set to 0 during prediction)      |
| return_pct    | (unknown yet → 0)                 |
| holding_days  | (unknown yet → 0)                 |

It’s a lightweight model intentionally designed to be simple and fast.

---

# 🔧 Setup Instructions

### **1️⃣ Install dependencies**

```
pip install -r requirements.txt
```

Or manually:

```
pip install pandas numpy matplotlib yfinance statsmodels scikit-learn
```

---

### **2️⃣ Run the full pipeline**

```
python main.py
```

This will:

```
✓ Download stock data
✓ Analyze correlations & cointegration
✓ Generate trading pairs
✓ Run backtest
✓ Train ML model
✓ Run final backtest with ML predictions
✓ Print insights
```

---

# 📊 Sample Output (Shortened)

```
=== CORRELATION ANALYSIS ===
AAPL - SPY: 0.687
MSFT - META: 0.620
XOM - CVX: 0.806

=== COINTEGRATION RESULTS ===
GLD - IAU: p-value = 0.0010 (Cointegrated)

=== BACKTEST ===
📈 2024-03-15: ENTER SELL_A_BUY_B SPY / IVV | Z-score: 2.97
🤖 ML Model Prediction: GOOD signal ✔️

📉 2024-03-22: EXIT SELL_A_BUY_B SPY/IVV | P&L: $1.81
```

---

# 📈 Example: ML-Enhanced Trade Print

```
📈 2024-06-03: ENTER BUY_A_SELL_B BRK-B / BRK-A | Z-score: -2.50
🤖 ML Model Prediction: BAD signal ❌
```


Just tell me!
