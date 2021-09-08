import sys
import os
import os.path
import json

import numpy
import cv2
import skimage.morphology
import tensorflow as tf
import imageio

from ..Mask_RCNN_tf2.mrcnn import utils
from ..Mask_RCNN_tf2.mrcnn import visualize
from ..Mask_RCNN_tf2.mrcnn import model

from .. import common
from . import nuclei_config
from . import kutils

class Segmentation(object):

    def __init__(self, pModelPath, pConfidence=0.5, pNMSThreshold = 0.35, pMaxDetNum=512, maxDim=1024):

        if not os.path.isfile(pModelPath):
            raise ValueError("Invalid model path: " + pModelPath)

        self.confidence = pConfidence
        self.nms_threshold = pNMSThreshold
        self.max_det_num = pMaxDetNum
        self.last_max_dim = maxDim
        self.default_max_dim = maxDim   # The default max dim

        self.model = None
        self.weights_updated = True
        self.weights_path = pModelPath

        self.session = tf.compat.v1.keras.backend.get_session()

    def segment(self, 
        image, 
        
        padding_ratio=0.0, 
        dilate=0, 
        cavity_fill=False, 
        
        predict_size=None,
        trained_size=40, 
        target_size=None):

        '''
        @arg target_size: the expected size of the objects in the image. If given (-1), the ratio of the
        target_size and trained_size will be computed to determine the scaling.
        @predict_size: if given, this scaling will be used for prediction and the trained size won't be considered.

        If both target_size and predict_size is given, an exception is raised.
        If none of them specified, then the default size will be used defined in the constructor.
        '''

        if target_size is not None and predict_size is not None:
            raise ValueError('Both target object size and predict size is defined.')

        with self.session.as_default():
            with self.session.graph.as_default():
                current_session = tf.compat.v1.keras.backend.get_session()

                print('NucleAIzer: using existing session:', current_session)

                # Rebuilding is needed when the Mask R-CNN config is changed.
                # or the model does not exist itself.
                rebuild = self.model is None

                image = kutils.RCNNConvertInputImage(image)

                # Determine the scale
                if target_size is not None:
                    print('Target size is provided: %.2f' % target_size)
                    computed_size = common.get_max_dim(trained_size, target_size, image.shape)
                    computed_size = max(128, computed_size)
                    computed_size = min(self.default_max_dim, computed_size)
                elif predict_size is not None:
                    print('Predict size is provided: %.2f' % predict_size)
                    computed_size = common.get_max_dim_pow2(predict_size)
                else:
                    print('Neither target size nor predict size is provided. Using default size: %.2f' % self.default_max_dim)
                    computed_size = self.default_max_dim

                if computed_size != self.last_max_dim:
                    print('Last max dim=%.2f is different than the current computed one=%.2f.' % (self.last_max_dim, computed_size))
                    self.last_max_dim = computed_size
                    rebuild = True
                else:
                    print('Last max dim is the same as the current computed one.')

                print('Input image shape: %s; computed max dim: %s' % (image.shape, computed_size))

                if rebuild:
                    print("Instatiating the Mak R-CNN model because it does not exist or config changed.")
                    print('Using image max dim:', computed_size)

                    config = nuclei_config.NucleiConfig()
                    config.DETECTION_MIN_CONFIDENCE = self.confidence
                    config.DETECTION_NMS_THRESHOLD = self.nms_threshold
                    config.IMAGE_MAX_DIM = computed_size
                    config.IMAGE_MIN_DIM = computed_size
                    config.DETECTION_MAX_INSTANCES=self.max_det_num
                    
                    config.__init__()

                    self.model = model.MaskRCNN(mode="inference", config=config, model_dir=os.path.dirname(self.weights_path))

                if self.weights_updated or rebuild:
                    print("Loading weights:", self.weights_path)
                    self.model.load_weights(self.weights_path, by_name=True)
                    self.weights_updated = False



                offsetX = 0
                offsetY = 0
                width = image.shape[1]
                height = image.shape[0]

                if padding_ratio > 0.0:
                    image, (offsetX, offsetY) = kutils.PadImageR(image, padding_ratio)

                results = self.model.detect([image], verbose=0)

                r = results[0]
                masks = r['masks']
                scores = r['scores']
                class_ids = r['class_ids']

                if masks.shape[0] != image.shape[0] or masks.shape[1] != image.shape[1]:
                    print("Invalid prediction")
                    return numpy.zeros((height, width), numpy.uint16), \
                        numpy.zeros((height, width, 0), numpy.uint8),\
                        numpy.zeros(0, numpy.float)


                count = masks.shape[2]
                if count < 1:
                    return numpy.zeros((height, width), numpy.uint16), \
                        numpy.zeros((height, width, 0), numpy.uint8),\
                        numpy.zeros(0, numpy.float)

                if padding_ratio > 0.0:
                    newMasks = numpy.zeros((height, width, count), numpy.uint8)
                    for i in range(count):
                        newMasks[:, :, i] = masks[offsetY: (offsetY + height), offsetX: (offsetX + width), i]
                    masks = newMasks

                if dilate > 0:
                    dilatioKernel = skimage.morphology.disk(dilate)
                    for i in range(count):
                        masks[:, :, i] = cv2.dilate(masks[:, :, i], kernel=dilatioKernel)

                if cavity_fill and False:
                    for i in range(count):
                        temp = cv2.bitwise_not(masks[:, :, i])
                        _, temp = cv2.findContours(temp, cv2.RETR_CCOMP, cv2.CHAIN_APPROX_SIMPLE)
                        masks[:, :, i] = cv2.bitwise_not(temp)

                for i in range(count):
                    masks[:, :, i] = numpy.where(masks[:, :, i] == 0, 0, 255)

                return kutils.MergeMasks(masks), masks, class_ids, scores

    def updateWeights(self, weights_file):
        if self.weights_path != weights_file:
            self.weights_updated = True
        
        self.weights_path = weights_file

    def presegmentation(self, input_path, output_path, predict_size=None):
        for image_path in input_path.iterdir():
            print('Presegment:', image_path.name)
            if image_path.name.endswith('.png'):
                image = imageio.imread(image_path)
                mask, masks, class_ids, scores = self.segment(image, predict_size=predict_size)
                imageio.imwrite(output_path/('%s.tiff' % image_path.stem), mask)

    def executeSegmentation(self, image, target_size):
        '''
        Called from Napari to segment an image.
        '''

        mask, masks, class_ids, scores = self.segment(image=image, target_size=target_size)

        count = masks.shape[2]
        print("  Nuclei (including cropped):", str(count))
        if count < 1:
            return None, None, None

        return mask, class_ids, scores