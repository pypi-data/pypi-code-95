import subprocess
import os
import gdown
from IPython import display
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from time import time
from sklearn.preprocessing import MinMaxScaler
from keras.preprocessing.sequence import TimeseriesGenerator
import numpy as np

def показать_примеры(база, старт, финиш):
  #Загружаем датафрейм с сессионного хранилища
 
  plt.figure(figsize=(12, 6)) # Создаем полотно для визуализации
  #Переводим тип данных со столбика с ценами из текста (string) на числа с плавающей запятой (float)
  plt.plot(база['Трафик'][старт:финиш], label = 'Трафик')
  plt.legend()
  plt.show()

def создать_выборки_трафик(база, xLen):
  batch_size=20
  curTime = time()
  #Загружаем данные в переменную dataframe
  data = база.iloc[:,1]
  data = np.array(data) #Превращаем в numpy массив
  for i in range(len(data)):
    data[i] = float(data[i])
  
  #Разделяем на проверочную/обучаюшую выборки с соотношением 20%/80%
  #Формируем параметры загрузки данных
  valLen = 300  # Используем 300 записей для проверки

  trainLen = data.shape[0]-valLen # Размер тренировочной выборки

  # Делим данные на тренировочную и тестовую выборки 
  Train,Test = np.reshape(data[:trainLen],(-1,1)), np.reshape(data[trainLen+xLen+2:],(-1,1))

  # Масштабируем данные (отдельно для X и Y), чтобы их легче было скормить сетке
  Scaler = MinMaxScaler()
  Scaler.fit(Train)
  Train = Scaler.transform(Train)
  Test = Scaler.transform(Test)


  # Создаем генератор для обучения
  trainDataGen = TimeseriesGenerator(Train, Train,             # в качестве параметров наши выборки
                                length=xLen, sampling_rate=1, # для каждой точки
                                batch_size=20)                # размер batch, который будем скармливать модели

  # Создаем аналогичный генератор для валидации при обучении
  testDataGen = TimeseriesGenerator(Test, Test,
                                length=xLen, sampling_rate=1,
                                batch_size=20)

  # Создадим генератор проверочной выборки, из которой потом вытащим xVal, yVal для проверки
  DataGen = TimeseriesGenerator(Test, Test,
                                length=xLen, sampling_rate=1,
                                batch_size=len(Test)) # Размер batch будет равен длине нашей выборки

  xVal = []
  yVal = []
  for i in DataGen:
    xVal.append(i[0])
    yVal.append(i[1])

  xVal = np.array(xVal)
  yVal = np.array(yVal)
  print('Выборки созданы успешно')
  return trainDataGen, testDataGen, (xVal, yVal, Scaler)

def тест_модели_трафика(нейронка, наборы):

  def getPred(currModel, xVal, yVal, yScaler):
    # Предсказываем ответ сети по проверочной выборке
    # И возвращаем исходны масштаб данных, до нормализации
    predVal = yScaler.inverse_transform(currModel.predict(xVal))
    yValUnscaled = yScaler.inverse_transform(yVal)
    
    return (predVal, yValUnscaled)
  
  # channel - какой канал отрисовываем
  def showPredict1(start, step, channel, predVal, yValUnscaled):
    plt.figure(figsize=(14,7))
    plt.plot(predVal[start:start+step, channel], 
            label='Прогноз')
    plt.plot(yValUnscaled[start:start+step, channel], 
            label='Базовый ряд')
    plt.xlabel('Время')
    plt.ylabel('Значение Close')
    plt.legend()
    plt.show()

  (predVal, yValUnscaled) = getPred(нейронка, наборы[0][0], наборы[1][0], наборы[2]) #Прогнозируем данные

  # Отображаем графики
  showPredict1(0, 400, 0, predVal, yValUnscaled)