import asyncio
from flask import Flask
from scanner import run_scanner
import threading
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("scanner")

app = Flask(__name__)

@app.route("/")
def home():
    return "✅ AsmanDip Future Signal Bot is LIVE!"

def start_async_loop():
    asyncio.run(run_scanner())

if __name__ == "__main__":
    logger.info("🟢 Starting AsmanDip Future Scanner Bot...")

    # Start async scanner in background thread
    thread = threading.Thread(target=start_async_loop)
    thread.start()

    # Start Flask app
    app.run(host="0.0.0.0", port=8000)