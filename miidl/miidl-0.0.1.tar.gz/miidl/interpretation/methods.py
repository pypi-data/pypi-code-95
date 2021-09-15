import captum.attr
import torch
# IntegratedGradients, Saliency, DeepLift, DeepLiftShap, InputXGradient, GuidedBackprop, GuidedGradCam, Deconvolution, FeaturePermutation, KernelShap, LRP

def explain(model, input, method='IntegratedGradients', target=2):
    interp = getattr(captum.attr, method)(model)
    attribution = interp.attribute(torch.tensor(input).type(torch.float32), target=target)
    return attribution