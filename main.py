import os
import json
import psutil
from flask import Flask, render_template
from datetime import datetime

app = Flask(__name__)

@app.route("/")
def home():
    return "<h1>✅ AsmanDip Trading Bot System is Live!</h1>"

@app.route("/status")
def show_status():
    try:
        with open("status.json", "r") as f:
            data = json.load(f)
        return render_template("status.html", data=data)
    except Exception as e:
        return f"<h1>Error loading status: {str(e)}</h1>", 500

@app.route("/update_status")
def update_status():
    try:
        cpu = psutil.cpu_percent()
        ram = psutil.virtual_memory().percent
        disk = psutil.disk_usage('/').percent

        status_data = {
            "timestamp": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC"),
            "cpu": cpu,
            "ram": ram,
            "disk": disk,
            "bot_status": "Running",
            "trades_executed": 15,
            "total_pnl": "+0.0847 BTC",
            "last_signal": "Buy BTC/USDT at 58900"
        }

        with open("status.json", "w") as f:
            json.dump(status_data, f)

        return "✅ Status updated successfully!"
    except Exception as e:
        return f"❌ Failed to update status: {str(e)}", 500

if __name__ == "__main__":
    app.run(debug=False, host="0.0.0.0", port=8000)