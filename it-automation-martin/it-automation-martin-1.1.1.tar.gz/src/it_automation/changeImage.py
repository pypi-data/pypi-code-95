#!/usr/bin/env python3
""" This module contains functions for converting images in a directory into
jpeg images.
"""
import os
from PIL import Image


def resize_image_directory(image_directory,
                           resize_width,
                           resize_height,
                           output_directory
                           ):
    """ Resizes image files in a given directory to a output directory.
    Args:
        image_directory: (string): Directory with image files to be resized.

        resize_width (int): The width in pixels of the new image.

        resize_height (int): The height in pixels of the new image.

        output_directory(string): Output directory where files will be
        saved.

    Returns:
        None
    """
    for root, dirs, files in os.walk(image_directory):
        # Ignoring hidden files and directories
        files = [f for f in files if not f[0] == '.']
        dirs[:] = [d for d in dirs if not d[0] == '.']
        for file in files:
            image_path = os.path.join(root, file)
            with Image.open(image_path) as im:
                im_resized = resize_image(im, resize_width, resize_height)
                save_image(im_resized, file, output_directory)


def resize_image(image, resize_width, resize_height):
    """ Resizes image to the given dimensions in pixels.

    Args:
        image (Image): The image to be resized.
        resize_width (int): The width in pixels of the new image.
        resize_height (int): The height in pixels of the new image.

    Returns:
        Image: Returns an Image object with new dimensions.
    """
    image_resized = image.resize((resize_width, resize_height))
    return image_resized


def save_image_jpeg(image, image_file_name, output_directory):
    """ Saves an Image object as a jpeg file to a given directory.

    Args:
        image (Image): The Image object to be saved.
        image_file_name (string): Name of file to be saved.
        output_directory (string): Directory where file will be saved.

    Returns:
        None
    """
    file_name, extension = os.path.splitext(image_file_name)
    out_file = os.path.join(output_directory , file_name + ".jpeg")
    image = image.convert('RGB')
    image.save(out_file)


def save_image(image, image_file_name, output_directory):
    out_file = os.path.join(output_directory, image_file_name)
    image.save(out_file)
    """ Saves an Image object into a file to a given directory.

    Args:
        image (Image): The Image object to be saved.
        image_file_name (string): Name of file to be saved.
        output_directory (string): Directory where file will be saved.

    Returns:
        None
    """


def convert_image(image_directory,
                  resize_width,
                  resize_height,
                  output_directory
                  ):
    """ Resizes and Converts tiff files to jpeg files in a given directory to
        a output directory.
    Args:
        image_directory: (string): Directory with tiff files to be converted.

        resize_width (int): The width in pixels of the new image.

        resize_height (int): The height in pixels of the new image.

        output_directory(string): Output directory where jpeg files will be
        saved.

    Returns:
        None
    """
    for root, dirs, files in os.walk(image_directory):
        # Ignoring hidden files and directories
        files = [f for f in files if not f[0] == '.']
        dirs[:] = [d for d in dirs if not d[0] == '.']
        for file in files:
            if '.jpeg' not in file:
                image_path = os.path.join(root, file)
                with Image.open(image_path) as im:
                    im_resized = resize_image(im, resize_width, resize_height)
                    save_image_jpeg(im_resized, file, output_directory)