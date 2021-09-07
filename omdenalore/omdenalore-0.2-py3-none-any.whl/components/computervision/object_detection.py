import cv2
import imutils
import numpy as np

import json


def hogdetection(image_path):
    """
    Histogram of gradients-based people detection function

    :param image_path: Path of the input image
    :type image_path: str
    :returns: List of (x,y,w,h) tuples for all the bbox of people detected in the image
    :rtype: list

    """
    # Initializing the HOG person detector
    hog = cv2.HOGDescriptor()
    hog.setSVMDetector(cv2.HOGDescriptor_getDefaultPeopleDetector())

    # Reading the Image
    image = cv2.imread(image_path)

    # Resizing the Image
    image = imutils.resize(image, width=min(400, image.shape[1]))

    # Detecting all the regions in the image that has a pedestrians inside it
    (regions, _) = hog.detectMultiScale(
        image, winStride=(4, 4), padding=(4, 4), scale=1.05
    )

    return regions


def MobileNet_SSDObjectDetector(image_path):
    """
    Use MobileNet_SSD Object detector to detect classes as mentioned bellow

    CLASSES = ["background", "aeroplane", "bicycle", "bird", "boat","bottle", "bus", "car",
                "cat", "chair", "cow", "diningtable","dog", "horse", "motorbike", "person",
                "pottedplant", "sheep","sofa", "train", "tvmonitor"]

    :param image_path: Path of the image
    :type image_path: str
    :returns: This is a list of tuples and tuples are in the form (label, [bbox])
    :rtype: list of tuples

    """

    with open("./components/computervision/config.json") as d:
        config = json.load(d)

    prototxt = config["MobileNet_SSDObjectDetector"]["prototxt"]
    model = config["MobileNet_SSDObjectDetector"]["model"]

    # initialize the list of class labels MobileNet SSD was trained to
    # detect, then generate a set of bounding box colors for each class
    CLASSES = [
        "background",
        "aeroplane",
        "bicycle",
        "bird",
        "boat",
        "bottle",
        "bus",
        "car",
        "cat",
        "chair",
        "cow",
        "diningtable",
        "dog",
        "horse",
        "motorbike",
        "person",
        "pottedplant",
        "sheep",
        "sofa",
        "train",
        "tvmonitor",
    ]

    # load our serialized model from disk
    print("[INFO] loading model...")
    net = cv2.dnn.readNetFromCaffe(prototxt, model)

    # by resizing to a fixed 300x300 pixels and then normalizing it
    # (note: normalization is done via the authors of the MobileNet SSD
    # implementation)

    image = cv2.imread(image_path)
    (h, w) = image.shape[:2]
    blob = cv2.dnn.blobFromImage(
        cv2.resize(image, (300, 300)), 0.007843, (300, 300), 127.5
    )

    # pass the blob through the network and obtain the detections and
    # predictions
    print("[INFO] computing object detections...")
    net.setInput(blob)
    detections = net.forward()

    result = []

    # loop over detections
    for i in np.arange(0, detections.shape[2]):
        # extract the confidence (i.e., probability) associated with the prediction
        confidence = detections[0, 0, i, 2]

        # filter out weak detections by ensuring the `confidence` is
        # greater than the minimum confidence
        if confidence > 0.2:
            # extract the index of the class label from the `detections`,
            # then compute the (x, y)-coordinates of the bounding box for
            # the object
            idx = int(detections[0, 0, i, 1])
            box = detections[0, 0, i, 3:7] * np.array([w, h, w, h])
            (startX, startY, endX, endY) = box.astype("int")
            label = "{}: {:.2f}%".format(CLASSES[idx], confidence * 100)

            result.append(tuple(label, [box]))

    return result
