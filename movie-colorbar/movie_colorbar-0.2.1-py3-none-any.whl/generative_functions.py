"""
Generative functions
--------------------

Created on 2019.08.28
:author: Felix Soubelet

Small module with different functions to handle color calculations on parsed images.
"""
import colorsys
import math
import random

from loguru import logger
from PIL import Image


def get_rgb_colors(source_image: Image) -> list:
    """
    Get all the rgb colors of an image.

    Args:
        source_image: a Pillow.Image instance.

    Returns:
        the list of RGB colors present in the image.
    """
    logger.trace("Extracting RBG components")
    image_rgb = source_image.convert("RGB")
    return image_rgb.getcolors(image_rgb.size[0] * image_rgb.size[1])


def get_average_rgb(source_image: Image) -> tuple:
    """
    Get the average of each R, G and B components of the colors in an image.

    Args:
        source_image: a Pillow.Image instance.

    Returns:
         a tuple of R, G and B calculated averages.
    """
    colors = get_rgb_colors(source_image)

    logger.trace("Computing average RGB components of the image")
    rgb_colors = tuple(
        sum(y[1][x] * y[0] for y in colors) / sum(z[0] for z in colors) for x in range(3)
    )
    return tuple(int(e) for e in rgb_colors)


def get_average_rgb_squared(source_image: Image) -> tuple:
    """
    Get the squared average of each R, G and B of the colors in an image.

    Args:
        source_image: a Pillow.Image instance.

    Returns:
        a tuple of R, G and B calculated squared averages.
    """
    colors = get_rgb_colors(source_image)
    logger.trace("Computing average RGB components squared of the image")
    average_rgb_squared = [
        sum((y[1][x] ** 2) * y[0] for y in colors) / float(sum(z[0] for z in colors))
        for x in range(3)
    ]

    return tuple(int(math.sqrt(x)) for x in average_rgb_squared)


def get_average_hsv(source_image: Image) -> tuple:
    """
    Get the average of each H, S and V of the colors in an image, as RGB.

    Args:
        source_image: a Pillow.Image instance.

    Returns:
        a tuple with average H, S and V of the image, as converted to RGB.
    """
    logger.trace("Extracting average HSV components of the image")
    colors = get_rgb_colors(source_image)
    colors_hsv = [(w, colorsys.rgb_to_hls(*[y / 255.0 for y in x])) for w, x in colors]
    average = [
        sum(y[1][x] * y[0] for y in colors_hsv) / sum(z[0] for z in colors_hsv) for x in range(3)
    ]
    average_rgb = colorsys.hsv_to_rgb(*average)
    return tuple(int(x * 255) for x in average_rgb)


def get_average_hue(source_image: Image) -> tuple:
    """
    Get the average hue of the colors in an image, as RGB.

    Args:
        source_image: a Pillow.Image instance.

    Returns:
        a tuple with average hue for the image, as converted to RGB.
    """
    logger.trace("Extracting average hue components of the image")
    average_hsv = get_average_hsv(source_image)
    average_hsv = colorsys.rgb_to_hsv(*[x / 255.0 for x in average_hsv])

    # Highest value and saturation
    average_hsv = [average_hsv[0], 1.0, 1.0]
    average_rgb = colorsys.hsv_to_rgb(*average_hsv)
    return tuple(int(x * 255) for x in average_rgb)


def calculate_distance_between_two_3d_points(point_1, point_2) -> float:
    """
    Get the euclidean distance between two 3d points.

    Args:
        point_1: Point 1 coordinates.
        point_2: Point 2 coordinates.

    Returns:
        Distance between those two points.
    """
    logger.trace(f"Computing Euclidean distance between {point_1} and {point_2}")
    return math.sqrt(sum((point_1[x] - point_2[x]) ** 2 for x in range(len(point_1))))


