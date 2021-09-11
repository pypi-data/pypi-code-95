#! /usr/bin/env python3
"""
@author  : MG
@Time    : 2021/6/20 下午12:19
@File    : path.py
@contact : mmmaaaggg@163.com
@desc    : 
"""
import importlib
import logging
import os
from typing import Optional

from ibats_utils.transfer import is_pattern_type
from pathlib import Path

logger = logging.getLogger(__name__)

CACHE_FOLDER_PATH_DIC = {}


def get_folder_path(target_folder_name=None, create_if_not_found=True) -> Optional[str]:
    """
    获得系统缓存目录路径
    :param target_folder_name: 缓存目录名称 或 正则表达式
    :param create_if_not_found: 如果不存在则创建一个目录，默认：True，当 target_folder_name 为正则表达式时，无法创建目录
    :return: 缓存路径
    """
    global CACHE_FOLDER_PATH_DIC
    if target_folder_name is None:
        target_folder_name = 'cache'
    if target_folder_name not in CACHE_FOLDER_PATH_DIC:
        cache_folder_path_tmp = None
        logger.debug('查找数据目录path:')
        parent_folder_path = os.path.abspath(os.curdir)
        par_path = parent_folder_path
        while not os.path.ismount(par_path):
            # print 'parent path = %s'%par_path
            dir_list = os.listdir(par_path)
            for dir_name in dir_list:
                # print d # .strip()
                if is_pattern_type(target_folder_name):
                    match = target_folder_name.match(dir_name)
                    if match is not None:
                        cache_folder_path_tmp = os.path.join(par_path, dir_name)
                        logger.debug('<%s>', cache_folder_path_tmp)
                        break
                elif dir_name == target_folder_name:
                    cache_folder_path_tmp = os.path.join(par_path, dir_name)
                    logger.debug('<%s>', cache_folder_path_tmp)
                    break
            if cache_folder_path_tmp is not None:
                break
            par_path = os.path.abspath(os.path.join(par_path, os.path.pardir))
        if cache_folder_path_tmp is None:
            if create_if_not_found and not is_pattern_type(target_folder_name):
                cache_folder_path_tmp = os.path.abspath(os.path.join(parent_folder_path, target_folder_name))
                logger.debug('<%s> 创建缓存目录', cache_folder_path_tmp)
                os.makedirs(cache_folder_path_tmp)
                CACHE_FOLDER_PATH_DIC[target_folder_name] = cache_folder_path_tmp
        else:
            CACHE_FOLDER_PATH_DIC[target_folder_name] = cache_folder_path_tmp
    return CACHE_FOLDER_PATH_DIC.setdefault(target_folder_name, None)


def get_cache_file_path(cache_folder_name, file_name, create_if_not_found=True):
    """
    返回缓存文件的路径
    :param file_name: 缓存文件名称
    :param cache_folder_name: 缓存folder名称
    :param create_if_not_found: 如果不存在则创建一个目录，默认：True
    :return: 缓存文件路径
    """
    cache_folder_path = get_folder_path(cache_folder_name, create_if_not_found)
    return os.path.join(cache_folder_path, file_name)


def get_module_file_path(stg_class: type):
    module_path = stg_class.__module__
    module = importlib.import_module(module_path)
    return module.__file__


def _test_get_module_file_path():
    # from ibats_common.example.tflearn.lstm3_stg import AIStg
    from ibats_utils.pandas import DataFrame
    file_path = get_module_file_path(DataFrame)
    print(file_path)


def get_file_name_iter(dir_path, pattern="*", recursive=False):
    """递归的获取目录下的每一个文件"""
    path = Path(dir_path)
    if recursive:
        yield from path.rglob(pattern)
    else:
        yield from path.glob(pattern)


if __name__ == "__main__":
    pass
