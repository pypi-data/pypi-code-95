import numpy as np

def labels_to_class_weights(labels, nc=None):
    """ 
    Get class weights (inverse frequency) from training labels

    :param labels: Target classes, list or numpy array if n-dimensional array then
                   classes need to be in the 0-dim.
                   examples: 
                   
                   Labels can be list

                   >>> labels =  [1,2,3,4,5] 

                   or n-dim array

                   >>> labels = [[[class1,x1,y1,x2,y2],
                                  [class2,x1,y1,x2,y2],
                                 ...
                                ]]


    :type labels: list, numpy.ndarray, 
    :param nc: (Optional) Minimum count of class occurance.
    :type nc: int

    return(list) = list of weights

    :example:

    >>> labels = [0,1,2,3,1,1,2,3,4,5,5,5]
    >>> labels_to_class_weights(labels)
    [0.27272727 0.09090909 0.13636364 0.13636364 0.27272727 0.09090909]

    >>> labels = np.array([[[0,0.2,0.2,0.3,0.5],[1,0.2,0.2,0.3,0.4],[1,0.2,0.3,0.4,0.5]]])
    >>> labels_to_class_weights(labels)
    [0.66666667 0.33333333]

    >>> labels = [[1],[2],[3],[4]]
    >>> labels_to_class_weights(labels)
    [0.2 0.2 0.2 0.2 0.2]
    
    """

    assert labels[0] is not None, "no labels passed"

    if type(labels) == list:
        labels = np.array(labels)

    if len(labels.shape) > 1:
        labels = np.concatenate(labels, 0)  # labels.shape = (866643, 5) for COCO
        
        # after concat if till not vector for case [[1],[2],[3],[4]]
        if len(labels.shape) > 1:
            labels = labels[:, 0].astype(np.int)  # labels = [class xywh]
    
    weights = np.bincount(labels, minlength=nc)  # occurrences per class
    # Prepend gridpoint count (for uCE training)
    # gpi = ((320 / 32 * np.array([1, 2, 4])) ** 2 * 3).sum()  # gridpoints per image
    # weights = np.hstack([gpi * len(labels)  - weights.sum() * 9, weights * 9]) ** 0.5  # prepend gridpoints to start

    weights[weights == 0] = 1  # replace empty bins with 1
    weights = 1 / weights  # number of targets per class
    weights /= weights.sum()  # normalize

    return weights
