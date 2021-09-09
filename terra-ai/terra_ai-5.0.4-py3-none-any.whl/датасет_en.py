from . import сегментация_en, повышение_размерности, обнаружение, обработка_текста, сегментация
import subprocess
from subprocess import STDOUT, check_call
import os, time, random, re,pymorphy2
import matplotlib.pyplot as plt
import numpy as np
from tensorflow.keras.preprocessing import image
from IPython import display
from tensorflow.keras.utils import to_categorical, plot_model # Полкючаем методы .to_categorical() и .plot_model()
from tensorflow.keras import datasets # Подключаем набор датасетов
import importlib.util, sys, gdown
from tqdm.notebook import tqdm_notebook as tqdm_
from PIL import Image
import pandas as pd
import requests
import ast
import json

###
###                 ЗАГРУЗКА ДАННЫХ
###
def загрузить_базу(база = '', справка = False):
  база = база.upper()
  print('Загрузка данных')
  print('Это может занять несколько минут...')  
  if база == 'MNIST':
    (x1, y1), (x2, y2) = загрузить_базу_МНИСТ()
    display.clear_output(wait=True)
    print('Загрузка данных завершена \n')
    if справка:
      print('Вы скачали базу рукописных цифр MNIST. \nБаза состоит из двух наборов данных: обучающего (60тыс изображений) и тестовго (10тыс изображений).')
      print('Размер каждого изображения: 28х28 пикселей')
    return (x1, y1), (x2, y2)
  
  elif база == 'АВТО-2':
    загрузить_базу_АВТОМОБИЛИ()
    display.clear_output(wait=True)
    print('Загрузка данных завершена \n')
    print('url:', url)
    if справка:
      print('Вы скачали базу с изображениями марок автомобилей. \nБаза состоит из двух марок: Феррари и Мерседес')
      print('Количество изображений в базе: 2249') 

  elif база == 'АВТО-3':
    загрузить_базу_АВТОМОБИЛИ_3()
    display.clear_output(wait=True)
    print('Загрузка данных завершена \n')
    print('url:', url)
    if справка:
      print('Вы скачали базу с изображениями марок автомобилей. \nБаза состоит из трех марок: Феррари, Мерседес и Рено')
      print('Количество изображений в базе: 3429')

  elif база == 'САМОЛЕТЫ':
    x,y = загрузить_базу_САМОЛЕТЫ()
    display.clear_output(wait=True)
    print('Загрузка данных завершена \n')
    print('url:', url)
    if справка:
      print('Вы скачали базу самолетов. \nБаза состоит из оригинальных изображений и соовтетствующих им размеченных сегментированных изображений.')
      print('Количество изображений в базе: 981')    
    return x, y

  elif база == 'САМОЛЕТЫ_МАКС':
    x,y = загрузить_базу_САМОЛЕТЫ_макс()
    display.clear_output(wait=True)
    print('Загрузка данных завершена \n')
    print('url:', url)
    if справка:
      print('Вы скачали базу самолетов. \nБаза состоит из оригинальных изображений и соовтетствующих им размеченных сегментированных изображений.')
      print('Количество изображений в базе: 981') 
      print('размер изображений (520х960 пикселей)')  
    return x, y
  
  elif база == 'ЛЮДИ':
    x,y = загрузить_базу_Люди()
    display.clear_output(wait=True)
    print('Загрузка данных завершена \n')
    print('url:', url)
    if справка:
      print('Вы скачали базу на которой изображены люди. \nБаза состоит из оригинальных изображений и соовтетствующих им размеченных сегментированных изображений.')
      print('Количество изображений в базе: ', len(x)) 
    return x, y


  elif база == 'КОЖНЫЕ ЗАБОЛЕВАНИЯ':
    загрузить_базу_БОЛЕЗНИ()
    display.clear_output(wait=True)
    print('Загрузка данных завершена \n')
    print('url:', url)
    if справка:
      print('Вы скачали базу кожных заболеваний. \nБаза состоит из оригинальных изображений и соовтетствующих им размеченных сегментированных изображений.')
      print('Количество категорий заболеваний: 10 (Акне, Витилиго, Герпес, Дерматит, Лишай, Невус, Псориаз, Сыпь, Хлоазма, Экзема)')    
      print('Количество изображений в базе: 981')    
  
  elif база == 'ПОВЫШЕНИЕ РАЗМЕРНОСТИ':
    x, y = загрузить_базу_HR()
    display.clear_output(wait=True)
    print('Загрузка данных завершена \n')
    print('url:', url)
    if справка:
      print('Вы скачали базу изображений для задачи повышения размерности')
      print('База содержит изображения высокого качества и соответствующие им изображения низкого качества')
    return x, y

  elif база == 'ОБНАРУЖЕНИЕ ЛЮДЕЙ':
    загрузить_базу_ЛЮДЕЙ()
    display.clear_output(wait=True)
    print('Загрузка данных завершена \n')
    print('url:', url)
    if справка:
      print('Загружена размеченная база изображений для обнаружения людей')      
    print()
    print('ВНИМАНИЕ!!! Были установлены дополнительные библиотеки. Необходимо перезапустить среду для продолжения работы')
    print('Выберите пункт меню Runtime/Restart runtime и нажмите «Yes»')
    print('После этого сделайте повторный запуск ячейки: import terra_ai')
  
  elif база == 'СИМПТОМЫ ЗАБОЛЕВАНИЙ':
    #Загрузка базы
    загрузить_базу_ЗАБОЛЕВАНИЯ()
    #display.clear_output(wait=True)
    print('Загрузка данных завершена \n')
    print('url:', url)
    if справка:
      print('Загружена база симптомов заболеваний') 
     
    print()
    
  elif база == 'ПИСАТЕЛИ':
    загрузить_базу_ПИСАТЕЛИ()
    display.clear_output(wait=True)
    print('Загрузка данных завершена \n')
    print('url:', url)
    if справка:
      print('Загружена база писателей')      
    print()

  elif база == 'ДИАЛОГИ':
    x,y = загрузить_базу_ДИАЛОГИ()
    display.clear_output(wait=True)
    print('Загрузка данных завершена \n')
    print('url:', url)
    if справка:
      print('Загружена база диалогов')
      print('Количество пар вопрос-ответ: 50 тысяч')
    print()
    return x,y

  elif база == 'ДОГОВОРЫ':
    x = загрузить_базу_ДОГОВОРА()
    display.clear_output(wait=True)
    print('Загрузка данных завершена \n')
    print('url:', url)
    if справка:
      print('Загружена база договоров')
      print('База размечена по 6 категориям: Условия - Запреты - Стоимость - Деньги - Сроки - Неустойка')
