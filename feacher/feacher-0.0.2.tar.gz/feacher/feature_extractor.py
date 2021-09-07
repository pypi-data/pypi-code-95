import torch
from feacher import preprocess as ps
from feacher import model as ml

def feature_vector(pretrained_model, image, resize_dim, layer):
    model = ml.Model(pretrained_model=pretrained_model)
    input_image = ps.image_preprocess(image, resize_dim)
    input_batch = input_image.unsqueeze(0)

    with torch.no_grad():
        feature_vector = None
        
        def hook(module_, input_, feature_vector_):
            nonlocal feature_vector
            feature_vector = feature_vector_

        a_hook = getattr(model, '%s' %layer).register_forward_hook(hook)        
        model(input_batch)
        a_hook.remove()
        
        return feature_vector
