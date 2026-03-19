import os


class Settings:
    # API Configuration
    API_HOST = os.getenv("API_HOST", "0.0.0.0")
    API_PORT = int(os.getenv("API_PORT", 8000))

    # Simulation Configuration
    API_URL = os.getenv("API_URL", "http://localhost:8000/predict")
    NUM_MACHINES = int(os.getenv("NUM_MACHINES", 5))
    ALERT_THRESHOLD = float(os.getenv("ALERT_THRESHOLD", 0.6))

    # Database
    DB_PATH = os.getenv("DB_PATH", "simulation/events.db")


settings = Settings()