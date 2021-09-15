import numpy as np
import cv2
from .Scale import Scale

class ScaleWithYoloAnnotation(Scale):

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

        
        ret_annotations = []

        for anno in img_annotations:

            class_id = anno[0]
            x_center = (anno[1] * width + left_offset)/(width + 2*left_offset)
            y_center = (anno[2] * height + top_offset)/(height + 2*top_offset)
            box_width = (anno[3] * width/ (width + 2*left_offset))
            box_height = (anno[3] *height/ (height + 2*top_offset))

            ret_annotations.append([class_id,x_center,y_center,box_width,box_height])


        return new_img,ret_annotations