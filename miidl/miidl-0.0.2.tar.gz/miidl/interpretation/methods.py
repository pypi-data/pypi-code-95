import torch
# IntegratedGradients, Saliency, DeepLift, DeepLiftShap, InputXGradient, GuidedBackprop, GuidedGradCam, Deconvolution, FeaturePermutation, KernelShap, LRP

try:
    import captum.attr
except:
    import sys
    print("The module 'captum' is not found, please install first.")
    print("\tconda install captum -c pytorch")
    sys.exit(0)

def explain(model, input, method='IntegratedGradients', target=2):
    interp = getattr(captum.attr, method)(model)
    attribution = interp.attribute(torch.tensor(input).type(torch.float32), target=target)
    return attribution