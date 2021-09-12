#  -*- coding: utf-8 -*-
#  Copyright (c) Huawei Technologies Co., Ltd. 2021-2021. All rights reserved.

import os


class FileUploadConstant:
    """
     资源文件类型，当前支持如下类型。上传时必须指定此字段以匹配校验规则：
     * 1--课程/会员包/专辑横版封面图片, (宽高)1280720像素，PNG/JPG格式，小于2MBytes
     * 2--宣传视频海报, (宽高)1280720像素，PNG/JPG格式, 小于2MBytes
     * 3--课程/会员包介绍图片, 宽1080像素，高度任意但不超过4096像素，PNG/JPG格式, 小于2MBytes
     * 4--教师头像, (宽高)312312像素，PNG/JPG格式, 小于0.5MBytes
     * 5--课程竖版封面图片, (宽高)405540像素，PNG/JPG格式，小于2MBytes
     * 6--专辑竖版封面图片，(宽高)1080360像素，PNG/JPG格式，小于2MBytes
    """
    RESOURCE_TYPE = {
        'COURSE_PACKAGE_HORIZONTAL_COVER': 1,
        'PROMOTIONAL_VIDEO_POSTER': 2,
        'COURSE_PACKAGE_INTRODUCTION': 3,
        'TUTOR_PORTRAIT': 4,
        'COURSE_PORTRAIT_COVER': 5,
        'ALBUM_LANDSCAPE_COVER': 6
    }

    MEDIA_FILE_TYPE = {
        'MP3': "audio/mp3",
        'WAV': "audio/wav",
        'MP4': "video/mp4",
        'MOV': "video/mov"
    }

    UPLOAD_FAILED = 'Upload failed! ErrorMessage:{}'

    # 允许上传的图片格式
    PICTURE_SUFFIX = ['.jpg', '.png']

    # 允许上传的媒体文件格式
    FILE_SUFFIX = ['.mp3', '.wav', '.mp4', '.mov']

    # 文件缓存目录
    FILE_CACHE_DIR = os.sep + 'storage' + os.sep + 'cache' + os.sep

    # 默认分片文件大小
    DEFAULT_PART_SIZE = 52428800

    # 特殊目录名
    DIR_POINT = '.'
    DIR_DUBLE_POINT = '..'

    # 相对路径正则
    RELATIVE_PATH_PATTERN = \
        '/\.\/|\.\.\/|%|\%00|\.\\\.\\\|\.\\\./'
    FILE_UPLOAD_LIMIT_TIME = 600
