import torch
torch.backends.cudnn.enabled = True
torch.backends.cudnn.benchmark = False
torch.cuda.is_available = lambda : True

from iqradre.prod.idcard import IDCardPredictor
import matplotlib.pyplot as plt

import pandas as pd
pd.set_option("max_rows", None)
import imutils
import pathlib
import os
import cv2 as cv
import pandas as pd
import json
import shutil
import tqdm
import numpy as np
import fire




def get_result(src_path, dst_path):
    spath = pathlib.Path(src_path)
    files = list(spath.glob('*/*.jpg'))

    dpath = pathlib.Path(dst_path)
    os.makedirs(str(dpath), exist_ok = True)
    
    config = {
        'segmentor': f'../weights/segment/unet_sfeat32_v5.pth',
        'detector': f'../weights/detect/craft_ktp_ohem.pth.tar',
        'recognitor': f'../weights/recog/ocrnet_pretrained_ktp_v3.pth',
        'extractor': f'../weights/extract/layoutlm_v2_ktp_1618258716_tacc0.9929_vacc1.0_tloss0.01265_vloss1.648e-05_epoch3_cli.pth',
        'tokenizer': "indobenchmark/indobert-base-p2"   
    }

    idcard = IDCardPredictor(config, device='cuda')

    for file in tqdm.tqdm(files):
        pdir = file.parent
        dirname = pdir.name
        fstem = file.stem

        saved_path = dpath.joinpath(dirname)
        os.makedirs(str(saved_path), exist_ok = True)
        saved_path = saved_path.joinpath(fstem)
        os.makedirs(str(saved_path), exist_ok = True)

        imname = file.name


        im_ori_fname = f'{fstem}_original.jpg'
        im_score_fname = f'{fstem}_score.jpg'
        im_score_text_fname = f'{fstem}_score_text.jpg'
        im_segment_fname = f'{fstem}_segment.jpg'
        im_rotated_fname = f'{fstem}_rotated.jpg'
        im_output_fname = f'{fstem}_output.jpg'
        jsname = f'{fstem}.json'
        csvname = f'{fstem}.csv'

        predict = idcard.predict(str(file), mode='scanner', 
                                   low_text=0.2, min_size_percent=3, 
                                   dsize=(750,1000))  
        json_data = {
            'prediction': predict['prediction'],
            'times': predict['times'],
            'dirname': dirname,
            'filename': imname,
            'path': str(file)
        }

        img_score = predict['score']
        img_score = (img_score * 255).astype(np.uint8)

        img_score_text = predict['score_text']
        img_score_text = (img_score_text * 255).astype(np.uint8)

        img_rotated = predict['rotated_image']
        img_rotated = cv.cvtColor(img_rotated, cv.COLOR_BGR2RGB)

        img_segment = predict['segment_image']
        img_segment = cv.cvtColor(img_segment, cv.COLOR_BGR2RGB)

        img_output = predict['image']
        img_output = cv.cvtColor(img_output, cv.COLOR_BGR2RGB)

        dataframe = predict['dataframe']

        #save json
        with open(str(saved_path.joinpath(jsname)), "wb") as f:
            f.write(json.dumps(json_data).encode("utf-8"))

        #save dataframeimg_rotated
        dataframe.to_csv(str(saved_path.joinpath(csvname)), index=False)

        #save image
        cv.imwrite(str(saved_path.joinpath(im_score_fname)), img_score)
        cv.imwrite(str(saved_path.joinpath(im_score_text_fname)), img_score_text)

        cv.imwrite(str(saved_path.joinpath(im_rotated_fname)), img_rotated)
        cv.imwrite(str(saved_path.joinpath(im_segment_fname)), img_segment)
        cv.imwrite(str(saved_path.joinpath(im_output_fname)), img_output)

        shutil.copy(str(file), str(saved_path.joinpath(im_ori_fname)))
        
        

if __name__ == '__main__':        
    fire.Fire(get_result)