import math

def get_max_dim(trained_size, target_size, image_shape):
    '''
    1.) determine the scaling factor based on the train cell size and image under prediction cell size
    2.) calculate the least size that is bigger than the input and dividable by 64 (finalSize)

    This size will be set up in the Mask R-CNN config as the max dim.
    If the user does not provide anything (targetObjSize = -1) then we use the default size for training (1024) defined in the Mask R-CNN config file.
    '''
    
    resizeFactor = (trained_size/target_size)
    resizedShape = (resizeFactor*image_shape[0], resizeFactor*image_shape[1])
    resizedMaxDim = max(resizedShape)
    computed_size = int(math.ceil(resizedMaxDim/64)*64)
    return computed_size

def get_max_dim_pow2(pPredictSize):
    maxdim = pPredictSize
    temp = maxdim / 2 ** 6
    if temp != int(temp):
        maxdim = (int(temp) + 1) * 2 ** 6

    return maxdim

def get_max_dim_legacy(trainedObjSize, targetObjSize, image_shape):
    '''
    Legacy image size computation.
    '''

    resizeTo = (float(trainedObjSize) / float(targetObjSize / 2.0)) * (float(image_shape[0] + image_shape[1]) / 2.0)
    finalSize = int(round(resizeTo / 64) * 64)
    return finalSize