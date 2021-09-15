import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.metrics import roc_curve, roc_auc_score, recall_score
from scipy import stats
from scipy.integrate import cumtrapz


def roc_auc_plot(
    model,
    X_tst,
    y_tst,
):
    ns_probs = [0 for _ in range(len(y_tst))]
    ns_auc = roc_auc_score(y_tst, ns_probs)
    pred_prob = model.predict_proba(X_tst)
    lr_probs = pred_prob[:, 1]
    lr_auc = roc_auc_score(y_tst, lr_probs)
    print("ROC AUC: %.3f" % (lr_auc))
    ns_fpr, ns_tpr, _ = roc_curve(y_tst, ns_probs)
    lr_fpr, lr_tpr, _ = roc_curve(y_tst, lr_probs)
    plt.plot(ns_fpr, ns_tpr, linestyle="--", label="No Skill")
    plt.plot(lr_fpr, lr_tpr, marker=".", label="model")
    plt.xlabel("False Positive Rate")
    plt.ylabel("True Positive Rate")
    plt.legend()
    plt.show()

    return lr_auc


def ks_2sample_plot(model, X, y, bins=None):
    y_prob = model.predict_proba(X)[:, 1]

    df = pd.DataFrame({"prob": y_prob, "y": y})
    dist_bad = df.loc[df["y"] == 1, "prob"]
    dist_good = df.loc[df["y"] == 0, "prob"]
    data_bad = dist_bad.sort_values()
    data_good = dist_good.sort_values()
    n_bad = len(data_bad)
    n_good = len(data_good)
    x_bad = np.linspace(0, 1, n_bad)
    x_good = np.linspace(0, 1, n_good)
    cdf_bad = cumtrapz(x=x_bad, y=data_bad)
    cdf_good = cumtrapz(x=x_good, y=data_good)
    cdf_bad = cdf_bad / max(cdf_bad)
    cdf_good = cdf_good / max(cdf_good)
    fig, ax = plt.subplots(ncols=1)
    ax1 = ax.twinx()
    ax.hist(data_bad, histtype="stepfilled", alpha=0.4, density=True, bins=bins)
    ax.hist(data_good, histtype="stepfilled", alpha=0.4, density=True, bins=bins)
    ax1.plot([0] + list(data_bad[1:]) + [1], [0] + list(cdf_bad) + [1], label="Bads")
    ax1.plot([0] + list(data_good[1:]) + [1], [0] + list(cdf_good) + [1], label="Goods")
    ax1.grid(True)
    ax1.legend(loc="right")
    ax1.set_title("Distributions of Bads and Goods (model)")
    ax.set_xlabel("Predict Prob")
    ax.set_ylabel("Probability Desnsity")
    plt.show()

    return stats.ks_2samp(dist_bad, dist_good)
