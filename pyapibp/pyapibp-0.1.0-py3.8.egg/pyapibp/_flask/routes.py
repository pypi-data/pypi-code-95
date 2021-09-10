# Create your routes here.

from app import app, db
from app.models import *

from flask import Response

@app.route("/")
def default():
    return Response(status=200)
