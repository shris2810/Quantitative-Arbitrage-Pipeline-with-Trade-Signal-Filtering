
import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
import pickle
import os

MODEL_PATH = "ml_pair_trading_model.pkl"


def train_ml_model(trade_history):
    """Train ML model from past trading history safely (no NaNs)."""

    df = pd.DataFrame(trade_history)
    df = df[df["action"] == "EXIT"]  # Only EXIT trades have PnL

    if df.empty:
        print("⚠️ Not enough data to train ML model.")
        return None

    df["label"] = (df["pnl"] > 0).astype(int)

    features = ["entry_z_score", "exit_z_score", "return_pct", "holding_days"]

    # Convert to numeric & fill NaNs
    for col in features:
        df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)

    X = df[features]
    y = df["label"]

    model = Pipeline([
        ("scaler", StandardScaler()),
        ("clf", LogisticRegression(max_iter=1000))
    ])

    model.fit(X, y)
    pickle.dump(model, open(MODEL_PATH, "wb"))
    print("🤖 ML model trained & saved!")

    return model


def load_model():
    """Load model if exists."""
    if os.path.exists(MODEL_PATH):
        print("🤖 Loaded ML model from disk.")
        return pickle.load(open(MODEL_PATH, "rb"))
    return None
