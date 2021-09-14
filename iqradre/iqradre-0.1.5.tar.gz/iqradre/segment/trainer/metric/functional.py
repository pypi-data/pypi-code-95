import torch
import torch.nn as nn
import torch.nn.functional as F



def jaccard_coeff(preds, targets, smooth=1.0):
    """
    Jaccard = (|X & Y|)/ (|X|+ |Y| - |X & Y|)
            = sum(|A*B|)/(sum(|A|)+sum(|B|)-sum(|A*B|))

    The jaccard distance loss is usefull for unbalanced datasets. This has been
    shifted so it converges on 0 and is smoothed to avoid exploding or disapearing
    gradient.

    Ref: https://en.wikipedia.org/wiki/Jaccard_index

    @url: https://gist.github.com/wassname/17cbfe0b68148d129a3ddaa227696496
    @author: wassname
    """
        
    preds_flatten = torch.flatten(preds)
    targets_flatten = torch.flatten(targets)

    intersection = torch.sum(torch.abs(preds_flatten) * torch.abs(targets_flatten))
    cardinality = torch.sum(torch.abs(preds_flatten) + torch.abs(targets_flatten))
    union = cardinality - intersection 

    jaccard_coeff = (intersection + smooth)/(union + smooth)
    
    return jaccard_coeff.mean()


def jaccard_loss(preds, targets, smooth=1.0):
    jacc_coeff = jaccard_coeff(preds, targets, smooth)
    jaccard_loss =  (1. - jacc_coeff) * smooth
    return jaccard_loss


def dice_coeff(preds, targets, smooth=1.0, epsilon=1e-6):
    # inspiration from
    # https://github.com/pytorch/pytorch/issues/1249
    # github.com/jeffwen/road_building_extraction/blob/master/src/utils/core.py
    # and other source
    
    preds_flatten = torch.flatten(preds)
    targets_flatten = torch.flatten(targets)

    intersection = (preds_flatten * targets_flatten).float().sum()
    cardinality = (preds_flatten +targets_flatten).float().sum()  + smooth + epsilon
    dice_coeff = (2. * intersection + smooth) / cardinality
    
    return dice_coeff


def dice_loss(preds, targets, smooth=1.0, epsilon=1e-6):
    dcoeff = dice_coeff(preds, targets, smooth, epsilon)
    dice_loss = torch.mean(1. - dcoeff)
    return dice_loss