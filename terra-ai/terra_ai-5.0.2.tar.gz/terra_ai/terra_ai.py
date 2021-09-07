print('Идет проверка и установка дополнительных библиотек, необходимых для работы terra_ai')
print('Это может занять несколько минут...')
import subprocess, os, warnings, time
from pandas.core.common import SettingWithCopyWarning
from subprocess import STDOUT, check_call
from IPython import display
import numpy as np
import requests
import librosa #Для параметризации аудио
import ast
import json
from tabulate import tabulate
import getpass
def выполнить_команду(команда='!ls'):
  proc = subprocess.Popen(f'{команда}', shell=True, stdin=None, stdout=open(os.devnull,"wb"), stderr=STDOUT, executable="/bin/bash")
  proc.wait()
  pass
import os
import time
import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3' 
import tensorflow as tf
tf.get_logger().setLevel("WARNING")
import logging
logging.getLogger("tensorflow").setLevel(logging.WARNING)
#tf.get_logger().setLevel(logging.ERROR)

выполнить_команду('pip -q install pymorphy2') 
выполнить_команду('pip -q install scikit-learn') 
import sklearn
from sklearn.model_selection import train_test_split #Разбиение на обучающую и проверочную выборку
from sklearn.preprocessing import LabelEncoder, StandardScaler #Для нормировки данных

from . import датасет, констр, модель, сегментация, traide, ряды, прачечная, обработка_текста, сегментация_договоров, квартиры, home, датасет_en, модель_en, сегментация_en, traide_en, обработка_текста_en, квартиры_en, home_en


import seaborn as sns
sns.set_style('darkgrid')
warnings.simplefilter(action="ignore", category=SettingWithCopyWarning)

display.clear_output(wait=True)
print('Все необходимые библиотеки установлены и готовы к работе')
  
def load_dataset(dataset_name = '', description = False):
  return датасет.загрузить_базу(
    база = dataset_name,
    справка = description
)
#Демонстрация
def load_ga_moduls():
  print('Выполняется загрузка и установка модулей')
  print('Это может занять несколько минут...')
  выполнить_команду('apt install swig cmake libopenmpi-dev zlib1g-dev > /dev/null 2>&1')
  выполнить_команду('pip -q install stable-baselines==2.5.1 box2d box2d-kengz > /dev/nul 2>&1')
  выполнить_команду('pip -q install gym pyvirtualdisplay > /dev/null 2>&1')
  выполнить_команду('pip -q install xvfbwrapper > /dev/null 2>&1')
  выполнить_команду('apt-get update > /dev/null 2>&1')
  выполнить_команду('sudo apt-get install xvfb > /dev/null 2>&1')
  выполнить_команду('apt-get install xdpyinfo > /dev/null 2>&1')
  display.clear_output(wait=True)
  from . import генетика
  print('Все модули установлены и готовы к работе')

def create_display(width, hight):
  from . import генетика
  ширина = width
  высота = hight
  генетика.создать_дисплей(ширина, высота)

def ga_example(task):
  from . import генетика
  задача = task
  генетика.показать_пример(задача)

def fit_ga(population_size, epochs, mutation_rate, survivors):
  from . import генетика
  размер_популяции = population_size
  количество_эпох = epochs
  коэфицент_мутации = mutation_rate
  количество_выживших = survivors
  генетика.обучить_алгоритм(размер_популяции, количество_эпох, коэфицент_мутации, количество_выживших)

def landing_ship():
  from . import генетика
  генетика.посадить_корабль()
  
def конструктор():
  return констр.конструктор()

def mnist_demo():
  return модель_en.демонстрация_МНИСТ()

def show_mask_mnist(number):
  return модель_en.показать_изменение_маски_MNIST(number)

def show_chenging_weights():
  return модель_en.показать_изменение_веса()

def auto_demo():
  return модель_en.демонстрация_АВТО()

def show_mask_auto(num):
  return модель_en.показать_изменение_маски_АВТО(num)

def show_masks():
  import logging
  tf.get_logger().setLevel(logging.ERROR)
  return модель_en.показать_маски()

#LabStory
# Авторизация
def авторизация_LabStory():
  return модель.авторизация_LabStory()  
  
# Добавление набора данных
def добавить_датасет_LabStory(dataset_dict):
  return модель.добавить_датасет_LabStory(dataset_dict)
  
# Получение списка набора данных
def список_датасетов_LabStory():
  return модель.список_датасетов_LabStory()

# Удаление набора данных
def удалить_датасет_LabStory(id):
  return модель.удалить_датасет_LabStory(id)

#Выбор датасета по id
def выбрать_датасет_LabStory(id):
  return модель.выбрать_датасет_LabStory(id)

# Вывод информации о текущем датасете
def текущий_датасет():
  return модель.текущий_датасет()

# Создание задачи    
def добавить_задачу_LabStory(task_dict):
  return модель.добавить_задачу_LabStory(task_dict)

