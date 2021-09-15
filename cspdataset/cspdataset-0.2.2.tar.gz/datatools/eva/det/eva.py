
import logging.handlers
import sys,os
import torch
import traceback
import numpy as np
 
from terminaltables import AsciiTable
from datatools.eva.det.utils.utils import get_ann, image_false_detection, image_false_detection, \
    image_object_detection, init_log, load_json,get_file_names,get_pre_data,get_class,plot_boxes

from datatools.eva.det.utils.voc_xml import gen_voc_xml,gen_object
 
logger = logging.getLogger(__name__) 
  
              
def evaluate_image_score(predicted_file_json_path: str, gold_json_file_path: str, iou_threshold: float,
                                     false_detection_weight: float,
                                     missed_detection_weight: float, object_detection_weight: float):
    """ calculate the  image score by the predicted and gold json file """
    try:
        gt_data = load_json(gold_json_file_path)
        pred_data = load_json(predicted_file_json_path)
        
        id_file_name,file_name_id = get_file_names(gt_data['images'])
        class_name_list,class_name_dict,catid_name_dict = get_class(gt_data)
        
        pred_data = get_pre_data(pred_data,file_name_id,class_name_dict)
        # load the names of categories  

        ap_table = [["category","false detection rate", "missed detection rate", "object detection correct rate",
                     "image score"]]
        
        sum_false_detection_rate = 0
        sum_missed_detection_rate = 0
        sum_object_detection_correct_rate = 0
        sum_image_score = 0
        bad_cases = []
        
        for class_name in class_name_list: 
            # traverse the images, a batch of one picture
            false_detection_count = 0
            detection_total_count = 0
            missed_detection_count = 0
            gold_total_count = 0
            object_detection_correct_count = 0
            object_detection_total_count = 0
            
            for i in range(len(gt_data['images'])):
                image_id = gt_data['images'][i]['id'] 
                # load gold annotations，ann_gt = n * [cls_id, x1, y1, x2, y2]
                _, ann_gt = get_ann(image_id, gt_data['annotations'])
                # load predicted annotations，ann_pred = n * [x1, y1, x2, y2, pred_score, cls_id]
                _, ann_pred = get_ann(image_id, pred_data)
                # sort the ann pred list by the confidence pred scores in a descending order
                if len(ann_pred):
                    ann_pred = ann_pred[(-ann_pred[:, 4]).argsort()]
    
                ann_pred = torch.Tensor(ann_pred)
                ann_gt = torch.Tensor(ann_gt)
    
                # predicted no_wear boxes and labels
                if len(ann_pred) == 0:
                    pred_no_wear_indices, pred_labels, pred_boxes = [], [], []
                else:
                    pred_no_wear_indices = torch.where(ann_pred[:, -1] == class_name_dict[class_name])
                    pred_labels = ann_pred[:, -1][pred_no_wear_indices]
                    pred_boxes = ann_pred[:, :4][pred_no_wear_indices]
    
                # target no_wear boxes and labels
                if len(ann_gt) == 0:
                    target_no_wear_indices, target_labels, target_boxes = [], [], []
                else:
                    target_no_wear_indices = torch.where(ann_gt[:, 0] == class_name_dict[class_name])
                    target_labels = ann_gt[:, 0][target_no_wear_indices]
                    target_boxes = ann_gt[:, 1:][target_no_wear_indices]
    
                false_detection_number, detection_number = image_false_detection(
                    pred_labels=pred_labels, pred_boxes=pred_boxes,
                    target_labels=target_labels, target_boxes=target_boxes,
                    iou_threshold=iou_threshold)
                false_detection_count += false_detection_number
                detection_total_count += detection_number
    
                missed_detection_number, gold_no_wear_number = image_false_detection(
                    pred_labels=pred_labels, pred_boxes=pred_boxes,
                    target_labels=target_labels, target_boxes=target_boxes,
                    iou_threshold=iou_threshold)
                missed_detection_count += missed_detection_number
                gold_total_count += gold_no_wear_number
                
                if false_detection_number > 0 or missed_detection_number >0:
                    bad_cases.append(image_id)
                
                object_detection_correct_number, object_detection_total_number = image_object_detection(
                    pred_labels=pred_labels, pred_boxes=pred_boxes,
                    target_labels=target_labels, target_boxes=target_boxes,
                    iou_threshold=iou_threshold)
                object_detection_correct_count += object_detection_correct_number
                object_detection_total_count += object_detection_total_number
    
            false_detection_rate = (false_detection_count / detection_total_count) if (
                    detection_total_count != 0) else 0
            missed_detection_rate = (missed_detection_count / gold_total_count) if (
                    gold_total_count != 0) else 0
            object_detection_correct_rate = (object_detection_correct_count / object_detection_total_count) if (
                    object_detection_total_count != 0) else 0
     
            logger.info("false_detection_rate: {} / {} = {}".format(false_detection_count, detection_total_count,
                                                                    false_detection_rate))
            logger.info("missed_detection_rate: {} / {} = {}".format(missed_detection_count, gold_total_count,
                                                                     missed_detection_rate))
            logger.info("object_detection_correct_rate: {} / {} = {}".format(object_detection_correct_count,
                                                                             object_detection_total_count,
                                                                             object_detection_correct_rate))
    
            image_score = 1 - (
                    false_detection_weight * false_detection_rate + missed_detection_weight * missed_detection_rate + object_detection_weight * (
                    1 - object_detection_correct_rate))
    
            logger.info("evaluation for {} and {}\n".format(predicted_file_json_path, gold_json_file_path))
            
            ap_table += [[class_name,false_detection_rate, missed_detection_rate, object_detection_correct_rate, image_score]]
            
            sum_false_detection_rate = sum_false_detection_rate + false_detection_rate
            sum_missed_detection_rate = sum_missed_detection_rate + missed_detection_rate
            sum_object_detection_correct_rate = sum_object_detection_correct_rate + object_detection_correct_rate
            sum_image_score = sum_image_score + image_score
             
        ap_table += [['total',sum_false_detection_rate/len(class_name_list), sum_missed_detection_rate/len(class_name_list), 
                      sum_object_detection_correct_rate/len(class_name_list), sum_image_score/len(class_name_list)]]
        
        logger.info("\n{}\n".format(AsciiTable(ap_table).table))  
         
        return float('{:.8f}'.format(sum_image_score/len(class_name_list))), "评测成功",list(set(bad_cases))
    except Exception as e:
        return -1, "格式错误"
    except AssertionError:
        _, _, tb = sys.exc_info()
        traceback.print_tb(tb)
        tb_info = traceback.extract_tb(tb)
        filename, line, func, text = tb_info[-1]

        logger.info('an error occurred on line {} in statement {}'.format(line, text))

        return -1, "格式错误"


