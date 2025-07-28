import asyncio
from flask import Flask
from scanner import run_scanner
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("scanner")

app = Flask(__name__)

@app.route("/")
def home():
    return "✅ AsmanDip Future Signal Bot is LIVE!"

if __name__ == "__main__":
    logger.info("🟢 Starting AsmanDip Future Scanner Bot...")
    asyncio.create_task(run_scanner())
    app.run(host="0.0.0.0", port=8000)