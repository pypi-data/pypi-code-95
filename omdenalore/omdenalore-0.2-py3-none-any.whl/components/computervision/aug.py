import cv2
import albumentations as A
from albumentations.pytorch import ToTensorV2


def get_basic_train_transforms(height: int, width: int, means: list, stds: list):
    """
    Apply only basic training transformations such as Resize and Normalize.

    :param height: int specifying new height
    :param width: int specifying new width
    :param means: List of means for normalization
    :param stds: List of stds for normalization
    :returns: Albumentation compose transform object for training dataset
    """
    trn_transform = A.Compose(
        [
            A.Resize(height, width, cv2.INTER_NEAREST),
            A.Normalize(mean=means, std=stds),
            ToTensorV2(),
        ]
    )
    return trn_transform


def get_mild_train_transforms(height: int, width: int, means: list, stds: list):
    """
    Apply few mild training transformations such as Resize, horizontal and vertical, Gaussian Noise,
    Perspective Shift and Normalize.

    :param height: int specifying new height
    :param width: int specifying new width
    :param means: List of means for normalization
    :param stds: List of stds for normalization
    :returns: Albumentation compose transform object for training dataset
    """
    trn_transform = A.Compose(
        [
            A.Resize(height, width, cv2.INTER_NEAREST),
            A.HorizontalFlip(p=0.5),
            A.VerticalFlip(p=0.5),
            A.GaussNoise(p=0.2),
            A.Perspective(p=0.5),
            A.Normalize(mean=means, std=stds),
            ToTensorV2(),
        ]
    )
    return trn_transform


def get_val_transforms(height: int, width: int, means: list, stds: list):
    """
    Apply only basic transformation such as Resize and Normalize.
    :param height: int specifying new height
    :param width: int specifying new width
    :param means: List of means for normalization
    :param stds: List of stds for normalization
    :returns: Albumentation compose transform object for validation dataset
    """
    val_transform = A.Compose(
        [
            A.Resize(height, width, cv2.INTER_NEAREST),
            A.Normalize(mean=means, std=stds),
            ToTensorV2(),
        ]
    )
    return val_transform
