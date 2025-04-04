import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
import joblib

# Load dataset
data = pd.read_csv('Crop_recommendation.csv.csv')

# Define features and labels
X = data[['pH', 'Moisture', 'Temperature']]
y = data[['Nitrogen', 'Phosphorus', 'Potassium']]

# Train-Test Split
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Train Random Forest Model
npk_model = RandomForestRegressor(n_estimators=100, random_state=42)
npk_model.fit(X_train, y_train)

# Save model
joblib.dump(npk_model, "npk_model.pkl")

print("✅ NPK Model saved successfully as 'npk_model.pkl'!")
