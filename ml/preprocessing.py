import pandas as pd
from sklearn.preprocessing import LabelEncoder


def load_and_prepare_data():
    # Load dataset

    df = pd.read_csv("ml/dataset/productivity_data.csv")

    # Convert day and category into numbers
    day_encoder = LabelEncoder()
    category_encoder = LabelEncoder()

    df["day_of_week"] = day_encoder.fit_transform(df["day_of_week"])
    df["category"] = category_encoder.fit_transform(df["category"])

    # Features used by the ML model
    X = df[
        [
            "day_of_week",
            "hour",
            "task_duration",
            "difficulty",
            "previous_completion_rate",
            "category",
        ]
    ]

    # Target: productivity score
    y = df["productivity_score"]

    return X, y


if __name__ == "__main__":
    X, y = load_and_prepare_data()

    print("Data loaded successfully!")
    print("Features:")
    print(X.head())

    print("\nTarget:")
    print(y.head())

    print("\nDataset shape:", X.shape)