import sqlite3
from core.config import settings
import json
import os
import mlflow
import mlflow.xgboost
import pandas as pd
from fastapi import FastAPI, Request
from pydantic import BaseModel
import logging
import time

# Configure structured logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s"
)

logger = logging.getLogger("predictive-maintenance-api")
request_count = 0

# Create FastAPI app
app = FastAPI(title="Predictive Maintenance API")

@app.middleware("http")
async def log_requests(request: Request, call_next):
    global request_count

    start_time = time.time()
    request_count += 1

    response = await call_next(request)

    process_time = time.time() - start_time

    logger.info(
        f"{request.method} {request.url.path} "
        f"status={response.status_code} "
        f"latency={process_time:.4f}s"
    )

    return response


# ✅ Load model from local mlruns folder (for Docker deployment)
MODEL_PATH = os.path.join(
    os.path.dirname(os.path.dirname(__file__)),
    "model_export"
)

model = mlflow.xgboost.load_model(MODEL_PATH)


# Define input schema
class MachineData(BaseModel):
    Type: int
    Air_temperature_K: float
    Process_temperature_K: float
    Rotational_speed_rpm: float
    Torque_Nm: float
    Tool_wear_min: float


@app.get("/")
def home():
    return {"message": "Predictive Maintenance API is running ✅"}

@app.get("/health")
def health():
    return {"status": "healthy"}

@app.get("/metrics")
def metrics():
    return {
        "total_requests": request_count
    }


@app.post("/predict")
def predict(data: MachineData):

    input_df = pd.DataFrame([data.model_dump()])

    # Rename columns to match training names
    input_df.columns = [
        "Type",
        "Air temperature K",
        "Process temperature K",
        "Rotational speed rpm",
        "Torque Nm",
        "Tool wear min"
    ]

    # Add missing columns used during training
    input_df["TWF"] = 0
    input_df["HDF"] = 0
    input_df["PWF"] = 0
    input_df["OSF"] = 0
    input_df["RNF"] = 0

    prediction = model.predict(input_df)[0]
    probability = model.predict_proba(input_df)[0][1]
    logger.info(
        f"Prediction made | "
        f"failure_prediction={int(prediction)} "
        f"failure_probability={float(probability):.6f}"
    )

    return {
        "failure_prediction": int(prediction),
        "failure_probability": float(probability)
    }

@app.get("/events")
def get_events():
    try:
        conn = sqlite3.connect(settings.DB_PATH)
        cursor = conn.cursor()

        cursor.execute("SELECT timestamp, machine_id, tool_wear, ml_probability, risk_score, event_type FROM events")
        rows = cursor.fetchall()

        conn.close()

        events = []
        for row in rows:
            events.append({
                "timestamp": row[0],
                "machine_id": row[1],
                "tool_wear": row[2],
                "ml_probability": row[3],
                "risk_score": row[4],
                "event_type": row[5]
            })

        return {"events": events}

    except Exception as e:
        return {"error": str(e)}