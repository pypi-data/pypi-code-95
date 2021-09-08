import sys
import os
import os.path
import random
import json

import numpy
import tensorflow
import albumentations as A

from ..Mask_RCNN_tf2.mrcnn import model
from ..Mask_RCNN_tf2.mrcnn import visualize
from ..Mask_RCNN_tf2.mrcnn import utils
from . import nuclei_config
from . import nuclei_dataset

class MaskRCNNTrain:

    def __init__(self, pParams):
        self.__mParams = pParams

    def get_augmentation_pipeline(self):
        augmentation = A.Compose([
            # Geometry
            A.RandomScale(scale_limit=(1., 1.5)),
            A.RandomCrop(width=1024, height=1024),
            A.Flip(p=.5),
            A.RandomRotate90(p=.5),
                                                            
            # Texture
            A.GaussianBlur(blur_limit=(3,9), p=.5),
            A.Blur(blur_limit=(3,9), p=.5),
            A.RandomBrightnessContrast(p=.5),
            #A.RGBShift(p=.5)
            A.ISONoise(p=.5)
        ])
        #A.save(augmentation, 'augmentation.json')
        
        return augmentation

    def test_augmentation(self, image, mask, augmentation_pipeline):
        '''
        @arg image: (h, w, 3)
        @arg mask: (h, w, n_obj)
        @arg augmentation_pipeline: The albumentations pipeline
        '''
        def augment_with_albumentations(image, mask, transform):
            masks = [mask[..., idx] for idx in range(mask.shape[-1])]
            transformed = transform(image=image, masks=masks)
            
            image_aug = transformed['image']
            mask_aug = transformed['masks']
            
            mask_aug = np.stack(mask_aug, -1)

            return image_aug, mask_aug

        return augment_with_albumentations(image, mask, augmentation)

    @staticmethod
    def process_dataset(imagesDir, masksDir):
        imagesAndMasks = {}

        imageFileList = [f for f in os.listdir(imagesDir) if os.path.isfile(os.path.join(imagesDir, f))]
        for imageFile in imageFileList:
            baseName = os.path.splitext(os.path.basename(imageFile))[0]
            imagePath = os.path.join(imagesDir, imageFile)
            maskPath = os.path.join(masksDir, baseName + ".tiff")
            if not os.path.isfile(imagePath) or not os.path.isfile(maskPath):
                print('Warning:', imageFile, 'not found!')
                continue
            
            imagesAndMasks[imagePath] = maskPath
        
        return imagesAndMasks
        

    def train(self, p_inModelPath=None, p_outModelPath=None, p_trainDir=None, p_evalDir=None):
        
        inModelPath = p_inModelPath 
        outModelPath = p_outModelPath 
        trainDir = p_trainDir 
        evalDir = p_evalDir

        # if "input_model" in self.__mParams:
        #     os.path.join(os.curdir, self.__mParams["input_model"])
        
        # if "output_model" in self.__mParams:
        #     os.path.join(os.curdir, self.__mParams["output_model"])
        
        # if "train_dir" in self.__mParams:
        #     os.path.join(os.curdir, self.__mParams["train_dir"])

        # if "eval_dir" in self.__mParams:
        #     os.path.join(os.curdir, self.__mParams["eval_dir"])

        maxdim = 1024
        fixedRandomSeed = None
        trainToValidationChance = 0.2
        includeEvaluationInValidation = True
        stepMultiplier = None
        stepCount = 1000
        showInputs = False
        detNMSThresh = 0.35
        rpnNMSThresh = 0.55

        if "image_size" in self.__mParams:
            maxdim = int(self.__mParams["image_size"])

        if "train_to_val_seed" in self.__mParams:
            fixedRandomSeed = self.__mParams["train_to_val_seed"]

        if "train_to_val_ratio" in self.__mParams:
            trainToValidationChance = float(self.__mParams["train_to_val_ratio"])

        if "use_eval_in_val" in self.__mParams:
            includeEvaluationInValidation = self.__mParams["use_eval_in_val"] == "true"

        if "step_ratio" in self.__mParams:
            stepMultiplier = float(self.__mParams["step_ratio"])

        if "step_num" in self.__mParams:
            stepCount = int(self.__mParams["step_num"])

        if "detection_nms_threshold" in self.__mParams:
            detNMSThresh = float(self.__mParams["detection_nms_threshold"])

        if "rpn_nms_threshold" in self.__mParams:
            rpnNMSThresh = float(self.__mParams["rpn_nms_threshold"])
        
        blankInput = self.__mParams["blank_mrcnn"] == "true"

        # iterate through train set
        imagesDirTrain = os.path.join(trainDir, "images")
        masksDirTrain = os.path.join(trainDir, "masks")
        trainImagesAndMasks = self.process_dataset(imagesDirTrain, masksDirTrain)

        imagesDirVal = os.path.join(evalDir, "images")
        masksDirVal = os.path.join(evalDir, "masks")
        validationImagesAndMasks = self.process_dataset(imagesDirVal, masksDirVal)

        if len(trainImagesAndMasks) < 1:
            raise ValueError("Empty train list")

        if len(validationImagesAndMasks) < 1:
            raise ValueError("Empty validation list")

        # Training dataset
        dataset_train = nuclei_dataset.NucleiDataset()
        dataset_train.initialize(pImagesAndMasks=trainImagesAndMasks)
        dataset_train.prepare()

        # Validation dataset
        dataset_val = nuclei_dataset.NucleiDataset()
        dataset_val.initialize(pImagesAndMasks=validationImagesAndMasks)
        dataset_val.prepare()

        print("training images (with augmentation):", dataset_train.num_images)
        print("validation images (with augmentation):", dataset_val.num_images)

        config = nuclei_config.NucleiConfig()
        config.IMAGE_MAX_DIM = maxdim
        config.IMAGE_MIN_DIM = maxdim
        config.STEPS_PER_EPOCH = stepCount
        if stepMultiplier is not None:
            steps = int(float(dataset_train.num_images) * stepMultiplier)
            config.STEPS_PER_EPOCH = steps

        config.VALIDATION_STEPS = dataset_val.num_images
        config.DETECTION_NMS_THRESHOLD = detNMSThresh
        config.RPN_NMS_THRESHOLD = rpnNMSThresh
        config.__init__()
        # show config
        config.display()

        # show setup
        for a in dir(self):
            if not callable(getattr(self, a)):
                print("{:30} {}".format(a, getattr(self, a)))
        print("\n")

        # Create model in training mode
        mdl = model.MaskRCNN(mode="training", config=config, model_dir=os.path.dirname(outModelPath))

        if blankInput:
            mdl.load_weights(inModelPath, by_name=True,
                             exclude=["mrcnn_class_logits", "mrcnn_bbox_fc", "mrcnn_bbox", "mrcnn_mask"])
        else:
            mdl.load_weights(inModelPath, by_name=True)

        augmentation = self.get_augmentation_pipeline()

        allcount = 0
        for epochgroup in self.__mParams["epoch_groups"]:
            epochs = int(epochgroup["epochs"])
            if epochs < 1:
                continue
            allcount += epochs
            mdl.train(dataset_train,
                      dataset_val,
                      learning_rate=float(epochgroup["learning_rate"]),
                      epochs=allcount,
                      layers=epochgroup["layers"],
                      augmentation=augmentation,
                      augmentation_lib='album')

        mdl.keras_model.save_weights(outModelPath)
