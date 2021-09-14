from tensorflow.keras.callbacks import History
from typing import List
from matplotlib import pyplot as plt


def plot_metric(history: History, metric: str, save_path: str = ""):
    """
    将train和validation的history数据绘制出来
    history.history中key为"loss"、"auc"的list存储的是训练集上的指标
    而key为"val_loss"和"val_auc"的list存储的是验证集上的指标
    """
    fig = plt.figure()
    train_metrics: List[float] = history.history[metric]
    val_metrics: List[float] = history.history.get("val_" + metric)
    epochs = range(1, len(train_metrics) + 1)
    plt.plot(epochs, train_metrics, "bo--")  # 蓝色描点虚线连接
    title = "Training"
    legend = ["train_" + metric]
    if val_metrics:
        plt.plot(epochs, val_metrics, "ro-")  # 红色描点实线连接
        title += " and validation "
        legend.append("val_" + metric)
    plt.title(f"{title} {metric}")
    plt.xlabel("Epochs")
    plt.ylabel(metric)
    plt.legend(legend)  # list的元素与前面多条plot语句所绘制内容对应
    plt.show()
    if save_path:
        fig.savefig(save_path)
        print(f"图像已保存在: {save_path}")
