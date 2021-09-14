import pathlib
from pathlib import Path
import pandas as pd
import numpy as np
import cv2 as cv
import json 
import PIL
import PIL.Image as Image
from PIL import Image, ImageOps
import torch
from torch.utils.data import Dataset
from sklearn.model_selection import train_test_split
import matplotlib.pyplot as plt
from tqdm import trange, tqdm
import xmltodict, json
from IPython.display import JSON
from collections import OrderedDict
import random
from torch.utils.data import ConcatDataset
import string




class TextRendererDataset(Dataset):
    def __init__(self, root, mode='train',  val_size = 0.2, transform=None, **kwargs):
        super(TextRendererDataset, self).__init__()
        self._init_default_attrs(**kwargs)
        self.root: Path = Path(root)
        self.mode: str = mode
        self.val_size = val_size
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
        self.random_state = kwargs.get('random_state', 1261)
        self.is_sensitive = kwargs.get('is_sensitive', True)
        self.usage_ratio:float = kwargs.get('usage_ratio', 1.0)
        self.debug = kwargs.get('debug', False)
            
        
    def _build_workpath(self):
        self.image_path = self.root.joinpath('images')
        self.json_path = self.root.joinpath('labels.json')
        
    def _build_dataframe(self):
        json_data = self._load_json(self.json_path)
        index = list(json_data['labels'].keys())
        labels = [json_data['labels'][k] for k in index]

        train_index, valid_index, train_labels, valid_labels = train_test_split(
            index, labels, 
            test_size=self.val_size, 
            random_state=self.random_state
        )

        if self.mode=='train':
            train_files = [f'{index}.jpg' for index in train_index]
            train_data = { 'index': train_index, 'image_path': train_files, 'labels': train_labels}
            train_df = pd.DataFrame(train_data)
            self.dataframe = train_df
        else:
            valid_files = [f'{index}.jpg' for index in valid_index]
            valid_data = { 'index': valid_index, 'image_path': valid_files, 'labels': valid_labels}
            valid_df = pd.DataFrame(valid_data) 
            self.dataframe = valid_df
            
        self._filter_by_batch_max_length()
        self._filter_by_usage_ratio()
        self._filter_multi_words()
        self._filter_character()
            
        return self.dataframe
    
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
            self.dataframe = self.dataframe[self.dataframe['labels'].apply(is_single_words)]
    
    def _filter_character(self):
        import re
        def character_filter(label):
            out_of_char = f'[^{self.character}]'
            label = re.sub(out_of_char, self.re_char, label)
            return label
        
        self.dataframe['labels'] = self.dataframe['labels'].apply(character_filter)
    
    def _filter_by_batch_max_length(self):
        self.dataframe = self.dataframe[self.dataframe['labels'].str.len() <= self.batch_max_length]
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
    
    def _load_image(self, path):
        image = cv.imread(path)
        image = cv.cvtColor(image, cv.COLOR_BGR2RGB)
        
        image = Image.fromarray(image).convert("RGB")
        image = PIL.ImageOps.exif_transpose(image)
        if  self.force_htranspose:
            if image.size[1]>image.size[0]: 
                image = image.transpose(Image.ROTATE_90)
        
        
        return image

    def _load_data(self, idx):
        data = self.dataframe.iloc[idx]
        impath, label = data['image_path'], data['labels']
        impath = self.image_path.joinpath(impath)
        if self.debug:
            print(f'file from path {impath} is exist={impath.exists()}')
        return str(impath), label
    
        
    def __len__(self):
        return len(self.dataframe)
    
    def __getitem__(self, idx):
        impath, text = self._load_data(idx)
        image = self._load_image(impath)
                
        if not self.is_sensitive:
            text = text.lower()
        
        if self.transform:
            image = self.transform(image)
        
        return image, text
    
    
class TextRendererMultiDataset(Dataset):
    def __init__(self, root, mode='train', val_size = 0.2, glob_keyword="*", transform=None, **kwargs):
        super(TextRendererMultiDataset, self).__init__()
        self._init_default_attrs(**kwargs)
        self.root: Path = Path(root)
        self.mode: str = mode
        self.val_size = val_size
        self.transform = transform
        self.glob_keyword = glob_keyword
        
        self._build_multi_dataset()
        
        
    def _init_default_attrs(self, **kwargs):
        self.data_filtering_off: bool = kwargs.get('data_filtering_off', False)
        self.batch_max_length: int = kwargs.get('batch_max_length', 25)
        self.character = kwargs.get('character', '0123456789abcdefghijklmnopqrstuvwxyz')
        self.is_rgb: bool = kwargs.get('is_rgb', False)
        self.force_htranspose = kwargs.get('force_htranspose', False)
        self.random_state = kwargs.get('random_state', 1261)
        self.debug = kwargs.get('debug', False)
        
    def _valid_dirs(self):
        files = list(self.root.glob(self.glob_keyword))
        dirs = [p for p in files if p.is_dir()]
        
        valid_dirs = []
        for dr in dirs:
            if dr.joinpath('labels.json').exists() and dr.joinpath("images").is_dir():
                try:
                    has_data = next(dr.joinpath("images").glob("*.jpg"))
                    has_data = True
                except:
                    has_data = False

                if has_data: valid_dirs.append(dr)
            
        
        return valid_dirs
    
    def _build_multi_dataset(self):
        self.valid_dirs = self._valid_dirs()
        
        self.multiset = []
        for rpath in tqdm(self.valid_dirs):
            dset = TextRendererDataset(root=str(rpath), mode=self.mode, 
                                       val_size=self.val_size, transform=self.transform,
                                       random_state=self.random_state, 
                                       character=self.character, is_rgb=self.is_rgb,
                                       force_htranspose=self.force_htranspose,
                                       batch_max_length=self.batch_max_length,
                                       data_filtering_off=self.data_filtering_off)
            self.multiset.append(dset)
            if self.debug:
                print(f'added dataset({len(dset)}): {dset.root}')
        
        from torch.utils.data import ConcatDataset
        self.concatset = ConcatDataset(self.multiset)
        
    def __len__(self):
        return len(self.concatset)
    
    def __getitem__(self, idx):
        return self.concatset[idx]
        
        
        
