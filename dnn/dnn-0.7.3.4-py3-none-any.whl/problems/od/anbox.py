# CODEBASE: https://github.com/PacktPublishing/Advanced-Deep-Learning-with-Keras/blob/master/chapter11-detection/layer_utils.py

import numpy as np
import math
from tensorflow.keras import backend as K
import random

def stretch_box (img, box, limit = 0.3):
    h, w = img.shape [:2]
    bw = box [1] - box [0]
    bh = box [3] - box [2]
    newbox = np.array ([
        max (0, box [0] - bw * (random.random () * limit)),
        min (w, box [1] + bw * (random.random () * limit)),
        max (0, box [2] - bh * (random.random () * limit)),
        min (h, box [3] + bh * (random.random () * limit)),
    ])
    return newbox.astype (np.int32)

def nms (preds, offsets, anchors, class_threshold, iou_threshold, detect_threshold, soft_nms = True, normalize = False):
    if normalize:
        anchors_centroid = minmax2centroid (anchors)
        offsets[:, 0:2] *= 0.1
        offsets[:, 0:2] *= anchors_centroid[:, 2:4]
        offsets[:, 0:2] += anchors_centroid[:, 0:2]
        offsets[:, 2:4] *= 0.2
        offsets[:, 2:4] = np.exp(offsets[:, 2:4])
        offsets[:, 2:4] *= anchors_centroid[:, 2:4]
        offsets = centroid2minmax (offsets)
        # convert fr cx,cy,w,h to real offsets
        offsets[:, 0:4] = offsets[:, 0:4] - anchors

    preds = preds.copy () # original preds is read only
    # get all non-zero (non-background) objects
    objects = np.argmax(preds, axis=1)
    # non-zero indexes are not background
    nonbg = np.nonzero(objects)[0]

    if nonbg.size > detect_threshold:
        # too many detections, assumming failure
        # added by Hans June 9, 2021
        nonbg = np.array ([], dtype = np.int32)

    # D and S indexes in Line 1
    indexes = []
    while True:
        # list of zero probability values
        scores = np.zeros((preds.shape[0],))
        # set probability values of non-background
        scores[nonbg] = np.amax(preds[nonbg], axis=1)

        # max probability given the list
        # Lines 3 and 4
        score_idx = np.argmax(scores, axis=0)
        score_max = scores[score_idx]

        # get all non max probability & set it as new nonbg
        # Line 5
        nonbg = nonbg[nonbg != score_idx]

        # if max obj probability is less than threshold (def 0.8)
        if score_max < class_threshold:
            # we are done
            break

        # Line 5
        indexes.append(score_idx)
        score_anc = anchors[score_idx]
        score_off = offsets[score_idx][0:4]
        score_box = score_anc + score_off
        score_box = np.expand_dims(score_box, axis=0)
        nonbg_copy = np.copy(nonbg)

        # get all overlapping predictions (Line 6)
        # perform Non-Max Suppression (NMS)
        for idx in nonbg_copy:
            # hans roh Aug 17, 2021: skip if not the same class
            if (objects [idx] != objects [score_idx]):
                continue

            anchor = anchors[idx]
            offset = offsets[idx][0:4]
            box = anchor + offset
            box = np.expand_dims(box, axis=0)
            iou_ = iou(box, score_box)[0][0]
            # if soft NMS is chosen (Line 7)
            if soft_nms:
                # adjust score: Line 8
                iou_ = -2 * iou_ * iou_
                preds[idx] *= math.exp(iou_)
            # else NMS (Line 9), (iou threshold def 0.2)
            elif iou_ >= iou_threshold:
                # remove overlapping predictions with iou>threshold
                # Line 10
                nonbg = nonbg[nonbg != idx]

        # Line 2, nothing else to process
        if nonbg.size == 0:
            break

    # get the array of object scores
    scores = np.zeros((preds.shape[0],))
    scores[indexes] = np.amax(preds[indexes], axis=1)
    return objects, indexes, scores, offsets

