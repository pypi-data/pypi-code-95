# Create your routes here.

from app import app

from flask import Response

@app.route("/")
def default():
    return Response(status=200)
