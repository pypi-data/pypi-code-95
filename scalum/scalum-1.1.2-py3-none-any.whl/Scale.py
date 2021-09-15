import numpy as np
import cv2

class Scale:

    def __init__(self,width, height):
        self.width = width
        self.height = height


    def get_scale_ratio(self,img):
        height_ratio = img.shape[0] / self.height
        width_ratio = img.shape[1] / self.width

        max_ratio = max(height_ratio, width_ratio)
        return max_ratio


    def __call__(self,img,img_annotations=None):
        return self.scale_img(img,img_annotations)



    def scale_img(self,img,img_annotations):

        ratio = self.get_scale_ratio(img)

        new_img = np.zeros((self.height,self.width,3)).astype(np.uint8)
        img = cv2.resize(img, (int(img.shape[1] // ratio), int(img.shape[0] // ratio)))

        x_offset = (self.width - img.shape[1])
        y_offset = (self.height - img.shape[0])

        left_offset = x_offset // 2 + x_offset % 2
        top_offset = y_offset // 2 + y_offset % 2

        height = img.shape[0]
        width = img.shape[1]

        new_img[top_offset:top_offset+img.shape[0],left_offset:left_offset+img.shape[1],:] = img

    
        return new_img


        