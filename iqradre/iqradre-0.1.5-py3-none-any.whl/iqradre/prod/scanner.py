import cv2 as cv
import numpy as np
import imutils
import matplotlib.pyplot as plt
from skimage.filters import threshold_local # scikit-image
from skimage.transform import rotate
from deskew import determine_skew
from iqradre.detect.ops import boxes
from . import utils


def order_points(pts):
	# initialzie a list of coordinates that will be ordered
	# such that the first entry in the list is the top-left,
	# the second entry is the top-right, the third is the
	# bottom-right, and the fourth is the bottom-left
	rect = np.zeros((4, 2), dtype = "float32")

	# the top-left point will have the smallest sum, whereas
	# the bottom-right point will have the largest sum
	s = pts.sum(axis = 1)
	rect[0] = pts[np.argmin(s)]
	rect[2] = pts[np.argmax(s)]

	# now, compute the difference between the points, the
	# top-right poi
	# nt will have the smallest difference,
	# whereas the bottom-left will have the largest difference
	diff = np.diff(pts, axis = 1)
	rect[1] = pts[np.argmin(diff)]
	rect[3] = pts[np.argmax(diff)]

	# return the ordered coordinates
	return rect

def four_point_transform(image, pts):
	# obtain a consistent order of the points and unpack them
	# individually
	rect = order_points(pts)
	(tl, tr, br, bl) = rect

	# compute the width of the new image, which will be the
	# maximum distance between bottom-right and bottom-left
	# x-coordiates or the top-right and top-left x-coordinates
	widthA = np.sqrt(((br[0] - bl[0]) ** 2) + ((br[1] - bl[1]) ** 2))
	widthB = np.sqrt(((tr[0] - tl[0]) ** 2) + ((tr[1] - tl[1]) ** 2))
	maxWidth = max(int(widthA), int(widthB))

	# compute the height of the new image, which will be the
	# maximum distance between the top-right and bottom-right
	# y-coordinates or the top-left and bottom-left y-coordinates
	heightA = np.sqrt(((tr[0] - br[0]) ** 2) + ((tr[1] - br[1]) ** 2))
	heightB = np.sqrt(((tl[0] - bl[0]) ** 2) + ((tl[1] - bl[1]) ** 2))
	maxHeight = max(int(heightA), int(heightB))

	# now that we have the dimensions of the new image, construct
	# the set of destination points to obtain a "birds eye view",
	# (i.e. top-down view) of the image, again specifying points
	# in the top-left, top-right, bottom-right, and bottom-left
	# order
	dst = np.array([
		[0, 0],
		[maxWidth - 1, 0],
		[maxWidth - 1, maxHeight - 1],
		[0, maxHeight - 1]], dtype = "float32")

	# compute the perspective transform matrix and then apply it
	M = cv.getPerspectiveTransform(rect, dst)
	warped = cv.warpPerspective(image, M, (maxWidth, maxHeight))

	# return the warped image
	return warped

def grayscale_yuv(image):
    # change the color space to YUV
    image_yuv = cv.cvtColor(image, cv.COLOR_BGR2YUV)
    
    # grap only the Y component
    image_y = np.zeros(image_yuv.shape[0:2], np.uint8)
    image_y[:, :] = image_yuv[:, :, 0]
    return image_y

def super_edges(image):
    ygray = grayscale_yuv(image)
    
    # blur the image to reduce high frequency noises
    image_blurred = cv.GaussianBlur(ygray, (3, 3), 5)
    
    morph = cv.morphologyEx(image_blurred, cv.MORPH_OPEN, np.ones((3,3), np.uint8))
    edges = cv.Canny(morph, 50, 200, apertureSize=3)
    return edges



def create_mask(image, resize_width=320):
    h,w = image.shape[:2]
    ratio = w/h
    nh, nw = int(resize_width/ratio), resize_width
    
    print(f'hw;{h,w}, nh,nw:{nh,nw}')
    
    
