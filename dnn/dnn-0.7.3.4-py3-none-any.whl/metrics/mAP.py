import glob
import json
import os
import shutil
import operator
import sys
import argparse
import math
import numpy as np

def voc_ap(rec, prec):
    rec.insert(0, 0.0) # insert 0.0 at begining of list
    rec.append(1.0) # insert 1.0 at end of list
    mrec = rec[:]
    prec.insert(0, 0.0) # insert 0.0 at begining of list
    prec.append(0.0) # insert 0.0 at end of list
    mpre = prec[:]

    for i in range(len(mpre)-2, -1, -1):
        mpre[i] = max(mpre[i], mpre[i+1])
    i_list = []
    for i in range(1, len(mrec)):
        if mrec[i] != mrec[i-1]:
            i_list.append(i) # if it was matlab would be i + 1
    ap = 0.0
    for i in i_list:
        ap += ((mrec[i]-mrec[i-1])*mpre[i])
    return ap, mrec, mpre

def get_gt_classes (ground_truth):
    gt_counter_per_class = {}
    for gt in ground_truth:
        for label in gt ['labels']:
            try:
                gt_counter_per_class [label] += 1
            except KeyError:
                gt_counter_per_class [label] = 1
    return gt_counter_per_class

def file_lines_to_list(path):
    # open txt file lines to a list
    with open(path) as f:
        content = f.readlines()
    # remove whitespace characters like `\n` at the end of each line
    content = [x.strip() for x in content]
    return content

def make_smaples ():
    GT_PATH = os.path.join(os.getcwd(), 'input', 'ground-truth')
    DR_PATH = os.path.join(os.getcwd(), 'input', 'detection-results')

    dr_files_list = glob.glob(DR_PATH + '/*.txt')
    dr_files_list.sort()

    bounding_boxes = []
    for txt_file in dr_files_list:
        #print(txt_file)
        # the first time it checks if all the corresponding ground-truth files exist
        file_id = txt_file.split(".txt",1)[0]
        file_id = os.path.basename(os.path.normpath(file_id))
        lines = file_lines_to_list(txt_file)
        boxes, labels, scores = [], [], []
        for line in lines:
            tmp_class_name, confidence, left, top, right, bottom = line.split()
            left, top, right, bottom = int (left), int (top), int (right), int (bottom)
            #print("match")
            boxes.append ([left, right, top, bottom])
            labels.append (tmp_class_name)
            scores.append (confidence)
        bounding_boxes.append ({'labels': labels, 'boxes': boxes, 'scores': scores})

    with open('pr.json', 'w') as outfile:
        json.dump(bounding_boxes, outfile)

    print (len (bounding_boxes))
    ground_truth_files_list = glob.glob(GT_PATH + '/*.txt')
    ground_truth_files_list.sort()
    bounding_boxes = []
    for txt_file in ground_truth_files_list:
        file_id = txt_file.split(".txt", 1)[0]
        file_id = os.path.basename(os.path.normpath(file_id))
        lines_list = file_lines_to_list(txt_file)
        boxes, labels = [], []
        for line in lines_list:
            if "difficult" in line:
                class_name, left, top, right, bottom, _difficult = line.split()
                is_difficult = True
            else:
                class_name, left, top, right, bottom = line.split()
            left, top, right, bottom = int (left), int (top), int (right), int (bottom)
            boxes.append ([left, right, top, bottom])
            labels.append (class_name)
        bounding_boxes.append ({'labels': labels, 'boxes': boxes})

    with open('gt.json', 'w') as outfile:
        json.dump(bounding_boxes, outfile)
    print (len (bounding_boxes))

