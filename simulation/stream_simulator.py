from core.config import settings
import sqlite3
import requests
import time
import random
import threading
from datetime import datetime
from rich.console import Console
from rich.table import Table
from rich.live import Live

def init_database():
    conn = sqlite3.connect(settings.DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT,
            machine_id INTEGER,
            tool_wear REAL,
            ml_probability REAL,
            risk_score REAL,
            event_type TEXT
        )
    """)

    conn.commit()
    conn.close()

API_URL = settings.API_URL
NUM_MACHINES = settings.NUM_MACHINES
ALERT_THRESHOLD = settings.ALERT_THRESHOLD

console = Console()

fleet_status = {}
lock = threading.Lock()


# ✅ Event persistence
def persist_event(machine_id, tool_wear, probability, risk_score):
    conn = sqlite3.connect(settings.DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO events (
            timestamp,
            machine_id,
            tool_wear,
            ml_probability,
            risk_score,
            event_type
        ) VALUES (?, ?, ?, ?, ?, ?)
    """, (
        datetime.utcnow().isoformat(),
        machine_id,
        tool_wear,
        probability,
        risk_score,
        "CRITICAL_FAILURE"
    ))

    conn.commit()
    conn.close()


class Machine:
    def __init__(self, machine_id):
        self.machine_id = machine_id
        self.tool_wear = random.uniform(1, 5)

    def generate_data(self):
        self.tool_wear += random.uniform(0.8, 2.0)

        stress_factor = 0
        if self.tool_wear > 40:
            stress_factor = random.uniform(5, 15)

        return {
            "Type": 0,
            "Air_temperature_K": 300 + random.uniform(-2, 2) + stress_factor,
            "Process_temperature_K": 310 + random.uniform(-2, 2) + stress_factor,
            "Rotational_speed_rpm": 1500 + random.uniform(-50, 50),
            "Torque_Nm": 40 + random.uniform(-5, 5) + stress_factor * 0.5,
            "Tool_wear_min": self.tool_wear
        }

    def calculate_risk(self, probability, data):
        risk_score = probability

        if self.tool_wear > 40:
            risk_score += 0.2
        if data["Air_temperature_K"] > 315:
            risk_score += 0.2
        if data["Torque_Nm"] > 50:
            risk_score += 0.2

        return risk_score

    def determine_state(self, risk_score):
        if risk_score < 0.3:
            return "NORMAL"
        elif risk_score < 0.6:
            return "WARNING"
        else:
            return "CRITICAL"

    def stream(self):
        while True:
            data = self.generate_data()

            try:
                response = requests.post(API_URL, json=data)
                result = response.json()

                probability = result["failure_probability"]
                risk_score = self.calculate_risk(probability, data)
                state = self.determine_state(risk_score)

                with lock:
                    fleet_status[self.machine_id] = {
                        "tool_wear": self.tool_wear,
                        "probability": probability,
                        "risk_score": risk_score,
                        "state": state
                    }

                if state == "CRITICAL":
                    console.print(
                        f"[red]🚨 CRITICAL FAILURE — Machine {self.machine_id} SHUTDOWN[/red]"
                    )

                    persist_event(
                        self.machine_id,
                        self.tool_wear,
                        probability,
                        risk_score
                    )

                    break

            except Exception as e:
                console.print(f"[red]Machine {self.machine_id} error: {e}[/red]")

            time.sleep(2)


def generate_dashboard():
    table = Table(title="Predictive Maintenance Fleet Monitor")

    table.add_column("Machine", justify="center")
    table.add_column("Tool Wear", justify="center")
    table.add_column("ML Prob", justify="center")
    table.add_column("Risk Score", justify="center")
    table.add_column("State", justify="center")

    normal = warning = critical = 0

    with lock:
        for machine_id, data in fleet_status.items():
            state = data["state"]

            if state == "NORMAL":
                normal += 1
            elif state == "WARNING":
                warning += 1
            else:
                critical += 1

            color = (
                "green" if state == "NORMAL"
                else "yellow" if state == "WARNING"
                else "red"
            )

            table.add_row(
                str(machine_id),
                f"{data['tool_wear']:.2f}",
                f"{data['probability']:.5f}",
                f"{data['risk_score']:.2f}",
                f"[{color}]{state}[/{color}]"
            )

    table.caption = (
        f"NORMAL: {normal} | "
        f"WARNING: {warning} | "
        f"CRITICAL: {critical}"
    )

    return table


def start_simulation():
    machines = [Machine(i) for i in range(1, NUM_MACHINES + 1)]

    threads = []
    for machine in machines:
        t = threading.Thread(target=machine.stream)
        t.start()
        threads.append(t)

    with Live(generate_dashboard(), refresh_per_second=2) as live:
        while True:
            live.update(generate_dashboard())
            time.sleep(1)


if __name__ == "__main__":
    init_database()
    start_simulation()