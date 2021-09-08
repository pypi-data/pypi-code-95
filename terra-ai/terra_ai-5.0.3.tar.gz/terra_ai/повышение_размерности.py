from . import датасет, модель
from os import listdir
from PIL import Image as PImage
import tensorflow as tf #Импортируем tensorflow
import matplotlib.pyplot as plt
from PIL import Image
import random
import importlib.util, sys, gdown
from IPython import display

import tensorflow as tf #Импортируем tensorflow
from tensorflow.python.data.experimental import AUTOTUNE #Импортируем AUTOTUNE для создания нескольких процессорных потоков при обучении 
from tensorflow.keras.applications.vgg19 import preprocess_input, VGG19 #Импортируем метод загрузки датасетов из директории во время обучения сети
#VGG19 - метод создания продвинутой модели нейронной сети для работы с полноразмерными изображениями 

from tensorflow.keras.losses import BinaryCrossentropy, MeanAbsoluteError, MeanSquaredError #Импортируем методы подсчета ошибок
from tensorflow.keras.metrics import Mean #Импортируем метрику
from tensorflow.keras.optimizers import Adam #Импортируем оптимайзеры
from tensorflow.keras.optimizers.schedules import PiecewiseConstantDecay
from tensorflow.python.keras.layers import Add, BatchNormalization, Conv2D, Dense, Flatten, Input, LeakyReLU, PReLU, Lambda, MaxPooling2D #Импортируем слои
from tensorflow.python.keras.models import Model, Sequential  #Импортируем метод создания модели

import os #Импортируем для работы с файловой системой
import matplotlib.pyplot as plt #Импортируем для вывода изображений
import numpy as np #Импортируем для работы с матрицами
from PIL import Image #Импортируем для загрузки изображений из директории
import time #Импортируем для подсчета времени 

