#Библиотеки
import random as random # Импортируем библиотку генерации случайных значений
import numpy as np # Импортируем библиотеку numpy
import matplotlib.pyplot as plt # Импортируем модуль pyplot библиотеки matplotlib
import matplotlib.colors as colors # Импортируем модуль colors библиотеки matplotlib
import pandas as pd
import random
from tabulate import tabulate
import seaborn as sns
from IPython.display import display, HTML
sns.set_style('darkgrid')


'''
    Функция получения выжившей популяции
        Входные параметры:
        - popul - наша популяция
        - val - текущие значения
        - nsurv - количество выживших
        - reverse - указываем требуемую операцию поиска результата: максимизация или минимизация
'''
def getSurvPopul(
        popul,
        val,
        nsurv,
        reverse
        ):
    newpopul = [] # Двумерный массив для новой популяции
    sval = sorted(val, reverse=reverse) # Сортируем зачения в val в зависимости от параметра reverse    
    for i in range(nsurv): # Проходимся по циклу nsurv-раз (в итоге в newpopul запишется nsurv-лучших показателей)
        index = val.index(sval[i]) # Получаем индекс i-того элемента sval в исходном массиве val
        newpopul.append(popul[index]) # В новую папуляцию добавляем элемент из текущей популяции с найденным индексом
    return newpopul, sval # Возвращаем новую популяцию (из nsurv элементов) и сортированный список

'''
    Функция получения родителей
        Входные параметры:
        - curr_popul - текущая популяция
        - nsurv - количество выживших
'''
def getParents(
        curr_popul,
        nsurv
        ):   
    indexp1 = random.randint(0, nsurv - 1) # Случайный индекс первого родителя в диапазоне от 0 до nsurv - 1
    indexp2 = random.randint(0, nsurv - 1) # Случайный индекс второго родителя в диапазоне от 0 до nsurv - 1    
    botp1 = curr_popul[indexp1] # Получаем первого бота-родителя по indexp1
    botp2 = curr_popul[indexp2] # Получаем второго бота-родителя по indexp2    
    return botp1, botp2 # Возвращаем обоих полученных ботов

'''
    Функция смешивания (кроссинговера) двух родителей
        Входные параметры:
        - botp1 - первый бот-родитель
        - botp2 - второй бот-родитель
        - j - номер компонента бота
'''
def crossPointFrom2Parents(
        botp1,
        botp2, 
        j
        ):
    pindex = random.random() # Получаем случайное число в диапазоне от 0 до 1
    
    # Если pindex меньше 0.5, то берем значения от первого бота, иначе от второго
    if pindex < 0.5:
        x = botp1[j]
    else:
        x = botp2[j]
    return x # Возвращаем значние бота

    #доп функции
def pprint_df(dframe):
    print(tabulate(dframe, headers='keys', tablefmt='psql', showindex=False))

# Custom function to color the desired cell
def закрасить_ячейку(дата_фрейм, номер_строки, номер_столбца, длительность, цвет_ячейки,  цвет_текста):
    color1 = 'background-color: green; color: white'
    color2 = 'background-color: yellow; color: black'
    df_styler = pd.DataFrame('', index=дата_фрейм.index, columns=дата_фрейм.columns)
    df_styler.iloc[номер_строки, номер_столбца] = color1
    for i in range(длительность):
      df_styler.iloc[номер_строки, номер_столбца-i-1] = color2
    return df_styler 
    
