"""This modul provides custom PyTorch datasets on V1 cortex neural response to stimuli
as presented by Lurz et al. 2021: 
GENERALIZATION IN DATA-DRIVEN MODELS OF PRIMARY VISUAL CORTEX"""

import pathlib
import numpy as np
import torch
from torch.utils.data import Dataset

path_assertation_message = 'pathlib Path object was expected as data_dir input'

class Lurz2020DatasetSubset(Dataset):
    """Map-style mouse V1 dataset of stimulus (images) and neural response (average number of spikes)
    as presented by Lurz et al. 2020: 
    GENERALIZATION IN DATA-DRIVEN MODELS OF PRIMARY VISUAL CORTEX.
    Contains:
    Data for one scans (nine) in one animal (mouse) from one session (five):
        inputs: 5993 images (64x36) as *.npy file
        responses: 5993 responses of 5335 neurons each as *.npy file
    ...
    Attributes
    -----------
    data_dir (pathlib Path): Path to data directory
    transform (callable, optional): Optional transforms to be applied to sample
    ...
    Methods
    -------
    get_neuroncount():
        returns number of neurons observed in specified region
    """
    def __init__(self, data_dir, transform = None):
        """
        Args
        ----
        data_dir (pathlib Path): Path to data directory
        transform (callable, optional): Optional transforms to be applied to sample
        """
        assert isinstance(data_dir, pathlib.PurePath), path_assertation_message
        self.data_dir = data_dir
        self.image_dir = data_dir/'static20457-5-9-preproc0'/'data'/'images'
        self.response_dir = data_dir/'static20457-5-9-preproc0'/'data'/'responses'
        self.pupil_center_dir = data_dir/'static20457-5-9-preproc0'/'data'/'pupil_center'
        self.behavior = data_dir/'static20457-5-9-preproc0'/'data'/'behavior'
        self.transform = transform

    def __len__(self):
        return 5993 #subset session five scan_idx nine consists of 5993 images

    def __getitem__(self,idx):
        """
        Args
        ----
        idx (int): index of item to get
        ...
        Returns
        sample (touple): touple of image and the corresponding response tensor
        """
        if torch.is_tensor(idx):
            idx = idx.tolist()
        image = np.load(self.image_dir/f'{idx}.npy').reshape(36,64,1) #reshape to image representation without channel
        label = torch.tensor(np.load(self.response_dir/f'{idx}.npy'))
        if self.transform:
            image = self.transform(image)
        sample = (image, label)
        return sample  

    def get_neuroncount(self):
        return 5335 # in subset session five scan_idx nine 5335 responses are measured for each image
