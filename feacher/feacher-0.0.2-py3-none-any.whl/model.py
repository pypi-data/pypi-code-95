import torchvision.models as models

def Model(pretrained_model):
    model = getattr(models, '%s' %pretrained_model)(pretrained=True)    
    # Set the model to Evaluation mode
    model.eval()
    
    return model