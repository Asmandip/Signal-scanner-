import os
import asyncio
from flask import Flask
from scanner import run_scanner
from dotenv import load_dotenv

load_dotenv()
app = Flask(__name__)

@app.route('/')
def home():
    return "✅ AsmanDip Future Scanner Bot is running..."

if __name__ == '__main__':
    print("🟢 Starting AsmanDip Future Scanner Bot...")
    asyncio.run(run_scanner())
    app.run(host='0.0.0.0', port=8000)