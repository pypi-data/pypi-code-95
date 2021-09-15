import numpy as np
import cv2
from .Scale import Scale

class ScaleWithPolyAnnotation(Scale):

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

            rescaled_anno = []

            for point in anno:
                rescaled_anno.append([point[0] // ratio + left_offset,point[1] // ratio + top_offset])

            ret_annotations.append(rescaled_anno)


        return new_img,ret_annotations
