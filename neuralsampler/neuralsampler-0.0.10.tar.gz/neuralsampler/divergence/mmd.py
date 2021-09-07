# here contains the metric for mmd divergence
import torch

# how to make a different name for the two methods 
def mmd2(x1, y1, x2, y2, ratio1, ratio2, beta = 1.0):
    """
    maximum mean discrepancy (MMD) based on Gaussian kernel
    function for keras models (pytorch backend)
    
    - Gretton, Arthur, et al. "A kernel method for the two-sample-problem."
    Advances in neural information processing systems. 2007.

    - code adapted from https://github.com/wzell/mann/blob/master/models/maximum_mean_discrepancy.py#L23-L39
    """
    # ratio11 = torch.outer(ratio1, ratio1)
    ratio12 = torch.outer(ratio1, ratio2)
    ratio21 = torch.outer(ratio2, ratio1)

    x1x1 = gaussian_kernel(x1, x2, beta)
    x1x2 = gaussian_kernel(x1, y2, beta)
    x2x1 = gaussian_kernel(x2, y1, beta)
    x2x2 = gaussian_kernel(y1, y2, beta)

    diff = x1x1 * ratio12 -  x1x2 * ratio12 - x2x1 * ratio21 + x2x2 * ratio12  
    diff = diff.mean()
    return diff


def mmd(x1, x2, ratio, beta = 1.0):
    """
    maximum mean discrepancy (MMD) based on Gaussian kernel
    function for keras models (pytorch backend)
    
    - Gretton, Arthur, et al. "A kernel method for the two-sample-problem."
    Advances in neural information processing systems. 2007.

    - code adapted from https://github.com/wzell/mann/blob/master/models/maximum_mean_discrepancy.py#L23-L39
    """
    ratio_outer = torch.outer(ratio, ratio)
    x1x1 = gaussian_kernel(x1, x1, beta)
    x1x2 = gaussian_kernel(x1, x2, beta)
    x2x2 = gaussian_kernel(x2, x2, beta)
    # diff = x1x1.mean() - 2 * x1x2.mean() + x2x2.mean()
    diff = x1x1 - 2 * x1x2 + x2x2 
    diff = diff * ratio_outer
    diff = diff.mean()
    return diff

def gaussian_kernel(x1, x2, beta = 1.0):
    # the std of the gaussian kernel is 
    # sigma = 1 / sqrt( 2 * beta )
    r = torch.unsqueeze(x1, 1)
    return torch.exp( -beta * torch.square(r - x2).sum(axis=-1))