def generate_anchors (feature_shapes, input_shape, n_layers = 4, aspect_ratios = (1, 2, 0.5)):
    all_anchors = []
    for index, feature_shape in enumerate (feature_shapes):
        anchors = anchor_boxes(feature_shape, input_shape, index, n_layers, aspect_ratios = aspect_ratios)
        anchors = np.reshape(anchors, [-1, 4])
        all_anchors.extend (anchors)
    return np.array (all_anchors)

def anchor_sizes (n_layers=4):
    s = np.linspace(0.2, 0.9, n_layers + 1)
    sizes = []
    for i in range(len(s) - 1):
        # size = [s[i], (s[i] * 0.5)]
        size = [s[i], math.sqrt(s[i] * s[i + 1])]
        sizes.append(size)
    return sizes

def anchor_boxes (feature_shape, image_shape, index = 0, n_layers = 4, aspect_ratios = (1, 2, 0.5)):
    # anchor box sizes given an index of layer in ssd head
    sizes = anchor_sizes(n_layers)[index]
    # number of anchor boxes per feature map pt
    n_boxes = len(aspect_ratios) + 1
    # ignore number of channels (last)
    image_height, image_width, _ = image_shape
    # ignore number of feature maps (last)
    feature_height, feature_width, _ = feature_shape

    # normalized width and height
    # sizes[0] is scale size, sizes[1] is sqrt(scale*(scale+1))
    norm_height = image_height * sizes[0]
    norm_width = image_width * sizes[0]
    # list of anchor boxes (width, height)
    width_height = []
    # anchor box by aspect ratio on resized image dims
    # Equation 11.2.3
    for ar in aspect_ratios:
        box_width = norm_width * np.sqrt(ar)
        box_height = norm_height / np.sqrt(ar)
        width_height.append((box_width, box_height))
    # multiply anchor box dim by size[1] for aspect_ratio = 1
    # Equation 11.2.4
    box_width = image_width * sizes[1]
    box_height = image_height * sizes[1]
    width_height.append((box_width, box_height))

    # now an array of (width, height)
    width_height = np.array(width_height)

    # dimensions of each receptive field in pixels
    grid_width = image_width / feature_width
    grid_height = image_height / feature_height

    # compute center of receptive field per feature pt
    # (cx, cy) format
    # starting at midpoint of 1st receptive field
    start = grid_width * 0.5
    # ending at midpoint of last receptive field
    end = (feature_width - 0.5) * grid_width
    cx = np.linspace(start, end, feature_width)

    start = grid_height * 0.5
    end = (feature_height - 0.5) * grid_height
    cy = np.linspace(start, end, feature_height)

    # grid of box centers
    cx_grid, cy_grid = np.meshgrid(cx, cy)
    # for np.tile()
    cx_grid = np.expand_dims(cx_grid, -1)
    cy_grid = np.expand_dims(cy_grid, -1)

    # tensor = (feature_map_height, feature_map_width, n_boxes, 4)
    # aligned with image tensor (height, width, channels)
    # last dimension = (cx, cy, w, h)
    boxes = np.zeros((feature_height, feature_width, n_boxes, 4))

    # (cx, cy)
    boxes[..., 0] = np.tile(cx_grid, (1, 1, n_boxes))
    boxes[..., 1] = np.tile(cy_grid, (1, 1, n_boxes))

    # (w, h)
    boxes[..., 2] = width_height[:, 0]
    boxes[..., 3] = width_height[:, 1]

    # convert (cx, cy, w, h) to (xmin, xmax, ymin, ymax)
    # prepend one dimension to boxes
    # to account for the batch size = 1
    boxes = centroid2minmax(boxes)

    boxes = np.expand_dims(boxes, axis=0)
    return boxes

