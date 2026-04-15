import pandas as pd
import numpy as np
import xgboost as xgb
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import mean_absolute_error, mean_squared_error
import matplotlib.pyplot as plt

# Load the dataset
df_original = pd.read_csv('retail_store_inventory.csv')

# Prepare a copy for machine learning processing
df_ml = df_original.copy()

# Feature Engineering: Extract numeric features from Date
df_ml['Date'] = pd.to_datetime(df_ml['Date'])
df_ml['Year'] = df_ml['Date'].dt.year
df_ml['Month'] = df_ml['Date'].dt.month
df_ml['Day'] = df_ml['Date'].dt.day
df_ml['DayOfWeek'] = df_ml['Date'].dt.dayofweek

# Encode Categorical Columns (converting strings to numbers for XGBoost)
cat_cols = ['Store ID', 'Product ID', 'Category', 'Region', 'Weather Condition', 'Seasonality']
for col in cat_cols:
    #le = LabelEncoder()
    #df_ml[col] = le.fit_transform(df_ml[col].astype(str))
    df_ml[col] = df_ml[col].astype('category')

# Define Features (X) and Target (y)
target = 'Units Sold'
X = df_ml.drop(['Date', 'Demand Forecast'], axis=1) # Keep all columns except Date (raw) and Demand Forecast
y = df_ml[target]

# Train the XGBoost Model
# (Using 80% of the data to train the model)
# X_train contains 80% of the features, y_train contains the target data for the rows in X_train
# X_test contains 20% of the features, it's compared to y_test after the model makes guesses to see how accurate the model is.
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, shuffle=False, random_state=42) 

model = xgb.XGBRegressor(
    objective='reg:squarederror',
    n_estimators=100,
    learning_rate=0.1,
    max_depth=6,
    random_state=42,
    enable_categorical=True
)

# Training data
model.fit(X_train, y_train)

# we specifically use X_test (the 20% of data the model never saw during training) for this step. 
# We do this to get an unbiased evaluation
full_predictions = model.predict(X_test)

# Evaluation Metrics
mae = mean_absolute_error(y_test, full_predictions)
rmse = np.sqrt(mean_squared_error(y_test, full_predictions))

print(f"--- Model Evaluation ---")
print(f"Mean Absolute Error: {mae:.2f}")
print(f"Root Mean Squared Error: {rmse:.2f}")


# Add Predictions to the ORIGINAL Dataframe
# to keep (Category, Store ID, etc.)
# This part tells the trained model to look at the entire feature set (X).
df_original['Predicted_Demand_Forecast'] = model.predict(X)

# Save to CSV
df_original.to_csv('retail_forecast_with_original_values.csv', index=False)

print("Process complete. 'retail_forecast_with_original_values.csv' created with original labels.")

# Plotting

# Comparison Graph (First 100 points of validation)
plt.figure(figsize=(15, 7))
plt.plot(y_test.values[:100], label='Actual Units Sold', color='#1f77b4', linewidth=2, marker='o')
plt.plot(full_predictions[:100], label='XGBoost Forecast', color='#ff7f0e', linewidth=2, linestyle='--', marker='x')

plt.title('Demand Forecasting: Actual vs Predicted (Sample)', fontsize=16)
plt.xlabel('Time Step (Validation Set Data)', fontsize=12)
plt.ylabel('Units Sold', fontsize=12)
plt.legend(loc='upper right')
plt.grid(True, linestyle='--', alpha=0.6)
plt.tight_layout()
plt.show()

# Feature Importance Diagram
plt.figure(figsize=(10, 8))
xgb.plot_importance(model, max_num_features=15, importance_type='weight', ax=plt.gca(), color='#2ca02c')
plt.title('Key Drivers of Demand (Top 15 Features)', fontsize=16)
plt.tight_layout()
plt.show()