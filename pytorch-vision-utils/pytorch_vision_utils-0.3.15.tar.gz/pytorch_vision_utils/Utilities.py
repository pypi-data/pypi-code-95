import numpy as np 
import matplotlib.pyplot as plt
import seaborn as sns
import torch
import json
import os
import hashlib
import random
import copy

from mdutils.mdutils import MdUtils
from datetime import datetime
from PIL import Image
from statistics import mean

from sklearn.metrics import confusion_matrix, classification_report, roc_curve, auc
from sklearn.model_selection import StratifiedKFold
from sklearn.preprocessing import OneHotEncoder, LabelEncoder

from torch import nn, optim
from torchvision.transforms.functional import to_tensor
from torchvision import datasets, transforms, models
from torchvision.utils import save_image
from torch.utils.data import DataLoader, Dataset
from tqdm.auto import tqdm

# from .CustomModels import AlexNetWrapper, DenseNetWrapper, InceptionV3Wrapper, MobileNetV2Wrapper
# from .CustomModels import ResNetWrapper, SqueezeNetWrapper, VGGWrapper, XceptionWrapper
# from .CustomModels import MobileNetV2Wrapper, XceptionWrapper, get_avail_models

from .CustomModels import avail_models

# from torchvision.models import alexnet
# from torchvision.models import densenet121, densenet161, densenet169, densenet201
# from torchvision.models import inception_v3
# from torchvision.models import resnet18, resnet34, resnet50, resnet101, resnet152
# from torchvision.models import squeezenet1_0, squeezenet1_1
# from torchvision.models import vgg11, vgg11_bn, vgg13, vgg13_bn, vgg16, vgg16_bn, vgg19, vgg19_bn
  
sns.set_theme()


### Helpful functions that can be used throughout ###
def get_timestamp():
    '''Creates a timestamp, typically useful for generating unique file names for models and images.
    '''
    now = datetime.now()
    timestamp = now.strftime("%d.%m.%Y %H:%M:%S,%f")
    return timestamp



def build(params="parameters.json"):
    """
    Creates all of the necessary directories.

    Parameters
    ----------
    `params` : `str`\n
        String representation of the path to the json file containing the necessary parameters, by default `"parameters.json"`
    """    
    with open(params, "r") as f:
        print("Loading parameters...\n")
        params_ = dict(json.load(f))
        
        DATA_DIR = params_["DATA_DIR"]
        TEST_DIR = params_["TEST_DIR"]
        MODEL_DIR = params_["MODEL_DIR"]
        MEDIA_DIR = params_["MEDIA_DIR"]
        INC_DIR = params_["INC_DIR"]
          
    DIRS = [DATA_DIR, TEST_DIR, MODEL_DIR, MEDIA_DIR, INC_DIR]
    
    for dirs in DIRS:
        clear_dirs(dirs)
        print("Creating:", dirs)
        os.makedirs(dirs, exist_ok=True)
       


def reload_models(model:nn.Module, model_dir:str, folder_name:str, device="cuda", debug=False) -> list:
    '''Reloads multiple models based on a directory passed through. Useful for quickly loading directories 
    
    Parameters
    ----------
    `model` : `nn.Module`\n
        The model.
    `model_dir` : `str`\n
        Path to the directory.
    `folder_name` : `str`\n
        Name of the folder.
    `device` : `str`, `optional`\n
        String representation of the GPU core to use or the CPU, by default "cuda".
    `debug` : `bool`, `optional`\n
        Boolean indicating whether to print out debugging information or not.

    
    Returns
    -------
    `models` : `list`\n
        List of all the saved models in evaluation mode.
    
    '''
    
    models = []

    print('Reading in models...')
    path = os.path.join(model_dir, folder_name)
    for i, (subdir, dirs, files) in enumerate(os.walk(path)):
        if not files:
            continue

        for f in files:
            if debug:
                print(f'Reading {f}')
                
            model = model.to(device)
            model.load_state_dict(state_dict=torch.load(subdir+'/'+f)['model_state_dict'])
            model.eval()
            models.append(model)

    return models


def clear_dirs(dir:str):
    '''Clears out files in a directory. 
    
    Parameters
    ----------
    `dir` : `str`\n
        Path to the directory
            
    '''
    
    walk = list(os.walk(dir))
    walk.sort()
    for i, (subdir, dirs, files) in enumerate(walk):
        if not files:
            continue
        
        for f in files:
            os.remove(subdir+"/"+f)
            

def create_fold_dirs(target_dir:str, dir_names:list):
    '''Creates fold directories.
    
    Parameters
    ----------
    `target_dir` : `str`\n
        String representation of the path to the directory.
    `dir_names` : `list`\n
        List of the subdirectory names.
    
    '''
    
    for d in dir_names:
        try:
            os.makedirs(target_dir+'/'+d)
        except FileExistsError:
            continue
    
        
def create_fold_names(model_name:str, n_splits=5) -> list:
    """
    List comprehension that creates the folder names.

    Parameters
    ----------
    `model_name` : `str`\n
        Model name.
    `n_splits` : `int`, `optional`\n
        Number of splits used for kfold cross validation, by default 5

    Returns
    -------
    `list`\n
        Returns a list of all the folder names.
    """    
    
    return [f"{model_name}_fold_{idx}" for idx in range(1, n_splits+1)]

            
