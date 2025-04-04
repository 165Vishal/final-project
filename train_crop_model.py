import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, classification_report
import joblib

# Step 1: Load the dataset (Replace 'your_dataset.csv' with your actual dataset path)
data = pd.read_csv('Crop_recommendation.csv.csv')

# Step 2: Prepare features and target variable
X = data[['Nitrogen','Phosphorus', 'Potassium','pH','Moisture']]  # Features
y = data['PlantType']  # Target

# Step 3: Split the data into training and testing sets
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Step 4: Initialize and train the model
model = RandomForestClassifier(n_estimators=100, random_state=42)
model.fit(X_train, y_train)

# Step 5: Make predictions and evaluate the model
y_pred = model.predict(X_test)
print("Accuracy:", accuracy_score(y_test, y_pred))
print("Classification Report:\n", classification_report(y_test, y_pred))

# Step 6: Save the model for future use
joblib.dump(model, 'crop_model.pkl')

# Step 7: Load the model and make predictions with new data
# Example: Predicting the best plant for a new set of sensor data
new_data = [[40, 45, 18, 5.261285926, 55.20522037]]  # Replace with actual sensor values
best_plant = model.predict(new_data)
print("Recommended Plant:", best_plant[0])