# s6 Всё про адреса и геолокации
    print()
    return x

  elif база == 'КВАРТИРЫ':
    загрузить_базу_КВАРТИРЫ()
    display.clear_output(wait=True)
    print('Загрузка данных завершена \n')
    print('url:', url)
    if справка:
      print('Загружена база квартир')
    print()

  elif база == 'ГУБЫ':
    x,y = загрузить_базу_ГУБЫ()
    display.clear_output(wait=True)
    print('Загрузка данных завершена \n')
    print('url:', url)
    if справка:
      print('Загружена база сегментации женских губ')
    print()
    return x,y

  elif база == 'ТРАФИК':
    x = загрузить_базу_ТРАФИК()
    display.clear_output(wait=True)
    print('Загрузка данных завершена \n')
    print('url:', url)
    if справка:
      print('Загружена база трафика компании')
    print()
    return x

  elif база == 'УМНЫЙ ДОМ':
    загрузить_базу_УМНЫЙ_ДОМ()
    display.clear_output(wait=True)
    print('Загрузка данных завершена \n')
    print('url:', url)
    if справка:
      print('Загружена база голосовых команд для умного дома')
    print()

  elif база == 'ТРЕЙДИНГ':
    загрузить_базу_ТРЕЙДИНГ()
    display.clear_output(wait=True)
    print('Загрузка данных завершена \n')
    print('url:', url)
    if справка:
      print('Загружены базы акций трех вариантов: полиметаллы, газпром и яндекс')
    print()
  else:
    display.clear_output(wait=True)
    print('Указанная база не найдена \n')

def загрузить_базу_конструктора():
  url = 'https://storage.googleapis.com/aiu_bucket/UI.zip' # Указываем URL-файла
  output = 'UI.zip' # Указываем имя файла, в который сохраняем файл
  gdown.download(url, output, quiet=True) # Скачиваем файл по указанному URL
  распаковать_архив(откуда = "UI.zip", куда = "/content") 
def загрузить_базу_МНИСТ():
  (x_train_org, y_train_org), (x_test_org, y_test_org) = datasets.mnist.load_data() # Загружаем данные набора MNIST
  return (x_train_org, y_train_org), (x_test_org, y_test_org)

def загрузить_базу_ТРАФИК():
  global url
  url = 'https://storage.googleapis.com/terra_ai/DataSets/traff.csv'
  output = 'traff.csv' # Указываем имя файла, в который сохраняем файл
  gdown.download(url, output, quiet=True)
  dataframe = pd.read_csv('traff.csv', header=None)
  dataframe.rename(columns={0: "Дата", 1: "Трафик"}, inplace=True)
  
  for i in range(dataframe.shape[0]):
    dataframe.iloc[i, 1] = float(dataframe.iloc[i, 1].replace(',',''))
  return dataframe