def remove_outliers(data:list, constant=1.5):
    """
    Removes outliers from a given dataset. Must be numerical.

    Parameters
    ----------
    `data` : `list`\n
        List of the data points.
    `constant` : `float`, `optional`\n
        Constant used for determining an outlier using the IQR, by default 1.5.

    Returns
    -------
    `ndarray`\n
        ndarray of data with outliers removed.
        
    """    
    
    data.sort()
    upper_quartile = np.percentile(data, 75, interpolation="nearest")
    lower_quartile = np.percentile(data, 25, interpolation="nearest")
    iqr = upper_quartile - lower_quartile
    l_outlier = lower_quartile - (constant * iqr)
    u_outlier = upper_quartile + (constant * iqr)
    data_clean = [d for d in data if d >= l_outlier and d <= u_outlier]
  
    return np.array(data_clean)


def time_to_predict(model:nn.Module, loader:DataLoader, constant=1.5, device="cuda") -> list:
    """
    Calculates the time to predict on a dataset and removes outliers.

    Parameters
    ----------
    `model` : `nn.Module`\n
        The model.
    `loader` : `DataLoader`\n
        Dataloader with the images to predict on.
    `constant` : `float`, `optional`\n
        Constant used for determining an outlier using the IQR, by default 1.5.
    `device` : `str`, `optional`\n
        String representation of the GPU core to use or the CPU, by default "cuda".

    Returns
    -------
    `list`\n
        Prints some information about the deltas distribution and returns a list of the deltas
    """    
    
    deltas = []
        
    for images, labels in tqdm(loader, desc="Predicting...".title()):
        images = images.to(device, dtype=torch.float)
        labels = labels.to(device, dtype=torch.long)
        start = datetime.now()
        model(images).to(device, dtype=torch.long) # we don't care about the output
        end = datetime.now()
        delta = (end - start).total_seconds() * 1000
        deltas.append(delta)

    deltas = remove_outliers(deltas)
        
    print(f'\nNumber of Predictions:{len(deltas)}\tClassification Time Mean: {np.mean(deltas):.4f}ms\tClassification Time Max: {np.max(deltas):.4f}ms\tClassification Time Min: {np.min(deltas):.4f}ms')
    return deltas


def random_sampling(dataset:dict, num_of_images=1000) -> list:
    """
    Does a random oversampling of the `dataset` to balance all of the classes.

    Parameters
    ----------
    `dataset` : `dict`\n
        Dict representation of the dataset.
    `num_of_images` : `int`, `optional`\n
        Number of images for each class, will repopulate the other classes proportionally, by default 1000.

    Returns
    -------
    `list`\n
        Returns a list 
    """    

    balanced_data = list()
    num_of_classes = len(dataset.keys())
    for i in range(num_of_classes):
        num_of_additional_imgs = num_of_images - len(dataset[i])
        for j in range(num_of_additional_imgs):
            dataset[i].append(random.choice(dataset[i]))
            
        balanced_data += dataset[i]

    return balanced_data



class CustomDataset(Dataset):
    
    def __init__(self, train_utils, mode="train"):
        """
        Extending class of `torchvision`'s `Dataset` abstract class.

        Attributes
        ----------
        `TODO`
        
        Parameters
        ----------
        `train_utils`\n
            Training Utilities instance.
        `mode` : `str`, `optional`\n
            String representation of whether we're testing/validating or training, by default "train".
        """        
        
        super(Dataset, self).__init__()
        folds, X, y, ids = train_utils.split_data_and_create_folds()
        self.folds = folds
        self.X = X
        self.y = y
        self.ids = ids
        self.train_transform = train_utils.train_transform
        self.test_transform = train_utils.test_transform
        self.mode = mode
        self.selected_item = ()
        

    def __getitem__(self, index):
        item = self.X[index]
        label = self.y[index]
        item = transforms.ToPILImage()(item)
            
        if self.mode == "train":
            ret = (self.train_transform(item), label) if self.train_transform else (item, label)
            
        elif self.mode == "test":
            ret = (self.test_transform(item), label) if self.test_transform else (item, label)
        
        self.selected_item = (self.ids[index], ret) # (filename, picture)
        return ret

        
    def set_mode(self, new_mode:str):
        """
        Changes the mode to either 'train' or 'test'.

        Parameters
        ----------
        `new_mode` : `str`\n
            String representation of the new mode.
            
        Raises
        ------
        `TypeError`\n
            If `new_mode` is not either 'train' or 'test'
        """   
        if new_mode != "train" and new_mode != "test":
            raise TypeError("Invalid string entered. Must be either 'train' or 'test'.")
            return
            
        self.mode = new_mode


    def __len__(self):
        return len(self.X)

  
