import pathlib
import pandas as pd
import numpy as np
import cv2 as cv
import json 
import PIL
import PIL.Image as Image
import torch
from torch.utils.data import Dataset
from sklearn.model_selection import train_test_split


class MIDVDataset(Dataset):
    def __init__(self, root, mode='train', valid_size=0.2,
                 image_glob="*/images/*/*.tif", gt_glob='*/ground_truth/*/*.json',
                 image_transform=None, pair_transform=None, mask_transform=None):
        super(MIDVDataset, self).__init__()
        self.root = pathlib.Path(root)
        self.image_glob = image_glob
        self.gt_glob = gt_glob
        self.valid_size = valid_size
        self.mode = mode
        self.image_transform = image_transform
        self.pair_transform = pair_transform
        self.mask_transform = mask_transform
        
        self._load_files()
        self._create_dataframe()
        self._train_test_split()
        
    
    def _load_files(self):
        self.image_files = sorted(list(self.root.glob(self.image_glob)))
        self.gtruth_files = sorted(list(self.root.glob(self.gt_glob)))
    
    def _create_dataframe(self):
        names, categories, image_fpath, gtruth_fpath = [],[],[],[]
        for (impath, gtpath) in zip(self.image_files, self.gtruth_files):
            if impath.stem == gtpath.stem:
                names.append(impath.stem)
                catname = "_".join(impath.parent.parent.parent.name.split("_")[1:])
                categories.append(catname)
                image_fpath.append(str(impath))
                gtruth_fpath.append(str(gtpath))

        data = {
            'name': names,
            'category': categories,
            'image_files': image_fpath,
            'gtruth_files': gtruth_fpath
        }

        self.dataframe = pd.DataFrame(data)
    
    def _train_test_split(self):
        train, valid = train_test_split(self.dataframe, test_size=self.valid_size, random_state=1261)
        train.reset_index(drop=True, inplace=True)
        valid.reset_index(drop=True, inplace=True)
        self.trainframe = train
        self.validframe = valid
        
        if self.mode == 'train':
            self.dframe = self.trainframe
        elif self.mode == 'valid':
            self.dframe = self.validframe
        else:
            raise Exception('mode supported only "train" or "valid"')
        
    
    def __len__(self):
        return len(self.dframe)
    
    def _load_image_mask(self, idx):
        impath = self.dframe['image_files'].iloc[idx]
        gtpath = self.dframe['gtruth_files'].iloc[idx]
        
        image = cv.imread(impath)
        image = cv.cvtColor(image, cv.COLOR_BGR2RGB)
        mask = np.zeros(image.shape[:2], dtype=np.uint8)
        
        # mask preprocessing
        jsdata = json.load(open(gtpath, 'r'))
        coords = np.array(jsdata['quad'], dtype=np.int32)
        cv.fillPoly(mask, coords.reshape(-1, 4, 2), color=(255))
        mask = cv.threshold(mask, 0,255, cv.THRESH_BINARY)[1]
        
        image = Image.fromarray(image).convert("RGB")
        mask = Image.fromarray(mask).convert("L")
        return image, mask
        
    
    def __getitem__(self, idx):
        image, mask = self._load_image_mask(idx)
        
        if self.image_transform:
            image = self.image_transform(image)
            
        if self.pair_transform:
            image, mask = self.pair_transform(image, mask)
            
        if self.mask_transform:
            mask = self.mask_transform(mask)
        
        return image, mask
    

class MIDV500Dataset(MIDVDataset):
    def __init__(self, root, mode='train', valid_size=0.2,
             image_glob="*/images/*/*.tif", gt_glob='*/ground_truth/*/*.json',
             image_transform=None, pair_transform=None, mask_transform=None):
        super(MIDV500Dataset, self).__init__(root=root, mode=mode, valid_size=valid_size,
                                            image_glob=image_glob, gt_glob=gt_glob,
                                            image_transform=image_transform,
                                            pair_transform=pair_transform,
                                            mask_transform=mask_transform)

class MIDV2019Dataset(MIDVDataset):
    def __init__(self, root, mode='train', valid_size=0.2,
             image_glob="images/*/*.tif", gt_glob='ground_truth/*/*.json',
             image_transform=None, pair_transform=None, mask_transform=None):
        super(MIDV2019Dataset, self).__init__(root=root, mode=mode, valid_size=valid_size,
                                            image_glob=image_glob, gt_glob=gt_glob,
                                            image_transform=image_transform,
                                            pair_transform=pair_transform,
                                            mask_transform=mask_transform)