def загрузить_базу_ТРЕЙДИНГ():
  global url
  url = 'https://storage.googleapis.com/terra_ai/DataSets/shares.zip'
  output = 'shares.zip' # Указываем имя файла, в который сохраняем файл
  gdown.download(url, output, quiet=True) 
  распаковать_архив(
      откуда = "shares.zip",
      куда = "/content"
  )

def загрузить_базу_АВТОМОБИЛИ():
  global url
  url = 'https://storage.googleapis.com/terra_ai/DataSets/car_2.zip'
  output = 'car.zip' # Указываем имя файла, в который сохраняем файл
  gdown.download(url, output, quiet=True) # Скачиваем файл по указанному URL
  распаковать_архив(
      откуда = "car.zip",
      куда = "/content/автомобили"
  )

def загрузить_базу_УМНЫЙ_ДОМ():
  global url
  url = 'https://storage.googleapis.com/terra_ai/DataSets/cHome.zip'
  output = 'cHome.zip' # Указываем имя файла, в который сохраняем файл
  gdown.download(url, output, quiet=True) # Скачиваем файл по указанному URL
  распаковать_архив(
      откуда = "cHome.zip",
      куда = "/content/Умный_дом"
  )

def загрузить_базу_КВАРТИРЫ():
  global url
  url = 'https://storage.googleapis.com/terra_ai/DataSets/moscow.csv'
  output = 'moscow.csv' # Указываем имя файла, в который сохраняем файл
  gdown.download(url, output, quiet=True) # Скачиваем файл по указанному URL

def загрузить_базу_ДИАЛОГИ():
  global url
  #обнаружение.выполнить_команду('mkdir content')
  url = 'https://storage.googleapis.com/terra_ai/DataSets/dialog.txt'
  output = 'dialog.txt' # Указываем имя файла, в который сохраняем файл
  gdown.download(url, output, quiet=True) # Скачиваем файл по указанному URL
  f = open('dialog.txt', 'r', encoding='utf-8')
  text= f.read()
  text = text.replace('"','')
  text = text.split('\n')
  question = text[::3]
  answers = text[1::3]
  return question[:-1], answers
  
def загрузить_базу_АВТОМОБИЛИ_3():
  global url
  url = 'https://storage.googleapis.com/terra_ai/DataSets/car.zip'
  output = 'car.zip' # Указываем имя файла, в который сохраняем файл
  gdown.download(url, output, quiet=True) # Скачиваем файл по указанному URL
  распаковать_архив(
      откуда = "car.zip",
      куда = "/content/автомобили"
  )

def загрузить_базу_ЗАБОЛЕВАНИЯ(): 
  global url
  url = 'https://storage.googleapis.com/terra_ai/DataSets/symptoms.zip'
  output = 'symptoms.zip' # Указываем имя файла, в который сохраняем файл
  gdown.download(url, output, quiet=True) # Скачиваем файл по указанному URL

  # Скачиваем и распаковываем архив
  распаковать_архив(
      откуда = "symptoms.zip",
      куда = "content/"
  )

def загрузить_базу_ПИСАТЕЛИ():
  global url
  url = 'https://storage.googleapis.com/terra_ai/DataSets/writers.zip'
  output = 'writers.zip' # Указываем имя файла, в который сохраняем файл
  gdown.download(url, output, quiet=True) # Скачиваем файл по указанному URL

  # Скачиваем и распаковываем архив
  распаковать_архив(
      откуда = "writers.zip",
      куда = "content/"
  )
  
def загрузить_базу_ЛЮДЕЙ():
  global url
  url = 'https://github.com/ultralytics/yolov5/archive/master.zip'
  output = 'tmp.zip' # Указываем имя файла, в который сохраняем файл
  gdown.download(url, output, quiet=True) # Скачиваем файл по указанному URL

  распаковать_архив(
      откуда = "tmp.zip",
      куда = "/content"
  )
  # Скачиваем и распаковываем архив
  url = 'https://github.com/ultralytics/yolov5/releases/download/v1.0/coco2017val.zip'
  output = 'tmp.zip' # Указываем имя файла, в который сохраняем файл
  gdown.download(url, output, quiet=True) # Скачиваем файл по указанному URL

  распаковать_архив(
      откуда = "tmp.zip",
      куда = "/content"
  )

  url = 'https://github.com/ultralytics/yolov5/releases/download/v1.0/coco128.zip'
  output = 'tmp.zip' # Указываем имя файла, в который сохраняем файл
  gdown.download(url, output, quiet=True) # Скачиваем файл по указанному URL

  распаковать_архив(
      откуда = "tmp.zip",
      куда = "/content"
  )
  обнаружение.выполнить_команду('echo y|pip uninstall albumentations > /dev/null')
  обнаружение.выполнить_команду('pip install -q --no-input -U git+https://github.com/albumentations-team/albumentations > /dev/null')
  обнаружение.выполнить_команду('pip install -q -U PyYAML')
  
  
