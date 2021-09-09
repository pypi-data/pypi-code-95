import os

import cv2
import numpy as np
import tensorflow as tf
from sklearn.model_selection import train_test_split


class ModelCreator(object):
    IMG_WIDTH = 200
    IMG_HEIGHT = 200
    img_data = None
    class_name = None
    target_dict = None
    target_val = None

    def __init__(self, output, image_folder, image_width=None, image_height=None):
        self.output = output
        self.image_folder = image_folder
        self.image_width = image_width if image_width else self.IMG_WIDTH
        self.image_height = image_height if image_height else self.IMG_HEIGHT
        self.set_image_and_class_name()
        self.set_targets()

    def create_dataset(self):
        img_data_array = []
        class_name = []

        for dir1 in os.listdir(self.image_folder):
            for file in os.listdir(os.path.join(self.image_folder, dir1)):
                image_path = os.path.join(self.image_folder, dir1, file)
                image = cv2.imread(image_path, cv2.COLOR_BGR2RGB)
                image = cv2.resize(image, (self.image_height, self.image_width), interpolation=cv2.INTER_AREA)
                image = np.array(image)
                image = image.astype('float32')
                image /= 255
                img_data_array.append(image)
                class_name.append(dir1)
        return img_data_array, class_name

    def set_image_and_class_name(self):
        self.img_data, self.class_name = self.create_dataset()

    def set_targets(self):
        self.target_dict = {k: v for v, k in enumerate(np.unique(self.class_name))}
        self.target_val = [self.target_dict[self.class_name[i]] for i in range(len(self.class_name))]

    def save_model(self):
        model = tf.keras.Sequential(
            [
                tf.keras.layers.InputLayer(input_shape=(self.image_height, self.image_width, 3)),
                tf.keras.layers.Conv2D(filters=32, kernel_size=3, strides=(2, 2), activation='relu'),
                tf.keras.layers.Conv2D(filters=64, kernel_size=3, strides=(2, 2), activation='relu'),
                tf.keras.layers.Flatten(),
                tf.keras.layers.Dense(6)
            ])
        model.compile(optimizer='rmsprop', loss='sparse_categorical_crossentropy', metrics=['accuracy'])
        model.fit(x=np.array(self.img_data, np.float32), y=np.array(list(map(int, self.target_val)), np.float32),
                  epochs=5)
        model.save(self.output)

    def get_train_test_split(self):
        x = np.array(self.img_data, np.float32)
        y = np.array(list(map(int, self.target_val)))
        return train_test_split(x, y)
