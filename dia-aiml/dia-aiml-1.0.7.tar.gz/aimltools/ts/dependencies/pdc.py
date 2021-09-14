import numpy as np
from scipy.stats import wasserstein_distance
import math

def find_position(p):
    if len(p)==1:
        return [0]
    else:
        q = np.sort(p)
        return [np.where(q == p[0])[0][0]]+find_position(p[1:])


def rolling_window(a, window, step_size):
    shape = a.shape[:-1] + (a.shape[-1] - window + 1 - step_size + 1, window)
    strides = a.strides + (a.strides[-1] * step_size,)
    return np.lib.stride_tricks.as_strided(a, shape=shape, strides=strides)


def compute_probs(data, n=10): 
    h, e = np.histogram(data, n)
    p = h/data.shape[0]
    return e, p


def kl_divergence(p, q): 
    return np.sum(p*np.log(p/q))


def js_divergence(p, q):
    m = (1./2.)*(p + q)
    return (1./2.)*kl_divergence(p, m) + (1./2.)*kl_divergence(q, m)


def compute_lehmer(w):
    
    fact = [math.factorial(i) for i in range(len(w)-1,0,-1)]+[0]
    q = find_position(w)
    return  np.sum(np.multiply(fact,q))


def compute_kl_divergence(train_sample, test_sample, n_bins=10): 
    """
    Computes the KL Divergence using the support intersection between two different samples
    """
    e, p = compute_probs(train_sample, n=n_bins)
    _, q = compute_probs(test_sample, n=e)

#     list_of_tuples = support_intersection(p, q)
#     p, q = get_probs(list_of_tuples)
    
    q = np.where(q==0,np.finfo(np.float32).eps,q)
    p = np.where(p==0,np.finfo(np.float32).eps,p)
    
    return kl_divergence(p, q)


def compute_js_divergence(train_sample, test_sample, n_bins=10): 
    """
    Computes the JS Divergence using the support intersection between two different samples
    """
    e, p = compute_probs(train_sample, n=n_bins)
    _, q = compute_probs(test_sample, n=e)
    
#     list_of_tuples = support_intersection(p, q)
#     p, q = get_probs(list_of_tuples)
    
    q = np.where(q==0,np.finfo(np.float32).eps,q)
    p = np.where(p==0,np.finfo(np.float32).eps,p)
    
    return js_divergence(p, q)


def PD_distance(p, q, metric = 'kullback', m = 3, step = 1):
     
    m_p = rolling_window(p,m, step)
    m_q = rolling_window(q,m, step)
    
    p_lv = np.array([compute_lehmer(xi) for xi in m_p])
    q_lv = np.array([compute_lehmer(xi) for xi in m_q])
    
    if metric == 'kullback':
        return compute_kl_divergence(p_lv,q_lv)
    
    if metric == 'wasserstein':
        return wasserstein_distance(p_lv,q_lv)