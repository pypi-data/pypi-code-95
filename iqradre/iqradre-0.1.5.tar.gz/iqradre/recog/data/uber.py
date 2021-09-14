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




# plt.rcParams["figure.figsize"] = 12,12

class UberTextRecognitionDataset(Dataset):
    def __init__(self, root, mode='train', size_mode='1k', transform=None, **kwargs):
        super(UberTextRecognitionDataset, self).__init__()
        self._init_default_attrs(**kwargs)
        
        self.root: Path = Path(root)
        self.mode: str = mode
        self.mode_path: str = self._get_mode_path(mode)
        self.size_mode: str = size_mode
        self.size_path: str = self._get_size_path(size_mode)
            
        self.transform = transform
        
        self._build_workpath()
        self._load_dataframe()
        
    def _init_default_attrs(self, **kwargs):
        self.data_filtering_off: bool = kwargs.get('data_filtering_off', False)
        self.batch_max_length: int = kwargs.get('batch_max_length', 25)
        self.character = kwargs.get('character',  string.printable[:-6])
        self.re_char: str = '' 
        self.filter_multi_words = True
        self.is_rgb: bool = kwargs.get('is_rgb', False)
        self.force_htranspose = kwargs.get('force_htranspose', True)
        self.is_sensitive = kwargs.get('is_sensitive', True)
        self.usage_ratio:float = kwargs.get('usage_ratio', 1.0)
        self.random_state = kwargs.get('random_state', 1261)
        self.debug = kwargs.get('debug', False)
        
    def _build_workpath(self):
        if self.mode_path =='valid':
            mode_path = 'val'
        else:
            mode_path = self.mode_path
            
        self.workpath = self.root.joinpath(mode_path).joinpath(self.size_path)
        
    def _get_size_path(self, size_mode):
        if size_mode == '1k': return "1Kx1K"
        elif size_mode == '4k':return "4Kx4K"
        else:
            raise Exception("Only 1k and 4k value are accepted!")
            
    def _get_mode_path(self, mode):
        if mode == "train": return 'train'
        elif mode == "valid": return 'valid'
        elif mode == "test": return "test"
        else:
            raise Exception("Only 'train', 'valid', or 'test' value are accepted!")
    
    def _load_dataframe(self):
        fname = f'{self.mode_path }_{self.size_path}_recog.csv'
        csv_path = self.root.joinpath(fname)
        self.dataframe = pd.read_csv(csv_path)
        
        self._filter_by_batch_max_length()
        self._filter_by_usage_ratio()
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
            self.dataframe = self.dataframe[self.dataframe['texts'].apply(is_single_words)]
        
        
    def _filter_character(self):
        import re
        def character_filter(label):
            out_of_char = f'[^{self.character}]'
            label = re.sub(out_of_char, self.re_char, label)
            return label
        
        self.dataframe['texts'] = self.dataframe['texts'].apply(character_filter)
    
    def _filter_by_batch_max_length(self):
        self.dataframe = self.dataframe[self.dataframe['texts'].str.len() <= self.batch_max_length]
        self.dataframe.reset_index(drop=True, inplace=True)
        
        
    def _filter_by_usage_ratio(self):
        self.dataframe = self.dataframe.sample(
            frac=self.usage_ratio, 
            random_state=self.random_state
        )
        self.dataframe.reset_index(drop=True, inplace=True)
        
          
    def load_data(self, idx):
        record = self.dataframe.iloc[idx]
        imfile = self.workpath.joinpath(record['image_files'])
        points = [int(pts) for pts in record['points'].strip().split(" ")]
        points = list(zip(points[::2], points[1::2]))
        text = record['texts']
#         clazz = self.class2idx(record['class_name'])
        
        return imfile, points, text
    
    def _load_image(self, path):
        image = cv.imread(path)
#         info = f'uber_image_type: {type(image)} from path {path}'
#         print(info)
        image = cv.cvtColor(image, cv.COLOR_BGR2RGB)
        return image
    
    def load_croped_image(self, imfile, points, bg_color='black'):
        img = self._load_image(str(imfile))
        pts = np.array(points)
        
        ## (1) Crop the bounding rect
        rect = cv.boundingRect(pts)
        x,y,w,h = rect
        croped = img[y:y+h, x:x+w].copy()
        
        image = Image.fromarray(croped).convert("RGB")
        image = PIL.ImageOps.exif_transpose(image)
        if  self.force_htranspose:
            if image.size[1]>image.size[0]: 
                image = image.transpose(Image.ROTATE_90)
        
        return image
        
    
    @property
    def classname(self):
        return ["StreetNumber","BusinessName", "StreetName", "StreetNumberRange", "None"]
    
    def class2idx(self, name):
        dct = {}
        for idx, clz in enumerate(self.classname):
            dct[clz] = idx
        return dct[name]
    
    def idx2class(self, idx):
        self.classname[idx]
        
    def __len__(self):
        return len(self.dataframe)
    
    def __getitem__(self, idx):
        imfile, points, text = self.load_data(idx)
        img = self.load_croped_image(imfile, points)
        
        if not self.is_sensitive:
            text = text.lower()
        
        if self.transform:
            img = self.transform(img)
            
        return img, text