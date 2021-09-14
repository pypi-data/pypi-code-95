import pathlib
from pathlib import Path
import pandas as pd
import numpy as np
import cv2 as cv
import json 
import PIL
from tqdm import trange, tqdm
import PIL.Image as Image
from PIL import Image, ImageOps
import torch
from torch.utils.data import Dataset
from sklearn.model_selection import train_test_split
import matplotlib.pyplot as plt
import xmltodict, json
import string

from ..ops import boxes as boxes_ops 


class SVTDataset(Dataset):
    def __init__(self, root, mode='train', transform=None, **kwargs):
        super(SVTDataset, self).__init__()
        self._init_default_attrs(**kwargs)
        self.root: Path = Path(root)
        self.mode: str = mode
        self.transform = transform
        
        self._load_dataframe()
        
    def _init_default_attrs(self, **kwargs):
        self.data_filtering_off: bool = kwargs.get('data_filtering_off', False)
        self.batch_max_length: int = kwargs.get('batch_max_length', 25)
        self.character = kwargs.get('character',  string.printable[:-6])
        self.re_char: str = '' 
        self.filter_multi_words = True
        self.is_rgb: bool = kwargs.get('is_rgb', False)
        self.force_htranspose = kwargs.get('force_htranspose', False)
        self.random_state = kwargs.get('random_state', 1261)
        self.is_sensitive = kwargs.get('is_sensitive', True)
        self.usage_ratio:float = kwargs.get('usage_ratio', 1.0)
        self.debug = kwargs.get('debug', False)
        
        
    def _load_dataframe(self):
        if self.mode == 'train':
            self.csv_file = self.root.joinpath('train.csv')
        elif self.mode == 'valid':
            self.csv_file = self.root.joinpath('test.csv')
        else:
            raise Exception('Only train and valid values are accepted for mode!')
            
        self.dataframe = pd.read_csv(str(self.csv_file))
        
        self._filter_by_batch_max_length()
        self._filter_by_usage_ratio()
        self._filter_outside_image_box()
        self._filter_multi_words()
        self._filter_character()
        
    
    def _filter_multi_words(self):
        def is_single_words(x):
            x = x.strip()
            if len(x)!=0:
                word_list = x.split(" ")
                if len(word_list)==1:
                    return True
                else:
                    return False
            else:
                return False
        
        if self.filter_multi_words:
            self.dataframe = self.dataframe[self.dataframe['label'].apply(is_single_words)]
        
        
    def _filter_outside_image_box(self):
        def exclude_box_outside_image_size(rows):
            stats = False
            box = [int(val) for val in rows['boxes'].split(",")]
            box = boxes_ops.xywh2xymm(box)
            xmin,ymin,xmax,ymax = box
            w, h = rows['size'].split(",")
            w, h = int(w), int(h)
            
            if 0<=xmin<=w and 0<=ymin<=h and 0<=xmax<=w and 0<=ymax<=h and xmax-xmin>0 and ymax-ymin>0:
                 stats = True
            return stats
        
        self.dataframe = self.dataframe[self.dataframe.apply(exclude_box_outside_image_size, axis=1)]
        self.dataframe.reset_index(drop=True, inplace=True)
        
    def _filter_character(self):
        import re
        def character_filter(label):
            out_of_char = f'[^{self.character}]'
            label = re.sub(out_of_char, self.re_char, label)
            return label
        
        self.dataframe['label'] = self.dataframe['label'].apply(character_filter)
        
        
    def _filter_by_batch_max_length(self):
        self.dataframe = self.dataframe[self.dataframe['label'].str.len() <= self.batch_max_length]
        self.dataframe.reset_index(drop=True, inplace=True)
        
        
    def _filter_by_usage_ratio(self):
        self.dataframe = self.dataframe.sample(
            frac=self.usage_ratio, 
            random_state=self.random_state
        )
        self.dataframe.reset_index(drop=True, inplace=True)
        
        
    def _load_data(self, idx):
        record = self.dataframe.iloc[idx]
        image_file = record['image_file']
        image_path = str(self.root.joinpath(image_file))
        
        box = [int(val) for val in record['boxes'].split(",")]
        box = boxes_ops.xywh2xymm(box)
        
        label = record['label'] 
        
        return image_path, box, label
    
    def _load_image(self, path):
        image = cv.imread(path)
        image = cv.cvtColor(image, cv.COLOR_RGB2BGR)
        return image
    
    def _crop_image(self, image, box):
        xmin, ymin, xmax, ymax = box
        croped = image[ymin:ymax, xmin:xmax].copy()

        image = Image.fromarray(croped).convert("RGB")
        image = PIL.ImageOps.exif_transpose(image)
        if  self.force_htranspose:
            if image.size[1]>image.size[0]: 
                image = image.transpose(Image.ROTATE_90)
        
        return image
    
    def _load_croped_image(self, path, box):
        image = self._load_image(path)
        image = self._crop_image(image, box)
        return image
        
    def __len__(self):
        return len(self.dataframe)
    
    def __getitem__(self, idx):
        impath, boxes, label = self._load_data(idx)
        image = self._load_croped_image(impath, boxes)
        
        if not self.is_sensitive:
            label = label.lower()
            
        if self.transform:
            image = self.transform(image)
            
        return image, label