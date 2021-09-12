import numpy as np


def lcb(x, model, params):
    """
    GP-Lower Confidence Bound acquisition function with increasing exploration

    Takes one parameter: the exploration weight.
    """

    explr_weight = params[0]
    m, s, dmdx, dsdx = model.predict_mean_sd_grads(x)
    f_acqu = m - explr_weight * s
    df_acqu = dmdx - explr_weight * dsdx
    scipygradient = np.asmatrix(df_acqu).transpose()
    return f_acqu, scipygradient
