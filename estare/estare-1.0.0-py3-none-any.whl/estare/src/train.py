import numpy as np
#from sklearn.model_selection import train_test_split
from tensorflow import keras
import csv
import os


# featurePath = '../data/features/pixels/'
# refusedPath = '../data/refuse/pixels/'

# for filename in os.listdir(featurePath):
#     if filename.endswith('.npy'):
#         dataArray = np.load(os.path.join(featurePath, filename))
#         # dataShape = np.shape(dataArray)
#         # dataCount = 1
#         # for dim in dataShape:
#         #     dataCount *= dim
#         # data_1D = np.reshape(dataArray, dataCount)
#         data_1D = dataArray.flatten()
#         dataAugmented = np.insert(data_1D, 0, 1)   # Insert a 1 at index 0 indicating this row as a feature
#         with open('pixel_data.csv','a') as csv_data:
#             csv_writer = csv.writer(csv_data)
#             csv_writer.writerow(dataAugmented)

# for filename in os.listdir(refusedPath):
#     if filename.endswith('.npy'):
#         dataArray = np.load(os.path.join(refusedPath, filename))
        
#         data_1D = dataArray.flatten()
#         dataAugmented = np.insert(data_1D, 0, 0)   # Insert a 0 at index 0 marking this row as refused 
#         with open('pixel_data.csv','a') as csv_data:
#             csv_writer = csv.writer(csv_data)
#             csv_writer.writerow(dataAugmented)

print('Data preparation completed.')



img_rows, img_cols = 20, 20
num_classes = 2

def prep_data(raw):
    y = raw[:, 0]
    out_y = keras.utils.to_categorical(y, num_classes)
    
    x = raw[:,1:]
    num_images = raw.shape[0]
    out_x = x.reshape(num_images, img_rows, img_cols, 1)
    #out_x = out_x / 255
    return out_x, out_y

fashion_file = "./pixel_data.csv"
fashion_data = np.loadtxt(fashion_file, skiprows=1, delimiter=',')
x, y = prep_data(fashion_data)

# Set up code checking
#from learntools.core import binder
#binder.bind(globals())
#from learntools.deep_learning.exercise_7 import *
print("Setup Complete")

#-----------------------------------------------------------------
from tensorflow import keras
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, Flatten, Conv2D


fashion_model = Sequential()

fashion_model.add(Conv2D(12, kernel_size=(3,3), activation='relu', input_shape=(img_rows, img_cols, 1)))

fashion_model.add(Conv2D(20, kernel_size=(3,3), activation='relu'))
fashion_model.add(Conv2D(20, kernel_size=(3,3), activation='relu'))
fashion_model.add(Flatten())
fashion_model.add(Dense(100, activation='relu'))
fashion_model.add(Dense(num_classes, activation='softmax'))

fashion_model.compile(loss='categorical_crossentropy', optimizer='adam', metrics=['accuracy'])

fashion_model.fit(x, y, batch_size=100, epochs=4, validation_split=0.2)

#-----------------------------------------------------------------


