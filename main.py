main.py

import os import asyncio import threading from flask import Flask from dotenv import load_dotenv from scanner import run_scanner

Load environment variables

load_dotenv()

Flask setup

app = Flask(name)

@app.route('/') def index(): return "✅ AsmanDip Future Scanner Bot is Running"

@app.route('/status') def status(): return "🟢 Scanner Status: Active"

def start_async_loop(): loop = asyncio.new_event_loop() asyncio.set_event_loop(loop) loop.run_until_complete(run_scanner())

def start_bot(): print("🟢 Starting AsmanDip Future Scanner Bot...") print("📡 Scanner started...") scanner_thread = threading.Thread(target=start_async_loop) scanner_thread.start()

if name == 'main': start_bot() app.run(host='0.0.0.0', port=8000)

