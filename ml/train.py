import os
import joblib

from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score

from preprocessing import load_and_prepare_data


# --------------------------------------------------
# Load data
# --------------------------------------------------

X, y = load_and_prepare_data()

print("Training data loaded!")
print("Features:", X.shape)
print("Target:", y.shape)


# --------------------------------------------------
# Split data
# --------------------------------------------------

X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.2,
    random_state=42
)


print("Training samples:", len(X_train))
print("Testing samples:", len(X_test))


# --------------------------------------------------
# Create ML model
# --------------------------------------------------

model = RandomForestRegressor(
    n_estimators=100,
    random_state=42
)


# --------------------------------------------------
# Train model
# --------------------------------------------------

print("\nTraining Random Forest model...")

model.fit(X_train, y_train)

print("Model training completed!")


# --------------------------------------------------
# Predictions
# --------------------------------------------------

predictions = model.predict(X_test)


# --------------------------------------------------
# Evaluation
# --------------------------------------------------

mae = mean_absolute_error(y_test, predictions)
rmse = mean_squared_error(y_test, predictions) ** 0.5
r2 = r2_score(y_test, predictions)


print("\n-----------------------------")
print("MODEL EVALUATION")
print("-----------------------------")

print(f"MAE  : {mae:.2f}")
print(f"RMSE : {rmse:.2f}")
print(f"R2   : {r2:.2f}")


# --------------------------------------------------
# Save model
# --------------------------------------------------

model_path = os.path.join(
    os.path.dirname(__file__),
    "productivity_model.pkl"
)

joblib.dump(model, model_path)

print("\nModel saved successfully!")
print("Location:", model_path)