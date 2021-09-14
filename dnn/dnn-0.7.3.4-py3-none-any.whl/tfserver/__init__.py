import os
import tensorflow as tf
import numpy as np
import time
import pickle
from tensorflow.python.framework import tensor_util
from tensorflow.core.framework import tensor_pb2
import sys
from .. import saved_model

__version__ = "0.2.0.12"

def preference (path = None):
    import skitai
    pref =  skitai.preference (path = path)
    pref.config.tf_models = {}
    return pref

def get_labels (model_path):
    with open (os.path.join (model_path, "labels"), "rb") as f:
        return pickle.load (f)

class Session:
    def __init__ (self, model_dir, tfconfig = None):
        self.model_dir = model_dir
        try:
            self.version = int (os.path.basename (model_dir))
        except:
            self.version = 0
        self.tfconfig = tfconfig
        self.graph = tf.Graph ()
        self.tfsess = tf.compat.v1.Session (config = tfconfig, graph = self.graph)
        self.interp =  saved_model.load (model_dir, self.tfsess)
        try:
            self.labels = get_labels (model_dir)
        except OSError:
            self.labels = None

    def get_version (self):
        return self.version

    def run (self, feed_dict, signature_def_name = tf.saved_model.DEFAULT_SERVING_SIGNATURE_DEF_KEY):
        return self.interp._run (feed_dict, signature_def_name)

    def close (self):
        self.tfsess.close ()

tfsess = {}
def load_model (alias, model_dir, tfconfig = None):
    global tfsess

    tfsess [alias] = Session (model_dir, tfconfig)

def run (spec_name, signature_name, **inputs):
    global tfsess

    feed_dict = {}
    sess = tfsess [spec_name]
    interp = sess.interp
    for k, v in inputs.items ():
        tensor_name, tensor, dtype, shape = interp.input_map [signature_name][k]
        if isinstance(v, tensor_pb2.TensorProto):
            v = tensor_util.MakeNdarray (v)
        elif type (v) is not np.ndarray:
            v = np.array (v)
        if k == "x": v = interp.normalize (v)
        feed_dict [tensor] = v
    predict_results = sess.run (feed_dict, signature_name)

    response = {}
    for i, result in enumerate (interp.outputs [signature_name]):
        predict_result = predict_results [i]
        response [interp.outputs [signature_name][i][0]] = predict_result
    return response

def close ():
    global tfsess

    for sess in tfsess.values ():
        sess.close ()
    tfsess = {}


