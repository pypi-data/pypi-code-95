import os
from PIL import Image

def DataLoader(path):
    images = []
    for file in os.listdir(path):
        f_img = path+"/"+file
        img = Image.open(f_img)
        images.append(img)
    
    return images