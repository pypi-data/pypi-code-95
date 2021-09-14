import pathlib
from pathlib import Path
import json 
import xmltodict
import random
import string
import pandas as pd
import numpy as np
import cv2 as cv
from copy import deepcopy
from collections import OrderedDict
from numerize.numerize import numerize


import PIL
from PIL import Image, ImageOps
from tqdm import trange, tqdm

# from iqradre.recog.data import 
# from iqradre.recog.data import IDCardDatagenOCRDataset, TextRendererDataset, TextRendererMultiDataset, KTPLabelImageDataset

import torch
from torch.utils.data import Dataset, ConcatDataset, DataLoader
import torchvision.transforms as VT
from sklearn.model_selection import train_test_split

from . import *
from ..ops import boxes as boxes_ops
from ..transforms import transforms as NT



base_config = {
    'root': None,
    'usage_ratio': 1.0,
    'force_htranspose': False,
    'is_sensitive': True,
    'character': string.printable[:-6],
    'batch_max_length': 25,
    'DatasetClass': None,
}

dataset_config = {
    'ubertext': deepcopy(base_config),
    'cocotext': deepcopy(base_config),
    'fbocr': deepcopy(base_config),
    'svt': deepcopy(base_config),
    'datagen': deepcopy(base_config),
    'renderer': deepcopy(base_config),
    'labelimg': deepcopy(base_config),
}

# dataset_config['fbocr']['usage_ratio'] = 0.2
dataset_config['datagen']['usage_ratio'] = 0.5

dataset_config['ubertext']['DatasetClass'] = UberTextRecognitionDataset
dataset_config['cocotext']['DatasetClass'] = COCOTextDataset
dataset_config['fbocr']['DatasetClass'] = FacebookTextOCRDataset
dataset_config['svt']['DatasetClass'] = SVTDataset
dataset_config['datagen']['DatasetClass'] = IDCardDatagenOCRDataset
dataset_config['renderer']['DatasetClass'] = TextRendererMultiDataset
dataset_config['labelimg']['DatasetClass'] = KTPLabelImageDataset


imagenet_mean=[0.485, 0.456, 0.406]
imagenet_std=[0.229, 0.224, 0.225]

clova_mean = [0.5, 0.5, 0.5]
clova_std = [0.5, 0.5, 0.5]


def transform_function(img_size=(32,100), grayscale=False, 
                       mean=clova_mean, std=clova_std):
    trans_list = []
    trans_list.append(NT.ResizeRatioWithRightPad(size=img_size))
    
    if not grayscale: 
        trans_list.append(VT.ToTensor())
        trans_list.append(VT.Normalize(mean=mean, std=std))
    else:
        trans_list.append(VT.Grayscale())
        trans_list.append(VT.ToTensor())
        
        mean_avg = sum(mean) / len(mean)
        std_avg = sum(std) / len(std)
        
        trans_list.append(VT.Normalize(mean=(mean_avg), std=(std_avg)))
    
    trans_func = VT.Compose(trans_list)
    return trans_func


def load_multi_dataset(dataset_root, mode='train', 
                        batch_size=32, num_workers=8, shuffle=True,
                        is_sensitive=True, batch_max_length=25,
                        img_size=(32, 100),  grayscale=False,
                        character="0123456789abcdefghijklmnopqrstuvwxyz",
                        re_char='*'):

    dset_list = []
    tform_func = transform_function(img_size=img_size, grayscale=grayscale)
    for key, value in tqdm(dataset_root.items()):
        key = key.split("_")[0]
        config = deepcopy(dataset_config[key])
        if type(value)==str:
            config['root'] = value
            config['mode'] = mode
            config['transform']=  tform_func
            config['batch_max_length'] = batch_max_length
            config['is_sensitive'] = is_sensitive
            config['character'] = character
            config['re_char'] = re_char
            
            DatasetClass = config['DatasetClass']
            activeset = DatasetClass(**config)
            dset_list.append(activeset)
            
        elif type(value)==list:
            for idx, val in enumerate(value):
                config['root'] = val
                config['mode'] = mode
                config['transform']=  tform_func
                config['batch_max_length'] = batch_max_length
                config['is_sensitive'] = is_sensitive
                config['character'] = character
                config['re_char'] = re_char
                
                DatasetClass = config['DatasetClass']
                activeset = DatasetClass(**config)
                dset_list.append(activeset)

    dset = ConcatDataset(dset_list)
                            
    dloader = DataLoader(dset, batch_size=batch_size,
                         shuffle=shuffle, num_workers=num_workers,
                         pin_memory=True)
    
    return dloader, dset, dset_list, config