def генератор_данных_DIV2K():
  curr_time = time.time()
  print('Загрузка и обработка данных')
  print('Это может занять несколько минут...') 
  print() 
  #Класс, созданный разработчиками архитектуры SRGAN
  #Нужен для создания выборки из директории с фотографиями прямо во время обучения 
  class DIV2K:
      def __init__(self,
                  subset='train', #Определяем выборку при создании 
                  images_dir='повышение_размерности/images', #Директория для хранения тестовой и обучающей выборки
                  caches_dir='повышение_размерности/caches'): #Директория для хранения кэша 

          self.scale =  4 #Масштаб уменьшения изображения по каждой оси  (суммарно изображение, подаваемое на вход меньше возвращаемого в 4 раза)
          self.downgrade = 'bicubic' #Определяем метод с которым уменьшаются изображения

          #Все фотографии в датасете пронумерованы по порядку. Поэтому имена для 
          #загрузки будут формироваться по порядку при помощи подствления к порядковому номеру 
          #формата изображения (.png). Ниже в зависимости от выборки определяем какие порядковые номера
          #изображений нам нужно брать, если на вход функции было подано train или valid.
          #Иначе выдаем ошибку
          if subset == 'train':
              self.image_ids = range(1, 801)
          elif subset == 'valid':
              self.image_ids = range(801, 901)
          else:
              raise ValueError("subset must be 'train' or 'valid'")

          self.subset = subset #Записываем тип выборки 
          self.images_dir = images_dir #Записываем путь для изображений
          self.caches_dir = caches_dir #Записываем путь для кэша изображений

          #Создаем папки для обучающей и тестовой выборки 
          os.makedirs(images_dir, exist_ok=True)
          os.makedirs(caches_dir, exist_ok=True)

      def __len__(self):
          return len(self.image_ids)

      #Функция для создания датасета. На вход получает:
      #batch_size - размер батча 
      #repeat_count - число повторений датасета 
      #random_transform - делаем ли трансофрмации изображения
      def dataset(self, batch_size=16, repeat_count=None, random_transform=True):
          #Формируем датасет, создавая струткуру [(изображение1 в плохом разрешении, изображение1 в хорошем разрешении), (изображение2 в плохом разрешении, изображение2 в хорошем разрешении)]
          ds = tf.data.Dataset.zip((self.lr_dataset(), self.hr_dataset()))
          if random_transform: #Если нужно делать трансформации
              ds = ds.map(lambda lr, hr: random_crop(lr, hr, scale=self.scale), num_parallel_calls=AUTOTUNE) #Делаем случайную обрезку изображений
              ds = ds.map(random_rotate, num_parallel_calls=AUTOTUNE) #Случайно поворачиваем изображения
              ds = ds.map(random_flip, num_parallel_calls=AUTOTUNE) #Случайно зеркалим изображения
          ds = ds.batch(batch_size) #Разбиваем на батчи
          ds = ds.repeat(repeat_count) #Делаем повторения, если требуется 
          #Делаем многопоточную загрузку данных 
          #Создаем набор данных. Большинство конвейеров ввода набора данных должны заканчиваться вызовом предварительной выборки. 
          #Это позволяет подготовить более поздние элементы, пока обрабатывается текущий элемент. 
          #Это часто уменьшает задержку и увеличивает пропускную способность за счет использования дополнительной памяти для хранения предварительно выбранных элементов.
          ds = ds.prefetch(buffer_size=AUTOTUNE)
          return ds #Возвращаем датасет

      #Функция для создания датасета из фотографий с высоким разрешением 
      def hr_dataset(self):
          
          if not os.path.exists(self._hr_images_dir()):#Если не в директории нет фотографий
              download_archive(self._hr_images_archive(), self.images_dir, extract=True) #Скачиваем их 

          ds = self._images_dataset(self._hr_image_files()).cache(self._hr_cache_file()) #Формируем датасет, создавая кэш фотографий 
          #Кэш нужен для ускорения загрузки данных 

          if not os.path.exists(self._hr_cache_index()): #Если не в директории нет кэша
              self._populate_cache(ds, self._hr_cache_file()) #Создаем кэш

          return ds #Возвращаем датасет

      #Функция для создания датасета из фотографий с низким разрешением 
      def lr_dataset(self):
          if not os.path.exists(self._lr_images_dir()): #Если не в директории нет фотографий
              download_archive(self._lr_images_archive(), self.images_dir, extract=True) #Скачиваем их 

          ds = self._images_dataset(self._lr_image_files()).cache(self._lr_cache_file()) #Формируем датасет, создавая кэш фотографий 
          #Кэш нужен для ускорения загрузки данных 

          if not os.path.exists(self._lr_cache_index()): #Если не в директории нет кэша 
              self._populate_cache(ds, self._lr_cache_file()) #Создаем кэш

          return ds

      def _hr_cache_file(self): #Формируем путь кэша изображений с высоким качеством
          return os.path.join(self.caches_dir, f'DIV2K_{self.subset}_HR.cache')

      def _lr_cache_file(self): #Формируем путь кэша изображений с низким качеством
          return os.path.join(self.caches_dir, f'DIV2K_{self.subset}_LR_{self.downgrade}_X{self.scale}.cache')

      def _hr_cache_index(self): #Формируем индексы кэша изображений с высоким качеством
          return f'{self._hr_cache_file()}.index'

      def _lr_cache_index(self): #Формируем индексы кэша изображений с низким качеством
          return f'{self._lr_cache_file()}.index'

      def _hr_image_files(self): #Функция для создания списка путей изображений с высоким качеством для датасета
          images_dir = self._hr_images_dir() #Задаем путь 

          #Возвращаем список изображений с высоким качеством для датасета
          return [os.path.join(images_dir, f'{image_id:04}.png') for image_id in self.image_ids] 

      def _lr_image_files(self): #Функция для создания списка путей изображений с низким качеством для датасета
          images_dir = self._lr_images_dir() #Задаем путь

          #Возвращаем список изображений с низким качеством для датасета
          return [os.path.join(images_dir, self._lr_image_file(image_id)) for image_id in self.image_ids]

      #Формируем имена для изображений по id
      def _lr_image_file(self, image_id):
              return f'{image_id:04}x{self.scale}.png'

      #Формируем путь к изображениям высокого качества
      def _hr_images_dir(self):
          return os.path.join(self.images_dir, f'DIV2K_{self.subset}_HR')

      def _lr_images_dir(self):
          return os.path.join(self.images_dir, f'DIV2K_{self.subset}_LR_{self.downgrade}', f'X{self.scale}')

      #Формируем путь архиву с изображениями высокого качества
      def _hr_images_archive(self):
          return f'DIV2K_{self.subset}_HR.zip'

      #Формируем путь к архиву с изображениями низкого качества
      def _lr_images_archive(self):
          return f'DIV2K_{self.subset}_LR_{self.downgrade}_X{self.scale}.zip'

      #Функция для формирования датасета
      @staticmethod
      def _images_dataset(image_files): #Передаем пути изображений
          ds = tf.data.Dataset.from_tensor_slices(image_files) #Преобразуем в датасет
          ds = ds.map(tf.io.read_file) #По каждому пути читаем изображение и вносим в датасет 
          ds = ds.map(lambda x: tf.image.decode_png(x, channels=3), num_parallel_calls=AUTOTUNE) #Преобразуем четырехканальные изображения в трехканальные 
          return ds #Возвращаем датасет 

      #Функция для вывода информации о формировании кэша
      @staticmethod
      def _populate_cache(ds, cache_file):
          pass
          #print(f'Caching decoded images in {cache_file} ...')
          #for _ in ds: pass
          #print(f'Cached decoded images in {cache_file}.')


  #Функция для случайной вырезки фразментов из изображений с низким качеством и высоким качеством 
  #Принимает на вход параметры:
  #lr_img - изображение с низким качеством
  #hr_img - изображение с высоким качеством 
  #hr_crop_size - размер обрезанного изображения с выоским качеством
  #scale - масштаб во сколько раз по каждой из осей изображение с низким качеством меньше изображения с выоским качеством
  def random_crop(lr_img, hr_img, hr_crop_size=96, scale=2):
      lr_crop_size = hr_crop_size // scale #Считаем размер обрезанного изображения с низким качеством
      lr_img_shape = tf.shape(lr_img)[:2] #Тензорная размерность уменьшенного изображения

      #Задаем случайные координаты для фрагментов, которые будем вырезать из фотографии
      lr_w = tf.random.uniform(shape=(), maxval=lr_img_shape[1] - lr_crop_size + 1, dtype=tf.int32)
      lr_h = tf.random.uniform(shape=(), maxval=lr_img_shape[0] - lr_crop_size + 1, dtype=tf.int32)

      #Умножаем координаты на масштаб, чтобы на фотографиях с большим и маленьким разрешением вырезать соответствующие фрагменты 
      hr_w = lr_w * scale
      hr_h = lr_h * scale

      #Вырезаем фрагменты
      lr_img_cropped = lr_img[lr_h:lr_h + lr_crop_size, lr_w:lr_w + lr_crop_size]
      hr_img_cropped = hr_img[hr_h:hr_h + hr_crop_size, hr_w:hr_w + hr_crop_size]

      return lr_img_cropped, hr_img_cropped # Возвращаем фрагменты 


  #Функция для отзеркаливания изображений
  def random_flip(lr_img, hr_img):
      #Случайно определяем стоит ли зеркалить изображения или нет 
      rn = tf.random.uniform(shape=(), maxval=1)
      #Возвращаем изображения 
      return tf.cond(rn < 0.5,
                    lambda: (lr_img, hr_img),
                    lambda: (tf.image.flip_left_right(lr_img),
                              tf.image.flip_left_right(hr_img)))

  #Функция для поворота изображений
  def random_rotate(lr_img, hr_img):
      #Случайно определяем стоит ли поворачивать изображения или нет 
      rn = tf.random.uniform(shape=(), maxval=4, dtype=tf.int32)
      #Возвращаем изображения 
      return tf.image.rot90(lr_img, rn), tf.image.rot90(hr_img, rn)

  #Функция для скачивания архива
  def download_archive(file, target_dir, extract=True):
      source_url = f'http://data.vision.ee.ethz.ch/cvl/DIV2K/{file}'
      target_dir = os.path.abspath(target_dir)
      tf.keras.utils.get_file(file, source_url, cache_subdir=target_dir, extract=extract)
      os.remove(os.path.join(target_dir, file))

  div2k_train = DIV2K(subset='train') #Инициализируем тренировочный датасет 
  div2k_valid = DIV2K(subset='valid') #Инициализируем тестовый датасет 
  train_ds = div2k_train.dataset(batch_size=16, random_transform=True) #Инициализируем тренировочный датасет 
  valid_ds = div2k_valid.dataset(batch_size=16, random_transform=True, repeat_count=1) #Инициализируем тестовый датасет 
  display.clear_output(wait=True)
  print('Загрузка данных завершена! Длительность загрузки:', round(time.time() - curr_time, 2), 'секунд')  
  return train_ds, valid_ds


