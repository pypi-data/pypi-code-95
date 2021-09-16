from flask import Flask
import json
from . import (health)

app = Flask(__name__)
app.register_blueprint(health.bp)

@app.route("/")
def index():
    return "Hello World!"

@app.route("/test")
def index():
    return "Hello IKS World!"