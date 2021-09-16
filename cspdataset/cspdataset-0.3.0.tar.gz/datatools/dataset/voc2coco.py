#!/usr/bin/env python
# encoding: utf-8
"""
# @Time    : 2021/8/30 8:56
# @Author  : xgy
# @Site    :
# @File    : voc_split.py
# @Software: PyCharm
# @python version: 3.7.4
"""

import shutil
import os
import json
import xml.etree.ElementTree as ET
import argparse
from loguru import logger


START_BOUNDING_BOX_ID = 1
# PRE_DEFINE_CATEGORIES = {'hat': 1, 'head': 2}
# PRE_DEFINE_CATEGORIES = None
img_types = [".jpg", ".JPG", ".JPEG", ".PNG", ".png"]


def get(root, name):
    vars = root.findall(name)
    return vars


def get_and_check(root, name, length):
    vars = root.findall(name)
    if len(vars) == 0:
        raise ValueError("Can not find %s in %s." % (name, root.tag))
    if 0 < length != len(vars):
        raise ValueError(
            "The size of %s is supposed to be %d, but is %d."
            % (name, length, len(vars))
        )
    if length == 1:
        vars = vars[0]
    return vars


def get_categories(xml_files):
    """Generate category name to id mapping from a list of xml files.
    
    Arguments:
        xml_files {list} -- A list of xml file paths.
    
    Returns:
        dict -- category name to id mapping.
    """
    classes_names = []
    for xml_file in xml_files:
        tree = ET.parse(xml_file)
        root = tree.getroot()
        for obj_item in root.findall("object"):
            name = obj_item.find("name").text
            if name not in classes_names:
                classes_names.append(name)

    # classes_names.sort()
    return {name: i + 1 for i, name in enumerate(classes_names)}


def convert(xml_files, json_path): 

    json_dict = {"images": [], "type": "instances", "annotations": [], "categories": []}

    categories = get_categories(xml_files)
    bnd_id = START_BOUNDING_BOX_ID
    for i, xml_file in enumerate(xml_files):
        tree = ET.parse(xml_file)
        root = tree.getroot()

        # todo 图片后缀不一定为 .jpg
        filename = os.path.basename(xml_file.split('.')[0] + '.jpg')
        # image_id = 100000 + i
        image_id = i
        width = int(root.find("size").find("width").text)
        height = int(root.find("size").find("height").text)
        image = {
            "file_name": filename,
            "height": height,
            "width": width,
            "id": image_id}
        json_dict["images"].append(image)

        for obj in root.findall("object"):
            try:
                bndbox = obj.find("bndbox")
                xmin = int(bndbox.find("xmin").text) - 1
                ymin = int(bndbox.find("ymin").text) - 1
                xmax = int(bndbox.find("xmax").text)
                ymax = int(bndbox.find("ymax").text)
                category_name = obj.find("name").text

                assert xmax > xmin
                assert ymax > ymin
                o_width = abs(xmax - xmin)
                o_height = abs(ymax - ymin)
                ann = {
                    "area": o_width * o_height,
                    "iscrowd": 0,
                    "image_id": image_id,
                    "bbox": [xmin, ymin, o_width, o_height],
                    "category_id": categories[category_name],
                    "id": bnd_id,
                    "ignore": 0,
                    "segmentation": [],
                }
                json_dict["annotations"].append(ann)
                bnd_id = bnd_id + 1
            except:
                print(xml_file) 

    for cate, cid in categories.items():
        cat = {"supercategory": "", "id": cid, "name": cate}
        json_dict["categories"].append(cat)

    # os.makedirs(os.path.dirname(json_path), exist_ok=True)
    # json_fp = open(json_path, "w", encoding='utf-8')
    # json_str = json.dumps(json_dict, ensure_ascii=False, indent=4)
    # json_fp.write(json_str)
    # json_fp.close()
    with open(json_path, "w", encoding="utf-8") as fw:
        json.dump(json_dict, fw, ensure_ascii=False, indent=4)