class DataVisualizationUtilities:
    
    def __init__(self, device=""):
        """
        This class serves as a collection of helpful functions when working with `torchvision` and image data in general.

        Attributes
        ----------
        `device` : str\n
            String representation of the GPU core to use or the CPU
        
        """                
        self.device = torch.device(device) if device else torch.device("cuda" if torch.cuda.is_available() else "cpu")
    
    
    def _im_convert(self, tensor, mean=(0.485, 0.456, 0.406), std=(0.229, 0.224, 0.225)) -> np.ndarray:
        """
        Private function for converting an image so it can be displayed using matplotlib functions properly.

        Parameters
        ----------
        `tensor`\n
            Tensor represention of image data.
        `mean` : `tuple` or `list`, `optional`\n
            Mean of the data; used for de-normalization of the image, by default (0.485, 0.456, 0.406).
        `std` : `tuple` or `list`, `optional`\n
            Standard deviation of the data; used for de-normalaztion of the image, by default (0.229, 0.224, 0.225).

        Returns
        -------
        `ndarray`\n
            Returns ndarry de-normalizazed representation of an image.
        """        
        
        image = tensor.clone().detach().numpy()
        image = image.transpose(1, 2, 0)
        image = image * np.array(std) + np.array(mean) # [0, 1] -> [0, 255]
        image = image.clip(0, 1)
        return image
    

    def display_dataset(self, train_utils):
        """
        Displays the dataset. Useful for making sure your data was loaded properly.

        Parameters
        ----------
        `train_utils`\n
            TrainingUtilities instance.
        """        
        
        print(train_utils.mode)
        dataiter = iter(train_utils.loader)
        images, labels = dataiter.next()
        print(images.shape)
        fig = plt.figure(figsize=(25, 4))

        for idx in np.arange(min(train_utils.batch_size, 20)):
            ax = fig.add_subplot(2, 10, idx+1, xticks=[], yticks=[])
            plt.imshow(self._im_convert(images[idx], mean=train_utils.mean, std=train_utils.std))
            ax.set_title(train_utils.classes[labels[idx].numpy()])

                
    
    def display_metric_results(self, fold:int, train_utils, figsize=(7, 7), img_dir="./incorrect_images", media_dir="./media"):
        """
        Displays classification report and confusion matrix.

        Parameters
        ----------
        `fold` : `int`\n
            Number representing the current fold during k-fold cross validation.
        `train_utils`\n
            TrainingUtilities instance.
        `figsize` : `tuple`, `optional`\n
            Tuple representing the dimensions of the figure in inches, by default (7, 7).
        `img_dir` : `str`, `optional`\n
            String representation of the path to the incorrect images directory, by default "./incorrect_images".
        `media_dir` : `str`\n
            String representation of the path to the media directory.
            
        """        
        
        with torch.no_grad():
            y_pred, y_true = train_utils.get_predictions(fold, img_dir=img_dir)
            
        # y_true = torch.tensor(y_true).to(self.device, dtype=torch.long).clone().detach()
        xticks = yticks = train_utils.classes
        
        print("Classification Report\n")
        clr = classification_report(y_true.cpu(), y_pred.argmax(dim=1).cpu(), target_names=xticks)
        print(clr)
        train_utils.md_file.new_line("### Classification Report [{}]".format(fold))
        train_utils.md_file.insert_code(str(clr))
        print("Confusion Matrix")
        cnf_mat = confusion_matrix(y_true.cpu(), y_pred.argmax(dim=1).cpu())

        # plot
        plt.figure(figsize=figsize)
        sns.heatmap(cnf_mat, 
                    xticklabels=xticks, 
                    yticklabels=yticks, 
                    annot=True, 
                    cmap="Blues_r", 
                    fmt=".4g", 
                    linewidths=1)
        
        plt.ylabel('Ground Truth')
        plt.xlabel('Predictions')
        return plt
        
        
        
    def display_results(self, loss:float, acc:float, val_loss:float, val_acc:float, title:str, figsize=(7, 7)):
        """
        Displays the accuracy and loss training results.

        Parameters
        ----------
        `loss` : `float`\n
            Training loss.
        `acc` : `float`\n
            Training accuracy.
        `val_loss` : `float`\n
            Validation loss.
        `val_acc` : `float`\n
            Validation accuracy.
        `title` : `str`\n
            Title of the graph.
        `figsize` : `tuple`, `optional`\n
            Tuple representing the dimensions of the figure in inches, by default (7, 7).
            
        """        
            
        plt.figure(figsize=figsize)
        plt.subplot(2, 1, 1)

        plt.plot(acc, label='Training Accuracy', color='blue')
        plt.plot(val_acc, label='Validation Accuracy', color='lightseagreen')
        plt.legend(loc='lower right')
        plt.ylabel('Accuracy')
        plt.ylim([0, 1.2])
        plt.title('Training and Validation Accuracy '+ title)

        y_upper_bound = max(max(loss), max(val_loss))
        plt.subplot(2, 1, 2)
        plt.plot(loss, label='Training Loss', color='blue')
        plt.plot(val_loss, label='Validation Loss', color='lightseagreen')
        plt.legend(loc='upper right')
        plt.ylabel('Cross Entropy')
        plt.ylim([0, y_upper_bound+y_upper_bound*0.2])
        plt.title('Training and Validation Loss '+ title)
        plt.xlabel('epoch')
        return plt
        
        
    def display_benchmark_results(self, pred_times1, pred_times2, model_name1:str, model_name2:str, figsize=(7, 7), shade=True, 
                                  legend=True, bw_adjust=5, color1="blue", color2="purple"):
        """
        Displays benchmark prediction times.

        Parameters
        ----------
        `pred_times1` : `list` or `ndarray`\n
            Collection of predicition times for the first model for comparison.
        `pred_times2` : `list` or `ndarray`\n
            Collection of predicition times for the second model for comparison.
        `model_name1` : `str`\n
            First model name.
        `model_name2` : `str`\n
            Second model name.
        `figsize` : `tuple`, `optional`\n
            Tuple representing the dimensions of the figure in inches, by default (7, 7).
        `shade` : `bool`, `optional`\n
            Boolean representing whether to shade in the figure or not, by default True.
        `legend` : `bool`, `optional`\n
            Boolean representing whether to show the legend or not, by default True.
        `bw_adjust` : `int`, `optional`\n
            Number representing the width of the line in pixels, by default 5.
        `color1` : `str`, `tuple`, `list`\n
            Structured representation of the color for model 1, by default "blue".
        `color2` : `str`, `optional`\n
            Structured representation of the color for model 2, by default "purple".
        """        
        
        plt.figure(figsize=(7, 7))
        x_max = max(max(pred_times1), max(pred_times2))
        sns.kdeplot(x=pred_times1, color=color1, shade=shade, label=model_name1, bw_adjust=bw_adjust)
        sns.kdeplot(x=pred_times2, color=color2, shade=shade, label=model_name2, bw_adjust=bw_adjust)
        
        plt.xlabel('Time (ms)')
        plt.xlim([0, x_max+x_max*0.3])
        plt.title(f'Benchmark Results')
        plt.legend(loc="upper right")
        plt.show()
        # return plt

        
    def display_roc_curve(self, fold:int, train_utils, figsize=(7, 7)):
        """
        Displays ROC curve.

        Parameters
        ----------
        `fold` : int\n
            Number representing the current fold during k-fold cross validation.
        `train_utils` : `TrainingUtilities`\n
            TrainingUtilities instance.
        `figsize` : `tuple`, `optional`\n
            Tuple representing the dimensions of the figure in inches, by default (7, 7).
        """        
        
        with torch.no_grad():
            y_pred, y_true = train_utils.get_predictions(fold, img_dir="")
            y_pred, y_true = y_pred.argmax(dim=1).cpu().clone().detach(), torch.tensor(y_true).cpu().clone().detach()
        
        fpr, tpr, thresholds = roc_curve(y_pred, y_true)
        roc_auc = auc(fpr, tpr)
        
        plt.title('ROC Results for {}'.format(train_utils.model_name.title()))
        plt.figure(figsize=figsize)
        plt.plot(fpr, tpr, linewidth=2, label=train_utils.model_name + f" area: {roc_auc:.4f}", color='blue')
        plt.plot([0, 1], [0, 1], 'k--')
        plt.axis([0, 1, 0, 1])
        plt.xlim([-0.02, 1.0])
        plt.ylim([0.0, 1.05])
        plt.xlabel("False Positive Rate")
        plt.ylabel("True Positive Rate")
        plt.legend(loc="lower right")
        
        return plt


