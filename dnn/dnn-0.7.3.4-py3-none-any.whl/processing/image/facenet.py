import os
import tensorflow as tf
import cv2
from . import face
import numpy as np

def prewhiten(x):
    mean = np.mean(x)
    std = np.std(x)
    std_adj = np.maximum(std, 1.0/np.sqrt(x.size))
    y = np.multiply(np.subtract(x, mean), 1/std_adj)
    return y

class Facenet:
    def __init__ (self, model = 'vgg'):
        self.model = model
        self.sess = self.create_session ()

    def create_session (self):
        config = tf.compat.v1.ConfigProto(log_device_placement=False)
        config.gpu_options.allow_growth = True
        graph = tf.compat.v1.Graph ()
        sess = tf.compat.v1.Session(config = config, graph = graph)

        with graph.as_default ():
            model_exp = os.path.join (os.path.dirname (__file__), 'facenet', self.model == 'vgg' and '20180402-114759-VGGFace2.pb' or '20180408-102900-CASIA.pb')
            with tf.compat.v1.gfile.GFile (model_exp,'rb') as f:
                graph_def = tf.compat.v1.GraphDef()
                graph_def.ParseFromString(f.read())
                tf.import_graph_def(graph_def, input_map=None, name='')
        return sess

    def embed_aligned (self, image):
        with self.sess.graph.as_default ():
            # Get input and output tensors
            images_placeholder = tf.compat.v1.get_default_graph().get_tensor_by_name("input:0")
            embeddings = tf.compat.v1.get_default_graph().get_tensor_by_name("embeddings:0")
            phase_train_placeholder = tf.compat.v1.get_default_graph().get_tensor_by_name("phase_train:0")

            # Run forward pass to calculate embeddings
            feed_dict = { images_placeholder: [image], phase_train_placeholder:False }
            emb = self.sess.run(embeddings, feed_dict=feed_dict)
            return emb