def загрузить_базу_ДОГОВОРА():
  global url
  url = 'https://storage.googleapis.com/terra_ai/DataSets/docs.zip'
  output = 'Договоры.zip' # Указываем имя файла, в который сохраняем файл
  gdown.download(url, output, quiet=True) # Скачиваем файл по указанному URL

  # Скачиваем и распаковываем архив
  распаковать_архив(
      откуда = "Договоры.zip",
      куда = "/content/Договоры"
      )
 
  url = 'https://storage.googleapis.com/terra_ai/DataSets/test_doc.txt'
  output = '/content/Договоры/test_doc.txt' # Указываем имя файла, в который сохраняем файл
  gdown.download(url, output, quiet=True) # Скачиваем файл по указанному URL


  def readText(fileName):
    f = open(fileName, 'r', encoding='utf-8') #Открываем наш файл для чтения и считываем из него данные 
    text = f.read() #Записываем прочитанный текст в переменную 
    delSymbols = ['\n', "\t", "\ufeff", ".", "_", "-", ",", "!", "?", "–", "(", ")", "«", "»", "№", ";"]
    for dS in delSymbols: # Каждый символ в списке символов для удаления
      text = text.replace(dS, " ") # Удаляем, заменяя на пробел
    text = re.sub("[.]", " ", text) 
    text = re.sub(":", " ", text)
    text = re.sub("<", " <", text)
    text = re.sub(">", "> ", text)
    text = ' '.join(text.split()) 
    return text # Возвращаем тексты

  def text2Words(text):
    morph = pymorphy2.MorphAnalyzer() # Создаем экземпляр класса MorphAnalyzer
    words = text.split(' ') # Разделяем текст на пробелы
    words = [morph.parse(word)[0].normal_form for word in words] #Переводим каждое слово в нормалную форму  
    return words # Возвращаем слова   
  directory = 'Договоры/Договора432/' # Путь к папке с договорами
  agreements = [] # Список, в который запишем все наши договоры
  for filename in os.listdir(directory): # Проходим по всем файлам в директории договоров
    try:    
        txt = readText(directory + filename) # Читаем текст договора
        if txt != '': # Если текст не пустой
          agreements.append(readText(directory + filename)) # Преобразуем файл в одну строку и добавляем в agreements
    except:
        continue
  words = [] # Здесь будут храниться все договора в виде списка слов
  curTime = time.time() # Засечем текущее время
  for i in tqdm_(range(len(agreements)), desc='Обработка догововров', ncols=1000): # Проходимся по всем договорам
    words.append(text2Words(agreements[i])) # Преобразуем очередной договор в список слов и добавляем в words
  wordsToTest = words[-10:] # Возьмем 10 текстов для финальной проверки обученной нейронной сети 
  words = words[:-10] # Для обученающей и проверочной выборок возьмем все тексты, кроме последних 10
  display.clear_output(wait=True)
  return (agreements, words, wordsToTest)  #, agreements

def загрузить_базу_САМОЛЕТЫ():
  global url
  url = 'https://storage.googleapis.com/terra_ai/DataSets/%D0%A1%D0%B0%D0%BC%D0%BE%D0%BB%D0%B5%D1%82%D1%8B.zip'
  output = 'самолеты.zip' # Указываем имя файла, в который сохраняем файл
  gdown.download(url, output, quiet=True) # Скачиваем файл по указанному URL
  # Скачиваем и распаковываем архив
  распаковать_архив(
      откуда = "самолеты.zip",
      куда = "/content"
  )
  url = 'https://storage.googleapis.com/terra_ai/DataSets/segment.zip' # Указываем URL-файла
  output = 'сегменты.zip' # Указываем имя файла, в который сохраняем файл
  gdown.download(url, output, quiet=True) # Скачиваем файл по указанному URL
  # Скачиваем и распаковываем архив
  распаковать_архив(
      откуда = "сегменты.zip",
      куда = "/content"
  )
  display.clear_output(wait=True)  
  # Обрабатываем скаченные изображения
  x, y = обработка_изображений(
      оригиналы = 'Самолеты',
      сегменты = 'Сегменты',
      размер = (176, 320)
  )
  return x, y

