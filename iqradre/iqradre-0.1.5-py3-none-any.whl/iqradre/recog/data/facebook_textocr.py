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

class FacebookTextOCRDataset(Dataset):
    def __init__(self, root, mode='train', transform=None, **kwargs):
        super(FacebookTextOCRDataset, self).__init__()
        self._init_default_attrs(**kwargs)
        self.root: Path = Path(root)
        self.mode: str = mode
        self.json_file: str = self._json_filename(mode)
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
        image_dirname = self._image_dirname(self.mode)
        self.workpath = self.root.joinpath(image_dirname)
    
    def _build_dataframe(self):
        anno_fname = self._json_filename(self.mode)
        anno_path = self.root.joinpath(anno_fname)
        
        mainframe = self._convert_json2dframe(str(anno_path))
        mainframe = mainframe[mainframe['label']!='.']
        
        if self.mode == 'train':
            self.dataframe = mainframe[mainframe['mode']=='train']
        else:
            self.dataframe = mainframe[mainframe['mode']=='val']
            
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
            box = boxes_ops.xywh2xymm(rows['bbox'], to_int=True)
            xmin,ymin,xmax,ymax = box
            w, h = rows['image_size'].split(",")
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
            
    def _convert_json2dframe(self, path):
        main_dict = self._load_json(path)
        image_data = main_dict['imgs']
        image_keys = list(image_data.keys())

        anno_data = main_dict['anns']
        anno_keys = list(anno_data.keys())

        data = {
            'image_id': [], 'anno_id': [], 'image_path': [], 'image_size': [],
            'mode': [], 'points':[], 'bbox': [], 'label': [], 'area': [], 
        }

        for idx in range(len(anno_keys)):
            anno_id = anno_keys[idx]
            anno_row = anno_data[anno_id]

            img_id = str(anno_row['image_id'])
            img_row = image_data[img_id]

            img_fname = img_row['file_name'].split('/')[-1]

            mode_set = img_row['set']
            img_size = f'{img_row["width"]},{img_row["height"]}'

            points = anno_row['points']

            bbox = boxes_ops.xywh2xymm(anno_row['bbox'], to_int=True)
            label = anno_row['utf8_string']
            area = anno_row['area']

            data['image_id'].append(img_id)
            data['anno_id'].append(anno_id)
            data['image_path'].append(img_fname)
            data['image_size'].append(img_size)
            data['mode'].append(mode_set)
            data['bbox'].append(bbox)
            data['points'].append(points)
            data['label'].append(label)
            data['area'].append(area)

        df = pd.DataFrame(data)
        return df
        
    def _json_filename(self, mode):
        if not (mode == 'train' or mode == 'valid' or mode =='test'):
            raise Exception('Only train, valid and test values are accepted for mode!')
        
        if mode == 'valid': mode = 'val'
        fname = f'TextOCR_0.1_{mode}.json'
        return fname
    
    def _image_dirname(self, mode):
        if mode == 'train' or mode == 'valid':
            return 'trainval_images'
        elif mode == 'test':
            return 'test_images'
        else:
            raise Exception('Only train, valid and test values are accepted for mode!')
    
    def _load_json(self, path):
        data = None
        with open(path, 'r') as file:
            data = json.load(file)
        return data
    
    def _load_image(self, path):
        image = cv.imread(path)
        image = cv.cvtColor(image, cv.COLOR_BGR2RGB)
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
    

    def _load_data(self, idx):
        data = self.dataframe.iloc[idx]
        impath, box, label = data['image_path'], data['bbox'], data['label']
        impath = self.workpath.joinpath(impath)
#         print(impath, impath.exists())
        return str(impath), box, label
    
        
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
    