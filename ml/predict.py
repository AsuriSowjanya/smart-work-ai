import os
import joblib
import pandas as pd


# --------------------------------------------------
# Load trained model
# --------------------------------------------------

MODEL_PATH = os.path.join(
    os.path.dirname(__file__),
    "productivity_model.pkl"
)

model = joblib.load(MODEL_PATH)


# --------------------------------------------------
# Predict productivity
# --------------------------------------------------

def predict_productivity(
    day_of_week,
    hour,
    task_duration,
    difficulty,
    previous_completion_rate,
    category
):

    # Same encoding used during training
    day_mapping = {
        "Monday": 1,
        "Tuesday": 5,
        "Wednesday": 6,
        "Thursday": 4,
        "Friday": 0,
        "Saturday": 2,
        "Sunday": 3,
    }

    category_mapping = {
        "Coding": 0,
        "Reading": 1,
        "Study": 2,
    }

    day_value = day_mapping[day_of_week]
    category_value = category_mapping[category]

    data = pd.DataFrame([
        {
            "day_of_week": day_value,
            "hour": hour,
            "task_duration": task_duration,
            "difficulty": difficulty,
            "previous_completion_rate": previous_completion_rate,
            "category": category_value,
        }
    ])

    prediction = model.predict(data)[0]

    # Keep score between 0 and 100
    prediction = max(0, min(100, prediction))

    return round(prediction, 2)


# --------------------------------------------------
# Test prediction
# --------------------------------------------------

if __name__ == "__main__":

    score = predict_productivity(
        day_of_week="Thursday",
        hour=18,
        task_duration=120,
        difficulty=3,
        previous_completion_rate=90,
        category="Study",
    )

    print("--------------------------------")
    print("SMARTWORK AI PRODUCTIVITY PREDICTION")
    print("--------------------------------")
    print(f"Predicted productivity: {score}%")