# Получение списка задач 
def список_задач_LabStory():
  return модель.список_задач_LabStory()

# Выбор задачи по id    
def выбрать_задачу_LabStory(id):
  return модель.выбрать_задачу_LabStory(id)

def текущая_задача():
  return модель.текущая_задача()

# Сохранение эксперимента
def сохранить_эксперимент_LabStory(experiment_dict):
  return модель.сохранить_эксперимент_LabStory(experiment_dict)
  
def сохранить_эксперимент_LabStory_terra_ai(experiment_dict):
  return модель.сохранить_эксперимент_LabStory_terra_ai(experiment_dict)

# Получение списка экспериметов
def список_экспериметов_LabStory():
  return модель.список_экспериметов_LabStory()

# Получение эксперимета по id  
def посмотреть_эксперимент_по_id_LabStory(id):
  return модель.посмотреть_эксперимент_по_id_LabStory(id)
  
def все_эксперименты_по_задаче(id):
    return модель.все_эксперименты_по_задаче(id)

def получить_архитектуру(id_exp):
    return модель.получить_архитектуру(id_exp)
    
## Прачечная
def input_data():
  прачечная.ввод_данных()
def make_day_plan(общее_число_ботов, количество_выживших, количество_эпох, коэффициент_мутаций):
  прачечная.рассчитать_план_на_день(общее_число_ботов, количество_выживших, количество_эпох, коэффициент_мутаций)
def show_plan_ga():
  прачечная.план_на_день()
def bags_info(n=None):
  прачечная.информация_о_мешке(n)
  
### ДАТАСЕТ
def examples(**kwargs):
  датасет_en.показать_примеры(**kwargs)

def contract_examples(количество = 1):
    сегментация_договоров.показать_пример(количество)

def time_series_examples(база, старт, финиш):
    return ряды.показать_примеры(база, старт, финиш)

def flat_examples(quantity = 1):
    количество = quantity
    квартиры_en.samples(количество)

def smart_home_examples():
    home_en.показать_примеры_голосовых_команд()

def traide_examples(данные):
    traide_en.show_full_data(данные)

def traide_example_intervals(данные, start, end):
    traide_en.show_data(данные, start, end)

def preprocessing_data(**kwargs):
  return датасет_en.предобработка_данных(**kwargs)

def get_input_size(arr):
  return arr.shape[1:]

def get_output_size(arr):
  return arr.max()+1

def create_array(path, size, коэф_разделения=0.9):
  путь = path
  размер = size
  return датасет_en.создать_выборки(путь, размер, коэф_разделения)

def create_txt_array(MWC, xLen, step, путь_к_базе='content/Болезни/'):
  return обработка_текста.создать_выборки(MWC, xLen, step, путь_к_базе)

def create_flat_array():
  return квартиры_en.создать_выборки()

def create_traide_array(shares,analyzed_days,period):
  акции = shares
  количество_анализируемых_дней = analyzed_days
  период_предсказания = period
  return traide_en.получить_данные(акции,
  количество_анализируемых_дней,
  период_предсказания)

def create_smart_home_array(длина, шаг):
  return home_en.создать_выборки(длина, шаг)

def create_time_series_array(база, период):
  return ряды.создать_выборки_трафик(база, период)

def create_txt_segmentation_array(договоры):
  return сегментация_договоров.создать_выборки_договоров(договоры)
  
def create_chat_bot_array(вопросы, ответы,количество_пар=10000):
  return обработка_текста.создать_выборки_чатбота(вопросы, ответы,количество_пар)
  
def create_segmentation_array(images_airplane, segments_airplane):
   return сегментация_en.create_xy(images_airplane, segments_airplane)

def create_high_resolution_array():
  return повышение_размерности.генератор_данных_DIV2K()

# МОДЕЛЬ
def show_plan(мод):
  return модель_en.схема_модели(мод)

def fit_flat_model(мод, x_train, y_train, x_test=[], y_test=[], batch_size=None, epochs=None, коэф_разделения = 0.2, scaler = None):
  размер_пакета = batch_size
  количество_эпох = epochs
  инструменты = scaler
  return модель_en.обучение_модели_квартиры(мод, x_train, y_train, x_test, y_test, размер_пакета, количество_эпох, коэф_разделения, инструменты)

def fit_model(мод, x_train, y_train, x_test=[], y_test=[], batch_size=None, epochs=None, коэф_разделения = 0.2):
  global history
  размер_пакета = batch_size
  количество_эпох = epochs
  return модель_en.обучение_модели(мод, x_train, y_train, x_test, y_test, размер_пакета, количество_эпох, коэф_разделения)

def fit_time_series_model(мод, ген1, ген2, количество_эпох=None):
  модель_en.обучение_модели_трафик(мод, ген1, ген2, количество_эпох)
  return history