def загрузить_базу_САМОЛЕТЫ_макс():
  global url
  url = 'https://storage.googleapis.com/terra_ai/DataSets/airplane_max.zip' # Указываем URL-файла
  output = 'airplane_max.zip' # Указываем имя файла, в который сохраняем файл
  gdown.download(url, output, quiet=True) # Скачиваем файл по указанному URL
  # Скачиваем и распаковываем архив
  распаковать_архив(
      откуда = "airplane_max.zip",
      куда = "/content"
  )
  url = 'https://storage.googleapis.com/terra_ai/DataSets/segment_max.zip' # Указываем URL-файла
  output = 'segment_max.zip' # Указываем имя файла, в который сохраняем файл
  gdown.download(url, output, quiet=True) # Скачиваем файл по указанному URL
  # Скачиваем и распаковываем архив
  распаковать_архив(
      откуда = "segment_max.zip",
      куда = "/content"
  )
  display.clear_output(wait=True)  
  # Обрабатываем скаченные изображения
  x, y = обработка_изображений(
      оригиналы = 'airplane_max',
      сегменты = 'segment_max',
      размер = (520, 960)
  )
  return x, y

def загрузить_базу_Люди():
  global url
  url = 'https://storage.googleapis.com/terra_ai/DataSets/original_people.zip' # Указываем URL-файла
  output = 'original_people.zip' # Указываем имя файла, в который сохраняем файл
  gdown.download(url, output, quiet=True) # Скачиваем файл по указанному URL
  # Скачиваем и распаковываем архив
  распаковать_архив(
      откуда = "original_people.zip",
      куда = "/content"
  )
  url = 'https://storage.googleapis.com/terra_ai/DataSets/segment_people.zip' # Указываем URL-файла
  output = 'segment_people.zip' # Указываем имя файла, в который сохраняем файл
  gdown.download(url, output, quiet=True) # Скачиваем файл по указанному URL
  # Скачиваем и распаковываем архив
  распаковать_архив(
      откуда = "segment_people.zip",
      куда = "/content"
  )
  display.clear_output(wait=True)  
  # Обрабатываем скаченные изображения
  x, y = обработка_изображений(
      оригиналы = 'original',
      сегменты = 'segment',
      размер = (256, 384)
  )
  return x, y
  
def загрузить_базу_ГУБЫ():
  global url
  url = 'https://storage.googleapis.com/terra_ai/DataSets/lips.zip' # Указываем URL-файла
  output = 'lips.zip' # Указываем имя файла, в который сохраняем файл
  gdown.download(url, output, quiet=True) # Скачиваем файл по указанному URL
  # Скачиваем и распаковываем архив
  распаковать_архив(
      откуда = "lips.zip",
      куда = "/content"
  )
  display.clear_output(wait=True)  
  # Обрабатываем скаченные изображения
  x, y =  обработка_изображений(
      оригиналы = 'Губы/оригинал',
      сегменты = 'Губы/сегментация',
      размер = (192, 256)
  )
  print('x',len(x))
  print('y',len(y))
  return x, y

def загрузить_базу_БОЛЕЗНИ():
  global url
  url = 'https://storage.googleapis.com/terra_ai/DataSets/origin.zip'
  output = 'diseases.zip' # Указываем имя файла, в который сохраняем файл
  gdown.download(url, output, quiet=True) # Скачиваем файл по указанному URL
  # Скачиваем и распаковываем архив
  распаковать_архив(
      откуда = "diseases.zip",
      куда = "/content/diseases"
  )
  url = 'https://storage.googleapis.com/terra_ai/DataSets/segmentation.zip'
  output = 'segm.zip' # Указываем имя файла, в который сохраняем файл
  gdown.download(url, output, quiet=True) # Скачиваем файл по указанному URL
  # Скачиваем и распаковываем архив
  распаковать_архив(
      откуда = "segm.zip",
      куда = "/content/diseases"
  )

