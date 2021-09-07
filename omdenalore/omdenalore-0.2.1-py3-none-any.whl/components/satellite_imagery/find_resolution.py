import rasterio


def resolution(input_tiff):
    """
    Calculate the resolution of the given TIF file.

    :param input_tiff: Path to TIF file.
    :type input_tiff: str

    :returns: resolution as a (x, y) tuple
    """

    tiff = rasterio.open(input_tiff)
    # get dimensions, in units
    # 1 degree latitude is approx 111 kms
    # 1 degree longitude is approx 111 kms

    # longitude
    width = (
        (tiff.bounds.right - tiff.bounds.left) * 111 * 1000
    )  # converting kms to meters
    # latitude
    height = (tiff.bounds.top - tiff.bounds.bottom) * 111 * 1000

    # get dimentions in pixels
    px_width = tiff.width
    px_height = tiff.height
    print("Width {} , height {} in pixels".format(px_width, px_height))

    # meters in one pixel
    w = width / px_width
    h = height / px_height

    return (w, h)