# Универсальный класс, нужный для тренировки моделей
class Trainer:
    def __init__(self,
                 model,                           #модель
                 loss,                            #Ошибка 
                 learning_rate,                   #Скорость обучения 
                 checkpoint_dir='./ckpt/edsr'):   #Директория для сохранения контрольных точек

        self.now = None #Текущее время 
        self.loss = loss #Ошибка 

        #Метод сохранения контрольной точки  
        self.checkpoint = tf.train.Checkpoint(step=tf.Variable(0), 
                                              psnr=tf.Variable(-1.0),
                                              optimizer=Adam(learning_rate),
                                              model=model)
        #Метод конфигурации сохранения контрольной точки  
        #self.checkpoint_manager = tf.train.CheckpointManager(checkpoint=self.checkpoint,
               #                                              directory=checkpoint_dir,
              #                                               max_to_keep=3)
        
        #self.restore() #Восстанавливаем, если есть сохраненная контрольная точка 

    #Функция для создания модели из контрольной точки
    @property
    def model(self):
        return self.checkpoint.model

    #Функция для тренировки сети 
    #На вход подаем:
    #train_dataset - обучающий датасет 
    #valid_dataset - тестовый датасет
    #steps - число шагов обучения 
    #evaluate_every - с какой частотой сохранять контрольную точку
    #save_best_only - будем ли сохранять только наилучший результат 

    def train(self, train_dataset, valid_dataset, steps, evaluate_every=1000, save_best_only=False):
        loss_mean = Mean() #Создаем экземпляр для посчета средней ошибки 

        #ckpt_mgr = self.checkpoint_manager #Создаем конфигурацию сохранения контрольной точки
        ckpt = self.checkpoint #Создаем контрольную точку 

        self.now = time.perf_counter() #Засекаем время
      
        for lr, hr in train_dataset.take(steps - ckpt.step.numpy()): #Перебираем изображения
            ckpt.step.assign_add(1) #Делаем контрольную точку
            step = ckpt.step.numpy() #Считаем шаг
            loss = self.train_step(lr, hr)#Обучаем пошагово 
            loss_mean(loss)#Считаем ошибку
            #Если число шагов обучения кратно параметру evaluate_every - производим подсчеты и выводим информацию
            if step % evaluate_every == 0:
                #Считаем среднюю ошибку
                loss_value = loss_mean.result()
                loss_mean.reset_states()

                # Считаем PSNR на тестовой выборке
                psnr_value = self.evaluate(valid_dataset)

                duration = time.perf_counter() - self.now #Считаем длительность обучения
                print(f'{step}/{steps}: ошибка = {loss_value.numpy():.3f}, точность = {psnr_value.numpy():3f} ({duration:.2f}s)') #Выводим информацию

                #Если выбран параметр для сохранения только лучших весов и psnr_value меньше, чем значение в контрольной точке
                if save_best_only and psnr_value <= ckpt.psnr: 
                    self.now = time.perf_counter() #Пропускаем сохранение контрольной точки так как PSNR не улучшился
                    continue
                
                #Иначе сохраняем контрольную точку 
                ckpt.psnr = psnr_value
                #ckpt_mgr.save()

                #Перезадаем текущее время 
                self.now = time.perf_counter()       

    @tf.function
    def train_step(self, lr, hr):

        with tf.GradientTape() as tape: #Используя градиентный спуск 
            
            #Переводим входные тензоры в новый тип данных
            lr = tf.cast(lr, tf.float32) 
            hr = tf.cast(hr, tf.float32)

            #Считаем ошибку
            sr = self.checkpoint.model(lr, training=True)
            loss_value = self.loss(hr, sr)

        #Применяем градиенты 
        gradients = tape.gradient(loss_value, self.checkpoint.model.trainable_variables)
        self.checkpoint.optimizer.apply_gradients(zip(gradients, self.checkpoint.model.trainable_variables))

        return loss_value

    #Считаем результаты
    def evaluate(self, dataset):
        return evaluate(self.checkpoint.model, dataset)

    #Восстанавливаем модель из контрольной точки 
    def restore(self):
        if self.checkpoint_manager.latest_checkpoint:
            self.checkpoint.restore(self.checkpoint_manager.latest_checkpoint)
            print(f'Model restored from checkpoint at step {self.checkpoint.step.numpy()}.')
