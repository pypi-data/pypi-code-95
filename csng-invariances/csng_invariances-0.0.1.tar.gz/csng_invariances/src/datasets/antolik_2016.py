"""This modul provides custom pytorch datasets on V1 cortex neural response to stimuli
as presented by Antolik et al. 2016: 
Model Constrained by Visual Hierarchy Improves Prediction of Neural Responses to Natural Scenes"""

import pathlib
import numpy as np
import torch
from torch.utils.data import Dataset

path_assertation_message = 'pathlib Path object was expected as data_dir input'

# map-style datasets

class Antolik2016Dataset(Dataset):
    """Map-style mouse V1 dataset of stimulus (images) and neural response (average number of spikes) 
    as prensented in Antolik et al. 2016: 
    Model Constrained by Visual Hierachy Improves Prediction of Neural Responses to Natural Scenes.
    Contains:
    Data for three regions in two animals (mice):
        training_inputs: n images (31x31) as *.npy file
        training_set: m neural responses as *.npy file
        validation_inputs: 50 images (31x31) as *.npy file
        validation_set: m neural responses as *.npy file
    ...
    Attributes
    -----------
    data_dir (pathlib Path): Path to data directory
    region (string): region to examine
        options: 'region1', 'region2', 'region3'
    dataset_type (string, default = 'training'): dataset type
        options: 'training', 'validation'
    transform (callable, optional): Optional transforms to be applied to sample
    ...
    Methods
    -------
    get_neuroncount():
        returns number of neurons observed in specified region
    """
    def __init__(self, data_dir, region, dataset_type = 'training', transform = None):
        """
        Args
        ----
        data_dir (pathlib Path): Path to data directory
        region (string): region to examine
            options: 'region1', 'region2', 'region3'
        dataset_type (string, default = 'training'): dataset type
            options: 'training', 'validation'
        transform (callable, optional): Optional transforms to be applied to sample
        """
        assert isinstance(data_dir, pathlib.PurePath), path_assertation_message
        assert dataset_type in ['training','validation'], 'dataset_type should be one of "training", "validation"'
        assert region in ['region1','region2','region3'], 'region should be one of "region1", "region2", "region3"'
        self.data_dir = data_dir
        self.region = region
        self.training_sets = np.load(self.data_dir/self.region/'training_set.npy')
        self.training_inputs = np.load(self.data_dir/self.region/'training_inputs.npy')
        self.training_inputs = self.training_inputs.reshape(self.training_inputs.shape[0],31,31,1) #reshape to image representation (n, h,w,c)
        self.validation_sets = np.load(self.data_dir/self.region/'validation_set.npy')
        self.validation_inputs = np.load(self.data_dir/self.region/'validation_inputs.npy').reshape(50,31,31,1)
        self.dataset_type = dataset_type
        self.transform = transform

    def __len__(self):
        if self.dataset_type == 'training':
            length = self.training_sets.shape[0]
        else:
            length = 50 #validation set size always 50
        return length

    def __getitem__(self,idx):
        """
        Args
        ----
        idx (int): index of item to get
        ...
        Returns
        sample (touple): touple of image and label tensor
        """
        if torch.is_tensor(idx):
            idx = idx.tolist()
        if self.dataset_type == 'training':
            image = self.training_inputs[idx,:,:]
            label = torch.tensor(self.training_sets[idx,:])
        else:
            image = self.validation_inputs[idx,:,:]
            label = torch.tensor(self.validation_sets[idx,:])
        if self.transform:
            image = self.transform(image)
        sample = (image, label)
        return sample

    def get_neuroncount(self):
        """
        Returns
        -------
        neuroncount (int): number of neurons observed in the specific dataset
        """
        if self.dataset_type == 'training':
            neuroncount = self.training_sets.shape[1]
        else:
            neuroncount = self.validation_sets.shape[1]
        return neuroncount
