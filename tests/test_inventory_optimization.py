import pytest
import pandas as pd
import numpy as np
import json
from pathlib import Path
from inventory_optimization.solver import solve_inventory_allocation, solve_biased_allocation, load_sustainability_config

def test_load_sustainability_config(tmp_path, mocker):
    # Mock DATA_DIR to use tmp_path
    mocker.patch("inventory_optimization.solver.DATA_DIR", tmp_path)
    
    # Test default values
    config = load_sustainability_config()
    assert config["storage_emission_factor"] == 0.12
    
    # Test loaded values
    config_file = tmp_path / "sustainability_config.json"
    with open(config_file, "w") as f:
        json.dump({"storage_emission_factor": 0.5, "emissions_target_reduction": 0.2}, f)
        
    config = load_sustainability_config()
    assert config["storage_emission_factor"] == 0.5
    assert config["emissions_target_reduction"] == 0.2

def test_solve_inventory_allocation(tmp_path, mocker):
    mocker.patch("inventory_optimization.solver.DATA_DIR", tmp_path)
    csv_path = tmp_path / "test_inventory.csv"
    df = pd.DataFrame({
        "Product": ["A", "B"],
        "Price": [100, 50],
        "Predicted Demand Forecast": [50, 80]
    })
    df.to_csv(csv_path, index=False)
    
    results = solve_inventory_allocation(csv_path)
    
    assert "LP_Max_Revenue_Stock" in results.columns
    assert "Prop_Stock_LRM" in results.columns
    assert "Carbon_Efficient_Stock" in results.columns
    assert results["LP_Max_Revenue_Stock"].sum() <= 100
    assert results["Prop_Stock_LRM"].sum() == 100

def test_solve_biased_allocation(tmp_path):
    csv_path = tmp_path / "test_inventory_bias.csv"
    df = pd.DataFrame({
        "Product": ["A", "B"],
        "Price": [100, 50],
        "Predicted Demand Forecast": [100, 100]
    })
    df.to_csv(csv_path, index=False)
    
    results = solve_biased_allocation(csv_path, bias_pct=0.20)
    
    assert "Final_Stock" in results.columns
    assert "Revenue" in results.columns
    assert results["Final_Stock"].sum() == 100
    # With 20% bias, product A (higher price) should get more stock than product B if demands are equal
    # Fair share would be 50 each. 1-bias = 0.8. Min stock is 40.
    # Product A should get more because it's higher price.
    assert results.loc[results["Product"] == "A", "Final_Stock"].values[0] >= 50