def get_kmeans_color(source_image: Image) -> tuple:
    """
    Get the average color of an image, using the kmeans method.

    Args:
        source_image: a Pillow.Image instance.

    Returns:
        a tuple of the color.
    """
    logger.trace("Starting kmeans algorithm")
    colors_rgb = get_rgb_colors(source_image)
    num_centers = 5
    centers = []

    logger.trace("Checking if number of colors is less than number of centers")
    if len(colors_rgb) < num_centers:
        centers = [x for _, x in colors_rgb]
        num_centers = len(colors_rgb)

    logger.trace("Choosing random starting centers")
    while len(centers) != num_centers:
        random_color = random.choice(colors_rgb)[1]
        if random_color not in centers:
            centers.append(random_color)

    logger.trace("Iterating on means")
    for _ in range(20):
        previous_centers = centers[:]
        color_groups = [[] for _ in range(num_centers)]
        for element in colors_rgb:
            logger.trace("Calculating the center with the smallest distance to the color")
            min_distance_index = sorted(
                range(num_centers),
                key=lambda x: calculate_distance_between_two_3d_points(centers[x], element[1]),
            )[0]
            logger.trace("Appending determined color to the group")
            color_groups[min_distance_index].append(element)

        logger.trace("Calculating new centers")
        centers = [
            tuple(sum(y[1][x] * y[0] for y in group) / sum(z[0] for z in group) for x in range(3))
            for group in color_groups
        ]

        logger.trace("Calculating center difference")
        difference = sum(
            calculate_distance_between_two_3d_points(centers[x], previous_centers[x])
            for x in range(num_centers)
        )

        logger.trace("Checking beakoff point")
        if difference < 4:
            logger.trace("Converged")
            break

    logger.trace("Getting group with largest number of colors")
    group = centers[
        sorted(range(num_centers), key=lambda x: sum(y[0] for y in color_groups[x]))[-1]
    ]
    return tuple(int(e) for e in group)


def get_most_common_colors_as_rgb(source_image: Image) -> tuple:
    """
    Get the most common color in this image, as RGB.

    Args:
        source_image: a Pillow.Image instance.

    Returns:
        a tuple with the R, G and B values of the most common color in the image.
    """
    logger.trace("Getting most common color")
    colors = source_image.getcolors(source_image.size[0] * source_image.size[1])
    return sorted(colors)[-1][1]


def get_average_xyz(source_image: Image) -> tuple:
    """
    Get the average of each X, Y and Z of the colors in an image.

    Args:
        source_image: a Pillow.Image instance.

    Returns:
        a tuple with the average X, Y and Z values of the image.
    """
    logger.trace("Extracting average XYZ components of the image.")
    colors = get_rgb_colors(source_image)
    colors_xyz = [(w, convert_rgb_to_xyz(x)) for (w, x) in colors]

    average = tuple(
        sum(y[1][x] * y[0] for y in colors_xyz) / sum(z[0] for z in colors_xyz) for x in range(3)
    )
    return convert_xyz_to_rgb(average)


def get_average_lab(source_image: Image) -> tuple:
    """
    Get the average of each Lightness, A channel and B channel values of the colors in an image.

    Args:
        source_image: a Pillow.Image instance.

    Returns:
        a tuple with the average L, A and B values of the image.
    """
    logger.trace("Extracting average LAB components of the image")
    colors = get_rgb_colors(source_image)
    colors_lab = [(w, convert_xyz_to_lab(convert_rgb_to_xyz(x))) for (w, x) in colors]
    average = tuple(
        sum(y[1][x] * y[0] for y in colors_lab) / sum(z[0] for z in colors_lab) for x in range(3)
    )
    return convert_xyz_to_rgb(convert_lab_to_xyz(average))


def get_resized_1px_rgb(source_image: Image) -> list:
    """
    Get the image's 1px by 1px equivalent, and return the R, G and B channels of this pixel.

    Args:
        source_image: a Pillow.Image instance.

    Returns:
        a tuple with the R, G and B values of the image as 1 by 1 pixel.
    """
    logger.trace("Resizing image to 1 pixel")
    return source_image.convert("RGB").resize((1, 1)).getcolors(1)[0][1]


def get_quantized_color(source_image: Image) -> list:
    """
    Use Pillow's color quantization to reduce the image to one color, then return that color.

    Args:
        source_image:

    Returns:
         a tuple with the R, G and B values of the image reduced to one collor by Pillow.
    """
    logger.trace("Quantizing image to 1 color")
    return source_image.quantize(1).convert("RGB").getcolors()[0][1]