def centroid2minmax (boxes):
    minmax= np.copy(boxes).astype(np.float)
    minmax[..., 0] = boxes[..., 0] - (0.5 * boxes[..., 2])
    minmax[..., 1] = boxes[..., 0] + (0.5 * boxes[..., 2])
    minmax[..., 2] = boxes[..., 1] - (0.5 * boxes[..., 3])
    minmax[..., 3] = boxes[..., 1] + (0.5 * boxes[..., 3])
    return minmax

def minmax2centroid (boxes):
    centroid = np.copy(boxes).astype(np.float)
    centroid[..., 0] = 0.5 * (boxes[..., 1] - boxes[..., 0])
    centroid[..., 0] += boxes[..., 0]
    centroid[..., 1] = 0.5 * (boxes[..., 3] - boxes[..., 2])
    centroid[..., 1] += boxes[..., 2]
    centroid[..., 2] = boxes[..., 1] - boxes[..., 0]
    centroid[..., 3] = boxes[..., 3] - boxes[..., 2]
    return centroid

def get_ground_truth (iou,
                n_classes=4,
                anchors=None,
                labels=None,
                normalize=False,
                threshold=0.6,
                additional_classes = []):

    # each maxiou_per_get is index of anchor w/ max iou
    # for the given ground truth bounding box
    maxiou_per_gt = np.argmax(iou, axis=0)
    # get extra anchor boxes based on IoU
    if threshold < 1.0:
        iou_gt_thresh = np.argwhere(iou>threshold)
        if iou_gt_thresh.size > 0:
            extra_anchors = iou_gt_thresh[:,0]
            extra_classes = iou_gt_thresh[:,1]
            #extra_labels = labels[:,:][extra_classes]
            extra_labels = labels[extra_classes]
            indexes = [maxiou_per_gt, extra_anchors]
            maxiou_per_gt = np.concatenate(indexes,
                                           axis=0)
            labels = np.concatenate([labels, extra_labels],
                                    axis=0)

    maxiou_col = np.reshape(maxiou_per_gt, (maxiou_per_gt.shape[0], 1))

    # mask generation
    gt_mask = np.zeros((iou.shape[0], 4))
    # only indexes maxiou_per_gt are valid bounding boxes
    gt_mask[maxiou_per_gt] = 1.0
    # class generation
    gt_class = np.zeros((iou.shape[0], n_classes))
    # by default all are background (index 0)
    gt_class[:, 0] = 1
    # but those that belong to maxiou_per_gt are not
    gt_class[maxiou_per_gt, 0] = 0
    # we have to find those column indexes (classes)
    label_col = np.reshape(labels[:,-1], (labels.shape[0], 1)).astype(int)
    row_col = np.append(maxiou_col, label_col, axis=1)
    # the label of object in maxio_per_gt
    gt_class[row_col[:,0], row_col[:,1]] = 1.0

    gt_extras = []
    if additional_classes:
        assert labels.shape [1] == 5 + len (additional_classes)
        for idx, n_extra in enumerate (additional_classes):
            gt_extra = np.zeros ((iou.shape[0], n_extra))
            label_col = np.reshape(labels[:,idx + 4], (labels.shape[0], 1)).astype(int)
            row_col = np.append(maxiou_col, label_col, axis=1)
            gt_extra[row_col[:,0], row_col[:,1]] = 1.0
            gt_extras.append (gt_extra)
    # offsets generation
    gt_offset = np.zeros((iou.shape[0], 4))

    #(cx, cy, w, h) format
    if normalize:
        anchors = minmax2centroid(anchors)
        labels = minmax2centroid(labels)
        # bbox = bounding box
        # ((bbox xcenter - anchor box xcenter)/anchor box width)/.1
        # ((bbox ycenter - anchor box ycenter)/anchor box height)/.1
        # Equation 11.4.8
        offsets1 = labels[:, 0:2] - anchors[maxiou_per_gt, 0:2]
        offsets1 /= anchors[maxiou_per_gt, 2:4]
        offsets1 /= 0.1

        # log(bbox width / anchor box width) / 0.2
        # log(bbox height / anchor box height) / 0.2
        # Equation 11.4.8
        offsets2 = np.log(labels[:, 2:4]/anchors[maxiou_per_gt, 2:4])
        offsets2 /= 0.2

        offsets = np.concatenate([offsets1, offsets2], axis=-1)

    # (xmin, xmax, ymin, ymax) format
    else:
        offsets = labels[:, 0:4] - anchors[maxiou_per_gt]

    gt_offset[maxiou_per_gt] = offsets

    return gt_class, gt_offset, gt_mask, gt_extras

