"""Main module."""
import pathlib

import matplotlib as mpl
import matplotlib.pyplot as plt

import torch
import torchvision
import src.datasets.antolik_2016 as antolik
import src.datasets.lurz_2021 as lurz

seed = 1
batch_size = 32

ds_lu = lurz.Lurz2020DatasetSubset(
    data_dir=pathlib.Path.cwd()/'datasets'/'Lurz2020',
    transform=torchvision.transforms.ToTensor(),
)

ds_al = antolik.Antolik2016Dataset(
    data_dir=pathlib.Path.cwd()/'datasets'/'Antolik2016',
    region='region1',
    transform=torchvision.transforms.ToTensor(),
)

ds = ds_lu

train_set, validation_set, test_set = torch.utils.data.random_split(
    dataset=ds, 
    lengths = [int(round(len(ds)*0.8,0)),int(round(len(ds)*0.05,0)),int(round(len(ds)*0.15,0))],
    generator = torch.Generator().manual_seed(seed),
    )

if __name__ == '__main__':  

    train_dataloader = torch.utils.data.DataLoader(
        dataset = train_set,
        batch_size = batch_size,
        shuffle = False, #default
        drop_last = False, #default
        )
    
    validation_dataloader = torch.utils.data.DataLoader(
        dataset = validation_set,
        batch_size = batch_size,
        shuffle = False, #default
        drop_last = False, #default
        )
    
    test_dataloader = torch.utils.data.DataLoader(
        dataset = test_set,
        batch_size = batch_size,
        shuffle = False, #default
        drop_last = False, #default
        )

    for X, y in test_dataloader:
        print("Shape of X [N, C, H, W]: ", X.shape)
        print("Shape of y: ", y.shape, y.type)
        break

    