def convert_rgb_to_xyz(source_color_rgb: tuple) -> tuple:
    """
    Converts a color from the RGB to the CIE XYZ 1931 colorspace.

    Args:
        source_color_rgb:  a tuple with R, G and B values of the color.

    Returns:
        a tuple with the X, Y, Z values of the color.
    """
    logger.trace("Converting RGB components to XYZ")
    colors = [x / 255.0 for x in source_color_rgb]

    for index in range(3):
        if colors[index] > 0.04045:
            colors[index] = ((colors[index] + 0.055) / 1.055) ** 2.4
        else:
            colors[index] /= 12.92
    colors = [100 * x for x in colors]

    x_val = colors[0] * 0.4124 + colors[1] * 0.3575 + colors[2] * 0.1805
    y_val = colors[0] * 0.2126 + colors[1] * 0.7152 + colors[2] * 0.0722
    z_val = colors[0] * 0.0193 + colors[1] * 0.1192 + colors[2] * 0.9505
    return x_val, y_val, z_val


def convert_xyz_to_rgb(source_color_xyz: tuple) -> tuple:
    """
    Converts a color from the CIE XYZ 1931 to the RGB colorspace.

    Args:
        source_color_xyz:  a tuple with X, Y and Z values of the color.

    Returns:
         a tuple with the R, G and B values of the color.
    """
    logger.trace("Converting XYZ components to RGB")
    xyz = [x / 100 for x in source_color_xyz]
    r_val = xyz[0] * 3.2406 + xyz[1] * -1.5372 + xyz[2] * -0.4986
    g_val = xyz[0] * -0.9689 + xyz[1] * 1.8758 + xyz[2] * 0.0415
    b_val = xyz[0] * 0.0557 + xyz[1] * -0.2040 + xyz[2] * 1.0570
    color = [r_val, g_val, b_val]

    for index in range(3):
        if color[index] > 0.0031308:
            color[index] = 1.055 * (color[index] ** (1 / 2.4)) - 0.055
        else:
            color[index] *= 12.92
    return tuple(int(x * 255) for x in color)


def convert_xyz_to_lab(source_color_xyz: tuple) -> tuple:
    """
    Converts a color from the CIE XYZ 1931 to the LAB colorspace.

    Args:
        source_color_xyz: a tuple with X, Y, and Z values of the color.

    Returns:
        a tuple with the Lightness, A channel and B channel values of the color.
    """
    logger.trace("Converting XYZ components to LAB")
    xyz = [source_color_xyz[0] / 95.047, source_color_xyz[1] / 100.0, source_color_xyz[2] / 108.883]

    for index in range(3):
        if xyz[index] > 0.008856:
            xyz[index] = xyz[index] ** (1.0 / 3)
        else:
            xyz[index] = (7.787 * xyz[index]) + (16.0 / 116)

    l_val = (116 * xyz[1]) - 16
    a_val = 500 * (xyz[0] - xyz[1])
    b_val = 200 * (xyz[1] - xyz[2])
    return l_val, a_val, b_val


def convert_lab_to_xyz(source_color_lab: tuple) -> tuple:
    """
    Converts a color from the LAB to the CIE XYZ 1931 colorspace.

    Args:
        source_color_lab: a tuple with the Lightness, A channel and B channel values of the color.

    Returns:
        a tuple with X, Y, and Z values of the color.
    """
    logger.trace("Converting LAB components to XYZ")
    y_val = (source_color_lab[0] + 16) / 116.0
    x_val = source_color_lab[1] / 500 + y_val
    z_val = y_val - source_color_lab[2] / 200.0
    xyz = [x_val, y_val, z_val]

    for index in range(3):
        if xyz[index] ** 3 > 0.008856:
            xyz[index] = xyz[index] ** 3
        else:
            xyz[index] = (xyz[index] - 16 / 116.0) / 7.787
    return xyz[0] * 95.047, xyz[1] * 100, xyz[2] * 108.883