def ввод_данных():
  global стиральные_машины
  global вместимость_машин
  global время_на_стирку
  global количество_мешков
  global вес_мешков
  global мешки
  global новые_мешки
  global количество_новых_мешков
  global вес_новых_мешков

  global cycle_time
  global data_frame
  global data_frame_m

  global вектор_вместимости_на_день

  cycle_time = ['8:00','8:30',	'9:00',	'9:30',	'10:00',	'10:30',	'11:00',	'11:30',	
              '12:00',	'12:30',	'13:00',	'13:30',	'14:00',	'14:30',	'15:00',	
              '15:30',	'16:00', '16:30',	'17:00',	'17:30',	'18:00',	'18:30',	
              '19:00',	'19:30',	'20:00']

  rand_or_request = input('Ввести данные "случайно" или "вручную" ? ')
  rand_or_request = rand_or_request.lower()

  if all(i in 'случайно' for i in rand_or_request):
    стиральные_машины = np.arange(1, 3+1)

    вместимость_машин = [12, 12, 14] 
    # for m in стиральные_машины:
    #   sr = random.SystemRandom()
    #   c = sr.randrange(14, 20, 2)
    #   вместимость_машин.append(c)
    
    время_на_стирку = [60, 60, 90]
    # for m in стиральные_машины:
    #   rr = random.SystemRandom()
    #   cycle = rr.randrange(60, 120, 30)
    #   время_на_стирку.append(cycle)
    
    time = []
    мешки = 50
    for i in range(мешки):
      time.append(cycle_time[0])
    количество_мешков = np.arange(мешки) #Количество мешков   
    вес_мешков = np.random.randint(4, 10, len(количество_мешков)) #Масса каждого мешка
    
    новые_мешки = ['10:00', '12:00', '14:00']
    
    количество_новых_мешков = np.arange(10) #Количество мешков   
    вес_новых_мешков =  np.random.randint(4, 10, len(количество_новых_мешков))

    #добавляем в конец новые мешки
    for i in range(len(количество_новых_мешков)):
      id_maker = мешки + количество_новых_мешков[i]
      количество_мешков = np.append(количество_мешков, id_maker)
    
    #добавляем в конец новые веса
    for i in range(len(вес_новых_мешков)):
      вес_мешков = np.append(вес_мешков, вес_новых_мешков[i])

    for i in range(len(количество_мешков)):
      time.append(cycle_time[0])

    firs_bags_new = количество_новых_мешков[4]
    second_bags_new = количество_новых_мешков[3]
    fird_bags_new = количество_новых_мешков[3]

    time_new_bags = []
    for i in range(len(количество_новых_мешков)):
      if i == 1:
        for t in range(fird_bags_new):
          time_new_bags.append(новые_мешки[0])
      elif i == 2:
        for t in range(second_bags_new):
          time_new_bags.append(новые_мешки[1])
      elif i == 3:
        for t in range(firs_bags_new):
          time_new_bags.append(новые_мешки[2])
    time[мешки:] = time_new_bags

    data_frame = pd.DataFrame({'Машинки': стиральные_машины, 'Макс. загрузка': вместимость_машин, 'Время цикла': время_на_стирку})
    for t in cycle_time:
      data_frame[t] = 0

    for m in range(len(стиральные_машины)):
      for t in range(len(cycle_time)):
        if t == 0:
          data_frame.loc[(data_frame['Машинки'] == стиральные_машины[m]), '8:00'] = вместимость_машин[m]
        
        else:
          df_mach = data_frame[(data_frame['Машинки'] == стиральные_машины[m])]
          time_max = df_mach.values[:,2][0]
          cycle = time_max / 30 
          avalible_time = np.arange(int(cycle), len(cycle_time), int(cycle))

          for av in avalible_time:
            data_frame.loc[(data_frame['Машинки'] == стиральные_машины[m]), cycle_time[av]] = вместимость_машин[m]
  
    machines = pd.DataFrame({'Машинки': стиральные_машины, 'Вместимость(кг)': вместимость_машин, 'Время на один цикл': время_на_стирку})
    data_frame_m = pd.DataFrame(data = [вес_мешков, time], columns=количество_мешков, index=['вес мешка', 'время доступа'])
    machines = machines.set_index('Машинки').dropna()
    data_frame = data_frame.set_index('Машинки')
    #Вектор временных индексов
    numpy_df = data_frame.to_numpy()
    вместимость_на_день = numpy_df[:, 2:30]
    вектор_вместимости_на_день = вместимость_на_день.reshape(len(стиральные_машины)*25,)

    '''
    Блок принтов
    '''
    print('__________________________________________________________')
    print('Количество стиральных машинок:', len(стиральные_машины))
    print('Время цикла на стирку:', время_на_стирку)
    print('Вместимость:', вместимость_машин, '\n')

    print('Количество мешков в начале смены:', мешки)
    print('Количество новых мешков:', len(количество_мешков[мешки:]))
    print('Количество мешков на весь день:', len(количество_мешков))
    print('План на день:', вес_мешков.sum(), 'кг')
    print('Максимальная возможная загрузка на день:', вектор_вместимости_на_день.sum(),'кг')
    print()

    print('Информация о стиральных машинах')
    display(machines.head())
    print()
    print('Информация о мешках и времени когда мешок будет готов к стирке')
    display(data_frame_m.head())

    #Ввод от пользователя
  elif all(i in 'вручную' for i in rand_or_request):
    #Создаем массив с номерами стиральных машин
    time = []
    n_m = int(input('Введите количество стиральных машин: '))
    print()
    стиральные_машины = np.arange(1, n_m + 1 )

    вместимость_машин = [] #Список для максимальной загрузки
    for m in стиральные_машины:
      print('Максимальная загрузка в "кг" для стиральной машинки под номером:', m)
      n_temp = int(input('Введите вместимость в "кг": '))
      print()
      вместимость_машин.append(n_temp)

    #Вводим максимальное время цикла стирки для каждой машины
    время_на_стирку = []
    for m in стиральные_машины:
      print('Введите время цикла для стиральной машинки под номером:', m)
      print('От "30" - "720" минут, с интервалом в 30 минут' )
      print('Например 30 будет означать что машинка стирает "30" минут' )
      cycle = int(input('Время цикла стирки: '))
      print()
      время_на_стирку.append(cycle)

    #Количесвто мешков, количество которое известно в начале смены
    print('Введите количество мешков которые будут доступны к стирке,')
    print('cначала открытия рабочей смены:')
    мешки = int(input('Общее количество мешков:'))

    print()
    количество_мешков = np.arange(мешки)

    вес_мешков = np.random.randint(4, 8, len(количество_мешков))#Масса каждого мешка
    
    for i in range(мешки):
      time.append(cycle_time[0])

    #Новые мешки
    print('В какое время приедут новые мешки?')
    print('Введите время в диапазоне с 8:00 - 20:00')
    print('C интервалом в 30 минут, например 10:00 10:30:')
    новые_мешки = input().split()
    print()


    количество_новых_мешков = []
    temp_count_bags = []
    for i in range(len(новые_мешки)):
      print('Какое количество мешков приедет в: ', новые_мешки[i])
      temp = int(input('Введите количество мешков, например 5:'))
      temp_count_bags.append(temp)
      массив_мешков = np.arange(temp)
      количество_новых_мешков.append(массив_мешков)
      print()

    time_new_bags = []
    for i in range(len(количество_новых_мешков)):
      t = temp_count_bags[i]
      for j in range(t):
        time_new_bags.append(новые_мешки[i])
    time[мешки:] = time_new_bags

    вес_новых_мешков = []
    for nm in range(len(количество_новых_мешков)):
      n = количество_новых_мешков[nm][-1]+1
      вес_мешков_temp = np.random.randint(4, 8, n)
      вес_новых_мешков.append(вес_мешков_temp)

    #добавляем в конец новые мешки
    for i in range(len(количество_новых_мешков)):
      id_maker = (количество_мешков[-1] + (количество_новых_мешков[i] + 1))
      количество_мешков = np.concatenate([количество_мешков, id_maker])

    #добавляем в конец новые веса
    for i in range(len(вес_новых_мешков)):
      вес_мешков = np.concatenate([вес_мешков, вес_новых_мешков[i]])

    data_frame = pd.DataFrame({'Машинки': стиральные_машины, 'Макс. загрузка': вместимость_машин, 'Время цикла': время_на_стирку})
    for t in cycle_time:
      data_frame[t] = 0

    for m in range(len(стиральные_машины)):
      for t in range(len(cycle_time)):
        if t == 0:
          data_frame.loc[(data_frame['Машинки'] == стиральные_машины[m]), '8:00'] = вместимость_машин[m]
        
        else:
          df_mach = data_frame[(data_frame['Машинки'] == стиральные_машины[m])]
          time_max = df_mach.values[:,2][0]
          cycle = time_max / 30 
          avalible_time = np.arange(int(cycle), len(cycle_time), int(cycle))

          for av in avalible_time:
            data_frame.loc[(data_frame['Машинки'] == стиральные_машины[m]), cycle_time[av]] = вместимость_машин[m]
    
    machines = pd.DataFrame({'Машинки': стиральные_машины, 'Вместимость(кг)': вместимость_машин, 'Время на один цикл': время_на_стирку})
    data_frame_m = pd.DataFrame(data = [вес_мешков, time], columns=количество_мешков, index=['вес мешка', 'время доступа'])
    machines = machines.set_index('Машинки').dropna()
    data_frame = data_frame.set_index('Машинки')
    #Вектор временных индексов
    numpy_df = data_frame.to_numpy()
    вместимость_на_день = numpy_df[:, 2:30]
    вектор_вместимости_на_день = вместимость_на_день.reshape(len(стиральные_машины)*25,)
    '''
    Блок принтов
    '''
    print('__________________________________________________________')
    print('Количество стиральных машинок:', len(стиральные_машины))
    print('Время цикла на стирку:', время_на_стирку)
    print('Вместимость:', вместимость_машин, '\n')
    print('Количество мешков в начале смены:', мешки)
    print('Количество новых мешков:', len(количество_мешков[мешки:]))
    print('Количество мешков на весь день:', len(количество_мешков))
    print('План на день:', вес_мешков.sum(), 'кг')
    print('Максимальная возможная загрузка на день:', вектор_вместимости_на_день.sum(),'кг')
    print()
    print('Информация о стиральных машинах')
    display(machines.head())
    print()
    print('Информация о мешках и времени когда мешок будет готов к стирке')
    display(data_frame_m.head())