def fit_generator(генератор, обучающая_выборка, проверочная_выборка, количество_шагов, интервал_вывода):
  повышение_размерности.предобучение_генератора(генератор,обучающая_выборка, проверочная_выборка, количество_шагов, интервал_вывода)
  print('Предобучение генератора завершено')
  
def fit_high_resolution_model(нейронка,обучающая_выборка):
  нейронка.train(обучающая_выборка, steps=5000) #Обучаем Srgan полностью

def fit_detection_model(количество_эпох):
  обнаружение.обучение_модели_обнаружения(количество_эпох)

def test_classification(net, test_images, labels, classes, quantity=1):
  нейронка = net
  тестовый_набор = test_images
  правильные_ответы = labels
  классы = classes
  количество = quantity
  return модель_en.тест_модели_классификации(нейронка, тестовый_набор, правильные_ответы, классы, количество)

def test_symptoms(нейронка, xLen, step, симптомы, classes):
    классы = classes
    обработка_текста_en.тест_модели_симп(нейронка, xLen, step, симптомы, классы)

def test_writers(нейронка, xLen, step, текст, классы):
    обработка_текста_en.тест_модели_писатели(нейронка, xLen, step, текст, классы)
    
def test_own_image(net, size, classes):
  нейронка = net
  размер_изображения = size
  классы = classes
  return модель_en.тест_на_своем_изображении(нейронка, размер_изображения, классы)

def test_segmentation(мод, test_images,  **kwargs):
  тестовые_изображения = test_images
  сегментация_en.тест_модели(мод, тестовые_изображения,  **kwargs)

def test_segmentation_contract(мод, теги, договора):
  сегментация_договоров.тест_модели(мод, теги, договора)

def test_traide(нейронка,тестовая_выборка, метки_тестовой_выборки, данные, период_предсказания,количество_анализируемых_дней):
  traide_en.model_test(
    нейронка, 
    тестовая_выборка, метки_тестовой_выборки,
    данные,
    период_предсказания,
    количество_анализируемых_дней)

def recognizing_examples(нейронка_1, период_предсказания,количество_анализируемых_дней):
    traide_en.example_traid(нейронка_1, период_предсказания,количество_анализируемых_дней)

def test_high_resolution(нейронка):
  модель_en.тест_модели_HR(нейронка)

def trading(нейронка_1, тестовая_выборка, данные, type_traide):
  тип = type_traide
  traide_en.traiding(нейронка_1, тестовая_выборка, данные, тип)

def test_chat_bot(нейронка, размер_словаря, энкодер, декодер):
  обработка_текста_en.тест_модели_чат_бот(нейронка, размер_словаря, энкодер, декодер)
  
def test_trained_chat_bot():
  обработка_текста_en.загрузить_предобученную_модель()
  
def test_smart_home(нейронка, limit, length, step):
  порог = limit
  длина = length
  шаг = step
  home_en.тест_модели(нейронка, порог, длина, шаг)

def test_detection(нейронка):
  обнаружение.тест_модели()

def test_time_series(мод, данные):
  ряды.тест_модели_трафика(мод, данные)

def test_flat(нейронка, инструменты, *данные,):
  квартиры_en.тест_модели(нейронка, инструменты, *данные,)

def create_network(layer, input_size, task, параметры_модели=None):
  слои = layer
  входной_размер = input_size
  задача = task
  return модель_en.создать_сеть(слои, входной_размер, параметры_модели, задача)

def create_composite_network(данные, метки, *нейронки):
  return модель_en.создать_составную_сеть(данные, метки, *нейронки)

def create_flat_composite_network(данные, *нейронки):
  return модель_en.создать_составную_сеть_квартиры(данные, *нейронки)

def create_Sequence_to_Sequence(размер_словаря, энкодер, декодер):
  return модель_en.создать_сеть_чат_бот(размер_словаря, энкодер, декодер)

def create_generator(стартовый_блок, основной_блок, финальный_блок):
  мод = модель.создать_генератор_повышения_размерности(стартовый_блок, основной_блок, финальный_блок)
  предобучение_генератора = повышение_размерности.SrganGeneratorTrainer(мод, checkpoint_dir=f'folder')    
  print('Модель генератора создана')    
  return предобучение_генератора

def create_discriminator(блок_дискриминатора,количество_блоков, финальный_блок):
  return модель_en.создать_дискриминатор_повышения_размерности(блок_дискриминатора,количество_блоков, финальный_блок)

def create_PSP(**kwargs):
  return модель_en.создать_PSP(**kwargs)

def create_UNET(**kwargs):
  return модель_en.создать_UNET(**kwargs)

def create_high_resolution(генератор, дискриминатор):
  return повышение_размерности.создать_модель(генератор, дискриминатор)

def load_high_resolution():
  return повышение_размерности.загрузить_веса_готовой_модели()

def load_object_detection_model():
  return обнаружение.cоздать_модель_YOLO()  

def audio_parameterization(comand):
  файл = comand
  home_en.параметризация_аудио(файл)