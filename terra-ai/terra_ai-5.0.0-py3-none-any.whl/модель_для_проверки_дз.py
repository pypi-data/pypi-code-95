from . import сегментация, повышение_размерности, датасет, check_for_errors
from tensorflow.keras.preprocessing.text import tokenizer_from_json
from tensorflow.keras.layers import *
from tensorflow.keras.models import load_model, Sequential, Model # Подключаем модель типа Sequential
from tensorflow.keras.optimizers import Adam
import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns
from tensorflow.keras.utils import to_categorical, plot_model # Полкючаем методы .to_categorical() и .plot_model()
sns.set_style('darkgrid') 
from tensorflow.keras import backend as K # Импортируем модуль backend keras'а
from tensorflow.keras.optimizers import Nadam, RMSprop, Adadelta,Adam # Импортируем оптимизатор Adam
from tensorflow.keras.callbacks import ModelCheckpoint, LambdaCallback, ReduceLROnPlateau
from tensorflow.keras.layers import Input, RepeatVector, Conv2DTranspose, concatenate, Activation, Embedding, Input, MaxPooling2D, Conv2D, BatchNormalization # Импортируем стандартные слои keras
import importlib.util, sys, gdown
import tensorflow as tf
from PIL import Image
import pandas as pd
from IPython.display import clear_output
from tensorflow.keras.preprocessing import image
import termcolor
from termcolor import colored
from google.colab import files
import subprocess, os, warnings, time
from pandas.core.common import SettingWithCopyWarning
from subprocess import STDOUT, check_call
import requests
import random
import zipfile
from sklearn.model_selection import train_test_split
import ast
from tabulate import tabulate
import getpass
from tensorflow.keras.datasets import mnist
from tensorflow.keras.layers import *
from tensorflow.keras.models import *
warnings.filterwarnings('ignore')
import logging
tf.get_logger().setLevel(logging.ERROR)

import nltk, pymorphy2, io, json
from tensorflow.keras.preprocessing.text import Tokenizer, text_to_word_sequence
from keras.layers import *
from tensorflow.keras.preprocessing.sequence import pad_sequences
nltk.download('stopwords')


def создать_выборки_вакансии_test():
  global idx_val
  dir = '/content/Вакансии'
  """
  Parameters:
  dir (str)              Путь к папке с датасетом

  Return:
  x_train, y_train, x_val, y_val
  """

  data = np.load(dir + '/X_train.npy')
  labels = np.load(dir + '/Y_train.npy')

  x_val, y_val = data[300:], labels[300:]
  idx_val = [i for i in range(data[300:500].shape[0])]

  return (x_train, y_train), (x_val, y_val)



    
def создать_выборки_test(maxWordsCount, xLen, step, путь_к_базе='content/Болезни/'):
  path = путь_к_базе
  text = []
  classes = []
  n = 0
  codecs_list = ['UTF-8', 'Windows-1251']

  for filename in sorted(os.listdir(path)): # Проходим по всем файлам в директории договоров
      n +=1
      for codec_s in codecs_list:
        try:
            text.append(readText(path+filename, codec_s)) # Преобразуем файл в одну строку и добавляем в agreements
            classes.append(filename.replace(".txt", ""))
            break
        except UnicodeDecodeError:
            print('Не прочитался файл: ', path+currdir+'/'+filename, codec_s)
        else:
            next 

  stop_words = nltk.corpus.stopwords.words('russian')
  lexeme_list = ['POS', 'animacy', 'aspect', 'case', 'gender', 'involvement', 'mood', 'number', 'person', 'tense', 'transitivity', 'voice']

  words = [] # Здесь будут лежать все списки слов каждого из описаний заболеваний
  tags = []   # Здесь будут лежать все списки списков граммем для каждого слова
  tags_all = [] # Здесь будут лежать все списки граммем всех слов для тренировки токенайзера
  for i in range(len(text)):
    word, tag = text2Words(text[i])
    words.append(word)
    tags.append(tag)
  for k in tags:
    for t in k:
      tags_all.append(t)

  tokenizer = Tokenizer(num_words=maxWordsCount, filters='!"#$%&()*+,-––—./:;<=>?@[\\]^_`{|}~\t\n\xa0', lower=True, split=' ', oov_token='unknown', char_level=False)
  tokenizer.fit_on_texts(words) 
  items = list(tokenizer.word_index.items())


  tokenizer_json1 = tokenizer.to_json()
  with io.open('tokenizer1.json', 'w', encoding='utf-8') as f:
      f.write(json.dumps(tokenizer_json1, ensure_ascii=False))
  with open('tokenizer1.json') as f:
      data = json.load(f)
      tokenizer = tokenizer_from_json(data)

  items = list(tokenizer.word_index.items()) 

  maxWordsCount2 = 50 

  tokenizer2 = Tokenizer(num_words=maxWordsCount2, filters='!"#$%&()*+,-––—./:;<=>?@[\\]^_`{|}~\t\n\xa0', lower=True, split=' ', oov_token='unknown', char_level=False)

  tokenizer2.fit_on_texts(tags_all) 
  items2 = list(tokenizer2.word_index.items()) 

  tokenizer_json2 = tokenizer2.to_json()
  with io.open('tokenizer2.json', 'w', encoding='utf-8') as f:
      f.write(json.dumps(tokenizer_json2, ensure_ascii=False))

  with open('tokenizer2.json') as f:
      data = json.load(f)
      tokenizer2 = tokenizer_from_json(data)

  items2 = list(tokenizer2.word_index.items())

  xTrainIndexes = tokenizer.texts_to_sequences(words) 
  xTrainTagsIndexes = []
  for tag in tags:
    xTrainTagsIndexes.append(tokenizer2.texts_to_sequences(tag))
  nVal = 200   
  valWords = []    
  valTagsWords = []  
  for i in range(len(xTrainIndexes)):
    valWords.append(xTrainIndexes[i][-nVal:])
  for i in range(len(xTrainTagsIndexes)):
    valTagsWords.append(xTrainTagsIndexes[i][-nVal:])

  (xVal, yVal) = createSetsMultiClasses(valWords, xLen, step)
  (xTagsVal, _) = createSetsMultiClasses(valTagsWords, xLen, step)

  xVal01 = tokenizer.sequences_to_matrix(xVal.tolist(), mode="tfidf")
  xTagsVal = np.reshape(xTagsVal, (xTagsVal.shape[0], -1))
  xTagsVal01 = tokenizer2.sequences_to_matrix(xTagsVal.tolist())


  x_val = [xVal, xVal01, xTagsVal01]
  y_val = yVal
  clear_output(wait=True)
  print('Формирование выборки завершено')
  return x_val, y_val

