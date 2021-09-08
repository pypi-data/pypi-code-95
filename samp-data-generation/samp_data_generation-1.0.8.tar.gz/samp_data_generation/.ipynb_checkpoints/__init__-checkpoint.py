import json
import cv2
import re
import random
import numpy as np
from PIL import Image
import os
import math
from skimage import exposure


def noisy(noise_typ,image):
  if noise_typ == "gaussian":
    row,col,ch= image.shape
    mean = 0
    var = 0.1
    sigma = var**0.5
    gauss = np.random.normal(mean,sigma,(row,col,ch))
    noisy = image + gauss
    return noisy

  elif noise_typ == "salt_pepper":
    row,col,ch = image.shape
    s_vs_p = 0.5
    amount = 0.004
    out = np.copy(image)
    # Salt mode
    num_salt = np.ceil(amount * image.size * s_vs_p)
    coords = [np.random.randint(0, i - 1, int(num_salt)) for i in image.shape]
    out[coords] = 1
    # Pepper mode

    num_pepper = np.ceil(amount* image.size * (1. - s_vs_p))
    coords = [np.random.randint(0, i - 1, int(num_pepper)) for i in image.shape]
    out[coords] = 0
    return out
  
  elif noise_typ == "poisson":
    vals = len(np.unique(image))
    vals = 2 ** np.ceil(np.log2(vals))
    noisy = np.random.poisson(image * vals) / float(vals)
    return noisy
  
  elif noise_typ =="speckle":
    row,col,ch = image.shape
    gauss = np.random.randn(row,col,ch)
    gauss = gauss.reshape(row,col,ch)
    noisy = image + image * gauss
    return noisy

  elif noise_typ =="gamma":
    img = exposure.adjust_gamma(image.astype(np.uint8), 7)
    noisy = img 
    return noisy

  elif noise_typ =="log":
    img = exposure.adjust_log(image.astype(np.uint8), 10)
    noisy = img 
    return noisy

def generate_noisy_dataset(input_dataset_img_dir,annotation_folder,output_dataset_dir,annotate_type="superannotate",list_of_noise=['salt_pepper']):
    '''
    :param input_dataset_img_dir: path to images (for both Superannotate & COCO Formats)
    :type input_dataset_img_dir: str
    :param annotation_folder: path to JSON annotation files (for Superannotate, this is the folder path e.g. "PATH/".  For COCO Format, this is the link to the single JSON File e.g. "PATH/COCO.json")
    :type annotation_folder: str
    :param output_dataset_dir: path where Synthetic data will be saved (for both Superannotate & COCO Formats)
    :type output_dataset_dir: str
    :param output_dataset_dir: Type of Annotation. This can either be - "superannotate" or "COCO" 
    :type output_dataset_dir: str
    :param output_dataset_dir: List of Noise to be applied during data generation. Noise can either be "gaussian", "salt_pepper", "speckle","poisson","gamma" or "log"
    :type output_dataset_dir: list
    
    '''
    try:
        os.mkdir(os.path.join(output_dataset_dir,'Image'))
        os.mkdir(os.path.join(output_dataset_dir,'Annotation'))
    
    except OSError as error:
        #folder exists
        pass
    
    if annotate_type=="superannotate":
        #generate data from Superannotate Dataset
        for filename in os.listdir(input_dataset_img_dir):
            if re.search("\.(jpg|jpeg|JPEG|png|bmp|tiff)$", filename):
                #load image
                load_img_path = os.path.join(input_dataset_img_dir, filename)
                #load annotation
                annotation_x=None
                with open(annotation_folder+filename+'___objects.json') as f:
                    annotation_x = json.load(f)
                    
                    #save image variations
                    #1. Orginal-------------------------------
                    save_img_path_tmp = os.path.join(output_dataset_dir,'Image')
                    save_img_path = os.path.join(save_img_path_tmp,filename)
                    img = Image.open(load_img_path)
                    img.save(save_img_path, 'PNG')
                    print('Saving Orginal [PNG &JSON]:'+annotation_x['metadata']['name'])

                    #write json file
                    save_json_path_tmp = os.path.join(output_dataset_dir,'Annotation')

                    with open(save_json_path_tmp+'/'+filename+'___objects.json', 'w') as sub_json:
                        json.dump(annotation_x, sub_json)

                    #loop through noise
                    for noise_index in list_of_noise:
                        tmp_filename=noise_index+'_'+filename
                        save_img_path_tmp = os.path.join(output_dataset_dir,'Image')
                        save_img_path = os.path.join(save_img_path_tmp,tmp_filename)
                        img = Image.open(load_img_path)
                        #add noise
                        img=noisy(noise_index,np.array(img))
                        img=Image.fromarray(img)
                        img.save(save_img_path, 'PNG')

                        #write json file
                        annotation_tmp=annotation_x
                        #edit annotation
                        annotation_tmp['metadata']['name']=tmp_filename
                        print('Saving '+noise_index+'Noise [PNG &JSON]:'+annotation_tmp['metadata']['name'])

                        save_json_path_tmp = os.path.join(output_dataset_dir,'Annotation')
                        with open(save_json_path_tmp+'/'+tmp_filename+'___objects.json', 'w') as sub_json:
                            json.dump(annotation_tmp, sub_json)

    elif annotate_type=="COCO":
        #load annotation
        annotation_x=None

        with open(annotation_folder) as f:
            annotation_x = json.load(f)
            print(annotation_x['images'][-1])

            print('--------------')
            old_image_list=annotation_x['images'].copy()

            #loop through existing images to generate new
            for old_image in  old_image_list:
                load_img_path = os.path.join(input_dataset_img_dir, old_image['file_name'])
                
                #Save original image
                #1. Orginal-------------------------------
                save_img_path_tmp = os.path.join(output_dataset_dir,'Image')
                save_img_path = os.path.join(save_img_path_tmp,filename)
                img = Image.open(load_img_path)
                img.save(save_img_path, 'PNG')
                print('Saving Orginal [PNG]:'+old_image['file_name'])
                
                #Generate Synthetic version
                #loop through noise
                for noise_index in list_of_noise:
                    tmp_filename=noise_index+'_'+old_image['file_name']
                    save_img_path_tmp = os.path.join(output_dataset_dir,'Image')
                    save_img_path = os.path.join(save_img_path_tmp,tmp_filename)
                    img = Image.open(load_img_path)
                    #add noise
                    img=noisy(noise_index,np.array(img))
                    img=Image.fromarray(img)
                    img.save(save_img_path, 'PNG')
                    print('Saving Orginal [PNG]:'+tmp_filename)
                    #write json file
                    new_image=old_image.copy()
                    img_process_counter=0
                    new_image['id']=annotation_x['images'][-1]['id']+1
                    new_image['file_name']=tmp_filename
                    #print(annotation_x['images'][-1])
                    annotation_x['images'].append(new_image)
                    #add Annotations
                    old_sub_annotations= [sub_annot for sub_annot in annotation_x['annotations'] if sub_annot['image_id']==int(old_image['id'])]
                    new_sub_annotations= old_sub_annotations.copy()
                    
                    for sub__ in new_sub_annotations:
                        sub__['image_id']=new_image['id']
                        sub__['id']=annotation_x['annotations'][-1]['id']+1
                        annotation_x['annotations'].append(sub__)
                    
        print('Saving COCO JSON file')
        save_json_path_tmp = os.path.join(output_dataset_dir,'Annotation')
        with open(save_json_path_tmp+'/COCO_synthetic.json', 'w') as total_json:
            json.dump(annotation_x, total_json)
    
    else:
        print('Select a Valid Annotation Type')