class TrainingUtilities:
    
    def __init__(self, data_dir:str, model_dir:str, model_name:str, device="", parameters_path="parameters.json", mode="train"):
        """
        Useful functions for training PyTorch models. Providing a `/path/to/parameters.json` is required to work properly, assumed to be in
        the project directory. Encapsulates all of the hyperparameter tuning into one convenient class to toy with by hand or automate by 
        creating json file.\n
        CAUTION: Currently in flux constantly, check back often for any documentation updates.

        Attributes
        ----------
        `TODO`

        Parameters
        ----------
        `data_dir` : `str`\n
            String representation of the path to the directory containing the classes.
        `model_dir` : `str`\n
            String representation of the path to the directory of which to save the models.
        `model_name` : `str`\n
            Name of the model.
        `device` : `str`, `optional`\n
            String representation of the device to train on, by default ""
        `parameters_path` : `str`, `optional`\n
            String representation of the path to the "parameters.json" file, by default "parameters.json".
        `mode` : `str`, `optional`\n
            String representation of the mode of training, by default "train"
        """  
        
        self.data_dir = data_dir
        self.model_dir = model_dir
        self.parameters_path = parameters_path
        self.device = torch.device(device) if device else torch.device("cuda" if torch.cuda.is_available() else "cpu")     
        self.model = nn.Module().to(device=self.device)
        self.md_file = None
        
        # VARIABLE INITIALIZATION
        self.model_name = model_name
        self.classes = []
        self.batch_size = 0
        self.eta = 0
        self.patience = 0
        self.crop_size = 0
        self.degrees = 0
        self.hue = 0
        self.saturation = 0
        self.contrast = 0
        self.brightness = 0
        self.monitor = ""
        self.min_delta = float("inf")
        self.lr_patience = 0
        self.factor = 0
        self.n_splits = 0
        self.input_size = []
        self.mean = []
        self.std = []
        self.train_transform = None
        self.test_transform = None
        self.dataset = None
        self.loader = None
        self.mode = mode
        
        
        
    def set_model_parameters(self,  model_name:str, mode="train", debug=False):
        """
        Switches the model parameters based on which model architecture in use and whether we are training
        or testing. 

        Parameters
        ----------
        `model_name` : `str`\n
            Model name.
        `mode` : `str`, `optional`\n
            String representation of the mode of training, by default "train"
            
        Raises
        ------
        `TypeError`\n
            Raised when there `new_mode` is neither "train" or "test".
            
        """    
        if mode != "train" and mode != "test":
            raise TypeError("Invalid string entered. Must be either 'train' or 'test'.")
            return    
        
        with open(self.parameters_path, "r") as f:
            json_file = json.load(f)
            self.classes = json_file["CLASSES"]
            self.n_splits = json_file["N_SPLITS"]
            settings = json_file[model_name]
            
        print(settings)

        # HYPERPARAMETERS
        self.model_name = model_name
        self.batch_size = settings["BATCH_SIZE"]
        self.eta = settings["ETA"]
        self.patience = settings["PATIENCE"]
        self.crop_size = settings["CROP_SIZE"]
        self.degrees = settings["DEGREES"]
        self.hue = settings["HUE"]
        self.saturation = settings["SATURATION"]
        self.contrast = settings["CONTRAST"]
        self.brightness = settings["BRIGHTNESS"]
        self.monitor = settings["MONITOR"]
        self.min_delta = settings["MIN_DELTA"]
        self.lr_patience = settings["LR_PATIENCE"]
        self.factor = settings["FACTOR"]
        self.input_size = settings["INPUT_SIZE"]
        self.mean = settings["MEAN"]
        self.std = settings["STD"]
        self.mode = mode
        
        self.model = self._set_model(self.model_name, debug).to(self.device)
            
        self.train_transform = transforms.Compose([transforms.Resize(self.input_size),
                                                   transforms.ColorJitter(hue=self.hue, brightness=self.brightness,
                                                                          saturation=self.saturation, contrast=self.contrast),
                                                    transforms.CenterCrop(self.crop_size),
                                                    transforms.RandomRotation(degrees=self.degrees),
                                                    transforms.RandomPerspective(p=1.0), # we always want a bit of distortion
                                                    transforms.ToTensor(),
                                                    transforms.Normalize(mean=self.mean, std=self.std)])
        
        self.test_transform = transforms.Compose([transforms.Resize(self.input_size),
                                                  transforms.CenterCrop(self.crop_size),
                                                  transforms.ToTensor(),
                                                  transforms.Normalize(mean=self.mean, std=self.std)])
                                        
        self.dataset = CustomDataset(self, mode=self.mode)
        self.loader = self.create_loader(self.dataset, batch_size=self.batch_size, shuffle=True)
        
        self.md_file = MdUtils(file_name='media/report_{}.md'.format(self.model_name),title='{} Results'.format(self.model_name.title()))
    
        
    def set_test_transform(self, new_transform:transforms.Compose):
        """
        Sets the test transform.

        Parameters
        ----------
        `new_transform` : `transforms.Compose`\n
            The new transform to be used.
        """        
        self.test_transform = new_transform
        
    
    def set_mode(self, new_mode:str):
        """
        Sets the mode for both the TrainingUtilities instance, but also the CustomDataset.

        Parameters
        ----------
        `new_mode` : `str`\n
            String representation of the new mode.
        
        Raises
        ------
        `TypeError`\n
            Raised when there `new_mode` is neither "train" or "test".
            
        """   
        
        if new_mode != "train" and new_mode != "test":
            raise TypeError("Invalid string entered. Must be either 'train' or 'test'.")
            return
         
        self.mode = new_mode
        self.loader.dataset.mode = new_mode


    def _set_model(self, model_name:str, debug=False):
        """
        Changes the model based on a given name.

        Parameters
        ----------
        `model_name` : `str`\n
            The new model name.
            
        Raises
        ------
        `ValueError`\n
            Raised when there is an unrecognized `model_name`.
        """     
        model = avail_models[model_name](num_classes=len(self.classes))
        if debug:
            print(model)
            
        return model


    def reload_weights(self, model_name:str, model_weights_path:str, mode="train", debug=False):
        """
        Reloads a model with specific weights. Used for continuing training after some sort of interruption

        Parameters
        ----------
        `model_name` : `str`\n
            Model name.
        `model_weights_path` : `str`\n
            String representation to the model weights path.
        `mode` : `str`, `optional`\n
            String representation of the new mode, by default "test".
        """        
        
        weights = torch.load(model_weights_path)["model_state_dict"]
        self.set_model_parameters(model_name, mode=mode, debug=debug)
        self.model.load_state_dict(weights)


    def load_weights(self, model_name:str, model_weights_path:str, mode="test", debug=False):
        """
        Loads a model with specific weights. Used for testing.

        Parameters
        ----------
        `model_name` : `str`\n
            Model name.
        `model_weights_path` : `str`\n
            String representation to the model weights path.
        `mode` : `str`, `optional`\n
            String representation of the new mode, by default "test".
        """        
        
        weights = torch.load(model_weights_path)["model_state_dict"]
        self.set_model_parameters(model_name, mode=mode, debug=debug)
            
        self.model.load_state_dict(weights)
        self.model.eval()
        print("Model in eval mode.")
        

    def create_loader(self, dataset:Dataset, batch_size:int, shuffle=True) -> DataLoader:
        """
        Creates loader given a dataset.

        Parameters
        ----------
        `dataset` : `Dataset`\n
            Custom Dataset.
        `batch_size` : `int`\n
            Batch size.
        `shuffle` : `bool`, `optional`\n
            Boolean representing whether to shuffle the data or not, by default True.

        Returns
        -------
        `DataLoader`\n
            DataLoader with the correct setting for training.
        """        
        return torch.utils.data.DataLoader(dataset, batch_size=batch_size, shuffle=shuffle)
    

    def to_categorical(self) -> OneHotEncoder:
        """
        Converts the labels from names to integers.

        Returns
        -------
        `OneHotEncoder`\n
            A one-hot encoded scikit-learn object.
        """        
        
        labels = np.array(self.classes)
        label_encoder = LabelEncoder()
        integer_encoded = label_encoder.fit_transform(labels)
        
        onehot_encoder = OneHotEncoder(sparse=False)
        integer_encoded = integer_encoded.reshape(len(integer_encoded), 1)
        return onehot_encoder.fit_transform(integer_encoded)
        
    
    def split_data_and_create_folds(self) -> tuple:
        """
        Creates dataset and creates splits for k-fold cross validation.

        Returns
        -------
        `tuple`\n
            Returns a tuple containing a list fold indices, ndarray representation of the input image, ndarray of the ground-truth
            classification, and an ndarray containing the id's for each input image.\n
            NOTE: Keep in mind the negative class will not always be `0` using this function, will have to possibly be revised
        """        
        
        X = [] # inputs
        y = [] # outputs
        ids = []

        walk = list(os.walk(self.data_dir))
        walk.sort()
        for i, (subdir, dirs, files) in enumerate(walk):
            if not files:
                continue

            print(f'Creating {subdir}...')
            for f in files:
                ids.append(f"{i-1}_{files[:-4]}")
                img = Image.open(subdir+'/'+f)
                img = img.resize(size=self.input_size)
                img = img.convert('RGB')
                img = np.asarray(img)
                X.append(img)
                y.append(i-1)

        print(f'{len(X)} total images loaded')
        folds = list(StratifiedKFold(n_splits=self.n_splits, shuffle=True).split(X, y))
        return folds, np.array(X), np.array(y), np.array(ids)
    
    
    def _loop_fn(self, dataset:Dataset, loader:DataLoader, criterion, optimizer, ascii_=False) -> tuple:
        """
        The function that actually does the loop for training. Likely isn't used directly, refer to the `train` or `_train` function.

        Parameters
        ----------
        `dataset` : `Dataset`\n
            The custom dataset.
        `loader` : `DataLoader`\n
            The dataloader.
        `criterion`\n
            The loss function.
        `optimizer`\n
            The optimization function.
        `ascii_` : `bool`, `optional`\n
            Boolean representation of the ascii mode, by default False.

        Returns
        -------
        `tuple`\n
            Returns a tuple containing the average cost and accuracy of a given batch.
        """        
        
        if self.mode == "train":
            self.model.train()
        elif self.mode == "test":
            self.model.eval()

        cost = correct = 0
        for feature, target in tqdm(loader, ascii=ascii_, desc=self.mode.title()):
            feature, target = feature.to(self.device, dtype=torch.float32), target.to(self.device, dtype=torch.long)
            output = self.model(feature)
            loss = criterion(output, target)
            self.model.metric = loss
            
            if self.mode == "train":
                loss.backward()
                optimizer.step()
                optimizer.zero_grad()

            cost += loss.item() * feature.shape[0]
            correct += (output.argmax(1) == target).sum().item()

        cost = cost / len(dataset)
        acc = correct / len(dataset)
        return cost, acc
        
    
    @torch.no_grad() # https://deeplizard.com/learn/video/0LhiS6yu2qQ
    def get_predictions(self, fold, img_dir) -> tuple:
        """
        Gets all of the predictions. Useful for determining model performance.

        Parameters
        ----------
        `fold` : int\n
            Number representing the current fold during k-fold cross validation.
        `img_dir` : `str`\n
            String representation of the path to the incorrect image directory.

        Returns
        -------
        `tuple`\n
            Returns a tuple containing the model predictions and the ground truths.
        """        
        
        y_pred = torch.tensor([]).to(self.device, dtype=torch.long)
        y_true = torch.tensor([]).to(self.device, dtype=torch.long)
        
        for images, labels in self.loader:
            images = images.to(self.device, dtype=torch.float32)
            labels = labels.to(self.device, dtype=torch.long)
            target = labels.to(self.device, dtype=torch.long).cpu().numpy()[0]
            
            pred = self.model(images).to(self.device, dtype=torch.long)
            y_pred = torch.cat((y_pred, pred), dim=0)
            y_true = torch.cat((y_true, labels), dim=0)
            
            corrects = (labels == pred.argmax(1))
            for idx, is_correct in enumerate(corrects.cpu().numpy()):
                if img_dir and not is_correct:
                    tensor_img = transforms.ToTensor()(DataVisualizationUtilities()._im_convert(tensor=images[idx].cpu(), mean=self.mean, std=self.std))
                    
                    hash_ = hashlib.sha256(get_timestamp().encode('utf-8')).hexdigest()[:5]
                    save_image(tensor_img, img_dir+f"/{self.model_name}_fold_{fold}/{hash_}_{labels[idx]}.png")
                                     
        return y_pred, y_true
            
            
    def add_plot_to_md(self, title:str, plot_name:str, extension=".jpg"):
        """
        Adds a plot to the report markdown.

        Parameters
        ----------
        `title` : `str`\n
            The title for the plot
        `plot_name` : `str`\n
            The name of the plot
        """      
          
        self.md_file.new_line("### {}".format(title.title()))
        self.md_file.new_paragraph("![{}]({}{} \"{}\")".format(plot_name, "./"+plot_name, extension, plot_name))
    
    
    def _outer_loop(self, fold:int, model_dir: str, model_path: str, inc_path: str, show_graphs: bool, dry_run: bool) -> tuple:
        train_idx, test_idx = self.dataset.folds[fold]
        train_dataset = torch.utils.data.Subset(self.dataset, train_idx)
        test_dataset = torch.utils.data.Subset(self.dataset, test_idx)
        
        train_dataset.transform = self.train_transform
        test_dataset.transform = self.test_transform
        
        criterion = nn.CrossEntropyLoss()
        optimizer = torch.optim.Adam(self.model.parameters(), lr=self.eta)
        lr_scheduler = torch.optim.lr_scheduler.ReduceLROnPlateau(optimizer, mode='min', factor=self.factor, patience=self.lr_patience, verbose=True)
        return self._train(train_dataset, test_dataset, model_path, criterion, optimizer, fold+1, ascii_=True, scheduler=lr_scheduler, 
                                dry_run=dry_run, show_graphs=show_graphs, inc_path=inc_path)
    
    
    def train(self, model_name:str, model_path:str, inc_path:str, media_dir:str, show_graphs=True, dry_run=True, debug=False, max_epoch=1000) -> tuple:
        """
        Wrapper function for the actual training method. Will likely be edited in the future to be more customizable.

        Parameters
        ----------
        `model_name` : `str`\n
            Model name.
        `model_path` : `str`\n
            String representation of the path to the model checkpoint path.
        `inc_path` : `str`\n
            String representation of the path to the incorrect images path.
        `media_dir` : `str`\n
            String representation of the path to the media directory.
        `show_graphs` : `bool`, `optional`\n
            Boolean representing whether or not to display graphs, by default True.
        `dry_run` : `bool`, `optional`\n
            Boolean representing whether we're training to evaluate hyperparameter tuning or training the model for model comparisons, by default True.
        `max_epoch` : `int`, `optional`\n
            Integer representing the maximum number of epochs to train the model for, by default 1000.

        Returns
        -------
        `tuple`\n
            Returns a tuple containing the average loss and average accuracy.

        """        
        self.set_model_parameters(model_name=model_name, debug=debug)
        
        dir_names = create_fold_names(self.model_name, n_splits=self.n_splits)
        create_fold_dirs(inc_path, dir_names)
        losses = []
        accuracies = []
        
        # `dry_run=True` means that we're doing k-fold cross validation and to not save any of the models
        if dry_run:
            for fold, (train_idx, test_idx) in enumerate(self.dataset.folds):
                print('\nFold ', fold+1)
                loss, acc = self._outer_loop(fold=fold, model_dir=self.model_dir, model_path=model_path, 
                                             inc_path=inc_path, show_graphs=show_graphs, dry_run=dry_run)
                
                losses.append(loss)
                accuracies.append(acc)
                self._set_model(model_name=self.model_name, debug=debug) # creates a new instance of the model
                self.md_file.new_line()
          
        # `dry_run=False` means we're training this model to actually be used         
        else:
            fold = 0
            loss, acc = self._outer_loop(fold=fold+1, model_dir=self.model_dir, model_path=model_path, 
                                            inc_path=inc_path, show_graphs=show_graphs, dry_run=dry_run)

            losses.append(loss)
            accuracies.append(acc)
            
        avg_loss = mean(losses)
        avg_acc = mean(accuracies)
        
        results = f'Average Loss: {avg_loss:.5f}  |  Average Accuracy: {avg_acc:.5f}'
        print(results)
        
        self.md_file.new_paragraph("`{}`".format(results))
        self.md_file.create_md_file()
        return avg_loss, avg_acc
    
    
    def _generate_graphs(self, fold: int, early_stopping, media_dir: str, inc_path: str,
                        train_total_loss: list, train_total_acc: list, val_total_loss: list,
                        val_total_acc: list, show_graphs: bool):
        
        # RESULTS GRAPH
        results = "results_graph_{}_{}".format(self.model_name, fold)
        results_graph = DataVisualizationUtilities().display_results(train_total_loss, train_total_acc, val_total_loss, val_total_acc, 
                                                                     title=early_stopping.model_name)
        results_graph.savefig(media_dir+results+".jpg", dpi=300)
        self.add_plot_to_md("Training and Validation Results [{}]".format(fold), results)
        
        
        # METRICS GRAPH
        metrics = "metrics_graph_{}_{}".format(self.model_name, fold)
        metrics_graph = DataVisualizationUtilities().display_metric_results(fold=fold, train_utils=self, img_dir=inc_path)
        metrics_graph.savefig(media_dir+metrics+".jpg", dpi=300)
        self.add_plot_to_md("Confusion Matrix [{}]".format(fold), metrics)
        
        
        # ROC GRAPH
        roc = "roc_graph_{}_{}".format(self.model_name, fold)
        roc_graph = DataVisualizationUtilities().display_roc_curve(0, train_utils=self)
        roc_graph.savefig(media_dir+roc+".jpg", dpi=300)
        self.add_plot_to_md("ROC Curve [{}]".format(fold), roc)
    
    
        # DISPLAY GRAPHS
        if show_graphs:
            results_graph.show()
            metrics_graph.show()
            roc_graph.show()
    
    
    # https://stackoverflow.com/questions/58996242/cross-validation-for-mnist-dataset-with-pytorch-and-sklearn
    def _train(self, train_dataset:Dataset, test_dataset:Dataset, filepath:str, criterion, optimizer, fold:int, max_epoch=1000, 
               scheduler=None, shuffle=True, ascii_=False, show_graphs=True, dry_run=False, inc_path="incorrect_images/", media_dir="media/") -> tuple:
        """Does the actual training. Implements early stopping and some debugging.
        """        
        
        early_stopping = EarlyStopping(model_path=filepath, model_name=self.model_name, fold=fold, min_delta=self.min_delta)
        train_total_loss = []
        train_total_acc = []
        val_total_loss = []
        val_total_acc = []
        test_loader = self.create_loader(test_dataset, batch_size=self.batch_size, shuffle=shuffle)
        train_loader = self.create_loader(train_dataset, batch_size=self.batch_size, shuffle=shuffle)
            
        epoch = 1
        for e in range(max_epoch):
            print(f'\nEpoch {fold}.{epoch}')
            self.set_mode("train")
            train_cost, train_score = self._loop_fn(train_dataset, train_loader, criterion, optimizer, ascii_=ascii_)
            with torch.no_grad():
                self.set_mode("test")
                test_cost, test_score = self._loop_fn(test_dataset, test_loader, criterion, optimizer, ascii_=ascii_)
                
            if scheduler:
                scheduler.step(test_cost)
                
            train_total_loss.append(train_cost)
            train_total_acc.append(train_score)
            val_total_loss.append(test_cost)
            val_total_acc.append(test_score)
                
            es_counter = early_stopping.checkpoint(self.model, epoch, test_cost, test_score, optimizer, dry_run=dry_run)
            print(f'\nTrain Loss: {train_cost:.3f}   | Train Acc: {train_score:.4f}  | Val Loss: {test_cost:.3f}   | Val Acc: {test_score:.4f}')
            print(f'Early Stopping Patience at: {es_counter}')
                
            if es_counter == self.patience:
                
                self.model.eval()
                self._generate_graphs(fold=fold, early_stopping=early_stopping, 
                                     media_dir=media_dir, inc_path=inc_path,
                                     train_total_loss=train_total_loss, train_total_acc=train_total_acc,
                                     val_total_loss=val_total_loss, val_total_acc=val_total_acc, 
                                     show_graphs=show_graphs)
                    
                break
            
            epoch += 1

        return early_stopping.min_loss, early_stopping.max_acc
    
         
                
