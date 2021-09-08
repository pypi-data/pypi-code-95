import os

import skimage
import numpy as np

from ..Mask_RCNN_tf2.mrcnn import utils

from . import kutils

class NucleiDataset(utils.Dataset):

    def initialize(self, pImagesAndMasks):
        self.add_class("nuclei", 1, "nucleus")

        imageIndex = 0

        for imageFile, maskFile in pImagesAndMasks.items():
            baseName = os.path.splitext(os.path.basename(imageFile))[0]

            image = skimage.io.imread(imageFile)
            if image.ndim < 2 or image.dtype != np.uint8:
                continue

            self.add_image(
                source="nuclei", 
                image_id=imageIndex, 
                path=imageFile, 
                name=baseName, 
                width=image.shape[1], height=image.shape[0], 
                mask_path=maskFile, 
                augmentation_params=None)

            imageIndex += 1


    def image_reference(self, image_id):
        info = self.image_info[image_id]
        ref = info["name"]

        return ref


    def load_image(self, image_id):
        info = self.image_info[image_id]
        imagePath = info["path"]

        image = skimage.io.imread(imagePath)
        image = kutils.RCNNConvertInputImage(image)

        return image

    def load_mask(self, image_id):
        info = self.image_info[image_id]
        maskPath = info["mask_path"]

        mask = skimage.io.imread(maskPath)
        if mask.ndim > 2:
            mask = mask[:,:,0]

        count = np.max(mask)

        masks = np.zeros([mask.shape[0], mask.shape[1], count], dtype=np.uint8)
        for y in range(mask.shape[0]):
            for x in range(mask.shape[1]):
                index = int(mask[y,x]) - 1
                if index >= 0:
                    masks[y,x,index] = 1

        #assign class id 1 to all masks
        class_ids = np.array([1 for _ in range(count)])
        return masks, class_ids.astype(np.int32)
