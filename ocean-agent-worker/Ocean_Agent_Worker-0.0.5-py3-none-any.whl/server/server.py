import json
import logging

from flask import Flask, request

app = Flask(__name__)


def run(host, port):
    app.run(debug=True, host=host, port=port, use_reloader=False)


@app.route('/hello', methods=['get'])
def hello():
    data = request.get_json()
    logging.info(data)

    response = app.response_class(
        response=json.dumps({}),
        status=200,
        mimetype='application/json'
    )
    return response
