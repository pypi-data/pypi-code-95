import numpy as np


def elcb(x, model, params):
    """GP-Lower Confidence Bound acquisition function with increasing exploration.

    Doesn't take any parameters (apart from the model).
    The exploration weight is given by

    explr_weight = sqrt( 2*log[ ( i^((dim/2) + 2)*pi^(2) ) / ( 3*0.1 ) ] )

    The implementation is based on the following papers

    (1) N. Srinivas, A. Krause, S. M. Kakade, and M. Seeger.  Gaussian process optimization
    in the bandit setting: No regret and experimental design. Proc. ICML, 2010

    (2) E. Brochu, V. M. Cora, and N. de Freitas. A tutorial on Bayesian optimization of expensive
    cost functions, with application to active user modeling and hierarchical reinforcement learning.
    arXiv:1012.2599, 2010.

    where the delta parameter introduced in Brochu et al. has been set to 0.1.
    """
    ndata = model.X.shape[0]
    dim = model.X.shape[1]
    upstairs = (ndata ** ((dim / 2.0) + 2.0)) * (np.pi ** 2.0)
    downstairs = 3 * 0.1
    explr_weight = np.sqrt(2 * np.log10(upstairs / downstairs))

    m, s, dmdx, dsdx = model.predict_mean_sd_grads(x)
    f_acqu = m - explr_weight * s
    df_acqu = dmdx - explr_weight * dsdx
    scipygradient = np.asmatrix(df_acqu).transpose()
    return f_acqu, scipygradient
