"""
    Script for training a model.
"""
import argparse
import numpy as np
import matplotlib.pyplot as plt
import torch
import os
import seaborn as sns
import random
import json

from datetime import datetime
from PIL import Image
from statistics import mean
from torch import nn, optim
from torchvision import datasets, transforms, models
from torch.utils.data import DataLoader, Dataset
from tqdm import tqdm
# from pretrainedmodels.models.xception import Xception
# from pretrainedmodels.models.mobilenetv2 import MobileNetV2
from pytorch_vision_utils.Utilities import DataVisualizationUtilities, TrainingUtilities



##################### D E F A U L T S #####################

parser = argparse.ArgumentParser(description="Picks which model we're going to train.")
parser.add_argument("-m", "--model_name", type=str)
parser.add_argument("-p", "--parameters_path", type=str)
parser.add_argument("-d", "--debug", type=str)
args = parser.parse_args().__dict__
MODEL_NAME = args["model_name"] # "xception"
PARAMS = args["parameters_path"]
DEBUG = "True" == args["debug"]


# DIRECTORY NAMES
with open(PARAMS, "r") as f:
    print("Loading parameters...\n")
    params = dict(json.load(f))
    
    DATA_DIR = params["DATA_DIR"]
    TEST_DIR = params["TEST_DIR"]
    MODEL_DIR = params["MODEL_DIR"]
    MEDIA_DIR = params["MEDIA_DIR"]
    INC_DIR = params["INC_DIR"]
    
    print("Loading parameters complete!")
    print(MODEL_DIR)
    print(TEST_DIR)
    print(MEDIA_DIR)
    print(DATA_DIR)

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
print("Using: ", device)

train_utils = TrainingUtilities(data_dir=DATA_DIR, model_dir=MODEL_DIR, device=device, parameters_path=PARAMS, model_name=MODEL_NAME)
dataviz_utils = DataVisualizationUtilities()



##################### T R A I N I N G #####################

if __name__ == "__main__":
    loss, acc = train_utils.train(model_name=MODEL_NAME, model_path=MODEL_DIR, inc_path=INC_DIR, media_dir=MEDIA_DIR, show_graphs=False, dry_run=False, debug=DEBUG)
    