#Функция для преобразования картинки lr в sr
def resolve(model, lr_batch):
    lr_batch = tf.cast(lr_batch, tf.float32)
    sr_batch = model(lr_batch)
    sr_batch = tf.clip_by_value(sr_batch, 0, 255)
    sr_batch = tf.round(sr_batch)
    sr_batch = tf.cast(sr_batch, tf.uint8)
    return sr_batch
#Функция для подсчета psnr - значения
def evaluate(model, dataset):
    psnr_values = []
    for lr, hr in dataset:
        sr = resolve(model, lr)
        psnr_value = psnr(hr, sr)[0]
        psnr_values.append(psnr_value)
    return tf.reduce_mean(psnr_values)
#Метрика
def psnr(x1, x2):
    return tf.image.psnr(x1, x2, max_val=255)
#Создаем новый класс, который наследует признаки класса Trainer
class SrganGeneratorTrainer(Trainer):
    def __init__(self,
                 model,
                 checkpoint_dir,
                 learning_rate=1e-4):
        #Назначаем свои признаки класса
        super().__init__(model, loss=MeanSquaredError(), learning_rate=learning_rate, checkpoint_dir=checkpoint_dir)
    #Выставляем параметры обучения
    def train(self, train_dataset, valid_dataset, steps=1000000, evaluate_every=1000, save_best_only=True):
        super().train(train_dataset, valid_dataset, steps, evaluate_every, save_best_only)