class EarlyStopping():
    
    def __init__(self, model_path:str, model_name:str, fold:int, min_delta=0):
        """
        Class for early stopping, because only plebs rely on set amounts of epochs.
        
        Attributes
        ----------
        `TODO`

        Parameters
        ----------
        `model_name` : `str`\n
            Model name.
        `fold` : `int`\n
            Number representing the current fold.
        `min_delta` : `int`, `optional`\n
            Smallest number the given metric needs to change in order to count as progress, by default 0.
        """        
        
        self.min_loss = float('inf')
        self.max_acc = -float('inf')
        self.min_delta = min_delta
        self.model_name = model_name 
        self.path = str(os.path.join(model_path, self.model_name+'.pth'))
        self.count = 0
        self.first_run = True
        self.best_model = None
        
        
    def checkpoint(self, model:nn.Module, epoch:int, loss:float, acc:float, optimizer, dry_run=False) -> int:
        """
        Creates the checkpoint and keeps track of when we should stop training. You can choose whether or not you'd like to save the model based on the `dry_run` parameter.
        
        Parameters
        ----------
        `model` : `nn.Module`\n
            The model to be saved.
        `epoch` : `int`\n
            Number representing the current epoch.
        `loss` : `float`\n
            Current loss.
        `acc` : `float`\n
            Current accuracy.
        `optimizer`
            The optimization function currently in use.
        `dry_run` : `bool`, `optional`\n
            Boolean representing whether we're training to evaluate hyperparameter tuning or training the model for comel comparisons, by default True.

        Returns
        -------
        `int`\n
            Returns a number representing the current level of patience reached.
        """        
        
        print(f'Loss to beat: {(self.min_loss - self.min_delta):.4f}')
        if (self.min_loss - self.min_delta) > loss or self.first_run:
            self.first_run = False
            self.min_loss = loss
            self.max_acc = acc
            self.best_model = model
            self.count = 0
            if not dry_run:
                torch.save({'epoch': epoch,
                            'model_state_dict': model.state_dict(),
                            'optimizer_state_dict': optimizer.state_dict(),
                            'loss': loss,}, self.path)
            
        else:
            self.count += 1
            
        return self.count
   
             