def merge_aligned_near_boxes_by_label (boxes, size, closed = 10, direction = 'a'):
    def sort_boxes (boxes):
        # return boxes [np.lexsort ((boxes [:,2], boxes [:,0]))]
        boxes = boxes.tolist ()
        boxes.sort (key = lambda x: (x [2], x [0]))
        return np.array (boxes)

    def merge_one (boxes, size, direction, closed = 10):
        w, h = size
        boxes = np.array (boxes).copy ()
        boxes [:,:4] = np.array (boxes) [:,:4] + [-1, 1, -1, 1]
        boxes [:,:4] = np.clip (boxes [:,:4], [0, 0, 0, 0], [w, w, h, h])
        boxes = sort_boxes (boxes)
        for i in range (boxes.shape [0]):
            label1 = boxes [i][-1] if len (boxes [i]) > 4 else None
            box1 = boxes [i][:4]
            merged = False
            for j in range (i + 1, boxes.shape [0]):
                label2 = boxes [j][-1] if len (boxes [j]) > 4 else None
                if label1 != label2:
                    continue
                box2 = boxes [j][:4]
                if direction == 'h' and abs (box1 [1] - box2 [0]) <= closed:
                    # approx same vertical position
                    if abs (box1 [2] - box2 [2]) <= closed and abs (box1 [3] - box2 [3]) <= closed:
                        merged = True

                if direction == 'v' and abs (box1 [3] - box2 [2]) <= closed:
                    # approx same h pos
                    if abs (box1 [0] - box2 [0]) <= closed and abs (box1 [1] - box2 [1]) <= closed:
                        merged = True

                if merged:
                    merged_box = np.concatenate ([[
                        min (box1 [0], box2 [0]),
                        max (box1 [1], box2 [1]),
                        min (box1 [2], box2 [2]),
                        max (box1 [3], box2 [3])
                    ], boxes [i][4:]])
                    removables = [i, j]
                    break

            if merged:
                break

        if merged:
            new_boxes = [merged_box] + [box for i, box in enumerate (boxes) if i not in removables]
            boxes = np.array (new_boxes)
            boxes [:,:4] = boxes [:,:4] + [1, -1, 1, -1]
            boxes [:,:4] = np.clip (boxes [:,:4], [0, 0, 0, 0], [w, w, h, h])

        return boxes

    while direction in 'av':
        before = len (boxes)
        boxes = merge_one (boxes, size, 'v', closed)
        if len (boxes) == before:
            break

    while direction in 'ah':
        before = len (boxes)
        boxes = merge_one (boxes, size, 'h', closed)
        if len (boxes) == before:
            break

    return boxes


def remove_overlapped_boxes (labels, overlap_thresh = 0.5):
    def sort_boxes (boxes):
        boxes = np.array (boxes)
        boxes = boxes.tolist ()
        boxes.sort (key = lambda x: ((x [1] - x [0]) * (x [3] - x [2])), reverse = True)
        return np.array (boxes)

    if len (labels) == 1:
        return labels

    r = []
    labels = sort_boxes (labels)
    for lb in labels:
        if not r:
            r.append (lb)
            continue

        area = (lb [1] - lb [0]) * (lb [3] - lb [2])
        inst = intersection (np.array (r), np.array ([lb])) [0]
        overlapped = inst / area
        overlapped = np.sort (overlapped)
        overlapped
        if overlapped [-1] > overlap_thresh:
            # ignoring
            continue
        r.append (lb)
    return np.array (r)