def entrance(predicted_file_json_path: str, gold_json_file_path: str): 
    score, message,bad_cases = evaluate_image_score(predicted_file_json_path=predicted_file_json_path,
                                                      gold_json_file_path=gold_json_file_path, iou_threshold=0.5,
                                                      false_detection_weight=0.3,
                                                      missed_detection_weight=0.5, object_detection_weight=0.2)
    if message != "评测成功":
        status = 0
    else:
        status = 1

    return score, message, status,bad_cases

def gen_img_badcase(predicted_file_json_path: str, gold_json_file_path: str,bad_cases: list,origin_image_file_path:str,output_image_file_path:str): 
    '''
    生成badcase (拼接图片)
    ''' 
    import skimage.io as io
    gt_data = load_json(gold_json_file_path)
    pred_data = load_json(predicted_file_json_path)
    id_file_name,file_name_id = get_file_names(gt_data['images']) 
    class_name_list,class_name_dict,catid_name_dict = get_class(gt_data)
    pred_data = get_pre_data(pred_data,file_name_id,class_name_dict) 
    for image_id in bad_cases:
        _, ann_gt = get_ann(image_id, gt_data['annotations']) 
        origin_image_path = os.path.join(origin_image_file_path,id_file_name[image_id])#step 2原始的coco的图像存放位置 
        origin_draw_img = plot_boxes(origin_image_path,ann_gt) 
        # load predicted annotations，ann_pred = n * [x1, y1, x2, y2, pred_score, cls_id]
        _, ann_pred = get_ann(image_id, pred_data)  
        pred_draw_img = plot_boxes(origin_image_path,ann_pred) 
        
        # 合并图片
        pj1 = np.zeros((origin_draw_img.size[1],origin_draw_img.size[0] + origin_draw_img.size[0],3))   #横向拼接
        pj1[:,:origin_draw_img.size[0],:] = origin_draw_img   #图片jzg在左
        pj1[:,pred_draw_img.size[0]:,:] = pred_draw_img    #图片lgz在右
        # print(pj1.dtype)   #查看数组元素类型
        
        pj1=np.array(pj1,dtype=np.uint8)   #将pj1数组元素数据类型的改为"uint8"
        
        #import matplotlib.pyplot as plt
        # plt.imshow(pj1)   #查看拼接情况
        # plt.show()
        output_image = os.path.join(output_image_file_path,id_file_name[image_id])
        io.imsave(output_image, pj1)   #保存拼接后的图片

