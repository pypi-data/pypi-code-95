# -*- coding: utf-8 -*-
import os
import torch
from os.path import isfile


__version__ = '1.0.0'


def tensor2list(tensor):
    return tensor.detach().cpu().tolist()


def cat(tensors, dim=0):
    """ Efficient version of torch.cat that avoids a copy if there is only a single element in a list.
    """
    assert isinstance(tensors, (list, tuple))
    if len(tensors) == 1:
        return tensors[0]
    return torch.cat(tensors, dim)


def contiguous(tensor):
    if tensor.is_contiguous():
        return tensor
    else:
        return tensor.contiguous()


def load(model, ckpt_path):
    assert isfile(ckpt_path), 'No model checkpoint found!'
    try:
        model.load_state_dict(torch.load(ckpt_path))
    except:
        state_dict = torch.load(ckpt_path)
        new_state_dict = OrderedDict()
        for k, v in state_dict.items():
            name = k.replace('module.', '')
            new_state_dict[name] = v
        model.load_state_dict(new_state_dict)
    return model