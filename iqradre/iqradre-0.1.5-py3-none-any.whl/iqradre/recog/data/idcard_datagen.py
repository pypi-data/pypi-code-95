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
import string


from ..ops import boxes as boxes_ops



class IDCardDatagenOCRDataset(Dataset):
    def __init__(self, root, mode='train', transform=None, **kwargs):
        super(IDCardDatagenOCRDataset, self).__init__()
        self._init_default_attrs(**kwargs)
        self.root: Path = Path(root)
        self.mode: str = mode
        self.transform = transform
        
        self._build_workpath()
        self._build_dataframe()
    
    def _init_default_attrs(self, **kwargs):
        self.data_filtering_off: bool = kwargs.get('data_filtering_off', False)
        self.batch_max_length: int = kwargs.get('batch_max_length', 25)
        self.character = kwargs.get('character',  string.printable[:-6])
        self.re_char: str = '' 
        self.filter_multi_words = True
        self.is_rgb: bool = kwargs.get('is_rgb', False)
        self.force_htranspose = kwargs.get('force_htranspose', False)
        self.is_sensitive = kwargs.get('is_sensitive', True)
        self.usage_ratio = kwargs.get('usage_ratio', 1.0)
        self.random_state = kwargs.get('random_state', 1261)
        self.debug = kwargs.get('debug', False)
        
    
    def _build_workpath(self):
        self.workpath = self.root.joinpath('dataset')
    
    def _build_dataframe(self):
        if self.mode == 'train' or self.mode == 'valid' or self.mode == 'test':
            fname = f'{self.mode}.csv'
            fpath = str(self.root.joinpath(fname))
            self.dataframe = pd.read_csv(fpath)
            
            self._filter_by_batch_max_length()
            self._filter_by_usage_ratio()
            self._filter_multi_words()
            self._filter_character()
        else:
            raise Exception('Only train, valid and test are accepted values for mode!')
            
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
            self.dataframe = self.dataframe[self.dataframe['text'].apply(is_single_words)]
            
    def _filter_character(self):
        import re
        def character_filter(label):
            out_of_char = f'[^{self.character}]'
            label = re.sub(out_of_char, self.re_char, label)
            return label
        
        self.dataframe['text'] = self.dataframe['text'].apply(character_filter)
    
    
    def _filter_by_batch_max_length(self):
        self.dataframe = self.dataframe[self.dataframe['text'].str.len() <= self.batch_max_length]
        self.dataframe.reset_index(drop=True, inplace=True)
        
        
    def _filter_by_usage_ratio(self):
        self.dataframe = self.dataframe.sample(
            frac=self.usage_ratio, 
            random_state=self.random_state
        )
        self.dataframe.reset_index(drop=True, inplace=True)
    
    def _load_json(self, path):
        data = None
        with open(path, 'r') as file:
            data = json.load(file)
        return data
    
    def _clean_alt_list(self, list_):
        list_ = list_.replace(', ', ',')
        list_ = list_.replace('[', '')
        list_ = list_.replace(']', '')
        return list_
    
    def _reformat_string_points_to_list(self, points_string):
        points = [float(p) for p in points_string.split(",")]
        points = list(zip(points[::2], points[1::2]))
        return points
        
    def _load_image(self, path):
        image = cv.imread(path)
        image = cv.cvtColor(image, cv.COLOR_BGR2RGB)
        return image
    
    def _crop_image(self, image, points):
        np_points = np.array(points)
        xmin, ymin, xmax, ymax = boxes_ops.coord2xymm(np_points, to_int=True)
        nymin = ymin + int((ymax-ymin)*0.05)
        nymax = ymax + int((ymax - ymin)*0.15)
        nxmin = xmin - int((xmax-xmin)*0.05)
        nxmax = xmax + int((xmax-xmin)*0.05)

        croped = image[nymin:nymax, nxmin:nxmax].copy()

        image = Image.fromarray(croped).convert("RGB")
        image = PIL.ImageOps.exif_transpose(image)
        if  self.force_htranspose:
            if image.size[1]>image.size[0]: 
                image = image.transpose(Image.ROTATE_90)
        
        return image
    
    
    
    def _load_croped_image(self, path, points):
        image = self._load_image(path)
        image = self._crop_image(image, points)
        return image
    

    def _load_data(self, idx):
        data = self.dataframe.iloc[idx]
        impath, points, label = data['image_file'], data['points'], data['text']
        
        points = self._clean_alt_list(points)
        points = self._reformat_string_points_to_list(points)
        impath = self.workpath.joinpath(impath)
#         print(impath, impath.exists())
        return str(impath), points, label
    
        
    def __len__(self):
        return len(self.dataframe)
    
    def __getitem__(self, idx):
        impath, points, text = self._load_data(idx)
        image = self._load_croped_image(impath, points)
        
        if not self.is_sensitive:
            text = text.lower()
        
        if self.transform:
            image = self.transform(image)
        
        return image, text
    