def read_txt(filename):
    '''
    读取单个txt文件，文件中包含多行，返回[]
    '''
    with open(filename, encoding='utf-8') as f:
        return f.readlines()


def drop_imageset(folder):
    """
    # 判断是否有 ImageSets/Main/ 文件夹
    # 平台导出数据集有，标准voc没有，需分别处理
    # 没有则需先创建该文件夹并生成trainval.txt
    Args:
        folder:

    Returns:

    """
    data_types = ["trainval"]
    if not os.path.exists(folder):
        os.makedirs(folder)
        for root, _, files in os.walk(folder):
            for xml_item in files:
                xml_name = os.path.splitext(xml_item)[0]
                with open("trainval.txt", "a+", encoding="utf-8") as fw:
                    fw.write(xml_name)
                    fw.write("\n")

    for root, _, files in os.walk(folder):
        num_txt = len(files)
        assert num_txt == 1, "there should be only one file in {}".format(folder)
        for txt_item in files:
            txt_name = os.path.splitext(txt_item)[0]
            data_types = [txt_name]

    return data_types


def get_args():
    parser = argparse.ArgumentParser(description="Convert Pascal VOC annotation to COCO format.")
    parser.add_argument("--voc_dir", help="Directory path to voc.", type=str, default='C:/Users/xgy/Desktop/voc_coco/voc')
    parser.add_argument("--out_coco_path", help="Directory path to COCO.", type=str, default='C:/Users/xgy/Desktop/voc_coco/cocotest')
    # parser.add_argument("--data_types", help="ImageSets/main中的txt.", type=list, default=['trainval'])
    args = parser.parse_args()
    return args


def main(voc_dir, out_coco_path):

    voc_xml_dir = os.path.join(voc_dir, 'Annotations')
    voc_img_dir = os.path.join(voc_dir, 'JPEGImages')
    voc_txt_dir = os.path.join(voc_dir, 'ImageSets', 'Main')

    data_types = drop_imageset(voc_txt_dir)
    # if data_types is None:
    #     data_types = ["trainval"]

    coco_json_dir = os.path.join(out_coco_path, 'Annotations')
    coco_img_dir = os.path.join(out_coco_path, "train")
    os.makedirs(coco_json_dir, exist_ok=True)
    os.makedirs(coco_img_dir, exist_ok=True)

    for t in data_types:
        # os.makedirs(os.path.join(coco_img_dir, t), exist_ok=True)
        xml_files = []
        txt_file = os.path.join(voc_txt_dir, t + '.txt')
        txt_list = read_txt(txt_file)
        for txt in txt_list:
            filename = txt.replace('\n', '')
            xml_file = os.path.join(voc_xml_dir, filename + ".xml")
            # img_file = os.path.join(voc_img_dir, filename + ".jpg")
            # to_img_file = os.path.join(coco_img_dir, t, filename + ".jpg")
            # to_img_file = os.path.join(coco_img_dir, filename + ".jpg")
            xml_files.append(xml_file)
            # 把原始图像复制到目标文件夹

            for img_type in img_types:
                img_file = os.path.join(voc_img_dir, filename + img_type)
                if os.path.exists(img_file):
                    to_img_file = os.path.join(coco_img_dir, filename + img_type)
                    shutil.copy(img_file, to_img_file)
                else:
                    logger.warning("can not find img {} {} in {}".format(filename, img_types, voc_img_dir))

        print("Number of xml files: {}".format(len(xml_files)))
        # 不限制 txt 文件的名称
        out_json = os.path.join(coco_json_dir, t + '.json')
        # if t == "trainval":
        #     out_json = os.path.join(coco_json_dir, "train" + '.json')
        # elif t == "test":
        #     out_json = os.path.join(coco_json_dir, "test" + '.json')
        # else:
        #     raise TypeError("ImageSets/Main/ can only contain trainval.txt or test.txt. not {}".format(t + ".txt"))
        convert(xml_files, out_json)
        print("Success: {}".format(out_json))


if __name__ == "__main__":
    args = get_args()
    # main(args.voc_dir, args.out_coco_path, args.data_types)
    main(args.voc_dir, args.out_coco_path)
