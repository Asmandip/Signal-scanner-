import os
import time
import json
import psutil
import datetime
from flask import Flask, render_template
from dotenv import load_dotenv
from threading import Thread

load_dotenv()

app = Flask(__name__)

# === Status Data ===
status_data = {
    "bot_health": {"status": "Initializing", "uptime": "0", "cpu": "0%", "memory": "0MB"},
    "scanner": {"current": "None", "total": 0, "last_scan": "Never"},
    "telegram": {"last_sent": "Never", "status": "Not Connected"},
    "api": {"ping": "Unknown", "last_response": "Never"},
    "ai_filter": {"last_score": 0.0, "decision": "Pending"},
    "trade": {"last_pair": "None", "side": "None", "status": "None"},
    "backtest": {"last_run": "Never", "winrate": "0%", "tested": 0},
    "mongo": {"last_write": "Never", "total_logs": 0},
    "env": {
        "telegram": bool(os.getenv("TELEGRAM_TOKEN")),
        "bitget": bool(os.getenv("BITGET_API_KEY")),
        "mongo": bool(os.getenv("MONGO_URI"))
    },
    "logs": {"last_errors": []}
}

# === Save status to JSON ===
def update_status():
    with open("status.json", "w") as f:
        json.dump(status_data, f, indent=2)

# === Track uptime ===
start_time = time.time()

def update_live_status():
    while True:
        try:
            uptime = str(datetime.timedelta(seconds=int(time.time() - start_time)))
            status_data["bot_health"]["uptime"] = uptime
            status_data["bot_health"]["status"] = "Running ✅"
            status_data["bot_health"]["cpu"] = f"{psutil.cpu_percent()}%"
            status_data["bot_health"]["memory"] = f"{round(psutil.virtual_memory().used / (1024**2))}MB"
            update_status()
        except Exception as e:
            error_log(str(e))
        time.sleep(60)  # Update every 60 seconds

def error_log(msg):
    timestamp = datetime.datetime.now().strftime("%H:%M:%S")
    err = f"[{timestamp}] {msg}"
    status_data["logs"]["last_errors"] = [err] + status_data["logs"]["last_errors"][:9]
    update_status()

# === Flask Route ===
@app.route('/status')
def show_status():
    with open("status.json") as f:
        data = json.load(f)
    return render_template("status.html", data=data)

# === Start background thread ===
Thread(target=update_live_status, daemon=True).start()

# === Your bot logic will go below this ===
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)