def gen_voc_badcase(predicted_file_json_path: str, gold_json_file_path: str,bad_cases: list,origin_image_file_path:str,output_voc_file_path:str): 
    '''
    生成voc
    '''  
    gt_data = load_json(gold_json_file_path)
    pred_data = load_json(predicted_file_json_path)
    id_file_name,file_name_id = get_file_names(gt_data['images']) 
    class_name_list,class_name_dict,catid_name_dict = get_class(gt_data)
    pred_data = get_pre_data(pred_data,file_name_id,class_name_dict) 
    id_img_dict = { img_info['id']:img_info for img_info in gt_data['images']}
    for image_id in bad_cases:
        objs = []
        #_, ann_gt = get_ann(image_id, gt_data['annotations'])  
        img_info = id_img_dict[image_id]
        _, ann_pred = get_ann(image_id, pred_data)  
        for ann in ann_pred:
            xmin = int(ann[0])
            ymin = int(ann[1])
            xmax = int(ann[2])
            ymax = int(ann[3])
            
            obj = gen_object(catid_name_dict[ann[5]],xmin,ymin,xmax,ymax)
            objs.append(obj)
        xml_name = os.path.splitext(id_file_name[image_id])[0]  + '.xml'
        xml_name = os.path.join(output_voc_file_path,xml_name)
        gen_voc_xml(img_info['file_name'],objs,img_info['width'],img_info['height'],xml_name) 
        
def eva(args):
    # initialize log output configuration
    init_log(logging.INFO)

    # set predicted and gold json file paths
    predicted_file_json_path = args.contestant_submitted_file_name
    gold_json_file_path = args.gold_json_file_path
    origin_image_file_path = args.origin_image_file_path
    output_image_file_path = args.output_image_file_path
    output_voc_file_path = args.output_voc_file_path
     
    logger.info('predicted_file_json_path: {}'.format(predicted_file_json_path))
    logger.info('gold_json_file_path: {}'.format(gold_json_file_path))
    logger.info('origin_image_file_path: {}'.format(origin_image_file_path))
    logger.info('output_image_file_path: {}'.format(output_image_file_path))
    logger.info('output_voc_file_path: {}'.format(output_voc_file_path))
    
    score, message, status,bad_cases = entrance(predicted_file_json_path=predicted_file_json_path,
                                       gold_json_file_path=gold_json_file_path)

    if output_image_file_path:
        os.makedirs(output_image_file_path,exist_ok = True)
        gen_img_badcase(predicted_file_json_path,gold_json_file_path,bad_cases,origin_image_file_path,output_image_file_path)
        
    if output_voc_file_path:
        os.makedirs(output_voc_file_path,exist_ok = True)
        gen_voc_badcase(predicted_file_json_path,gold_json_file_path,bad_cases,origin_image_file_path,output_voc_file_path)
        
if __name__ == "__main__":
    from utils.options import args_parser
    args = args_parser()
    eva(args)
