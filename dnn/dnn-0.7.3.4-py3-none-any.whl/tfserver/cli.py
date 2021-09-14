#!/usr/bin/env python

# This is a placeholder for a Google-internal import.
import time
from grpc.beta import implementations
import numpy as np
from tensorflow.python.framework import tensor_util
from tensorflow.core.framework.tensor_pb2 import TensorProto
from . import prediction_service_pb2, predict_pb2
from urllib import parse

class Response:
	def __init__ (self, pb):
		self.pb = pb
		self.data = {}
		self.decode ()

	def __getattr__ (self, name):
		return self.data.get (name)

	def decode (self):
		for k, v in self.pb.outputs.items ():
			if isinstance (v, TensorProto):
				self.data [k] = tensor_util.MakeNdarray (v)
			else:
				self.data [k] = np.array (v.float_val)

class Server:
	def __init__ (self, addr):
		self.addr = addr

		scheme, netloc = parse.urlparse (self.addr) [:2]
		port = scheme == "https" and 443 or 80
		_ = netloc.split (":", 1)
		if len (_) == 1:
			host = netloc
		else:
			host, port = _ [0], int (_ [1])
		channel = scheme == "https" and implementations.channel (host, port) or implementations.insecure_channel (host, port)
		self.stub = prediction_service_pb2.beta_create_PredictionService_stub (channel)

	def predict (self, spec_name, spec_signature_name, timeout = 10, **params):
		request = build_request (spec_name, spec_signature_name, **params)
		pred = self.stub.Predict (request, timeout)
		return Response (pred)
Proxy = Server

def build_request (spec_name, spec_signature_name, **params):
	def _encode (obj):
		if isinstance (obj, (int, float, str)):
			return tensor_util.make_tensor_proto(obj, shape = ())
		if not isinstance (obj, TensorProto):
			if isinstance (obj, list):
				obj = np.array (obj)
			return tensor_util.make_tensor_proto(obj.astype('float32'), shape = obj.shape)
		return obj

	request = predict_pb2.PredictRequest()
	request.model_spec.name = spec_name
	request.model_spec.signature_name = spec_signature_name
	for k, v in params.items ():
		request.inputs [k].CopyFrom(_encode (v))
	return request
