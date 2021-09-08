from mrcnn.config import Config


class MRCNNConfig(Config):
    
    def __init__(self):
        super().__init__()

        '''
        Differences from the default config:
        * MEAN_PIXEL is missing
        * RPN_BBOX_STD_DEV is missing
        * BBOX_STD_DEV is missing
        * TRAIN_BN is missing
        * DETECTION_MIN_CONFIDENCE = 0.7 -> 0.5
        * DETECTION_NMS_THRESHOLD = 0.3 -> 0.35
        '''

        self.IMAGES_PER_GPU = 1

        self.IMAGE_MAX_DIM = 512
        self.IMAGE_MIN_DIM = 512
        self.IMAGE_RESIZE_MODE = "crop"
        self.IMAGE_CHANNEL_COUNT = 3
        #config.MEAN_PIXEL = numpy.array([127])

        self.STEPS_PER_EPOCH = 2000

        self.RPN_ANCHOR_SCALES = (4, 8, 16, 32, 64)
        self.RPN_ANCHOR_RATIOS = [0.5, 1, 2]
        self.RPN_NMS_THRESHOLD = 0.55
        self.RPN_TRAIN_ANCHORS_PER_IMAGE = 512
        self.TRAIN_ROIS_PER_IMAGE = 512
        self.MAX_GT_INSTANCES = 512
        self.POST_NMS_ROIS_INFERENCE = 1536
        self.DETECTION_MAX_INSTANCES = 1536
        self.NUM_CLASSES = 4
        self.LOSS_WEIGHTS = {
                "rpn_class_loss": 2.,
                "rpn_bbox_loss": 2.,
                "mrcnn_class_loss": 2.,
                "mrcnn_bbox_loss": 1.,
                "mrcnn_mask_loss": 1.

def main():
    conf = MRCNNConfig()
    conf.display()

if __name__ == '__main__':
    main()
