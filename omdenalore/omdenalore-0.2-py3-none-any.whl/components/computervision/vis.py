import numpy as np
from sklearn import metrics
import seaborn as sns
import matplotlib.pyplot as plt


def plot_cm(true, preds, classes: list, figsize: tuple = (8, 6)):
    """
    Plot unnormalized confusion matrix

    :param true: List of targets
    :param preds: List of predictions
    :param classes: List of classes
    :param figsize: Tuple specifying (height, width)
    :returns: matplotlib figure containing confusion matrix
    """
    cm = metrics.confusion_matrix(true, preds)
    fig = plt.figure(figsize=figsize)
    sns.heatmap(
        cm,
        xticklabels=classes,
        yticklabels=classes,
        annot=True,
        fmt="d",
        cmap="Blues",
        vmin=0.2,
    )
    plt.title("Confusion Matrix")
    plt.ylabel("True Class")
    plt.xlabel("Predicted Class")
    return fig


def unnormalize_image(img, means, stds):
    """
    Convert normalized image to get unnormalized image

    :param img: Tensor of shape (C, H, W)
    :param means: List of means used for normalization
    :param stds: List of stds used for normalization
    :returns: the unnormalized input tensor which can be used to display image
    """
    img = img.numpy()
    img = np.transpose(img, (1, 2, 0))
    # unnormalize
    img = img * np.array(stds) + np.array(means)
    return img


def plot_hist(history):
    """
    Plotting train acc, loss and val acc and loss stored in history dict.
    History dict contains keys = {train_acc, val_acc, train_loss, val_loss}
    Each key contains list of scores for every epoch.

    :param history: Dict
    :returns: plot the loss and acc plots for train and val
    """
    # summarize history for accuracy
    plt.plot(history["train_acc"])
    plt.plot(history["val_acc"])
    plt.title("model accuracy")
    plt.ylabel("accuracy")
    plt.xlabel("epoch")
    plt.legend(["train", "val"], loc="upper left")
    plt.show()
    # summarize history for loss
    plt.plot(history["train_loss"])
    plt.plot(history["val_loss"])
    plt.title("model loss")
    plt.ylabel("loss")
    plt.xlabel("epoch")
    plt.legend(["train", "val"], loc="upper left")
    plt.show()
