import pathlib
from pathlib import Path
import pandas as pd
import numpy as np
import cv2 as cv
import json 
import PIL
import PIL.Image as Image
import torch
from torch.utils.data import Dataset


class SegmentDataset(Dataset):
    def __init__(self, root, mode='train', valid_size=0.2, json_file='anno.json',
                 image_transform=None, pair_transform=None, mask_transform=None):
        super(SegmentDataset, self).__init__()
        self.root: Path = pathlib.Path(root)
        self.json_file = json_file
        self.valid_size = valid_size
        self.mode = mode
        self.image_transform = image_transform
        self.pair_transform = pair_transform
        self.mask_transform = mask_transform
        
        self._load_files()
        self._train_test_split()
        
    def _json2dict(self, path):
        with open(path, 'r') as f:
            data = json.load(f)
        return data
        
    def _load_files(self):
        self.anno_list = self._json2dict(self.root.joinpath(self.json_file))
        
        
    def _train_test_split(self):
        np.random.seed(1261)
        data_len = len(self.anno_list)
        valid_len = int(self.valid_size * data_len)
        
        indices = [i for i in range(data_len)]
        valid_indices = sorted(np.random.choice(indices, valid_len))
        train_indices = list(set(indices) - set(valid_indices))
        
        self.annoset = []
        if self.mode == "train":
            for idx in train_indices:
                self.annoset.append(self.anno_list[idx])
        else:
            for idx in valid_indices:
                self.annoset.append(self.anno_list[idx])
                
        
    def _create_mask_from_annoset(self, annoset):
        ow = annoset['label'][0]['original_width']
        oh = annoset['label'][0]['original_height']
        points = annoset['label'][0]['points']
        
        points = np.array(points)
        points[:,0] = (points[:,0] * ow) / 100
        points[:,1] = (points[:,1] * oh) / 100
        points = points.astype(np.int)
        
        mask_canvas = np.zeros((oh,ow), dtype=np.uint8)
        mask = cv.fillPoly(mask_canvas, pts=[points], color=(255))
        mask = cv.threshold(mask, 0, 255, cv.THRESH_BINARY)[1]
        
        return mask
        
    def _load_image_from_annoset(self, annoset):
        img_rel_path = annoset['image']
        img_path = self.root.joinpath(img_rel_path)
        image = cv.imread(str(img_path))
        image = cv.cvtColor(image, cv.COLOR_BGR2RGB)
        return image
    
    def _load_data(self, idx):
        annoset = self.annoset[idx]
        image = self._load_image_from_annoset(annoset)
        mask = self._create_mask_from_annoset(annoset)

        image = Image.fromarray(image).convert("RGB")
        mask = Image.fromarray(mask).convert("L")
        return image, mask
    
    def get_annoset(self, idx):
        return self.annoset[idx]
    
    def get_image_path(self, idx):
        img_rel_path = self.annoset[idx]['image']
        img_path = str(self.root.joinpath(img_rel_path))
        return img_path
    
        
    def __len__(self):
        return len(self.annoset)
    
    
    def __getitem__(self, idx):
        image, mask = self._load_data(idx)

        if self.image_transform:
            image = self.image_transform(image)

        if self.pair_transform:
            image, mask = self.pair_transform(image, mask)

        if self.mask_transform:
            mask = self.mask_transform(mask)

        return image, mask
