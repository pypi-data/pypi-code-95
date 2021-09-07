"""
OmdenaLore module containing useful functions on image processing and image features
"""

import cv2
import glob
import mahotas
import numpy as np
import imutils
from matplotlib import pyplot as plt
import numpy as np


def surf_features(image_path):
    """
    detect SURF features from an image path

    :param image_path: Path of the input image
    :type image_path: str
    :returns: SURF keypoints detected from an image

    """

    img = cv2.imread(image_path)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    surf = cv2.xfeatures2d.SURF_create(400)
    kp, des = surf.detectAndCompute(gray, None)

    return kp


def sift_features(image_path, grayscale=True):
    """
    detect SIFT features from an image path

    :param image_path: Path of the input image
    :type image_path: str
    :param grayscale: If you want to convert your image to grayscale before calculating features
    :type grayscale: boolean
    :returns: SIFT keypoints detected from an image

    """
    im = cv2.imread(image_path)

    if grayscale:
        gray = cv2.cvtColor(im, cv2.COLOR_BGR2GRAY)
        sift = cv2.xfeatures2d.SIFT_create()
        kp = sift.detect(gray, None)
    else:
        sift = cv2.xfeatures2d.SIFT_create()
        kp = sift.detect(im, None)

    return kp


def brief_features(image_path):
    """
    detect BRIEF features from an image path

    :param image_path: Path of the input image
    :type image_path: str
    :returns: BRIEF keypoints detected from an image
    """
    im = cv2.imread(image_path)
    star = cv2.xfeatures2d.StarDetector_create()
    brief = cv2.xfeatures2d.BriefDescriptorExtractor_create()
    kps = star.detect(im, None)
    kp, des = brief.compute(im, kps)
    return kp


def haralicks_features(image_path):
    """
    Detects Harlicks features from images in meaned four directions
    inside an folder with certain extentions
    and returns array of retrieved features

    :param image_path: Path of the folder which contains the png images
    :type image_path: string

    :returns: array of extracted features. The content of array is in form - (image_name , features)
    """
    assert isinstance(image_path, str), "the path should be string"

    accepted_image_extentions = ["jpeg", "png"]

    data = []
    label = []

    for imagePaths in glob.glob(image_path + "/*"):

        # check to see if a image is of acceptable format or not
        for i in range(len(accepted_image_extentions)):
            if not imagePaths.endswith(accepted_image_extentions[i]):
                print(
                    "Extention not accepted, please add this extention to the accepted extention list"
                )
                print(imagePaths)
                return None

        # load the image, convert it into greyscalse,
        image = cv2.imread(imagePaths)
        image = cv2.cvtColor(image, cv2.COLOR_BG2GRAY)

        # extract image name form the path
        label.append(imagePaths[imagePaths.rfind("/") + 1 :])

        # extract haralicks texture features in 4 directions,
        # take mean if each direction
        features = mahotas.features.haralick(image).mean(axis=0)

        # update the data with features
        data.append(features)

    return zip(label, data)


def discribe_with_zernike_moments(image_path):
    """
    Caclulates Zernike moments of images inside a folder.
    Returns list of features and cooresponding image names
    Zernike moments are great to discribing shapes of objects.

    :param image_path: Path of images
    :type image_path: string

    :returns: return a tuple of the contours and shapes (cnts, shapefeatures)
    """

    assert isinstance(image_path, str), "the path should be string"
    accepted_image_extentions = ["jpeg", "png"]
    shapeFeatures = []

    if not image_path.endswith(accepted_image_extentions[i]):
        print(
            "Extention not accepted, please add this extention to the accepted extention list"
        )
        print(image_path)
        return None

    # load the image, convert it into greyscalse,
    image = cv2.imread(image_path)
    gray = cv2.cvtColor(image, cv2.COLOR_BG2GRAY)
    blurred = cv2.GaussianBlur(gray, (13, 13), 9)
    thresh = cv2.threshold(blurred, 50, 255, cv2.THRESH_BINARY)[1]

    # perform a series of dilations and erosions to close holes
    # in the shapes
    thresh = cv2.dilate(thresh, None, iterations=4)
    thresh = cv2.erode(thresh, None, iterations=2)

    # detect contours in the edge map
    cnts = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    cnts = imutils.grab_contours(cnts)
    # loop over the contours
    for c in cnts:
        # create an empty mask for the contour and draw it
        mask = np.zeros(image.shape[:2], dtype="uint8")
        cv2.drawContours(mask, [c], -1, 255, -1)

        # extract the bounding box ROI from the mask
        (x, y, w, h) = cv2.boundingRect(c)
        roi = mask[y : y + h, x : x + w]

        # compute Zernike Moments for the ROI and update the list
        # of shape features
        features = mahotas.features.zernike_moments(
            roi, cv2.minEnclosingCircle(c)[1], degree=8
        )
        shapeFeatures.append(features)

    # return a tuple of the contours and shapes
    return (cnts, shapeFeatures)


def find_contours(image_path, show=False):
    """
    Detect contours from an image path

    :param image_path: Path of the input image
    :type image_path: str
    :param show: Whether to show the contours on a plot using matplotlib
    :type show: boolean
    :returns: contours detected from an image
    """

    assert type(image_path) == str, "Param image_path must be of type string"
    assert type(show) == bool, "Param show must be of type bool"

    im = cv2.imread(image_path)

    # convert to RGB
    rgb_image = cv2.cvtColor(im, cv2.COLOR_BGR2RGB)
    # convert to grayscale
    gray = cv2.cvtColor(im, cv2.COLOR_RGB2GRAY)

    # create a binary thresholded image
    _, binary = cv2.threshold(gray, 225, 255, cv2.THRESH_BINARY_INV)

    gray = cv2.cvtColor(im, cv2.COLOR_BGR2GRAY)

    contours, _ = cv2.findContours(binary, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

    if show:
        image = cv2.drawContours(rgb_image, contours, -1, (0, 255, 0), 3)
        plt.imshow(image)
        plt.show()

    return contours


def get_hough_lines(image_path, show=False):
    """
    Detect lines from an image path

    :param image_path: Path of the input image
    :type image_path: str
    :param show: Whether to show the lines on a plot using matplotlib
    :type show: boolean
    :returns: lines detected from an image
    """

    assert type(image_path) == str, "Param image_path must be of type string"
    assert type(show) == bool, "Param show must be of type bool"

    img = cv2.imread(image_path)

    grayscale = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # perform edge detection
    edges = cv2.Canny(grayscale, 30, 100)

    # detect lines in the image using hough lines technique
    lines = cv2.HoughLinesP(edges, 1, np.pi / 180, 60, np.array([]), 50, 5)

    if show:
        # iterate over the output lines and draw them
        for line in lines:
            for x1, y1, x2, y2 in line:
                cv2.line(img, (x1, y1), (x2, y2), (20, 220, 20), 3)

        # show the image
        plt.imshow(img)
        plt.show()

    return lines