# split_polyline_by_lines -----------------------------
def point_in_box (p, box):
    if p [0] < box [0] or p [0] > box [1]:
        return False
    elif p [1] < box [2] or p [1] > box [3]:
        return False
    return True

def split_polyline_by_line (base_line, polyline):
    line = base_line
    bxA = np.min (line [:,0]), np.max (line [:,0]) + 1, np.min (line [:,1]), np.max (line [:,1]) + 1
    polylines = []
    P = [polyline [0]]
    for b1, b2 in zip (polyline [:-1], polyline [1:]):
        B = np.array ((b1, b2))
        bxB = np.min (B [:,0]), np.max (B [:,0]) + 1, np.min (B [:,1]), np.max (B [:,1]) + 1
        try:
            t, s = np.linalg.solve (np.array([line [1] - line [0], B [0]-B [1]]).T, B [0] - line [0])
        except:
            cross = None
        else:
            cross = ((1 - t) * line [0] + t * line [1]).astype (np.int)
            if not point_in_box (cross, bxA):
                cross = None
            elif not point_in_box (cross, bxB):
                cross = None

        if cross is None:
            P.append (b2)
            continue

        P.append (cross)
        polylines.append (np.array (P).astype (np.int))
        P = [cross, b2]

    if len (P) > 1:
        polylines.append (np.array (P).astype (np.int))
    return polylines

def split_polyline_by_lines (base_lines, polyline):
    polylines = split_polyline_by_line (base_lines [0], polyline)
    for line in base_lines [1:]:
        polylines_ = []
        for polyline in polylines:
            polylines_.extend (split_polyline_by_line (line, polyline))
        polylines = polylines_
    return polylines


# box operations -----------------------------------
def intersect_boxes (boxA, boxB):
    x1 = max (boxA [0], boxB [0])
    x2 = min (boxA [1], boxB [1])
    y1 = max (boxA [2], boxB [2])
    y2 = min (boxA [3], boxB [3])
    if x2 - x1 <= 0 or y2 - y1 <= 0:
        return
    return (x1, x2, y1, y2)

def remove_overlap (boxA, boxB, keep = 'first'):
    # 1. 큰 박스는 남긴다
    # 2. 작은 박스는 인터섹션 부분을 트림하되, 최대 면적이 될 수 있도록 조정
    assert keep in ('first', 'bigger', 'smaller')
    boxA = np.array (boxA)
    boxB = np.array (boxB)

    _keep = boxA
    _trim = boxB
    _swapped = False
    if keep != 'first':
        areaA = (boxA [1] - boxA [0]) * (boxA [3] - boxA [2])
        areaB = (boxB [1] - boxB [0]) * (boxB [3] - boxB [2])
        if keep == 'bigger' and areaA < areaB:
            _keep = boxB
            _trim = boxA
            _swapped = True
        elif keep == 'smaller' and areaA > areaB:
            _keep = boxB
            _trim = boxA
            _swapped = True

    ib = intersect_boxes (boxA, boxB)
    if ib is None:
        return boxA, boxB

    # 가로절단
    trimh = _trim.copy ()
    if ib [0] == _trim [0]:
        trimh [0] = ib [1]
    else:
        trimh [1] = ib [0]

    # 세로 절단
    trimv = _trim.copy ()
    if ib [2] == _trim [2]:
        trimv [2] = ib [3]
    else:
        trimv [3] = ib [2]

    areaA = (trimh [1] - trimh [0]) * (trimh [3] - trimh [2])
    areaB = (trimv [1] - trimv [0]) * (trimv [3] - trimv [2])
    if _swapped:
        return np.array ([trimh if areaA > areaB else trimv, _keep])
    return np.array ([_keep, trimh if areaA > areaB else trimv])