def загрузить_базу_HR():
  global url
  # Скачиваем и распаковываем архив в колаб по ссылке
  url = 'http://data.vision.ee.ethz.ch/cvl/DIV2K/DIV2K_valid_LR_bicubic_X4.zip'          
  output = 'DIV2K_valid_LR_bicubic_X4.zip' # Указываем имя файла, в который сохраняем файл
  gdown.download(url, output, quiet=True) # Скачиваем файл по указанному URL
  распаковать_архив(
      откуда = "DIV2K_valid_LR_bicubic_X4.zip",
      куда = "/content/div2k"
  )
  url = 'http://data.vision.ee.ethz.ch/cvl/DIV2K/DIV2K_valid_HR.zip'
  output = 'DIV2K_valid_HR.zip' # Указываем имя файла, в который сохраняем файл
  gdown.download(url, output, quiet=True) # Скачиваем файл по указанному URL
  распаковать_архив(
      откуда = "DIV2K_valid_HR.zip",
      куда = "/content/div2k"
  )
  pathHR = '/content/div2k/DIV2K_valid_HR/'
  pathLR = '/content/div2k/DIV2K_valid_LR_bicubic/X4/'
  imagesList = [os.listdir(pathHR), os.listdir(pathLR)] # Список из корневых каталогов изображений, их два - hr и lr
  train_hr = []
  train_lr = []

  # В цикле проходимся по каталогу с hr изображениями
  for image in sorted(imagesList[0]):
      img = Image.open(pathHR + image)
      train_hr.append(img) # Добавляем все изображения в список

  # В цикле проходимся по каталогу с lr изображениями
  for image in sorted(imagesList[1]):
      img = Image.open(pathLR + image)
      train_lr.append(img) # Добавляем все изображения в список
  return train_hr, train_lr

###
###                    ДЕМОНСТРАЦИЯ ПРИМЕРОВ
###

def показать_примеры(**kwargs):
  if 'questions' in kwargs:  
    count = 1
    if 'quantity' in kwargs:
        count = kwargs['quantity']
    questions = kwargs['questions']
    answers = kwargs['ответы']
    for i in range(count):
        print()
        idx = np.random.randint(len(questions)-1)
        print('Вопрос:', questions[idx])
        print('Ответ:', answers[idx])
  if 'path' in kwargs:
    kwargs['path'] = '/content'+kwargs['path']
    count = len(os.listdir(kwargs['path']))
    fig, axs = plt.subplots(1, count, figsize=(25, 5)) #Создаем полотно из 3 графиков
    for i in range(count): #Проходим по всем классам
      car_path = kwargs['path'] + '/' + sorted(os.listdir(kwargs['path']))[i] + '/'#Формируем путь к выборке
      img_path = car_path + np.random.choice(os.listdir(car_path)) #Выбираем случайное фото для отображения
      axs[i].imshow(image.load_img(img_path, target_size=(108, 192))) #Отображение фотографии
      axs[i].axis('off') # отключаем оси
    plt.show() #Показываем изображения
  if 'dataset_name' in kwargs:    
    if kwargs['dataset_name'] == 'симптомы':        
        path = 'content/Болезни/'
        text = []
        classes = []
        n = 0
        codecs_list = ['UTF-8', 'Windows-1251']

        for filename in sorted(os.listdir(path)): # Проходим по всем файлам в директории договоров
            n +=1
            for codec_s in codecs_list:
                try:
                    text.append(обработка_текста.readText(path+filename, codec_s)) # Преобразуем файл в одну строку и добавляем в agreements
                    classes.append(filename.replace(".txt", ""))
                    break
                except UnicodeDecodeError:
                    print('Не прочитался файл: ', path+currdir+'/'+filename, codec_s)
                else:
                    next 
        nClasses = len(classes) #определяем количество классов
        print('В данной базе содержатся симптомы следующих заболеваний:')
        print(classes)        
        n = np.random.randint(10)
        print()
        print('Пример симптомов случайного заболевания:')
        print('Заболевание: ', classes[n])
        print('Симптомы:')
        print('     *', text[n][:100]) # Пример первых 100 символов первого документа      
        return classes, nClasses

    elif kwargs['dataset_name'] == 'писатели':        
        path = 'content/writers/'
        text = []
        classes = []
        n = 0
        codecs_list = ['UTF-8', 'Windows-1251']

        for filename in os.listdir(path): # Проходим по всем файлам в директории договоров
            n +=1
            for codec_s in codecs_list:
                try:
                    text.append(обработка_текста.readText(path+filename, codec_s)) # Преобразуем файл в одну строку и добавляем в agreements
                    classes.append(filename.replace(".txt", ""))
                    break
                except UnicodeDecodeError:
                    print('Не прочитался файл: ', path+currdir+'/'+filename, codec_s)
                else:
                    next 
        nClasses = len(classes) #определяем количество классов
        print('В данной базе содержатся произведения следующих писателей:')
        print(classes)        
        n = np.random.randint(6)
        print()
        print('Пример текста случайного произведения и автора:')
        print('Автор: ', classes[n])
        print('Произведение и пример: ', text[n][:78], '\n', text[n][78:178], '\n', text[n][178:278], '\n',
                                         text[n][278:378], '\n', text[n][378:478], '\n', text[n][578:678], '\n', 
                                         text[n][778:878], '\n', text[n][978:1078]) # Пример первых 1000 символов первого документа      
        return classes, nClasses

    elif kwargs['dataset_name'] == 'обнаружение':
      обнаружение.показать_примеры()
        
  elif ('images' in kwargs):
    if 'labels' in kwargs:
      count = kwargs['labels'].max() # Задачем количество примеров
    elif 'quantity' in kwargs:
      count = kwargs['quantity'] # Задачем количество примеров
    else:
      count = 5
    f, axs = plt.subplots(1,count,figsize=(22,5)) # Создаем полотно для визуализации
    idx = np.random.choice(kwargs['images'].shape[0], count) # Получаем 5 случайных значений из диапазона от 0 до 60000 (x_train_org.shape[0])
    for i in range(count):
      axs[i].imshow(kwargs['images'][idx[i]], cmap='gray') # Выводим изображение из обучающей выборки в черно-белых тонах
      axs[i].axis('off')
    plt.show()
  elif ('original' in kwargs):
    показать_примеры_сегментации(**kwargs)
  elif ('изображения_низкого_качества' in kwargs):
    показать_примеры_HR(**kwargs)
    

