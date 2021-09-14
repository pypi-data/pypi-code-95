from ..transforms import transforms as PT
from .pair import PairDataset
from .midv import MIDV500Dataset
from .label_studio import SegmentDataset

# import torch.utils.data as data, ConcatDataset
from torch.utils.data import ConcatDataset, DataLoader


train_tmft = PT.PairCompose([
    PT.PairResize((256, 256)),
    PT.PairRandomRotation(20),
#     PT.PairGrayscale(),
    PT.PairToTensor(),
])

valid_tmft = PT.PairCompose([
    PT.PairResize((256, 256)),
#     PT.PairGrayscale(),
    PT.PairToTensor(),
])


def get_transforms(mode='train'):
    if mode=='train':
        tmft = train_tmft
    else:
        tmft = valid_tmft
        
    return tmft


def pair_data_loader(root_path, mode='train', 
                     batch_size=24, shuffle=True, num_workers=16):

    tmft = get_transforms(mode=mode)
    dset = PairDataset(root=root_path, pair_transform=tmft, mode=mode)
    dloader = DataLoader(dset, batch_size=batch_size, shuffle=shuffle, 
                              num_workers=num_workers)
    
    return dloader, dset
    
def concat_data_loader(root_pair, root_midv=None, root_segment=None, mode='train', 
                       batch_size=24, shuffle=True, num_workers=16):
    
    tmft = get_transforms(mode=mode)
    dataset_list = []
    portrait_pair_dataset = PairDataset(root=root_pair, glob_base="portrait/*/", mode=mode, pair_transform=tmft)
    landscape_pair_dataset = PairDataset(root=root_pair,  glob_base="landscape/*/", mode=mode, pair_transform=tmft)
    dataset_list.append(portrait_pair_dataset)
    dataset_list.append(landscape_pair_dataset)

    if root_midv:
        midv_dataset = MIDV500Dataset(root=root_midv, mode=mode, pair_transform=tmft)
        dataset_list.append(midv_dataset)
        
    if root_segment:
        segment_dataset = SegmentDataset(root=root_segment, mode=mode, pair_transform=tmft)
        dataset_list.append(segment_dataset)
        
    dataset = ConcatDataset(dataset_list)
    
    data_loader = DataLoader(dataset, batch_size=batch_size, 
                             shuffle=shuffle, num_workers=num_workers)
    
    return data_loader, dataset
    