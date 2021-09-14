from atila import Atila
import tensorflow as tf
from dnn import tfserver
from dnn.tfserver import prediction_service_pb2, predict_pb2
from tensorflow.python.framework import tensor_util, dtypes
import numpy as np
import os

app = Atila (__name__)
app.debug = False
app.use_reloader = False
app.access_control_allow_origin = ["127.0.0.1"]

@app.before_mount
def before_mount (wasc):
	for alias, params in app.config.tf_models.items ():
		config = None
		if isinstance (params, str):
			model_dir = params
		elif len (params) == 1:
			model_dir = params [0]
		else:
			model_dir, config = params
		wasc.logger ("app", "serve tensorflow model '{}' on {}".format (alias, model_dir), 'info')
		tfserver.load_model (alias, model_dir, config)

@app.umounted
def umounted (wasc):
	tfserver.close ()

@app.route ("/tensorflow.serving.PredictionService/Predict")
def Predict (was, request, timeout = 10):
	sess = tfserver.tfsess.get (request.model_spec.name)
	interp = sess.interp
	signature_name = request.model_spec.signature_name

	result = tfserver.run (request.model_spec.name, signature_name, **request.inputs)
	response = predict_pb2.PredictResponse()
	for k, v in result.items ():
		response.outputs [k].CopyFrom (tensor_util.make_tensor_proto (v, np.float32))
	return response

@app.route ("/predict")
def predict (was, spec_name, signature_name = "predict", **inputs):
	sess = tfserver.tfsess.get (spec_name)
	interp = sess.interp

	result = tfserver.run (spec_name, signature_name, **inputs)
	response = {}
	for k, v in result.items ():
		response [k] = v.astype ("float32").tolist ()
	return was.response.api (result = response)

@app.route ("/model/<model>/version")
def version (was, model):
	sess = tfserver.tfsess.get (model)
	if sess is None:
		return was.response ("404 Not Found")
	return was.response.api (version = sess.get_version ())
