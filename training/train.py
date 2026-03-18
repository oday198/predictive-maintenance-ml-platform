import mlflow
import mlflow.xgboost
import xgboost as xgb
from sklearn.metrics import accuracy_score, classification_report
from training.config import (
    MODEL_PARAMS,
    EXPERIMENT_NAME,
)
from training.preprocess import load_data, preprocess_data, split_data


def train():
    # Set MLflow experiment
    mlflow.set_experiment(EXPERIMENT_NAME)

    with mlflow.start_run():

        # Load and preprocess data
        df = load_data()
        X, y = preprocess_data(df)
        X_train, X_test, y_train, y_test = split_data(X, y)

        # Initialize model
        model = xgb.XGBClassifier(**MODEL_PARAMS)

        # Train model
        model.fit(X_train, y_train)

        # Predictions
        y_pred = model.predict(X_test)

        # Metrics
        accuracy = accuracy_score(y_test, y_pred)

        # Log parameters
        mlflow.log_params(MODEL_PARAMS)

        # Log metrics
        mlflow.log_metric("accuracy", accuracy)

        # Log model
        mlflow.xgboost.log_model(model, "model")

        print("✅ Training complete")
        print(f"Accuracy: {accuracy:.4f}")
        print(classification_report(y_test, y_pred))


if __name__ == "__main__":
    train()