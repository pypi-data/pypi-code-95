import os
import binascii
import PIL 
from PIL import Image
import cv2 as cv
import numpy as np
from pathlib import Path
import json
import re

def save_json(path, data):
    with open(path, 'w') as outfile:
        json.dump(data, outfile)
        
        
def save_list_to_file(path, list_data):
    textfile = open(path, "w")
    for element in list_data:
        textfile.write(element + "\n")
    textfile.close()
        
def save_image(path):
    pass

def random_hex(num=16):
    bstr = binascii.hexlify(os.urandom(num))
    return str(bstr, "utf-8")



def single_save(impath, prediction, root_dst_path):
    rname = str(random_hex(num=8))
    dst_path = Path(root_dst_path).joinpath(rname)
    dst_path.mkdir(parents=True, exist_ok=True)

    #save image original
    image_ori = Image.open(impath)
    ori_fname = f'{rname}_original.jpg'
    ori_path = dst_path.joinpath(ori_fname)
    image_ori.save(ori_path)
    
    #save image croped
    image_croped = Image.fromarray(prediction['image'])
    croped_fname = f'{rname}_croped.jpg'
    croped_path = dst_path.joinpath(croped_fname)
    image_croped.save(croped_path)

    #save image mask
    segment_mask_img = np.array(prediction['segment_mask'])
    segment_mask_heatmap = cv.applyColorMap(segment_mask_img, cv.COLORMAP_VIRIDIS)
    segment_mask = Image.fromarray(segment_mask_heatmap)
    segmask_fname = f'{rname}_segment_mask.jpg'
    segmask_path = dst_path.joinpath(segmask_fname)
    segment_mask.save(segmask_path)
    
    #save image mask bbox
    segment_mask_bbox_img = np.array(prediction['segment_bbox_mask'])
    segment_mask_bbox_heatmap = cv.applyColorMap(segment_mask_bbox_img, cv.COLORMAP_VIRIDIS)
    segment_mask_bbox = Image.fromarray(segment_mask_bbox_heatmap)
    segmask_bbox_fname = f'{rname}_segment_mask_bbox.jpg'
    segmask_bbox_path = dst_path.joinpath(segmask_bbox_fname)
    segment_mask_bbox.save(segmask_bbox_path)

    #save image score
    score_img = np.clip(prediction['score'], a_min=0.00, a_max=1.0)
    score_img = np.uint8(score_img * 255)
    score_heatmap = cv.applyColorMap(score_img, cv.COLORMAP_VIRIDIS)
    score = Image.fromarray(score_heatmap)
    score_fname = f'{rname}_score.jpg'
    score_path = dst_path.joinpath(score_fname)
    score.save(score_path)
    
    #save score text
    score_text_img = np.uint8(np.array(prediction['score_text']) * 255)
    score_text_heatmap = cv.applyColorMap(score_text_img, cv.COLORMAP_VIRIDIS)
    score_text = Image.fromarray(score_text_heatmap)
    score_text_fname = f'{rname}_score_text.jpg'
    score_text_path = dst_path.joinpath(score_text_fname)
    score_text.save(score_text_path)
    
    #save prediction json
    pred_data = prediction['prediction']
    pred_fname = f'{rname}_prediction.json'
    pred_path = dst_path.joinpath(pred_fname)
    save_json(pred_path, pred_data)
    
    #save times json
    times_data = prediction['times']
    times_fname = f'{rname}_times.json'
    times_path = dst_path.joinpath(times_fname)
    save_json(times_path, times_data)
    
    #save csv data
    csv_data = prediction['dataframe']
    csv_fname = f'{rname}_dataframe.csv'
    csv_path = dst_path.joinpath(csv_fname)
    csv_data.to_csv(csv_path, index=False)
    
    #save_image patches
    save_image_patches(prediction, dst_path)
    
    
    
def save_image_patches(prediction, dst_path):
    rname = random_hex(num=4)
    dst_path = Path(dst_path).joinpath('patches')
    dst_path.mkdir(parents=True, exist_ok=True)
    
    
    impatch, texts = prediction['images_patch'], prediction['texts']
    
    names_data = []
    for idx, (patch, text) in enumerate(zip(impatch, texts)):
        fname = f'{rname}_{text}.jpg'
        nfname = re.sub('[^\w\-_\. ]', '_', fname)
        fpath = dst_path.joinpath(nfname)
        img = Image.fromarray(patch)
        img.save(fpath)
        
        ndata = nfname + '\t' + text
        names_data.append(ndata)
    
    info_path = dst_path.joinpath('info.txt')
    save_list_to_file(info_path, names_data)
    
    
    
    
