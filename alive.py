from flask import Flask
from threading import Thread
import os

app = Flask('')

@app.route('/')
def main():
    return "OK"

def keep_alive():
    # Use 0.0.0.0 to make it accessible to Render's health check
    port = int(os.environ.get("PORT", 8080))
    t = Thread(target=lambda: app.run(host="0.0.0.0", port=port))
    t.daemon = True
    t.start()