def remove_overlaps (mboxes, keep = 'first'):
    def _seperate_once (mboxes):
        adjusted = False
        for idx, box in enumerate (mboxes):
            stand = box
            others = mboxes [idx + 1:]
            if len (others) == 0:
                break

            intsects = intersection (np.array ([stand]), np.array (others))
            for j, intersect in enumerate (intsects [0]):
                stand, others [j]
                if intersect == 0:
                    continue
                adjusted = True
                a, b = remove_overlap (stand, others [j], keep)
                mboxes [idx] = a
                mboxes [idx + 1 + j] = b
                break

            if adjusted:
                break

        return adjusted, mboxes

    mboxes = np.array (mboxes).copy ()
    # iterating until all seperated
    adjusted = True
    while adjusted:
        adjusted, mboxes = _seperate_once (mboxes)
    return mboxes


# IoU ----------------------------------------------
def intersection (boxes1, boxes2):
    m = boxes1.shape[0] # The number of boxes in `boxes1`
    n = boxes2.shape[0] # The number of boxes in `boxes2`

    xmin = 0
    xmax = 1
    ymin = 2
    ymax = 3

    boxes1_min = np.expand_dims(boxes1[:, [xmin, ymin]], axis=1)
    boxes1_min = np.tile(boxes1_min, reps=(1, n, 1))
    boxes2_min = np.expand_dims(boxes2[:, [xmin, ymin]], axis=0)
    boxes2_min = np.tile(boxes2_min, reps=(m, 1, 1))
    min_xy = np.maximum(boxes1_min, boxes2_min)

    boxes1_max = np.expand_dims(boxes1[:, [xmax, ymax]], axis=1)
    boxes1_max = np.tile(boxes1_max, reps=(1, n, 1))
    boxes2_max = np.expand_dims(boxes2[:, [xmax, ymax]], axis=0)
    boxes2_max = np.tile(boxes2_max, reps=(m, 1, 1))
    max_xy = np.minimum(boxes1_max, boxes2_max)

    side_lengths = np.maximum(0, max_xy - min_xy)

    intersection_areas = side_lengths[:, :, 0] * side_lengths[:, :, 1]
    return intersection_areas

def union (boxes1, boxes2, intersection_areas):
    m = boxes1.shape[0] # number of boxes in boxes1
    n = boxes2.shape[0] # number of boxes in boxes2

    xmin = 0
    xmax = 1
    ymin = 2
    ymax = 3

    width = (boxes1[:, xmax] - boxes1[:, xmin])
    height = (boxes1[:, ymax] - boxes1[:, ymin])
    areas = width * height
    boxes1_areas = np.tile(np.expand_dims(areas, axis=1), reps=(1,n))
    width = (boxes2[:,xmax] - boxes2[:,xmin])
    height = (boxes2[:,ymax] - boxes2[:,ymin])
    areas = width * height
    boxes2_areas = np.tile(np.expand_dims(areas, axis=0), reps=(m,1))

    union_areas = boxes1_areas + boxes2_areas - intersection_areas
    return union_areas

def iou_v1 (boxes1, boxes2):
    intersection_areas = intersection(boxes1, boxes2)
    union_areas = union(boxes1, boxes2, intersection_areas)
    return intersection_areas / union_areas

def iou_v2 (bboxes1, bboxes2):
    x11, x12, y11, y12 = np.split(bboxes1, 4, axis=1)
    x21, x22, y21, y22 = np.split(bboxes2, 4, axis=1)
    xA = np.maximum(x11, np.transpose(x21))
    yA = np.maximum(y11, np.transpose(y21))
    xB = np.minimum(x12, np.transpose(x22))
    yB = np.minimum(y12, np.transpose(y22))
    interArea = np.maximum((xB - xA), 0) * np.maximum((yB - yA), 0)
    boxAArea = (x12 - x11) * (y12 - y11)
    boxBArea = (x22 - x21) * (y22 - y21)
    return interArea / ((boxAArea + np.transpose(boxBArea) - interArea) + 1e-7)

iou = iou_v2
