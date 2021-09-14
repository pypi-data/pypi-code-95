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
from IPython.display import JSON
from collections import OrderedDict
import random
import string


from ..ops import boxes as boxes_ops

class KTPLabelImageDataset(Dataset):
    def __init__(self, root, mode='train',  val_size = 0.2, transform=None, **kwargs):
        super(KTPLabelImageDataset, self).__init__()
        self._init_default_attrs(**kwargs)
        self.root: Path = Path(root)
        self.mode: str = mode
        self.val_size = val_size
        self.transform = transform
        
        self._build_dataframe_if_not_exists()
    
    def _init_default_attrs(self, **kwargs):
        self.data_filtering_off: bool = kwargs.get('data_filtering_off', False)
        self.batch_max_length: int = kwargs.get('batch_max_length', 25)
        self.character = kwargs.get('character',  string.printable[:-6])
        self.re_char: str = '' 
        self.filter_multi_words = True
        self.is_rgb: bool = kwargs.get('is_rgb', False)
        self.force_htranspose = kwargs.get('force_htranspose', False)
        self.random_state = kwargs.get('random_state', 1261)
        self.filter_by = kwargs.get('filter_by','word')
        self.is_sensitive = kwargs.get('is_sensitive', True)
        self.usage_ratio:float = kwargs.get('usage_ratio', 1.0)
        self.debug = kwargs.get('debug', False)
        
    def _build_dataframe_if_not_exists(self):
        # check csv exists
        train_csv_path = self.root.joinpath('train.csv')
        valid_csv_path = self.root.joinpath('valid.csv')
        dataset_path = self.root.joinpath('dataset')
        
        if train_csv_path.exists()==False or valid_csv_path.exists()==False:
            if self.debug: print(f'Info: Build dataset dataframe for the first time!!')
                
            main_df = self._load_xml_files_to_dataframe(dataset_path)
            
            if self.debug: print(f'Info: Splitting dataframe for train and validation purpose!')
            train_df, valid_df = self._split_dataset(main_df)
            if train_csv_path.exists()==True: train_csv_path.unlink()
            if valid_csv_path.exists()==True: valid_csv_path.unlink()
                
            if self.debug: print(f'Info: Saving train.csv and valid.csv data!')
            train_df.to_csv(str(train_csv_path), index=False)
            valid_df.to_csv(str(valid_csv_path), index=False)
            
            if self.mode == 'train':
                self.dataframe = train_df
            else:
                self.dataframe = valid_df
        else:
            if self.mode == 'train':
                self.dataframe = pd.read_csv(str(train_csv_path))
            else:
                self.dataframe = pd.read_csv(str(valid_csv_path))
                
                
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
            self.dataframe = self.dataframe[self.dataframe['text'].apply(is_single_words)]
        
        
    def _filter_outside_image_box(self):
        def exclude_box_outside_image_size(rows):
            stats = False
            bbox = [int(p) for p in rows['bbox'].split(",")]
            xmin, ymin, xmax, ymax = bbox
    
            w, h, d = rows['image_dim'].split(",")
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
    
        
        
    def _load_xml2dict(self, path):
        data = None
        with open(path, 'r') as file:
            data = xmltodict.parse(file.read())
        return data
    
    def _load_xml_files_to_dataframe(self, dataset_path):
        xml_files = list(dataset_path.glob("*.xml"))
        data = {
            'uindex': [], 'image_path': [], 'image_dim': [],
            'bbox': [], 'text': [], 'text_type': [],
        }
        for idx in tqdm(range(len(xml_files))):
            xml_file = xml_files[idx]
            xml_data = self._load_xml2dict(xml_file)
            img_name = xml_data['annotation']['filename']
            impath = self.root.joinpath('dataset').joinpath(img_name)
            if impath.exists():
                uindex = img_name.split("_")[0]

                img_dim = xml_data['annotation']['size']
                h, w = int(img_dim["height"]), int(img_dim["width"])
                img_dim = f'{img_dim["width"]},{img_dim["height"]},{img_dim["depth"]}'
#                 print(img_dim)

                objects = xml_data['annotation']['object']

                for obj in objects:
                    objbox = obj["bndbox"]
                    bbox = f'{objbox["xmin"]},{objbox["ymin"]},{objbox["xmax"]},{objbox["ymax"]}'
                    box_list = [int(p) for p in bbox.split(",")]
                    xmin, ymin, xmax, ymax = box_list
                    if 0<=xmin<=w and 0<=ymin<=h and 0<=xmax<=w and 0<=ymax<=h and xmax-xmin>0 and ymax-ymin>0:
                        text = obj['name']
                        if len(text)<=1:
                            text_type = 'char'
                        else:
                            text_type = 'word'

                        data['uindex'].append(uindex)
                        data['image_path'].append(img_name)
                        data['image_dim'].append(img_dim)
                        data['bbox'].append(bbox)
                        data['text'].append(text)
                        data['text_type'].append(text_type)


        df = pd.DataFrame(data)

        return df
    
    
    def _split_dataset(self, main_df):
        word_df = main_df[main_df['text_type']=='word']
        word_df.reset_index(drop=True, inplace=True)

        char_df = main_df[main_df['text_type']=='char']
        char_df.reset_index(drop=True, inplace=True)
        
        if self.filter_by=="word":
            choosed_df = word_df
        elif self.filter_by=="char":
            choosed_df = word_df
        else:
            choosed_df = main_df


        X = choosed_df[['uindex','image_path','image_dim','bbox']]
        y = choosed_df[['text','text_type']]

        X_train, X_valid, y_train, y_valid = train_test_split(
            X, y, 
            test_size=self.val_size, 
            random_state=self.random_state
        )

        train_df = X_train.copy()
        train_df['text'] = y_train['text'].to_list()
        train_df['text_type'] = y_train['text_type'].to_list()
        train_df.reset_index(drop=True, inplace=True)
        

        valid_df = X_valid.copy()
        valid_df['text'] = y_valid['text'].to_list()
        valid_df['text_type'] = y_valid['text_type'].to_list()
        valid_df.reset_index(drop=True, inplace=True)
        
        return train_df, valid_df
    
    
    def _load_data(self, idx):
        data = self.dataframe.iloc[idx]
        bbox = [int(p) for p in data['bbox'].split(",")]
        xmin, ymin, xmax, ymax = bbox
        
        text = data['text']
        
        img_fname = data['image_path']
        impath = self.root.joinpath('dataset').joinpath(img_fname)
        return str(impath), bbox, text
    
    
    def _load_image(self, path):
        image = cv.imread(path)
        image = cv.cvtColor(image, cv.COLOR_BGR2RGB)
        return image
    
    def _crop_image(self, image, box):
        xmin, ymin, xmax, ymax = box
        croped = image[ymin:ymax, xmin:xmax].copy()

        image = Image.fromarray(croped)
        image = image.convert("RGB")
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
        impath, box, text = self._load_data(idx)
        image = self._load_croped_image(impath, box)
        
        if not self.is_sensitive:
            text = text.lower()
        
        if self.transform:
            image = self.transform(image)
        
        return image, text