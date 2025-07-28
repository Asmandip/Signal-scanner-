import os
from dotenv import load_dotenv
from flask import Flask
from scanner import run_scanner

load_dotenv()
app = Flask(__name__)

@app.route("/")
def home():
    return "✅ AsmanDip Future Scanner is Running!"

if __name__ == "__main__":
    print("🟢 Starting AsmanDip Future Scanner Bot...")
    print("📡 Scanner started...")
    run_scanner()
    app.run(host="0.0.0.0", port=8000)