#     image_resize = cv.resize(image.copy(), dsize=(nw,nh), interpolation=cv.INTER_LINEAR)
    image_resize = imutils.resize(image.copy(), width=resize_width)
    ygray = grayscale_yuv(image_resize)
    
    # blur the image to reduce high frequency noises
    ygray = cv.GaussianBlur(ygray, (3, 3), sigmaX=5)    
    
    # Create horizontal kernel and dilate to connect text characters
    kernel = cv.getStructuringElement(cv.MORPH_RECT, (5,3))
    morph = cv.morphologyEx(ygray, cv.MORPH_OPEN, kernel)
    morph = cv.dilate(morph, kernel, iterations=5)
    plt.figure(figsize=(10,10))
    plt.imshow(morph, cmap='gray')
    #create edges
    ret, morph = cv.threshold(morph, 150, 240, cv.THRESH_OTSU)
    plt.figure(figsize=(10,10))
    plt.imshow(morph)
    
    edges = cv.Canny(morph, 55, 210, apertureSize=3)
    plt.figure(figsize=(10,10))
    plt.imshow(edges)
    
    # find contours in the edge map
    cnts = cv.findContours(edges.copy(), cv.RETR_TREE, cv.CHAIN_APPROX_SIMPLE)
    cnts = imutils.grab_contours(cnts)
    
    # ensure at least one contour was found
    if len(cnts) > 0:
        # grab the largest contour, then draw a mask for the pill
        c = max(cnts, key=cv.contourArea)
        mask = np.zeros(ygray.shape, dtype="uint8")
        cv.drawContours(mask, [c], -1, 255, thickness=cv.FILLED)
#         cv.fillConvexPoly(mask, c, 255, lineType=8, shift=0)
        
        # compute its bounding box of pill, then extract the ROI,
        # and apply the mask
        box = cv.boundingRect(c)
        (bx, by, bw, bh) = box
#         print(x, y, w, h)
#         image_roi = image[y:y + h, x:x + w]
#         mask_roi = mask[y:y + h, x:x + w]
#         image_roi = cv.bitwise_and(image, image, mask=mask_roi)
        
        mask = cv.resize(mask, dsize=(w,h), interpolation=cv.INTER_LINEAR)
#         mask = imutils.resize(mask, width=w, height=h)
        return mask
    else:
        return None
    

def idcard_autocrop_scanner(image, pad_factor=0.1):
    original_image = image.copy()
    
    # resize using ratio (old height to the new height)
    ratio = image.shape[0] / 500.0
    image = imutils.resize(image, height=500)
    edges = super_edges(image)
    
    
    plt.figure(figsize=(12,12))
    plt.imshow(edges, cmap='gray')
    
    contours, hierarchy = cv.findContours(edges, cv.RETR_EXTERNAL, cv.CHAIN_APPROX_SIMPLE)
    
    polygons = []
    # loop over the contours
    for cnt in contours:
        # find the convex hull
        hull = cv.convexHull(cnt)
        epsilon = 0.1 * cv.arcLength(hull, True)
        approx = cv.approxPolyDP(hull, epsilon, True)

        # compute the approx polygon and put it into polygons
        polygons.append(approx)
        
    sortedPoly = sorted(polygons, key=cv.contourArea, reverse=True)
    simplified_cnt = sortedPoly[0]

    
    # check if the polygon has four point
    if len(simplified_cnt) == 4:
        spad = simplified_cnt.reshape(4,2)
        spad = boxes.xymm2coord(boxes.pad(boxes.coord2xymm(spad.copy()), factor=pad_factor))
        spad = np.array(spad).astype(np.int32).reshape(4,1,2)
        simplified_cnt = spad
        
        # trasform the prospective of original image
        cropped_image = four_point_transform(original_image, simplified_cnt.reshape(4, 2) * ratio)
        return cropped_image, simplified_cnt.reshape(4,2)
    else:
        return None



def idcard_cropped_autodeskew(image):
    idcard_crop = image.copy()
#     h,w = idcard_crop.shape[:2]
    edges = super_edges(idcard_crop)
    
    plt.figure(figsize=(12,12))
    plt.imshow(edges, cmap='gray')
    angle = determine_skew(edges)
    rotated = rotate(image, angle, resize=True, cval=1)
    rotated = (rotated*255).astype(np.uint8)
    print('angle', angle)
    return rotated, angle

def auto_cropdeskew(impath, pad_factor=0.05, repeat=0):
    image = cv.imread(impath)
    result = idcard_autocrop_scanner(image, pad_factor=pad_factor)
    if result!=None:
        idcard_crop, box = result
        idcard_deskew, angle = idcard_cropped_autodeskew(idcard_crop)
        for i in range(repeat):
            idcard_deskew, angle_r = idcard_cropped_autodeskew(idcard_deskew)
            angle = angle + angle_r
        idcard_deskew = cv.cvtColor(idcard_deskew, cv.COLOR_BGR2RGB)
        return idcard_deskew, angle, box
    else:
        return None
    
    
    