def рассчитать_план_на_день(общее_число_ботов, количество_выживших, количество_эпох, коэфициент_мутаций):
  import time
  global data_frame
  n = общее_число_ботов # Общее число ботов
  nsurv = количество_выживших # Количество выживших (столько лучших переходит в новую популяцию)
  nnew = общее_число_ботов - количество_выживших  # Количество новых (столько новых ботов создается)
  epohs = количество_эпох # количество эпох
  mut = коэфициент_мутаций # коэфициент мутаций
  weights_dif = вектор_вместимости_на_день.sum() - вес_мешков.sum()
  # Длина бота(количество мешков)
  l = вес_мешков.shape[0] 
  trains = вектор_вместимости_на_день.shape[0] # Количество меток на каждый цикл
  straff = trains//25
  new_bags = вес_мешков[мешки:]
  popul = [] # Двумерный массив популяции, размерностью [n, l].
  val = [] # Одномерный массив значений этих ботов

  plotmeanval = [] # сюда будут заносится значения для графика по среднему значению
  plotminval = [] # сюда будут заносится значения для графика по минимальному значению
  
  for i in range(n): # Проходим по всей длине популяции
      popul.append([]) # Создаем пустого бота
      for j in range(l): # Проходим по всей длине бота
          
          # В каждый компонент бота записываем рандомное значение в диапазоне от 0 до количества циклов на день
          popul[i].append(random.randint(0, trains - 1)) 

  curr_time = time.time()
  for it in range(epohs): # Проходим по всем эпохам
     
      if (it == 500): # Меняем коэфициент мутации после 500-ой эпохи
          mut = 0.05  
      if (it == 800): # Меняем коэфициент мутации после 500-ой эпохи
          mut = 0.02 


      val = [] # Создаем пустой список для значений ботов
      for i in range(n): # Проходим по всей популяции
          bot = popul[i] # Берем очередного бота
          trainfill = np.zeros(shape=trains) # Массив, хранящий заполняемость каждой машинки во время цикла
          for j in range(l): # Проходим по всей длине бота
              trainfill[bot[j]] += вес_мешков[j] # Увеличиваем заполненность bot[j] на вес_мешков[j]          
          
          f = 0 # Обнуляем ошибку i-го бота 
          for t in range(trains): # Проходим по всем меткам циклов стирки
              # Увеличиваем ошибку i-го бота на модуль разницы между реальной вместимостью во время цикла 
              # и вместимостью, который посчитал бот
              f += abs(вектор_вместимости_на_день[t] - trainfill[t])
              
          # for i in range(1, straff+1):
          #   time_error = i*25
          #   if trainfill[time_error-1] != 0:
          #     f += 100

          for b in range(len(bot)):
              if cycle_time.index(cycle_time[bot[b]%25]) < cycle_time.index(data_frame_m.iloc[1,b]):
                f+=100         
          val.append(f) # Добавляем в val значение ошибки для i-го бота        
      
      newpopul, sval = getSurvPopul(popul, val, nsurv, 0) # Получаем новую популяцию и сортированный список значнией
      print('Выполняется эпоха №' '{:>2} {:>2}'.format(it, ''), '{:>3}'.format(np.round(time.time() - curr_time, 1)),
            'сек,', '{:>15}'.format('10 лучших ботов'), 
            np.array2string(np.round(sval[0:10] - weights_dif, 2).astype('int') ,  
            precision=2,suppress_small=True))   
      curr_time = time.time() # Обновляем текущее время
      plotmeanval.append(sum(val) / len(val)) # Добавляем среднее значение в список
      plotminval.append(sval[0]) # Добавляем минимальное значение в список
      
      for i in range(nnew): # Проходимся в цикле nnew-раз
          botp1, botp2 = getParents(newpopul, nsurv) # Из newpopul(новой популяции) получаем двух случайных родителей-ботов
          newbot = [] # Массив для нового бота
      
          for j in range(l): # Проходим по всей длине бота
              x = crossPointFrom2Parents(botp1, botp2, j) # Получаем значение для j-ого компонента бота
          
              # С вероятностью mut сбрасываем значение j-ого компонента бота на случайное
              if (random.random() < mut):
                  x = random.randint(0, trains - 1)        
              newbot.append(x) # Добавляем новое значение в бота      
          newpopul.append(newbot) # Добавляем бота в новую популяцию    
      popul = newpopul # Записываем в popul новую посчитанную популяцию

  # построение графиков 
  plt.plot(plotmeanval, 
          label='Среднее по популяции')
  plt.plot(plotminval, 
          label='Лучший бот')
  plt.xlabel('Эпоха обучения')
  plt.ylabel('Значение функции')
  plt.legend()
  plt.show()

  bot = popul[0] # Берем лучшее значение в популяции
  print('Значения лучшего бота:', bot, '\n') # Выводим значения бота

  trainfill = np.zeros(trains, dtype = 'int32') # Массив заполненности машинок
  for j in range(l): # Проходим по всей длине бота
      trainfill[bot[j]] += вес_мешков[j] # Увеличиваем заполненность bot[j]-ого поезда на size[j]вес_мешков

  print('Максимальная возможная загрузка на день:', вектор_вместимости_на_день.sum(),'кг', '\n')
  print('Плановое количество:', вес_мешков.sum(), 'кг')
  print('Постирано:', trainfill.sum(), 'кг')
  
  trainfill = np.full(len(вектор_вместимости_на_день), '', dtype='<U150') # Массив заполненности машинок

  for j in range(l): # Проходим по всей длине бота
    trainfill[bot[j]] += str(j) + '(' + str(вес_мешков[j]) + ') '
  trainfill_resh = trainfill.reshape(straff, 25)

  for m in range(len(trainfill_resh)):
    for t in range(len(cycle_time)):
      data_frame.loc[(data_frame.index == стиральные_машины[m]), cycle_time[t]] = trainfill_resh[m][t]
      
