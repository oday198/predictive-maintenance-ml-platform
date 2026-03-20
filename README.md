# 🚀 Predictive Maintenance ML Platform

A production-style, containerized machine learning system for real-time predictive maintenance simulation.

This project demonstrates how to design, deploy, monitor, and simulate an ML-powered system using modern MLOps and backend engineering practices.

---

## 📌 Overview

This system simulates an industrial predictive maintenance platform where multiple machines continuously stream sensor data to a containerized ML API that:

- Performs real-time inference
- Applies hybrid risk logic (ML + domain rules)
- Tracks machine lifecycle states
- Logs incidents
- Exposes monitoring endpoints
- Persists critical failure events

The system is built with production-oriented architecture principles rather than a notebook-only ML demo.

---

## 🏗 System Architecture

        +-----------------------+
        |  Multi-Machine        |
        |  Streaming Simulator  |
        +-----------+-----------+
                    |
                    v
            +----------------+
            |  FastAPI ML    |
            |  Inference API |
            +--------+-------+
                     |
                     v
           +-------------------+
           | Hybrid Risk Engine|
           | (ML + Rules)      |
           +--------+----------+
                    |
                    v
        +---------------------------+
        | Fleet Monitoring Dashboard|
        +---------------------------+
                    |
                    v
           +--------------------+
           | Event Persistence  |
           | events_log.json    |
           +--------------------+



---

## ⚙️ Tech Stack

- Python
- XGBoost
- FastAPI
- MLflow
- Docker
- Rich (Live Console Dashboard)
- Threading (Concurrent simulation)
- Structured Logging

---

## 🔥 Key Features

✅ ML model training with MLflow tracking  
✅ Containerized inference service (Docker)  
✅ Real-time REST API (`/predict`)  
✅ Observability:
  - Request logging
  - Latency tracking
  - `/health`
  - `/metrics`
✅ Multi-machine concurrent simulation  
✅ Hybrid risk scoring (ML + rule-based logic)  
✅ State transitions: NORMAL → WARNING → CRITICAL  
✅ Incident persistence (`events_log.json`)  
✅ Event retrieval API (`/events`)  
✅ Live fleet monitoring dashboard  

---

## 🧠 Hybrid Risk Logic

The system does not rely purely on ML probability.

It combines:

- Model prediction probability
- Tool wear thresholds
- Temperature spikes
- Torque stress

This simulates realistic industrial monitoring behavior where AI is integrated with domain knowledge.

---

## 📊 API Endpoints

| Endpoint | Description |
|----------|-------------|
| `/predict` | Perform ML inference |
| `/health` | Service health check |
| `/metrics` | Request statistics |
| `/events` | Retrieve persisted critical events |

---

## 🐳 Running With Docker

### Build Docker Image

```bash
docker build -t predictive-maintenance-api .


## 🌍 Live Deployment

This service is deployed on AWS EC2.

Public endpoints:

- /health
- /predict
- /events
- /docs

Deployment includes:

- Docker container
- SQLite persistent volume
- Public security group configurationg