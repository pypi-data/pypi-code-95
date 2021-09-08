#!/usr/bin/env python3

'''
This is the hctsa-core module, using Flask as a minimal backend webserver.
'''

# TODO Flask Server
# rest API:
# - potentielle nachfolgermethoden basierend auf spezifischer methode, array mit potentiellen methoden
# - add_method, return true, false
# - pipeline löschen/neu 'starten', return true, false
# - pipeline letztes element löschen, return true, false
# - pipeline run, return results

from hctsa.pipeline.pipeline import Pipeline
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

pipeline = Pipeline()

@app.route("/")
def hello_world():
    return "<p>Hello, World!</p>"

@app.route("/pipeline/rules", methods=['GET'])
def pipeline_rules():
    return jsonify(pipeline.method_rules)

@app.route("/pipeline/data", methods=['POST'])
def pipeline_data():
  filename = request.get_json()['filename']
  # TODO get data and store into pipeline
  return pipeline.load_data_csv(filename=filename)

@app.route("/pipeline/add", methods=['POST'])
def pipeline_add():
  add_function = request.get_json()['method']
  # TODO add parameters... e.g. visualize as graphic and return the graphic...
  if pipeline.add_method(add_function):
    return add_function + ' added'
  return add_function + ' not added - error'

@app.route("/pipeline/delete", methods=['GET', 'POST'])
def pipeline_delete():
  delete_position = request.get_json()['position']
  pipeline.del_method(delete_position)
  return 'method on position ' + str(delete_position) + ' deleted'

@app.route("/pipeline/run", methods=['GET', 'POST'])
def pipeline_run():
  _result = pipeline.run()
  return jsonify({'result': _result.to_json()})

@app.route("/pipeline/reset", methods=['GET', 'POST'])
def pipeline_reset():
  pipeline.reset_pipeline()
  return 'pipeline resetted'

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
