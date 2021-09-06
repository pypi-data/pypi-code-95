import flask
import time
import importlib
import os
import sys
import imp
from flask import request

app = flask.Flask(__name__)

@app.route('/')
def index():
    time.sleep(5)
    return 'hello world'

@app.route('/runFunc', methods=['POST'])
def run_func():
    param = request.get_json()
    file_path = param.get('pythonFile')
    func_name = param.get('function')
    args = param.get('args')
    kwargs = param.get('kwargs')
    module = import_py_file(file_path)

    try:
        ret = getattr(module, param.get('function'))(*args, **kwargs)
    except Exception as err:
        ret = str(err)
    return flask.jsonify({'ret':ret})

def import_py_file(file_path):
    module = imp.load_source('mymod', file_path)
    return module


def main():
    app.run(threaded=True)

if __name__ == "__main__":
    main()