def readText(fileName, encod):
    f = open(fileName, 'r', encoding=encod)
    text = f.read()
    text = text.replace("\n", " ")
    return text

def text2Words(text):
  stop_words = nltk.corpus.stopwords.words('russian')
  lexeme_list = ['POS', 'animacy', 'aspect', 'case', 'gender', 'involvement', 'mood', 'number', 'person', 'tense', 'transitivity', 'voice']

  text = text.replace(".", " ")
  text = text.replace("—", " ")
  text = text.replace(",", " ")
  text = text.replace("!", " ")
  text = text.replace("?", " ")
  text = text.replace("…", " ")
  text = text.replace("-", " ")
  text = text.replace("(", " ")
  text = text.replace(")", " ")
  text = text.replace(";", " ")
  text = text.replace("°c", " ")
  text = text.replace("–", " ")
  text = text.replace("и/ить", " ")
  text = text.lower()
  morph = pymorphy2.MorphAnalyzer()
  
  words = []
  tags = []
  currWord = ""
  for symbol in text[1:]:

    if (symbol != " "):
      currWord += symbol
    else:
      if (currWord != "") & (currWord not in stop_words): # 
        words.append(currWord)
        currWord = ""
      else:
        currWord = ""
  if (currWord != "") & (currWord not in stop_words): #
        words.append(currWord)
  # генератором списков проходимся по каждому сформированному слову и лемматиризируем его с помощью pymorphy до получения граммем
  #words = [morph.parse(word)[0].normal_form for word in words]
  #tags = [morph.parse(word)[0].tag for word in words] # .cyr_repr
  for word in words:
    tag_word = []
    lex_0 = morph.parse(word)[0].tag.POS  # Part of Speech, часть речи
    if lex_0 != None:
        tag_word.append(lex_0)
    else:
        tag_word.append('not')
    lex_1 = morph.parse(word)[0].tag.animacy  # одушевленность
    if lex_1 != None:
        tag_word.append(lex_1)
    else:
        tag_word.append('not')
    lex_2 = morph.parse(word)[0].tag.aspect # вид: совершенный или несовершенный
    if lex_2 != None:
        tag_word.append(lex_2)
    else:
        tag_word.append('not')
    lex_3 = morph.parse(word)[0].tag.case # падеж
    if lex_3 != None:
        tag_word.append(lex_3)  
    else:
        tag_word.append('not')     
    lex_4 = morph.parse(word)[0].tag.gender # род (мужской, женский, средний)
    if lex_4 != None:
        tag_word.append(lex_4)
    else:
        tag_word.append('not') 
    lex_5 = morph.parse(word)[0].tag.involvement  # включенность говорящего в действие
    if lex_5 != None:
        tag_word.append(lex_5)
    else:
        tag_word.append('not')
    lex_6 = morph.parse(word)[0].tag.mood # наклонение (повелительное, изъявительное)
    if lex_6 != None:
        tag_word.append(lex_6)
    else:
        tag_word.append('not')
    lex_7 = morph.parse(word)[0].tag.number # число (единственное, множественное)
    if lex_7 != None:
        tag_word.append(lex_7)
    else:
        tag_word.append('not')
    lex_8 = morph.parse(word)[0].tag.person # лицо (1, 2, 3)
    if lex_8 != None:
        tag_word.append(lex_8)
    else:
        tag_word.append('not')
    lex_9 = morph.parse(word)[0].tag.tense  # время (настоящее, прошедшее, будущее)
    if lex_9 != None:
        tag_word.append(lex_9)
    else:
        tag_word.append('not')
    lex_10 = morph.parse(word)[0].tag.transitivity  # переходность (переходный, непереходный)
    if lex_10 != None:
        tag_word.append(lex_10)
    else:
        tag_word.append('not')
    lex_11 = morph.parse(word)[0].tag.voice # залог (действительный, страдательный)
    if lex_11 != None:
        tag_word.append(lex_11)
    else:
        tag_word.append('not')
    tags.append(tag_word)
    # генератором списков проходимся по каждому сформированному слову и лемматиризируем его с помощью pymorphy
  words = [morph.parse(word)[0].normal_form for word in words]

  return words, tags
