from __future__ import division
import logging
import logging.handlers
import sys
import torch
import numpy as np
import json 

logger = logging.getLogger(__name__)


def init_log(base_level=logging.INFO):
    """ initialize log output configuration """
    _formatter = logging.Formatter("%(asctime)s: %(filename)s: %(lineno)d: %(levelname)s: %(message)s")
    logger = logging.getLogger()
    logger.setLevel(base_level)

    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(_formatter)
    console_handler.setLevel(base_level)
    logger.addHandler(console_handler)


def load_json(result_json):
    """ load predicted and gold json file """
    with open(result_json, 'rb') as f:
        raw_data = json.load(f)
    return raw_data
 
def get_file_names(images):
    """ get the gold annotation information """
     
    id_file_name = {}
    file_name_id = {}
    for j in range(len(images)):
        img_item = images[j]
        iid = img_item['id']
        file_name = img_item['file_name']
        id_file_name[iid] = file_name
        file_name_id[file_name] = iid
    return id_file_name,file_name_id


def get_pre_data(pred_data,file_name_id,class_name_dict):
    '''
    转换标准数据为coco评估数据
    '''
    new_pred_data = [] 
    for j in range(len(pred_data)):
        pred_item = pred_data[j]
        filename = pred_item['filename']
        category = pred_item['category']
        score = pred_item['score']
        bndbox = pred_item['bndbox'] 
        ann_item = { "image_id": file_name_id[filename],
                    "category_id": class_name_dict[category] + 1,
                    "score": score,
                    "bbox": [
                        int(bndbox['ymin']), #0 
                        int(bndbox['xmin']), #1
                        int(bndbox['ymax']) -  int(bndbox['ymin']), #3
                        int(bndbox['xmax']) - int(bndbox['xmin']) #2
                    ] 
            }  
        new_pred_data.append(ann_item)
    return new_pred_data

def get_class(gt_data): 
    '''
    获取分类与ID字典
    '''
    class_name_list = []
    class_name_dict = {}
    catid_name_dict = {}
    for class_item in gt_data['categories']:
        if isinstance(class_item['name'], list):
            class_name_list.append(class_item['name'][0])
            class_name_dict[class_item['name'][0]] = class_item['id']
            catid_name_dict[class_item['id']] = class_item['name'][0]
        else:
            class_name_list.append(class_item['name'])
            class_name_dict[class_item['name']] = class_item['id']
            catid_name_dict[class_item['id']] = class_item['name']
    return class_name_list,class_name_dict,catid_name_dict

def get_ann(image_id, annotations):
    """ get the gold annotation information """
    ann = []
    labels = []
    for j in range(len(annotations)):
        ann_item = annotations[j]
        if ann_item['image_id'] == image_id:
            cls_id = ann_item['category_id'] - 1
            #cls_id = ann_item['category_id'] 
            x1 = ann_item['bbox'][0]  # xmin
            x2 = ann_item['bbox'][0] + ann_item['bbox'][2]  # xmax
            y1 = ann_item['bbox'][1]
            y2 = ann_item['bbox'][1] + ann_item['bbox'][3]
            labels.append(cls_id)
            if "score" in ann_item:
                pred_score = ann_item["score"]
                ann.append([x1, y1, x2, y2, pred_score, cls_id])
            else:
                ann.append([cls_id, x1, y1, x2, y2])
    return labels, np.array(ann)  

def bbox_iou(box1, box2, x1y1x2y2=True):
    """ returns the IoU of two bounding boxes """
    if not x1y1x2y2:
        # transform from center and width to exact coordinates
        b1_x1, b1_x2 = box1[:, 0] - box1[:, 2] / 2, box1[:, 0] + box1[:, 2] / 2
        b1_y1, b1_y2 = box1[:, 1] - box1[:, 3] / 2, box1[:, 1] + box1[:, 3] / 2
        b2_x1, b2_x2 = box2[:, 0] - box2[:, 2] / 2, box2[:, 0] + box2[:, 2] / 2
        b2_y1, b2_y2 = box2[:, 1] - box2[:, 3] / 2, box2[:, 1] + box2[:, 3] / 2
    else:
        # get the coordinates of bounding boxes
        b1_x1, b1_y1, b1_x2, b1_y2 = box1[:, 0], box1[:, 1], box1[:, 2], box1[:, 3]
        b2_x1, b2_y1, b2_x2, b2_y2 = box2[:, 0], box2[:, 1], box2[:, 2], box2[:, 3]

    # get the corrdinates of the intersection rectangle
    inter_rect_x1 = torch.max(b1_x1, b2_x1)
    inter_rect_y1 = torch.max(b1_y1, b2_y1)
    inter_rect_x2 = torch.min(b1_x2, b2_x2)
    inter_rect_y2 = torch.min(b1_y2, b2_y2)

    # get intersection area and union area
    inter_area = torch.clamp(inter_rect_x2 - inter_rect_x1 + 1, min=0) * torch.clamp(
        inter_rect_y2 - inter_rect_y1 + 1, min=0
    )
    b1_area = (b1_x2 - b1_x1 + 1) * (b1_y2 - b1_y1 + 1)
    b2_area = (b2_x2 - b2_x1 + 1) * (b2_y2 - b2_y1 + 1)

    iou = inter_area / (b1_area + b2_area - inter_area + 1e-16)

    return iou


