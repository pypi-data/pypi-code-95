import sys
import os
import subprocess
import json
import shutil
import pprint
import subprocess
from statistics import median
from pathlib import Path
from multiprocessing import Process

import numpy as np
import imageio
from skimage.measure import regionprops
from skimage.transform import rescale

from .pix2pix_interface.style_transfer import StyleTransfer
from .mrcnn_interface import segmentation_prediction
from .mrcnn_interface.train import MaskRCNNTrain

pp = pprint.PrettyPrinter(indent=4)

class NucleaizerTraining:
    def set_native_paths(self, nucleaizer_dir):
        #r = /media/ervin/Backup/devel/biomagdsb/build/compiled
        r = os.path.join(nucleaizer_dir, 'native')
        p_ = ['%s/%s' % (str(r), x) for x in ['libfromClustersToStylesFunc', 'librunfromKaggleToClusters', 'libsetUpConfigAndDB', 'libSimpleScripts']]
        os.environ['PYTHONPATH'] = ':'.join(p_)
        print(os.environ['PYTHONPATH'])

    def __init__(self, inputs_dir, workflow_dir, nucleaizer_dir):
        self.set_native_paths(nucleaizer_dir)
        '''

        The inputs go to the inputs_dir. Structure:
        inputs_dir/
            train/
                images/*.png
                masks/*.tiff
            val/
                images/*.png
                masks/*.tiff
            test/*.png

        The workflow_dir is the working directory for the training.

        The (downloaded) models, aux files, training work dir (by default) go into the nucleaizer_dir.

        '''

        self.inputs_dir = Path(inputs_dir)
        self.outputs_dir = Path(workflow_dir)
        os.environ['NUCLEAIZER_CONFIG'] = str(self.outputs_dir)
        os.environ['SAC_ROOT'] = os.path.join(nucleaizer_dir, 'sac')

        self.style_learn_dir = self.outputs_dir/'styleLearnInput'
        self.split_ids = ['0', '1'] # Style transfer splits (in case of multiple train workers available)

        # Resize each image and mask pair to contain median cell sizes exaxtly this.
        self.train_cell_size = 40

        if (self.inputs_dir/'clustering').exists():
            self.clustering_dir = self.inputs_dir/'clustering'
        else:
            self.clustering_dir = Path(nucleaizer_dir)/'clustering'
        print('Clusters dir:', self.clustering_dir)

    def copy_input(self):
        # Copy test
        test_dir = self.inputs_dir/'test'
        
        workflow_input_images_dir = (self.outputs_dir/'images')
        print('Copying input files: %s -> %s' % (test_dir, workflow_input_images_dir))
        workflow_input_images_dir.mkdir(exist_ok=True, parents=True)

        for src_file in test_dir.glob('*.*'):
            shutil.copy(src_file, workflow_input_images_dir)

    @staticmethod
    def read_json(json_path):
        with open(json_path) as config_file:
            json_config = json.load(config_file)
        return json_config

    def presegment(self, model_path, config_path):
        json_config = self.read_json(config_path)

        segmentation = segmentation_prediction.Segmentation(model_path)
        output_path = self.outputs_dir/'presegment'

        if not output_path.exists():
            output_path.mkdir(exist_ok=True)

        segmentation.presegmentation(
            input_path=self.outputs_dir/'images', 
            output_path=output_path)

    def measure_cells(self):
        args = [
            str(self.outputs_dir/'presegment') + '/', 
            str(self.outputs_dir/'cellSizeEstimator'/'images')]
        
        self.call_matlab_func('libSimpleScripts', 'cellSizeDataGenerate', args)

    def setup_db(self):
        args = [
            str(self.clustering_dir/'masks'),  # The mask database directory
            str(self.outputs_dir),                          # The database will be saved here
            str(self.clustering_dir/'pretrainedDistanceLearner.mat'), # The weights will be loaded from here
            '.'                                             # the codeBase dir, will be deprecated!
        ]
        self.call_matlab_func('libsetUpConfigAndDB', 'setUpConfigAndDB', args)

    def clustering(self):
        args = [
            str(self.outputs_dir/'images'),
            str(self.outputs_dir/'clusters'),
            'Kmeans-correlation-Best3Cluster', 
            str(self.outputs_dir/'presegment'),
            '/media/ervin/Backup/devel/biomagdsb/biomag-kaggle/src/1_metalearning/matlab/sac/', 
            '0', 'False'
        ]

        self.call_matlab_func('librunfromKaggleToClusters', 'runfromKaggleToClusters', args)

    def create_style_train(self):
        args = [
            str(self.style_learn_dir),
            str(self.outputs_dir/'clusters'),
            str(self.outputs_dir/'presegment'),
            str(self.clustering_dir/'basicOptions_02.csv'),
            str(self.style_learn_dir)
        ]

        self.call_matlab_func('libfromClustersToStylesFunc', 'fromClustersToStylesFunc', args)
    
    def collect_style_transfer_output(self, target_dir):
        im_list = Path(self.outputs_dir, self.style_learn_dir).glob('*/%s/images/*' % StyleTransfer.P2P_FINAl_OUTPUT_REL_DIR)
        mask_list = Path(self.outputs_dir, self.style_learn_dir).glob('*/%s/masks/*' % StyleTransfer.P2P_FINAl_OUTPUT_REL_DIR)

        target_img = target_dir/'images'
        target_mask = target_dir/'masks'

        target_img.mkdir(exist_ok=True, parents=True)
        target_mask.mkdir(exist_ok=True, parents=True)

        for im in im_list:
            shutil.copy(im, str(target_img))

        for im in mask_list:
            shutil.copy(im, str(target_mask))

    def style_transfer(self):
        for split in self.split_ids:
            split_dir = str(self.style_learn_dir / split)
            st = StyleTransfer(split_dir)
            st.learn_styles()
            st.apply_styles()
            st.generate_output()

        self.collect_style_transfer_output(self.outputs_dir/'augmentations'/'style')

    @staticmethod
    def get_median_ob_size(m):
        '''
        Checks all of the objects in the mask and computes the median size.
        '''
        props = regionprops(m)
        sizes = []
        for region in props:
            if region.label != 0: # Skip background
                bbox = region['bbox']
                h = bbox[2]-bbox[0]
                w = bbox[3]-bbox[1]
                sizes.append(.5*(h+w))
        median_size = median(sizes)
        return median_size

    @staticmethod
    def rescale_mask(mask, scale_factor):
        original_dtype = mask.dtype
        return rescale(mask, scale=scale_factor, order=0, anti_aliasing=False, preserve_range=True).astype(original_dtype)

    @staticmethod
    def rescale_image(image, scale_factor):
        original_dtype = image.dtype
        return rescale(image, scale=scale_factor, order=1, multichannel=True, anti_aliasing=True, preserve_range=True).astype(original_dtype)

    def enumerate_training_samples(self):
        '''
        Enumerates all of the samples in the initial Mask R-CNN training set 
        provided by the user and the synthetic images.
        '''

        from_train_maskrcnn = self.inputs_dir/'train'
        initial_images_list = list((from_train_maskrcnn/'images').glob('*.png'))
        initial_masks_list = list((from_train_maskrcnn/'masks').glob('*.tiff'))

        synthetic_images_list = list(self.style_learn_dir.glob('*/p2psynthetic/*/*.png'))
        synthetic_masks_list = list(self.style_learn_dir.glob('*/generated/*/grayscale/*.tiff'))

        # We don't really want to sort the files but to match them based on filenames 
        # or filenames+parent folders if they are equal.
        match_lambda = lambda posix_path: str(posix_path)[::-1]

        initial_images_list.sort(key=match_lambda)
        initial_masks_list.sort(key=match_lambda)

        synthetic_images_list.sort(key=match_lambda)
        synthetic_masks_list.sort(key=match_lambda)

        initial_samples = zip(initial_images_list, initial_masks_list)
        synthetic_samples = zip(synthetic_images_list, synthetic_masks_list)

        return list(initial_samples) + list(synthetic_samples)

    def create_mask_rcnn_train(self):
        '''
        First, collectes all of the images that will be copied into the final training set
        and resizes them to make the object sizes uniform through the dataset.
        '''

        mask_rcnn_training_dir = self.outputs_dir/'train_maskrcnn'

        (mask_rcnn_training_dir / 'images').mkdir(exist_ok=True, parents=True)
        (mask_rcnn_training_dir / 'masks').mkdir(exist_ok=True, parents=True)

        all_samples = self.enumerate_training_samples()
        for image_path, mask_path in all_samples:
            image = imageio.imread(str(image_path))
            mask = imageio.imread(str(mask_path))
            
            median_ob_size = self.get_median_ob_size(mask)
            scale_factor = self.train_cell_size / median_ob_size
            
            image_rescaled = self.rescale_image(image, scale_factor)
            mask_rescaled = self.rescale_mask(mask, scale_factor)

            print('name', image_path.stem, 'scale factor:', scale_factor, 'resize:', image.shape, '->', image_rescaled.shape)

            imageio.imwrite(mask_rcnn_training_dir/'images'/image_path.name, image_rescaled)
            imageio.imwrite(mask_rcnn_training_dir/'masks'/mask_path.name, mask_rescaled)

    def train_maskrcnn(self, config_path, initial_model):
        json_config = self.read_json(config_path)
        mask_rcnn_training_dir = self.outputs_dir/'train_maskrcnn'
        
        trainer = MaskRCNNTrain(pParams=json_config["train_params"])
        output_model_path = self.outputs_dir/'output_model'
        output_model_path.mkdir(exist_ok=True)
        trainer.train(
            str(initial_model), 
            str(output_model_path/'model.h5'), 
            str(mask_rcnn_training_dir),
            str(self.inputs_dir/'val'))

    # These functions will be executed as subprocesses.
    def set_matlab_rt_paths(self):

        matlab_rt = os.environ['MATLAB_RUNTIME_PATHS']
        #path_list = '%s/v99/runtime/glnxa64:%s/v99/bin/glnxa64:%s/v99/sys/os/glnxa64:%s/v99/extern/bin/glnxa64' % (matlab_rt, matlab_rt, matlab_rt, matlab_rt)
        path_list = matlab_rt

        print('Path list:', path_list)

        if 'LD_LIBRARY_PATH' in os.environ:
            os.environ['LD_LIBRARY_PATH'] += ':' + path_list
        else:
            os.environ['LD_LIBRARY_PATH'] = path_list

    def call_matlab_func(self, library_name, func_name, args):
        self.set_matlab_rt_paths()
        wrapper_args = [library_name, func_name] + args
        subprocess.run("%s -m nucleaizer_backend.matlab_func_wrapper %s" % (sys.executable, ' '.join(wrapper_args)), shell=True)
