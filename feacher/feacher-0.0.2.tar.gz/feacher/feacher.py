from feacher import feature_extractor as fe
from feacher import dataloader as dl

def extract(path, pretrained_model='resnet18', resize_dim=256, layer=None):

    images = dl.DataLoader(path)
    image_features = []

    if(layer == None):
        layer = 'avgpool'

    for image in images:
        extracted_features = fe.feature_vector(pretrained_model,
                                               image,
                                               resize_dim,
                                               layer)
        image_features.append(extracted_features)

    print(f"\n\n=============================================")
    print(f"Feacher (@qpochlabs) - Parameters and Results")
    print(f"=============================================")
    print(f"Model         : {pretrained_model}")
    print(f"Layer         : {layer}")
    print(f"feature size  : {image_features[0].shape}")
    print(f"=============================================\n\n")

    return image_features