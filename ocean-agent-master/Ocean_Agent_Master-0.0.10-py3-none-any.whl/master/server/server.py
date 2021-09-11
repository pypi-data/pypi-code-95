import json
import logging

from flask import Flask, request

from master.server.join import join as worker_join

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


@app.route('/join', methods=['post'])
def join():
    join_data = worker_join()
    response = app.response_class(
        response=json.dumps(join_data),
        status=200,
        mimetype='application/json'
    )
    return response
