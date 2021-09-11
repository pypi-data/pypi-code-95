import io
import PIL
import pickle
import requests
from sklearn.preprocessing import normalize
import os

from botnoi import getbow as gb
tfidfpath = os.path.join(os.path.dirname(gb.__file__),'botnoitfidf_v1.mod')
modtfidf = pickle.load(open(tfidfpath,'rb'))
print('load model tfidf')
def extract_bowtfidf(textList):
  '''extract bow with tfidf vectors'''

  
  feat = gb.sentencevector(textList,modtfidf)
  feat = normalize(feat)
  return feat

from botnoi import getw2v as gw
w2vpath = os.path.join(os.path.dirname(gw.__file__),'botnoiw2v_small.mod')
modw2v = pickle.load(open(w2vpath,'rb'))
print('load model w2v')
def extract_w2vlight(textList):
  '''extract w2v vectors'''
  
  feat = gw.sentencevector(textList,modw2v)
  feat = normalize(feat)
  return feat

from botnoi import nlpcorrection as nc
sencor = os.path.join(os.path.dirname(nc.__file__),'botnoidict.p')
modworddict = pickle.load(open(sencor,'rb'))
print('load word dict')
def getsentencescore(sentence):
  '''get sentence score'''
  
  res = nc.sentencescore(sentence,modworddict)
  return res


def printhello():
  print('hello')