#Создаем новый класс, который который будет обучать модель 
#Нужен для подсчета ошибок, создания и сохранения контрольных точек 
class SrganTrainer:

    def __init__(self,
                 generator, #Указываем генератор
                 discriminator, #Указываем дискриминатор
                 content_loss='VGG54', #Указываем какую предобученную сеть для подсчета content loss будем использовать 
                 learning_rate=PiecewiseConstantDecay(boundaries=[100000], values=[1e-4, 1e-5])):
        #Назначаем методы подсчета ошибок, генератор, дискриминатор, оптимайзеры и скорости обучения 
        self.vgg = vgg_54()
        self.content_loss = content_loss
        self.generator = generator
        self.discriminator = discriminator
        self.generator_optimizer = Adam(learning_rate=learning_rate)
        self.discriminator_optimizer = Adam(learning_rate=learning_rate)

        self.binary_cross_entropy = BinaryCrossentropy(from_logits=False)
        self.mean_squared_error = MeanSquaredError()

    #Метод обучения сети 
    def train(self, train_dataset, steps=200000):
        #Добавляем метрику для:
        pls_metric = Mean() #Ошибки восприятия
        dls_metric = Mean() #Ошибки дискриминатора 
        #Указываем начальный шаг 
        step = 0

        #Проходим по каждому значению в выборке
        for lr, hr in train_dataset.take(steps):
            step += 1

            #Обучаем train_step, получаем ошибки
            pl, dl = self.train_step(lr, hr)
            pls_metric(pl)
            dls_metric(dl)

            #Каждые 50 шагов
            if step % 50 == 0:
                print(f'{step}/{steps}, Ошибка генератора = {pls_metric.result():.4f}, Ошибка дискриминатора = {dls_metric.result():.4f}') #Выводим текущую информацию
                #Сбрасываем значения для дальнейших рассчетов 
                pls_metric.reset_states() 
                dls_metric.reset_states()

    #Метод пошагового обучения сети, подсчета ошибок, применения градиентного спуска 
    @tf.function
    def train_step(self, lr, hr):
        with tf.GradientTape() as gen_tape, tf.GradientTape() as disc_tape:
            #Переводим входные тензоры в один формат данных 
            lr = tf.cast(lr, tf.float32)
            hr = tf.cast(hr, tf.float32)

            #Получаем Super Resolution - Image
            sr = self.generator(lr, training=True)

            #Отправляем в дискриминатор настоящее изображение, а затем то, что выдал дискриминатор
            hr_output = self.discriminator(hr, training=True)
            sr_output = self.discriminator(sr, training=True)

            con_loss = self._content_loss(hr, sr) #Считаем ошибку _content_loss для изображений
            gen_loss = self._generator_loss(sr_output) #Считаем вероятность того, что сгенерированное изображение похоже на реальное изображение
            
            perc_loss = con_loss + 0.001 * gen_loss #Считаем общую ошибку
            disc_loss = self._discriminator_loss(hr_output, sr_output) #Считаем ошибку дискриминатора

        #Считаем градиенты к генератору и дискриминатору
        gradients_of_generator = gen_tape.gradient(perc_loss, self.generator.trainable_variables)
        gradients_of_discriminator = disc_tape.gradient(disc_loss, self.discriminator.trainable_variables)

        #Применяем градиенты к генератору и дискриминатору
        self.generator_optimizer.apply_gradients(zip(gradients_of_generator, self.generator.trainable_variables))
        self.discriminator_optimizer.apply_gradients(zip(gradients_of_discriminator, self.discriminator.trainable_variables))

        return perc_loss, disc_loss

    #Метод подсчета ошибки _content_loss
    @tf.function
    def _content_loss(self, hr, sr):
        sr = preprocess_input(sr)
        hr = preprocess_input(hr)
        sr_features = self.vgg(sr) / 12.75
        hr_features = self.vgg(hr) / 12.75
        return self.mean_squared_error(hr_features, sr_features)

    #Метод подсчета ошибки _generator_loss
    def _generator_loss(self, sr_out):
        return self.binary_cross_entropy(tf.ones_like(sr_out), sr_out)

    #Метод подсчета ошибки _discriminator_loss
    def _discriminator_loss(self, hr_out, sr_out):
        hr_loss = self.binary_cross_entropy(tf.ones_like(hr_out), hr_out)
        sr_loss = self.binary_cross_entropy(tf.zeros_like(sr_out), sr_out)
        return hr_loss + sr_loss

def _vgg(output_layer):
    vgg = VGG19(input_shape=(None, None, 3), include_top=False)
    display.clear_output(wait=True)
    return Model(vgg.input, vgg.layers[output_layer].output)

def vgg_54():
    return _vgg(20)


def создать_модель(генератор, дискриминатор):
  return SrganTrainer(генератор.model, дискриминатор)

def предобучение_генератора(генератор, обучающая_выборка, проверочная_выборка, количество_шагов, интервал_вывода):
  генератор.train(обучающая_выборка,
                  проверочная_выборка.take(10),
                  steps=количество_шагов, 
                  evaluate_every=интервал_вывода, 
                  save_best_only=False)

def загрузить_веса_готовой_модели():
  # Location of model weights (needed for demo)

  
  url = 'https://storage.googleapis.com/aiu_bucket/gan_generator.h5'
  output = 'gan_generator.h5' # Указываем имя файла, в который сохраняем файл
  gdown.download(url, output, quiet=True) # Скачиваем файл по указанному URL
  
  gan_generator = модель.создать_модель_HighResolution()()

  gan_generator.load_weights('gan_generator.h5')
  return gan_generator


