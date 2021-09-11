import os
os.environ['TF_CPP_MIN_LOG_LEVEL']='3'
import argparse
import numpy as np
import sys
import tensorflow as tf
from keras.applications.resnet import ResNet50
from keras.applications.imagenet_utils import preprocess_input
from keras.preprocessing import image
from os.path import join
from PIL import Image, ImageOps
import glob
import numpy as np
import urllib.request
import requests
import io
import PIL
from sklearn.preprocessing import normalize

model = ResNet50(include_top=False, weights='imagenet', classes=1000)

def extract_feature(imgpath):
  if imgpath.find('http')!=-1:
      r = requests.get(imgpath, allow_redirects=True, timeout=10)
      image_bytes = io.BytesIO(r.content)
      img = PIL.Image.open(image_bytes)
  else:
  	  img = image.load_img(imgpath)
  img = ImageOps.fit(img, (224, 224), Image.ANTIALIAS)
  x = image.img_to_array(img)
  x = np.expand_dims(x, axis=0)
  x = preprocess_input(x)
  features = model.predict(x, batch_size=1,verbose=0)
  features = np.ndarray.flatten(features).astype('float64')
  feat = normalize([features])[0]
  return feat