def calcmap (ground_truth, result_dict, min_overlap = 0.5, verbose = False):
    gt_counter_per_class = get_gt_classes (ground_truth)
    gt_classes = sorted (gt_counter_per_class.keys ())
    n_classes = len(gt_classes)

    sum_AP = 0.0
    ap_dictionary = {}
    lamr_dictionary = {}
    count_true_positives = {}

    gt_data = []
    for obj in ground_truth:
        data = []
        for label, box in zip (obj ['labels'], obj ['boxes']):
            data.append ({"class_name": label, "bbox": box, "used": False})
        gt_data.append (data)

    logs = {'classes': {}}
    for class_index, class_name in enumerate (gt_classes):
        dr_data = []
        for idx, obj in enumerate (result_dict):
            for label, box, score in zip (obj ['labels'], obj ['boxes'], obj ['scores']):
                if label != class_name:
                    continue
                # print (label, box, score)
                dr_data.append ({"confidence":score, "id": idx, "bbox": box})
        dr_data.sort (key=lambda x: float(x['confidence']), reverse=True)

        count_true_positives[class_name] = 0
        nd = len(dr_data)
        tp = [0] * nd # creates an array of zeros of size nd
        fp = [0] * nd

        for idx, detection in enumerate(dr_data):
            ovmax = -1
            gt_match = -1
            xmin, xmax, ymin, ymax = detection ['bbox']
            bb = [ xmin, ymin, xmax, ymax ]

            for obj in gt_data [detection ["id"]]:
                # look for a class_name match
                if obj["class_name"] != class_name:
                    continue
                xmin, xmax, ymin, ymax = obj["bbox"]
                bbgt = [ xmin, ymin, xmax, ymax ]
                bi = [max(bb[0],bbgt[0]), max(bb[1],bbgt[1]), min(bb[2],bbgt[2]), min(bb[3],bbgt[3])]
                iw = bi[2] - bi[0] + 1
                ih = bi[3] - bi[1] + 1
                if iw > 0 and ih > 0:
                    # compute overlap (IoU) = area of intersection / area of union
                    ua = (bb[2] - bb[0] + 1) * (bb[3] - bb[1] + 1) + (bbgt[2] - bbgt[0]
                                    + 1) * (bbgt[3] - bbgt[1] + 1) - iw * ih
                    ov = iw * ih / ua
                    if ov > ovmax:
                        ovmax = ov
                        gt_match = obj

            # assign detection as true positive/don't care/false positive
            # set minimum overlap
            if ovmax >= min_overlap:
                if not bool(gt_match["used"]):
                    # true positive
                    tp[idx] = 1
                    gt_match["used"] = True
                    count_true_positives[class_name] += 1
                else:
                    # false positive (multiple detection)
                    fp[idx] = 1
            else:
                # false positive
                fp[idx] = 1

        #print(tp)
        # compute precision/recall
        cumsum = 0
        for idx, val in enumerate(fp):
            fp[idx] += cumsum
            cumsum += val
        cumsum = 0
        for idx, val in enumerate(tp):
            tp[idx] += cumsum
            cumsum += val
        #print(tp)
        rec = tp[:]
        for idx, val in enumerate(tp):
            rec[idx] = float(tp[idx]) / gt_counter_per_class[class_name]
        #print(rec)
        prec = tp[:]
        for idx, val in enumerate(tp):
            prec[idx] = float(tp[idx]) / (fp[idx] + tp[idx])
        #print(prec)

        ap, mrec, mprec = voc_ap (rec[:], prec[:])
        logs ['classes'][class_name] = {'ap': ap}
        sum_AP += ap
        text = "{0:.2f}%".format(ap*100) + " = " + class_name + " AP "
        rounded_prec = [ '%.2f' % elem for elem in prec ]
        rounded_rec = [ '%.2f' % elem for elem in rec ]
        verbose and print(text)
        ap_dictionary[class_name] = ap

    mAP = sum_AP / n_classes
    logs ['mAP'] = mAP
    text = "mAP = {0:.4f}".format(mAP)
    verbose and print(text)
    return logs


if __name__ == "__main__":
    # make_smaples ()
    with open('gt.json') as outfile:
        ground_truth = json.load(outfile)

    with open('pr.json') as outfile:
        result_dict = json.load(outfile)
    assert len (ground_truth) == len (result_dict)
    print (calcmap (ground_truth, result_dict, 0.5, True))

    '''
    22.73% = backpack AP
    85.94% = bed AP
    17.52% = book AP
    14.29% = bookcase AP
    23.48% = bottle AP
    31.86% = bowl AP
    7.93% = cabinetry AP
    53.84% = chair AP
    4.55% = coffeetable AP
    19.05% = countertop AP
    42.50% = cup AP
    39.66% = diningtable AP
    0.00% = doll AP
    20.69% = door AP
    7.69% = heater AP
    71.43% = nightstand AP
    42.86% = person AP
    17.71% = pictureframe AP
    13.01% = pillow AP
    62.31% = pottedplant AP
    73.21% = remote AP
    0.00% = shelf AP
    16.33% = sink AP
    90.48% = sofa AP
    1.39% = tap AP
    0.00% = tincan AP
    63.25% = tvmonitor AP
    18.75% = vase AP
    45.45% = wastecontainer AP
    23.53% = windowblind AP
    mAP = 31.05%
    '''