def показать_примеры_HR(**kwargs):
  lr = kwargs['изображения_низкого_качества']
  hr = kwargs['изображения_высокого_качества']
  '''
  показать_примеры_изображений - функция вырезает небольшие кусочки из hr и lr изображений и выводит в масштабе на экран
  вход:
    lr, hr - списки с lr, hr изображениями соответственно
  '''
  n = 3 # Указываем кол-во отображаемых пар изображений
  fig, axs = plt.subplots(n, 2, figsize=(10, 15)) # Задаем размера вывода изображения

  for i in range(n): # В цикле попарно выводим изображения
    ind = random.randint(0, len(lr)) # Выбираем случайный индекс изображения

    area = (100, 100, 200, 200) # Задаем координаты точек для вырезания участка из изображения низкого качества
    cropped_lr = lr[ind].crop(area) # Вырезаем участок
    area = (400, 400, 800,800) # Задаем координаты точек для вырезания участка из изображения высокого качества
    cropped_hr = hr[ind].crop(area) # Вырезаем участок

    axs[i,0].axis('off')
    axs[i,0].imshow(cropped_lr) # Отображаем lr изображение
    axs[i,0].set_title('Низкое качество', fontsize=30)
    axs[i,1].axis('off')
    axs[i,1].imshow(cropped_hr) # Отображаем hr изображение
    axs[i,1].set_title('Высокое качество', fontsize=30)
  plt.show() #Показываем изображения

###
###                СОЗДАНИЕ ВЫБОРОК
###

def создать_выборки(путь, размер, коэф_разделения=0.9):  
  путь = '/content'+путь
  x_train = [] # Создаем пустой список, в который будем собирать примеры изображений обучающей выборки
  y_train = [] # Создаем пустой список, в который будем собирать правильные ответы (метки классов: 0 - Феррари, 1 - Мерседес, 2 - Рено)
  x_test = [] # Создаем пустой список, в который будем собирать примеры изображений тестовой выборки
  y_test = [] # Создаем пустой список, в который будем собирать правильные ответы (метки классов: 0 - Феррари, 1 - Мерседес, 2 - Рено)
  print('Создание наборов данных для обучения модели...')
  for j, d in enumerate(sorted(os.listdir(путь))):
    files = sorted(os.listdir(путь + '/'+d))    
    count = len(files) * коэф_разделения
    for i in range(len(files)):
      sample = image.load_img(путь + '/' +d +'/'+files[i], target_size=(размер[0], размер[1])) # Загружаем картинку
      img_numpy = np.array(sample) # Преобразуем зображение в numpy-массив
      if i<count:
        x_train.append(img_numpy) # Добавляем в список x_train сформированные данные
        y_train.append(j) # Добавлеям в список y_train значение 0-го класса
      else:
        x_test.append(img_numpy) # Добавляем в список x_test сформированные данные
        y_test.append(j) # Добавлеям в список y_test значение 0-го класса
  display.clear_output(wait=True)
  print('Созданы выборки: ')
  x_train = np.array(x_train) # Преобразуем к numpy-массиву
  y_train = np.array(y_train) # Преобразуем к numpy-массиву
  x_test = np.array(x_test) # Преобразуем к numpy-массиву
  y_test = np.array(y_test) # Преобразуем к numpy-массиву
  x_train = x_train/255.
  x_test = x_test/255.
  print('Размер сформированного массива обучающая_выборка:', x_train.shape)
  print('Размер сформированного массива метки_обучающей_выборки:', y_train.shape)
  print('Размер сформированного массива тестовая_выборка:', x_test.shape)
  print('Размер сформированного массива метки_тестовой_выборки:', y_test.shape)
  return (x_train, y_train), (x_test, y_test)

