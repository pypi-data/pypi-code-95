import torchvision.transforms as T

def image_preprocess(image, resize_dim=256):
    preprocess = T.Compose([
            T.Resize(resize_dim),
            T.CenterCrop(224),
            T.ToTensor(),
            T.Normalize(mean=[0.485, 0.456, 0.406],
                        std=[0.229, 0.224, 0.225]),
    ])
    
    return preprocess(image)