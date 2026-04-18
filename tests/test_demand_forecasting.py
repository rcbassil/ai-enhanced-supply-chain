import numpy as np
import pandas as pd
import xgboost as xgb
from demand_forecasting.model import build_model, evaluate, load_data


def test_load_data(tmp_path):
    # Create a dummy CSV
    csv_path = tmp_path / "test_data.csv"
    df = pd.DataFrame(
        {
            "Date": ["2022-01-01", "2022-01-02"],
            "Store ID": ["S1", "S1"],
            "Product ID": ["P1", "P1"],
            "Category": ["C1", "C1"],
            "Region": ["R1", "R1"],
            "Weather Condition": ["Sunny", "Rainy"],
            "Seasonality": ["Spring", "Spring"],
            "Units Sold": [10, 20],
        }
    )
    df.to_csv(csv_path, index=False)

    df_original, df_ml = load_data(csv_path)

    assert len(df_original) == 2
    assert "Year" in df_ml.columns
    assert "Month" in df_ml.columns
    assert "Day" in df_ml.columns
    assert "DayOfWeek" in df_ml.columns
    assert df_ml["Store ID"].dtype == "category"


def test_build_model():
    model = build_model()
    assert isinstance(model, xgb.XGBRegressor)
    assert model.n_estimators == 100
    assert model.learning_rate == 0.1
    assert model.max_depth == 6


def test_evaluate(capsys):
    y_true = np.array([10, 20, 30])
    y_pred = np.array([11, 19, 31])

    evaluate(y_true, y_pred)

    captured = capsys.readouterr()
    assert "Mean Absolute Error: 1.00" in captured.out
    assert "Root Mean Squared Error: 1.00" in captured.out
