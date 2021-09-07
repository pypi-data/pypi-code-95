import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle 
import seaborn as sns
import utils
sns.set_style('darkgrid')

def clear_data(data):
    del data['Date']
    data = data.dropna() # удаляем строки с NaN
    return data

def getData():
  train_dataset = pd.read_csv('train_dataset.csv', sep=",")
  val_dataset = pd.read_csv('val_dataset.csv', sep=",")  
  train_dataset = clear_data(train_dataset)
  val_dataset = clear_data(val_dataset)
  return train_dataset, val_dataset

def show_data(data, start = 0, end = 0, param=['Close']):
    if end==0:
      end = data.shape[0]
    fig = plt.figure(figsize=(18,9))
    ax = fig.add_subplot(111) 
    for i in param:
      ax.plot(data[i][start:end], label=i)
    plt.legend()  
    plt.show() 

def show_full_data(train, val, param=['Close']):  
    data = train.append(val).reset_index() 
    fig = plt.figure(figsize=(18,9))
    ax = fig.add_subplot(111)
    for i in param:
      ax.plot(data[i], label=i)
    ax.add_patch( Rectangle((0, 600), 
                          train.shape[0], -600, 
                          fc ='none',  
                          ec ='g', 
                          lw = 2) )
    ax.add_patch( Rectangle((train.shape[0]+4, 600), 
                          val.shape[0]-4, -600, 
                          fc ='none',  
                          ec ='y', 
                          lw = 2) )
    ax.add_patch( Rectangle((train.shape[0]+val.shape[0]+8, 600), 
                          296, -600, 
                          fc ='none',  
                          ec ='b', 
                          lw = 2) )
    plt.legend()  
    plt.show() 