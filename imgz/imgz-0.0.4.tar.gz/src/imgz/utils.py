# -*- coding: utf8 -*-

from xlang import iox

# 图片后缀名
SUFFIX_IMAGE = ['.jpg', '.png', '.jpeg', '.bmp']


def is_image_file(file_path):
    _, _, suffix = iox.split_path(file_path)

    return suffix.lower() in SUFFIX_IMAGE
