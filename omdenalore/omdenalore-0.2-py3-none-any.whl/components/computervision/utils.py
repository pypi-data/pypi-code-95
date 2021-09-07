import numpy as np
from typing import Tuple, Sequence, Any
import importlib.util
from PIL import Image
import cv2
import json

try:
    import torch
except:
    print(
        "some of the functions use torch, if you use those, make sure torch is installed"
    )


class Params:
    """
    Class that loads hyperparameters from a json file.

    Example:

    >>> params = Params(json_path)
    >>> print(params.learning_rate)
    >>> params.learning_rate = 0.5  # change the value of learning_rate in params

    """

    def __init__(self, json_path: str):
        """
        :param json_path: patht to save files in
        :paramtype json_path: str:
        """
        self.update(json_path)

    def save(self, json_path: str):
        """
        Saves parameters to json file

        :param json_path: patht to save files in
        :paramtype json_path: str:
        """
        with open(json_path, "w") as f:
            json.dump(self.__dict__, f, indent=4)

    def update(self, json_path: str):
        """
        Loads parameters from json file

        :param json_path: patht to save files in
        :paramtype json_path: str:
        """
        with open(json_path) as f:
            params = json.load(f)
            self.__dict__.update(params)

    def __str__(self) -> str:
        """
        String presentation of the class Params
        """
        return str(self.__dict__)

    @property
    def dict(self):
        """
        Gives dict-like access to Params instance by `params.dict['learning_rate']`
        """
        return self.__dict__


# ----------------------------functions to check environment-------------------------------


def check_imshow():
    """
    Check if environment supports image displays

    :return: Return true of false if you can display image using opencv or not
    :rtype: Boolean
    """
    try:
        assert not isdocker(), "cv2.imshow() is disabled in Docker environments"
        cv2.imshow("test", np.zeros((1, 1, 3)))
        cv2.waitKey(1)
        cv2.destroyAllWindows()
        cv2.waitKey(1)
        return True
    except Exception as e:
        print(
            f"WARNING: Environment does not support cv2.imshow() or PIL Image.show() image displays\n{e}"
        )
        return False


# --------------------------functions related to image, bbox and masks--------------------------------


def zoom_to_fill(image, mask, padding):
    """
    Use the mask to make the object as the center object of the image with paddings

    :param image: image from which the object is taken out of
    :type image:  numpy.array
    :param mask: 2d mask array
    :type mask:  numpy.array
    :param padding: add black pixel padding around the image
    :type padding: int
    :return: Image array
    :rtype: numpy.array

    """
    assert isinstance(padding, int), "Only integers are allowed in padding"

    (y, x) = np.where(mask == 255)
    (topy, topx) = (np.min(y), np.min(x))
    (bottomy, bottomx) = (np.max(y), np.max(x))
    image = image[
        topy - padding : bottomy + padding, topx - padding : bottomx + padding
    ]

    return image


def translate_boxes(
    boxes: Sequence[Sequence[Any]], left: Tuple[int], top: Tuple[int]
) -> Sequence[Sequence[Any]]:
    """
    Translates bouding box by moving its cooridantes left-wise by `left` pixels and top-wise by `top` pixels.

    :param boxes: list of box coordinates <label> <left> <top> <right> <bottom>
    :type boxes: sequence
    :param left: Number of pixels to subtract from horizontal coordinates of the bouding box.Moving bouding box to the left is done with *left* > 0, and moving to the right with *left* < 0
    :type left: int
    :param top: Number of pixels to subtract from vertical coordinates of the bouding box. Moving bouding box top is done with *top* > 0, and moving it down with *top* < 0.
    :type top: int
    :returns: list of new box coordinates
    :rtype: list,same as input

    """

    transl_boxes = []
    for box in boxes:
        label, xmin, ymin, xmax, ymax = box
        transl_box = [
            label,
            int(xmin - left[0]),
            int(ymin - top[1]),
            int(xmax - left[0]),
            int(ymax - top[1]),
        ]
        transl_boxes.append(transl_box)

    return transl_boxes


def load_image(path: str):
    """
    Load an image at `path` using PIL and return the Image object and the width and height

    :param path: path where the image to be loaded is
    :type path: str

    :returns:
        - (PIL.Image.Image): Image object of the image
        - (int): width of the image
        - (int): height of the image

    """

    try:
        img = Image.open(path)
    except:
        print(f"Image at path {path} cannot be loaded")

    return img, img.size[0], img.size[1]


# ----------------------------functions related to type converstions of data----------------------------------


def xyxy2xywh(x):
    """
    Convert nx4 boxes from [x1, y1, x2, y2] to [x, y, w, h] where xy1=top-left, xy2=bottom-right

    :param x: array of bbox

    :returns:
        - y: array of bbox
    """

    y = x.clone()
    y[:, 0] = (x[:, 0] + x[:, 2]) / 2  # x center
    y[:, 1] = (x[:, 1] + x[:, 3]) / 2  # y center
    y[:, 2] = x[:, 2] - x[:, 0]  # width
    y[:, 3] = x[:, 3] - x[:, 1]  # height

    return y


def xywh2xyxy(x):
    """
    Convert nx4 boxes from [x, y, w, h] to [x1, y1, x2, y2] where xy1=top-left, xy2=bottom-right

    :param x: array of bbox

    :returns:
        - y: array of bbox
    """

    y = x.clone()
    y[:, 0] = x[:, 0] - x[:, 2] / 2  # top left x
    y[:, 1] = x[:, 1] - x[:, 3] / 2  # top left y
    y[:, 2] = x[:, 0] + x[:, 2] / 2  # bottom right x
    y[:, 3] = x[:, 1] + x[:, 3] / 2  # bottom right y

    return y


