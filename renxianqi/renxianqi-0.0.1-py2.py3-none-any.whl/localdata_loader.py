#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time : 2021/8/31 2:43 下午
# @Author : LeiXueWei
# @CSDN/Juejin/Wechat: 雷学委
# @XueWeiTag: CodingDemo
# @File : localdata_loader.py
# @Project : hello

import os

import pinyin_sort

cur = os.getcwd()
_DATA_DIR = os.path.join(cur, "data")
DATA_DIR = {"value": _DATA_DIR}


def load_file(infile, opt=0):
    data = ''
    print("will load %s " % infile)
    if opt == 1:
        with open(os.path.join(DATA_DIR['value'], infile), 'r') as file:
            data = file.read()
    elif opt == 2:
        with open(os.path.join(DATA_DIR['value'], infile), 'r') as file:
            lines = file.readlines()
        lines[len(lines) - 1] = lines[len(lines) - 1] + "\n"
        items = sorted(lines, key=pinyin_sort.text2pinyin)
        data = ''.join(items)
    return data


def load_data_options():
    files = os.listdir(_DATA_DIR)
    dir_opts = []
    for f in files:
        full_path = os.path.join(_DATA_DIR, f)
        if os.path.isdir(full_path):
            dir_opts.append(f)
    return dir_opts


def reset_data_dir(dir):
    DATA_DIR['value'] = os.path.join(_DATA_DIR, dir)
    print("reset to %s " % DATA_DIR)


def load_all_member(opt=0):
    return load_file('all.txt', opt)


def load_attended(opt=0):
    return load_file('attended.txt', opt)


if __name__ == '__main__':
    print(load_attended())
    print("...")
    print(load_all_member())