def предобработка_данных(**kwargs):
  if kwargs['net'] == 'полносвязная':
    x_train = kwargs['images']/255. # Нормируем изображения, приводя каждое значение пикселя к диапазону 0..1
    x_train = x_train.reshape((-1, 28*28)) # Изменяем размер изображения, разворачивая в один вектор
    print('Размер сформированных данных:', x_train[0].shape) # Выводим размер исходного изображения
    return x_train
  elif kwargs['net'] == 'сверточная':
    x_train = kwargs['images']/255. # Нормируем изображения, приводя каждое значение пикселя к диапазону 0..1
    x_train = x_train.reshape((-1, 28,28,1)) # Изменяем размер изображения, разворачивая в один вектор
    print('Размер сформированных данных:', x_train[0].shape) # Выводим размер исходного изображения
    return x_train

def обработка_изображений(**kwargs):
  return сегментация_en.get_images(**kwargs)

def распаковать_архив(откуда='', куда=''):
  proc = subprocess.Popen('unzip -q "' + откуда + '" -d ' + куда, shell=True, stdin=None, stdout=open(os.devnull,"wb"), stderr=STDOUT, executable="/bin/bash")
  proc.wait()

def показать_примеры_сегментации(**kwargs):
  сегментация_en.show_sample(**kwargs)

def загрузить_базу_ОДЕЖДА():
  (x_train_org, y_train_org), (x_test_org, y_test_org) = datasets.fashion_mnist.load_data() # Загружаем данные набора MNIST
  display.clear_output(wait=True)
  print('Данные загружены')
  print('Размер обучающей выборки:', x_train_org.shape) # Отобразим размер обучающей выборки
  print('Размер тестовой выборки:', x_test_org.shape) # Отобразим размер тестовой выборки
  return (x_train_org, y_train_org), (x_test_org, y_test_org)

def загрузить_базу_СТРОЙКА(**kwargs):
  global url
  if 'путь' in kwargs:
	  path = '/content/drive/MyDrive/' + kwargs['путь'] + 'AIU.zip'
  else:
	  path = '/content/drive/MyDrive/AIU.zip'
  print('Загрузка данных')
  print('Это может занять несколько минут...')
  распаковать_архив(
    откуда = '/content/drive/MyDrive/AIU.zip',
    куда = '/content'
  )
  распаковать_архив(
      откуда = "Notebooks.zip",
      куда = "/content"
  )
  x_train = np.load('xTrain_st.npy')
  x_test = np.load('xVal_st.npy')
  y_train = np.load('yTrain_st.npy')
  y_test = np.load('yVal_st.npy')  
  print('Загрузка данных (Готово)')
  return (x_train, y_train), (x_test, y_test)
  
  print('Загрузка данных...')
  urls = ['https://drive.google.com/uc?export=download&confirm=no_antivirus&id=1WtUbopKzQw97W8DChDu0JidJYh08XQyy',
            'https://drive.google.com/uc?export=download&confirm=no_antivirus&id=14gsGpYv13IMUKXmjQEPhPt2bVpVkcJfY',
            'https://drive.google.com/uc?export=download&confirm=no_antivirus&id=1A9IThR5f7dUIHgohDDJBeFyAZquTiYIL',
            'https://drive.google.com/uc?export=download&confirm=no_antivirus&id=1PtMhqaPXYoJKuKjLy338rBgv-PsScYPh',
            'https://drive.google.com/uc?export=download&confirm=no_antivirus&id=1qRAPeOgCZ0g9nikKmop4uWGEe9cCSm4B',
            'https://drive.google.com/uc?export=download&confirm=no_antivirus&id=1MDJiPs1Lyh-ij5dldjAu-kwWWb2uPNKi',
            'https://drive.google.com/uc?export=download&confirm=no_antivirus&id=1S7bc5yR2fHsR81aDZsIpBcCfxf-43Cek'
            '']
  for url in urls:    
    output = 'data.zip' # Указываем имя файла, в который сохраняем файл
    gdown.download(url, output, quiet=True) # Скачиваем файл по указанному URL
    if os.path.exists('data.zip'):
        break  
  # Скачиваем и распаковываем архив
  распаковать_архив(
      откуда = "data.zip",
      куда = "/content"
  )
  x_train = np.load('xTrain_st.npy')
  x_test = np.load('xVal_st.npy')
  y_train = np.load('yTrain_st.npy')
  y_test = np.load('yVal_st.npy')  
  print('Загрузка данных (Готово)')
  return (x_train, y_train), (x_test, y_test)