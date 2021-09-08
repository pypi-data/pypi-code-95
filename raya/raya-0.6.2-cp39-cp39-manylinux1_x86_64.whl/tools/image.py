import cv2
from raya.utils import get_app_path
from raya.constants import *

def show_image(img, title=''):
    for i in range(3):
        cv2.imshow(title, img)
        cv2.waitKey(10)

def save_image(img, filename: str):
    if not filename.endswith('.jpg') and not filename.endswith('.png'):
        filename += '.jpg'
    filepath = get_app_path() / PATH_DATA_FOLDER / filename
    print(filepath)
    cv2.imwrite(str(filepath), img)