def план_на_день():
  display(data_frame.head())

def информация_о_мешке(n=None):
  if n == None:
    print('Введите номер мешка, от', 0, 'до', len(количество_мешков)-1)
    n = int(input('Ввдите номер мешка: '))

  план = data_frame.iloc[:, 2:].to_numpy().reshape(-1)
  мешок_доступен = data_frame_m.iloc[1:, 1:].to_numpy().reshape(-1)

  for i in range(len(план)):    
    data = план[i].split(' ')    
    for j in data:      
      if str(n) + '(' in j:
        if j.index(str(n)+'(') == 0:
          result = i        
          break
  idx = result // 25
  col = ((result + время_на_стирку[idx] // 30) %25) + 2   

  длительность = время_на_стирку[idx] // 30
  if result%25 == 24:
    длительность = 0

  print('Номер машинки: ', idx + 1)
  print('Номер мешка: ', n)
  print('Всего мешков:', len(количество_мешков)-1, '\n')
  print('Время когда мешок готов к стирке:', мешок_доступен[n-1])
  print('Время начала стирки:', cycle_time[result %25])
  if длительность>0:
    print('Время готовности: ', cycle_time[result %25 + время_на_стирку[idx] // 30], '\n')
  print('Зеленым цветом выделено время, когда мешок будет постиран:',n)
  print('Желтым цветом выделено время, когда мешок стирается:',n, '\n')

  
  display(data_frame.style.apply(
            закрасить_ячейку,    
            номер_строки = idx,
            номер_столбца = col,
            длительность = время_на_стирку[idx] // 30,
            цвет_ячейки = 'green',
            цвет_текста = 'white',
            axis = None))

