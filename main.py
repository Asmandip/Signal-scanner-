import os import time import json import psutil import datetime import requests from flask import Flask, render_template from dotenv import load_dotenv from threading import Thread

load_dotenv()

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN") CHAT_ID = os.getenv("CHAT_ID")

def send_telegram(msg): if TELEGRAM_TOKEN and CHAT_ID: url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage" payload = {"chat_id": CHAT_ID, "text": msg} try: requests.post(url, json=payload) except Exception as e: print("Telegram error:", e)

app = Flask(name)

status_data = { "bot_health": {"status": "Initializing", "uptime": "0", "cpu": "0%", "memory": "0MB"}, "scanner": {"current": "None", "total": 0, "last_scan": "Never"}, "telegram": {"last_sent": "Never", "status": "Not Connected"}, "api": {"ping": "Unknown", "last_response": "Never"}, "ai_filter": {"last_score": 0.0, "decision": "Pending"}, "trade": {"last_pair": "None", "side": "None", "status": "None"}, "backtest": {"last_run": "Never", "winrate": "0%", "tested": 0}, "mongo": {"last_write": "Never", "total_logs": 0}, "env": { "telegram": bool(os.getenv("TELEGRAM_TOKEN")), "bitget": bool(os.getenv("BITGET_API_KEY")), "mongo": bool(os.getenv("MONGO_URI")) }, "logs": { "last_errors": [], "signal_logs": [], "trade_logs": [], "system_status": [] } }

status_file = "status.json"

last_bot_status = "Initializing"

def update_status(): with open(status_file, "w") as f: json.dump(status_data, f, indent=2)

def error_log(msg): timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S") entry = f"[{timestamp}] {msg}" status_data["logs"]["last_errors"] = [entry] + status_data["logs"]["last_errors"][:9] update_status()

def log_event(log_type, msg): timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S") entry = f"[{timestamp}] {msg}" if log_type in status_data["logs"]: status_data["logs"][log_type] = [entry] + status_data["logs"][log_type][:49] update_status()

def update_live_status(): global last_bot_status while True: try: uptime = str(datetime.timedelta(seconds=int(time.time() - start_time))) cpu = f"{psutil.cpu_percent()}%" mem = f"{round(psutil.virtual_memory().used / (1024**2))}MB"

status_data["bot_health"].update({
            "uptime": uptime,
            "status": "Running ✅",
            "cpu": cpu,
            "memory": mem
        })

        # Detect status change
        if status_data["bot_health"]["status"] != last_bot_status:
            send_telegram(f"⚠️ Bot status changed: {status_data['bot_health']['status']}")
            log_event("system_status", f"Bot status changed to {status_data['bot_health']['status']}")
            last_bot_status = status_data["bot_health"]["status"]

        update_status()
    except Exception as e:
        error_log(str(e))
    time.sleep(60)

start_time = time.time() Thread(target=update_live_status, daemon=True).start()

@app.route("/status") def show_status(): with open(status_file) as f: data = json.load(f) return render_template("status.html", data=data)

if name == "main": app.run(host="0.0.0.0", port=8000)