# ------------------functions to calculate matrices----------------------------------------------


def box_iou(box1, box2):
    """
    Return intersection-over-union (Jaccard index) of boxes.
    Both sets of boxes are expected to be in (x1, y1, x2, y2) format.

    :param box1: (Tensor[N, 4])
    :param box2: (Tensor[M, 4])
    :returns:
        - iou (Tensor[N, M]): the NxM matrix containing the pairwise IoU values for every element in boxes1 and boxes2
    """
    assert importlib.util.find_spec("torch"), "torch is not installed"

    def box_area(box):
        # box = 4xn
        return (box[2] - box[0]) * (box[3] - box[1])

    area1 = box_area(box1.T)
    area2 = box_area(box2.T)

    # inter(N,M) = (rb(N,M,2) - lt(N,M,2)).clamp(0).prod(2)
    inter = (
        (
            torch.min(box1[:, None, 2:], box2[:, 2:])
            - torch.max(box1[:, None, :2], box2[:, :2])
        )
        .clamp(0)
        .prod(2)
    )
    return inter / (
        area1[:, None] + area2 - inter
    )  # iou = inter / (area1 + area2 - inter)


def ap_per_class(tp, conf, pred_cls, target_cls):
    """
    Compute the average precision, given the recall and precision curves.
    Source: https://github.com/rafaelpadilla/Object-Detection-Metrics.

    :param tp:  True positives (nparray, nx1 or nx10).
    :param conf:  Objectness value from 0-1 (nparray).
    :param pred_cls:  Predicted object classes (nparray).
    :param target_cls:  True object classes (nparray).
    :returns:
        - The average precision as computed in py-faster-rcnn.
    """

    # Sort by objectness
    i = np.argsort(-conf)
    tp, conf, pred_cls = tp[i], conf[i], pred_cls[i]

    # Find unique classes
    unique_classes = np.unique(target_cls)
    nc = unique_classes.shape[0]  # number of classes, number of detections

    # Create Precision-Recall curve and compute AP for each class
    px, py = np.linspace(0, 1, 1000), []  # for plotting
    ap, p, r = np.zeros((nc, tp.shape[1])), np.zeros((nc, 1000)), np.zeros((nc, 1000))
    for ci, c in enumerate(unique_classes):
        i = pred_cls == c
        n_l = (target_cls == c).sum()  # number of labels
        n_p = i.sum()  # number of predictions

        if n_p == 0 or n_l == 0:
            continue
        else:
            # Accumulate FPs and TPs
            fpc = (1 - tp[i]).cumsum(0)
            tpc = tp[i].cumsum(0)

            # Recall
            recall = tpc / (n_l + 1e-16)  # recall curve
            r[ci] = np.interp(
                -px, -conf[i], recall[:, 0], left=0
            )  # negative x, xp because xp decreases

            # Precision
            precision = tpc / (tpc + fpc)  # precision curve
            p[ci] = np.interp(-px, -conf[i], precision[:, 0], left=1)  # p at pr_score

            # AP from recall-precision curve
            for j in range(tp.shape[1]):
                ap[ci, j], mpre, mrec = compute_ap(recall[:, j], precision[:, j])

    # Compute F1 (harmonic mean of precision and recall)
    f1 = 2 * p * r / (p + r + 1e-16)
    i = f1.mean(0).argmax()  # max F1 index
    return p[:, i], r[:, i], ap, f1[:, i], unique_classes.astype("int32")


def compute_ap(recall, precision):
    """
    Compute the average precision, given the recall and precision curves

    :param recall: The recall curve (list)
    :param precision: The precision curve (list)
    :returns:
        - Average precision, precision curve, recall curve
    """

    # Append sentinel values to beginning and end
    mrec = np.concatenate(([0.0], recall, [recall[-1] + 0.01]))
    mpre = np.concatenate(([1.0], precision, [0.0]))

    # Compute the precision envelope
    mpre = np.flip(np.maximum.accumulate(np.flip(mpre)))

    # Integrate area under curve
    method = "interp"  # methods: 'continuous', 'interp'
    if method == "interp":
        x = np.linspace(0, 1, 101)  # 101-point interp (COCO)
        ap = np.trapz(np.interp(x, mrec, mpre), x)  # integrate
    else:  # 'continuous'
        i = np.where(mrec[1:] != mrec[:-1])[0]  # points where x axis (recall) changes
        ap = np.sum((mrec[i + 1] - mrec[i]) * mpre[i + 1])  # area under curve

    return ap, mpre, mrec


def set_logger(log_path: str):
    """
    Sets the logger to log info in terminal and file `log_path`.
    In general, it is useful to have a logger so that every output to the terminal is saved
    in a permanent file. Here we save it to `model_dir/train.log`.
    Example:
    ```
    logging.info("Starting training...")
    ```
    :param log_path: where to log
    """
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)

    if not logger.handlers:
        # Logging to a file
        file_handler = logging.FileHandler(log_path)
        file_handler.setFormatter(
            logging.Formatter("%(asctime)s:%(levelname)s: %(message)s")
        )
        logger.addHandler(file_handler)

        # Logging to console
        stream_handler = logging.StreamHandler()
        stream_handler.setFormatter(logging.Formatter("%(message)s"))
        logger.addHandler(stream_handler)
