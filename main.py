import os
import time
import json
import psutil
import datetime
import requests
from flask import Flask, render_template
from dotenv import load_dotenv
from threading import Thread

load_dotenv()

app = Flask(__name__)

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

# === Global Status ===
status_data = {
    "bot_health": {"status": "Initializing", "uptime": "0", "cpu": "0%", "memory": "0MB"},
    "scanner": {"current": "None", "total": 0, "last_scan": "Never"},
    "telegram": {"last_sent": "Never", "status": "Not Connected"},
    "api": {"ping": "Unknown", "last_response": "Never"},
    "ai_filter": {"last_score": 0.0, "decision": "Pending"},
    "trade": {"last_pair": "None", "side": "None", "status": "None"},
    "backtest": {"last_run": "Never", "winrate": "0%", "tested": 0},
    "mongo": {"last_write": "Never", "total_logs": 0},
    "logs": {"last_errors": [], "trade_events": [], "signal_stats": []},
    "env": {
        "telegram": bool(TELEGRAM_TOKEN),
        "bitget": bool(os.getenv("BITGET_API_KEY")),
        "mongo": bool(os.getenv("MONGO_URI"))
    }
}

# === Save status to JSON ===
def update_status():
    with open("status.json", "w") as f:
        json.dump(status_data, f, indent=2)

# === Error Logger ===
def error_log(msg):
    timestamp = datetime.datetime.now().strftime("%H:%M:%S")
    log = f"[{timestamp}] {msg}"
    status_data["logs"]["last_errors"] = [log] + status_data["logs"]["last_errors"][:9]
    update_status()
    send_telegram(f"❌ ERROR: {msg}")

# === Telegram Alert ===
def send_telegram(message):
    if TELEGRAM_TOKEN and CHAT_ID:
        try:
            url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
            payload = {"chat_id": CHAT_ID, "text": message}
            requests.post(url, data=payload)
        except Exception as e:
            print("Telegram Error:", e)

# === Status Checker ===
start_time = time.time()
last_bot_status = None

def update_live_status():
    global last_bot_status
    while True:
        try:
            uptime = str(datetime.timedelta(seconds=int(time.time() - start_time)))
            cpu = f"{psutil.cpu_percent()}%"
            mem = f"{round(psutil.virtual_memory().used / (1024 ** 2))}MB"

            # Update bot health
            status_data["bot_health"]["uptime"] = uptime
            status_data["bot_health"]["cpu"] = cpu
            status_data["bot_health"]["memory"] = mem
            status_data["bot_health"]["status"] = "Running ✅"

            # Detect status change
            if last_bot_status != status_data["bot_health"]["status"]:
                send_telegram(f"⚙️ Bot Status Changed:\n{status_data['bot_health']}")
                last_bot_status = status_data["bot_health"]["status"]

            update_status()

        except Exception as e:
            error_log(str(e))
        time.sleep(60)

# === Trade Logger ===
def log_trade_event(event):
    timestamp = datetime.datetime.now().strftime("%H:%M:%S")
    log = f"[{timestamp}] {event}"
    status_data["logs"]["trade_events"] = [log] + status_data["logs"]["trade_events"][:19]
    update_status()

# === Signal Logger ===
def log_signal_stat(stat):
    timestamp = datetime.datetime.now().strftime("%H:%M:%S")
    log = f"[{timestamp}] {stat}"
    status_data["logs"]["signal_stats"] = [log] + status_data["logs"]["signal_stats"][:19]
    update_status()

# === Flask Route ===
@app.route('/status')
def show_status():
    with open("status.json") as f:
        data = json.load(f)
    return render_template("status.html", data=data)

# === Start Background Thread ===
Thread(target=update_live_status, daemon=True).start()

# === Run Flask App ===
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)