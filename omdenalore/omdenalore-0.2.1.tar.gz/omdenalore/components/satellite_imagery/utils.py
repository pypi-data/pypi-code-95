import gdal
import numpy as np


def convert_pixels_to_geocoordinates(source_tiff_path, list_of_coords):

    """
    This function convert pixel coordinates into geo coordinates according to the transform informaton inside the source tiff file

    :param source_tiff_path: The source tiff file path from which the bounding box was predicted. Tiff file should contain geo-transform information
    :type source_tiff_path: string
    :param list_of_coords: list of coordinates in the form of ((x1, y1), (x2,y2), (x3,y3)...(xn, yn))
    :type bbox: List of list

    :returns: List of geo-coordinates

    """
    assert isinstance(source_tiff_path, str), "input source path should be string"

    tile = gdal.open(source_tiff_path)
    geotrans = tile.GetGeoTransform()

    # extract coefficients used to transform pixels to geo-grid points
    x_min = geotrans[0]
    x_size = geotrans[1]
    y_min = geotrans[3]
    y_size = geotrans[5]

    # create empty nx2 array with same length as origninal mask
    geocoords = np.empty([len(list_of_coords), 2], dtype=float)

    # convert all points to geo coordinates
    for i in range(len(list_of_coords)):
        geocoords[i][0] = list_of_coords[i][0] * x_size + x_min  # x pixel
        geocoords[i][1] = list_of_coords[i][1] * y_size + y_min  # y pixel

    return geocoords


def create_contours(coords):
    """
    Converting the coordinates of the masks to numpy array

    :param coords: List of Coordinates in the form the form of ((x1, y1), (x2,y2), (x3,y3)...(xn, yn))
    :type coords: List of lists

    :returns: list of contours in numpy format
    """
    cnts = []
    contours = coords
    maxlength = max(map(len, contours))

    for contour in contours:
        contour_arr = np.zeros(maxlength, dtype=np.int32)
        contour_arr[: len(contour)] = contour
        cnts.append(contour_arr)

    final_cnts = np.array(cnts)
    return final_cnts


def zoom_to_fill(image, mask, padding_val=0):
    """
    Use the mask of the object to center the object in the image and zoom to that object

    :param image: Input Image
    :type image: numpy array
    :param mask: Mask of the object that you want to center
    :type mask: numpy array
    :param padding_val: number of pixel padding to add around the centered object
    :type padding_val: int

    :returns: Numpy image with centered object

    """
    (y, x) = np.where(mask == 255)
    (topy, topx) = (np.min(y), np.min(x))
    (bottomy, bottomx) = (np.max(y), np.max(x))
    image = image[
        topy - padding_val : bottomy + padding_val,
        topx - padding_val : bottomx + padding_val,
    ]

    return image


def add_padding(image, padding_height, padding_width, color=(0, 0, 0)):
    """
    add padding around the image so that buildings touching the corners can be bought to center
    create new image of desired size and color (black) for padding
    This is necessary as corner buildings will not be detected by countour detection algorithm if the building edges are outsite of the image

    :param images: Image that you want padding around
    :type image: Numpy array
    :param padding_height: Amount of padding in y direction
    :type padding_height: int
    :param padding_width: Amount of padding in x direction
    :param padding_width: int
    :param color: RGB color of the padding
    :type color: 1x3 tuple

    :returns: Image with padding
    """
    ht, wd, cc = image.shape
    ww = wd + padding_width
    hh = ht + padding_height
    padded = np.full((hh, ww, cc), color, dtype=np.uint8)

    # compute center offset
    xx = (ww - wd) // 2
    yy = (hh - ht) // 2

    # copy img image into center of RGB_padded image
    padded[yy : yy + ht, xx : xx + wd] = image

    return padded