def image_false_detection(pred_labels, pred_boxes, target_labels, target_boxes,
                                 iou_threshold):
    """ check if the given helmet image is false detection """
    # if the given image predictions are all wear_helmet or empty, it is not false detection
    if len(pred_labels) == 0:
        return 0, 0

    # if the given image gold labels are all wear_helmet or empty, it is false detection
    if len(target_labels) == 0:
        return 1, 1

    # the predicted no_wear_helmet boxes number is more than twice as much as
    # the gold no_wear_helmet boxes number (no iou threshold requirements), it is false detection
    if len(pred_labels) / len(target_labels) > 2:
        # print("{} / {}".format(len(pred_labels), len(target_labels)))
        return 1, 1

    target_to_pred_no_wear_idx_list = []  # the indices of the boxes that have been detected

    for pred_idx, (pred_box, pred_label) in enumerate(zip(pred_boxes, pred_labels)):
        # if the detected boxes number is the same as gold boxes, break
        if len(target_to_pred_no_wear_idx_list) == len(target_labels):
            break

        # find the max iou value and index of the iou of the predicted boxes and target boxes
        iou, box_idx = bbox_iou(pred_box.unsqueeze(0), target_boxes).max(0)

        # the conf scores of the subsequent predicted boxes are smaller, they are useless
        # even if the ious are bigger
        # if correctly predict a no_wear_helmet box
        if (iou >= iou_threshold) and (box_idx not in target_to_pred_no_wear_idx_list):
            target_to_pred_no_wear_idx_list.append(box_idx)
            return 0, 1
    return 1, 1


def image_missed_detection(pred_labels, pred_boxes, target_labels, target_boxes,
                                 iou_threshold):
    """ check if the given helmet image is missed detection """
    # if the given image gold labels are all wear_helmet or empty, it is not missed detection
    if len(target_labels) == 0:
        return 0, 0

    # if the given image predictions are all wear_helmet or empty, it is missed detection
    if len(pred_labels) == 0:
        return 1, 1

    target_to_pred_no_wear_idx_list = []  # the indices of the boxes that have been detected

    for pred_idx, (pred_box, pred_label) in enumerate(zip(pred_boxes, pred_labels)):
        # if the detected boxes number is the same as gold boxes, break
        if len(target_to_pred_no_wear_idx_list) == len(target_labels):
            break

        # find the max iou value and index of the iou of the predicted boxes and target boxes
        iou, box_idx = bbox_iou(pred_box.unsqueeze(0), target_boxes).max(0)

        # the conf scores of the subsequent predicted boxes are smaller, they are useless
        # even if the ious are bigger
        # if correctly predict a no_wear_helmet box
        if (iou >= iou_threshold) and (box_idx not in target_to_pred_no_wear_idx_list):
            target_to_pred_no_wear_idx_list.append(box_idx)
            return 0, 1
    return 1, 1


def image_object_detection(pred_labels, pred_boxes, target_labels, target_boxes,
                                 iou_threshold):
    """ detect the predicted no_wear_helmet objects for the given helmet image """
    # if the given image is a background image
    if len(target_labels) == 0:
        return 0, 0

    correct_number, total_number = 0, len(target_labels)

    # if the given image predictions are all wear_helmet or empty
    if len(pred_labels) == 0:
        return correct_number, total_number

    target_to_pred_no_wear_idx_list = []  # the indices of the boxes that have been detected

    for pred_idx, (pred_box, pred_label) in enumerate(zip(pred_boxes, pred_labels)):
        # if the detected boxes number is the same as gold boxes, break
        if len(target_to_pred_no_wear_idx_list) == len(target_labels):
            break

        # find the max iou value and index of the iou of the predicted boxes and target boxes
        iou, box_idx = bbox_iou(pred_box.unsqueeze(0), target_boxes).max(0)

        # the conf scores of the subsequent predicted boxes are smaller, they are useless
        # even if the ious are bigger
        # if correctly predict a no_wear_helmet box
        if (iou >= iou_threshold) and (box_idx not in target_to_pred_no_wear_idx_list):
            target_to_pred_no_wear_idx_list.append(box_idx)
            correct_number += 1

    return correct_number, total_number


def plot_boxes(img_path, boxes, color='yellow'):
    '''
    根据bbox画框
    '''
    from PIL import Image
    from PIL import ImageDraw,ImageFont 
    img = Image.open(img_path) 
    draw = ImageDraw.ImageDraw(img)
    font = ImageFont.truetype(font='simhei.ttf',size=np.floor(3e-2 * np.shape(img)[1] + 0.5).astype('int32'))
    for bbox in boxes: 
        if len(bbox) > 5: # 兼容检测结果
            bbox = [bbox[5] ,bbox[0],bbox[1],bbox[2] ,bbox[3]]
        cli_id = int(bbox[0]) 
        left = bbox[1]
        top = bbox[2]
        bottom = bbox[3]
        right = bbox[4]  
        # 画框框
        label = '{}'.format(cli_id) 
        label_size = draw.textsize(label, font)
        label = label.encode('utf-8')
        # print(label)
        
        if top - label_size[1] >= 0:
            text_origin = np.array([left, top - label_size[1]])
        else:
            text_origin = np.array([left, top + 1])
 
        draw.rectangle((left, top,bottom, right), outline=color)   
        draw.rectangle([tuple(text_origin), tuple(text_origin + label_size)],outline=color)
        draw.text(text_origin, str(label,'UTF-8'), fill='red', font=font) 
            
        # draw.rectangle((x, y,width, height), outline=color, width=2)   
        # font = ImageFont.truetype(font='model_data/simhei.ttf',size=np.floor(3e-2 * np.shape(img)[1] + 0.5).astype('int32'))
        # draw.text(text_origin, str(label,'UTF-8'), fill=(0, 0, 0), font=font)
    del draw
    # img.show()
    return img