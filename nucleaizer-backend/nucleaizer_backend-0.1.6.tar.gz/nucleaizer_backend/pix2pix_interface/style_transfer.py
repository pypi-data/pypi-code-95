import os
import shutil

from ..CycleGAN import train
from ..CycleGAN import test_cus

class StyleTransfer:
    # The models dir
    P2P_MODELS_REL_DIR = 'p2pmodels'

    # The HTML results will be saved here
    P2P_HTML_RESULT_REL_DIR = 'p2pHTML'

    # The P2P train set
    P2P_TRAIN_REL_DIR = 'p2ptrain'

    # The generated masks set
    P2P_TEST_MASKS_REL_DIR = 'generated'

    # Where to put the results?
    P2P_RESULT_REL_DIR = 'p2psynthetic'

    # The final output directory
    P2P_FINAl_OUTPUT_REL_DIR = 'out'

    def __init__(self, work_dir):
        self.work_dir = work_dir

    '''
    Directory structure:

    p2ptrain/
        $CLUS_ID/
            train/
                img...

    The $CLUS_ID is the style.

    '''
    def learn_styles(self, n_iter=1000, gpu_ids='0', display_id=0):

        styles_train_dir = os.path.join(self.work_dir, self.P2P_TRAIN_REL_DIR)
        models_dir = os.path.join(self.work_dir, self.P2P_MODELS_REL_DIR)

        for style in os.listdir(styles_train_dir):  # Train a model for each cluster...
            style_path = os.path.join(styles_train_dir, style)
            style_train_path = os.path.join(style_path, 'train')

            n_files = len(os.listdir(style_train_path))
            print('Train directory for style: {}. Num of files: {}.'.format(style_train_path, n_files))

            num_of_iters = n_iter // n_files
            model_name = style
            
            args = [
            "--dataroot", "%s" % style_path,
            "--name", "%s" % model_name,
            "--model", "pix2pix",
            "--which_model_netG", "unet_256",
            "--which_direction", "BtoA",
            "--lambda_A", "100",
            "--dataset_mode", "aligned",
            "--no_lsgan",
            "--norm", "batch",
            "--pool_size", "0",
            "--save_epoch_freq", "%d" % (num_of_iters+40),
            "--niter", "%d" % num_of_iters,
            "--checkpoints_dir", "%s" % models_dir,
            "--gpu_ids", "%s" % gpu_ids,
            "--display_id", "%s" % display_id
            ]

            train.train(additional_args=args)

    def apply_styles(self, fine_size='512', gpu_ids='0', display_id='0'):
        result_path = os.path.join(self.work_dir, self.P2P_RESULT_REL_DIR)
        os.makedirs(result_path, exist_ok=True)
        # Iterates through the synthetic masks
        synthetic_masks_dir = os.path.join(self.work_dir, self.P2P_TEST_MASKS_REL_DIR)
        synthetic_images_dir = os.path.join(self.work_dir, self.P2P_RESULT_REL_DIR)
        checkpoints_dir =  os.path.join(self.work_dir, self.P2P_MODELS_REL_DIR)
        print('Checking directory: {}'.format(synthetic_masks_dir))
        if os.path.isdir(synthetic_masks_dir):
            clusters = os.listdir(synthetic_masks_dir)
            print(clusters)
        else:
            print('no clusters found')
            return
        
        for clus_id in clusters:
            os.makedirs(os.path.join(synthetic_images_dir, clus_id), exist_ok=True)
            print('Cluster: {}'.format(clus_id))
            
            args = [
                "--dataroot", "%s" % os.path.join(synthetic_masks_dir, clus_id),
                "--name", "%s" % clus_id,
                "--model", "pix2pix",
                "--which_model_netG", "unet_256",
                "--which_direction", "BtoA",
                "--dataset_mode", "aligned",
                "--norm", "batch",
                "--checkpoints_dir", "%s" % checkpoints_dir,
                "--output_dir", "%s" % os.path.join(synthetic_images_dir, clus_id),
                "--fineSize", "%s" % fine_size,
                "--nThreads", "1",
                "--gpu_ids", "%s" % gpu_ids,
                "--display_id", "%s" % display_id,
            ]

            test_cus.test(args)
    
    def generate_output(self):
        # Where to put the results...
        output_dir = os.path.join(self.work_dir, self.P2P_FINAl_OUTPUT_REL_DIR)    #$WORK_DIR/out
        output_dir_images = os.path.join(output_dir, 'images')                          #$WORK_DIR/out/images
        output_dir_masks = os.path.join(output_dir, 'masks')                            #$WORK_DIR/out/masks
        print('mkdir {}'.format(output_dir_images))
        print('mkdir {}'.format(output_dir_masks))
        os.makedirs(output_dir_masks, exist_ok=True)
        os.makedirs(output_dir_images, exist_ok=True)

        # Copy the generated masks into the output
        synthetic_masks_dir = os.path.join(self.work_dir, self.P2P_TEST_MASKS_REL_DIR)      #$WORK_DIR/generated
        
        print('Checking dir: %s' % synthetic_masks_dir)
        if os.path.isdir(synthetic_masks_dir):
            clusters = os.listdir(synthetic_masks_dir)
            print(clusters)
        else:
            print('no clusters found')
            return
        
        for clus_id in clusters:
            cluster_dir = os.path.join(synthetic_masks_dir, clus_id, 'grayscale')       #$WORK_DIR/generated/grayscale
            for mask_file_name in os.listdir(cluster_dir):
                mask_path = os.path.join(cluster_dir, mask_file_name)
                mask_target_path = os.path.join(output_dir_masks, mask_file_name)
                print('cp {} {}'.format(mask_path, mask_target_path))
                shutil.copyfile(mask_path, mask_target_path)

        # Copy the generated synthetic images into the output
        synthetic_path = os.path.join(self.work_dir, self.P2P_RESULT_REL_DIR)          #$WORK_DIR/p2psynthetic
        for clus_id in os.listdir(synthetic_path):
            cluster_dir = os.path.join(synthetic_path, clus_id)
            for im_file_name in os.listdir(cluster_dir):
                im_path = os.path.join(cluster_dir, im_file_name)
                im_target_path = os.path.join(output_dir_images, im_file_name)
                print('cp {} {}'.format(im_path, im_target_path))
                shutil.copyfile(im_path, im_target_path)
