import numpy as np
import scipy.stats


def ei(x, model, params):
    """
    Expected improvement acquisition function

    Doesn't take any parameters (apart from the model).
    """

    minacq = np.min(model.Y)
    m, v = model.predict(np.atleast_2d(x), noise=False)
    s = np.sqrt(v)
    dmdx, dvdx = model.predict_grads(np.atleast_2d(x))
    dmdx = dmdx[:, :, 0]
    z = (minacq - m) / s
    phi = scipy.stats.norm.pdf(z)
    Phi = scipy.stats.norm.cdf(z)
    f_acqu = -s * (z * Phi + phi)
    df_acqu = dmdx * Phi - dvdx / (2 * s) * phi
    scipygradient = np.asmatrix(df_acqu).transpose()
    return f_acqu, scipygradient
