from flask import Flask
from threading import Thread
import os

app = Flask('')

@app.route('/')
def home():
    return "ANYSNAP Bot Is Running Successfully!"

def run():
    # Render automatically assigns a PORT via environment variable
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)

def keep_alive():
    t = Thread(target=run)
    t.start()