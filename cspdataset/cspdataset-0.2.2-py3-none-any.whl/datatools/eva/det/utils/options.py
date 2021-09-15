# -*- coding: utf-8 -*-
import argparse


def args_parser():
    """ argument parser """
    parser = argparse.ArgumentParser()

    parser.add_argument('--contestant_submitted_file_name',  '-s',type=str, default="test_pred_simple.json",
                        help="contestant submitted json file name")
 
    parser.add_argument('--gold_json_file_path', '-t',type=str, default="test.json",
                        help="coco dataset json file name")
     
    parser.add_argument('--origin_image_file_path', '-o',type=str, default='e:/opt/local/object_detection/train1_coco_aug/images/val1',
                        help="origin image file path") 
    
    parser.add_argument('--output_image_file_path', '-i',type=str, default="",
                        help="origin image file path") 
     
    parser.add_argument('--output_voc_file_path', '-v',type=str, default="tmp",
                        help="output image file path")
    args = parser.parse_args()

    return args
