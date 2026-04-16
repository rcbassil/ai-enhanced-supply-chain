import pandas as pd
import numpy as np
import xgboost as xgb
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error, mean_squared_error
import matplotlib.pyplot as plt
from pathlib import Path

DATA_DIR = Path(__file__).parents[3] / "data"  # workspace root / data
INPUT_CSV = DATA_DIR / "retail_store_inventory.csv"
OUTPUT_CSV = DATA_DIR / "retail_forecast_with_original_values.csv"

TEST_SIZE = 0.2
N_ESTIMATORS = 100
LEARNING_RATE = 0.1
MAX_DEPTH = 6
PLOT_SAMPLE_SIZE = 100
MAX_IMPORTANCE_FEATURES = 15

CAT_COLS = ["Store ID", "Product ID", "Category", "Region", "Weather Condition", "Seasonality"]
TARGET = "Units Sold"


def load_data(path: Path) -> tuple[pd.DataFrame, pd.DataFrame]:
    df_original = pd.read_csv(path)
    df_ml = df_original.copy()

    df_ml["Date"] = pd.to_datetime(df_ml["Date"])
    df_ml["Year"] = df_ml["Date"].dt.year
    df_ml["Month"] = df_ml["Date"].dt.month
    df_ml["Day"] = df_ml["Date"].dt.day
    df_ml["DayOfWeek"] = df_ml["Date"].dt.dayofweek

    for col in CAT_COLS:
        df_ml[col] = df_ml[col].astype("category")

    return df_original, df_ml


def build_model() -> xgb.XGBRegressor:
    return xgb.XGBRegressor(
        objective="reg:squarederror",
        n_estimators=N_ESTIMATORS,
        learning_rate=LEARNING_RATE,
        max_depth=MAX_DEPTH,
        random_state=42,
        enable_categorical=True,
    )


def evaluate(y_true: np.ndarray, y_pred: np.ndarray) -> None:
    mae = mean_absolute_error(y_true, y_pred)
    rmse = np.sqrt(mean_squared_error(y_true, y_pred))
    print("--- Model Evaluation ---")
    print(f"Mean Absolute Error: {mae:.2f}")
    print(f"Root Mean Squared Error: {rmse:.2f}")


def plot_results(y_test: np.ndarray, predictions: np.ndarray, model: xgb.XGBRegressor) -> None:
    plt.figure(figsize=(15, 7))
    plt.plot(y_test[:PLOT_SAMPLE_SIZE], label="Actual Units Sold", color="#1f77b4", linewidth=2, marker="o")
    plt.plot(predictions[:PLOT_SAMPLE_SIZE], label="XGBoost Forecast", color="#ff7f0e", linewidth=2, linestyle="--", marker="x")
    plt.title("Demand Forecasting: Actual vs Predicted (Sample)", fontsize=16)
    plt.xlabel("Time Step (Validation Set Data)", fontsize=12)
    plt.ylabel("Units Sold", fontsize=12)
    plt.legend(loc="upper right")
    plt.grid(True, linestyle="--", alpha=0.6)
    plt.tight_layout()
    plt.savefig(DATA_DIR / "forecast_vs_actual.png")
    plt.close()

    plt.figure(figsize=(10, 8))
    xgb.plot_importance(model, max_num_features=MAX_IMPORTANCE_FEATURES, importance_type="weight", ax=plt.gca(), color="#2ca02c")
    plt.title("Key Drivers of Demand (Top 15 Features)", fontsize=16)
    plt.tight_layout()
    plt.savefig(DATA_DIR / "feature_importance.png")
    plt.close()


def run() -> None:
    df_original, df_ml = load_data(INPUT_CSV)

    X = df_ml.drop(["Date"], axis=1)
    y = df_ml[TARGET]

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=TEST_SIZE, shuffle=False, random_state=42
    )

    model = build_model()
    model.fit(X_train, y_train)

    test_predictions = model.predict(X_test)
    evaluate(y_test.values, test_predictions)

    df_original["Predicted_Demand_Forecast"] = model.predict(X)
    df_original.to_csv(OUTPUT_CSV, index=False)
    print(f"Process complete. '{OUTPUT_CSV.name}' created with original labels.")

    plot_results(y_test.values, test_predictions, model)


if __name__ == "__main__":
    run()
