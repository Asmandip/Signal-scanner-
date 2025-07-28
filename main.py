# main.py

import asyncio
import logging
from scanner import run_scanner
from flask import Flask

logging.basicConfig(level=logging.INFO)
app = Flask(__name__)

@app.route('/')
def home():
    return "✅ AsmanDip Future Scanner Bot is running."

# Use asyncio.create_task inside an async event loop
async def main_async():
    logging.info("🟢 Starting AsmanDip Future Scanner Bot...")
    while True:
        await run_scanner()
        await asyncio.sleep(60)  # Scan every 60 seconds (adjust as needed)

def start_async_loop():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.create_task(main_async())
    loop.run_forever()

if __name__ == '__main__':
    import threading
    # Run scanner in background thread
    threading.Thread(target=start_async_loop).start()
    # Run Flask app
    app.run(host='0.0.0.0', port=8000)